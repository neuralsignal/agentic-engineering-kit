import { appendFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';

const BOT = 'dependabot[bot]';
const BOT_ID = 49699333;
const SHA = /^[0-9a-f]{40}$/;
const ACTION = /^(\s*(?:-\s+)?uses:\s*)([\w.-]+\/[\w./-]+)@([\w./-]+)(?:\s+#.*)?\s*$/;
const WORKFLOW = /^\.github\/workflows\/[\w.-]+\.ya?ml$/;
const NPM_FILE = /^(?:[\w.-]+\/)*package(?:-lock)?\.json$/;
const MAX_FILES = 25;
const MAX_PATCH_BYTES = 24_000;
const MAX_COMMITS = 10;
const RELEASE_REPOSITORIES = new Set([
  'neuralsignal/obsidian-import',
  'neuralsignal/obsidian-export',
  'neuralsignal/m365-brain',
]);

class Ineligible extends Error {}

function requireEligible(condition, reason) {
  if (!condition) throw new Ineligible(reason);
}

function onlyActionRefs(lines) {
  for (let index = 0; index < lines.length; index += 1) {
    const line = lines[index];
    if (!/^[+-]/.test(line)) continue;
    if (!line.startsWith('-') || !lines[index + 1]?.startsWith('+')) return false;
    const prior = ACTION.exec(line.slice(1));
    const next = ACTION.exec(lines[++index].slice(1));
    if (!prior || !next || next[1] !== prior[1] || next[2] !== prior[2] || next[3] === prior[3]) return false;
  }
  return true;
}

export function dependencyPatch(files, changedFiles, branch) {
  requireEligible(files?.length > 0 && files.length <= MAX_FILES && files.length === changedFiles,
    'The complete changed file set is unavailable or too large.');
  const actions = branch.startsWith('dependabot/github_actions/');
  const npm = branch.startsWith('dependabot/npm_and_yarn/');

  const patch = files.map(({ filename, patch, status, additions, deletions }) => {
    requireEligible(status === 'modified' && typeof patch === 'string', 'A complete modification patch is required for every file.');
    const lines = patch.split('\n');
    const added = lines.filter((line) => line.startsWith('+')).map((line) => line.slice(1));
    const removed = lines.filter((line) => line.startsWith('-')).map((line) => line.slice(1));
    requireEligible(additions === added.length && deletions === removed.length,
      'GitHub returned an incomplete file patch.');

    if (actions) {
      requireEligible(WORKFLOW.test(filename) && added.length > 0 && onlyActionRefs(lines),
        'GitHub Actions updates may change dependency refs only.');
    } else {
      requireEligible(npm && NPM_FILE.test(filename), 'The update changes files outside the supported dependency manifests.');
    }
    return { filename, patch };
  });
  const encoded = JSON.stringify(patch);
  requireEligible(Buffer.byteLength(encoded) <= MAX_PATCH_BYTES, 'The patch exceeds the automatic review size limit.');
  return encoded;
}

export function successfulJobs(jobs, required) {
  return Array.isArray(jobs) && required.every((name) => {
    const matches = jobs.filter((job) => job.name === name);
    return matches.length === 1 && matches[0].status === 'completed' && matches[0].conclusion === 'success';
  });
}

export function structuredVerdict(raw) {
  try {
    const parsed = JSON.parse(raw);
    if (['approve', 'manual'].includes(parsed?.verdict) && Object.keys(parsed).length === 2 &&
        typeof parsed.reason === 'string' && parsed.reason.trim() && parsed.reason.length <= 240) return parsed;
  } catch {
    // Missing or malformed output leaves the PR for manual review.
  }
  return null;
}

export function summaryReason(reason) {
  return reason.replace(/[\p{C}\s]+/gu, ' ').trim()
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;');
}

function verifiedBotCommits(compare, base, head) {
  const commits = compare.commits;
  return compare.behind_by === 0 && compare.merge_base_commit?.sha === base &&
    commits?.length > 0 && commits.length <= MAX_COMMITS && compare.ahead_by === commits.length &&
    commits.at(-1).sha === head && commits.every((commit, index) =>
      SHA.test(commit.sha) && commit.parents?.length === 1 &&
      commit.parents[0].sha === (index === 0 ? base : commits[index - 1].sha) &&
      commit.author?.id === BOT_ID && commit.author?.login === BOT && commit.commit?.verification?.verified === true);
}

export async function candidate(api, { repo, repoId, branch, workflow, required, runId, attempt }) {
  const [run, source] = await Promise.all([
    api(`actions/runs/${runId}`),
    api(`actions/workflows/${workflow}`),
  ]);
  requireEligible(run.workflow_id === source.id && run.path === `.github/workflows/${workflow}` &&
    run.run_attempt === attempt && run.event === 'pull_request' && run.conclusion === 'success' &&
    run.head_repository?.id === repoId && run.actor?.id === BOT_ID && run.actor?.login === BOT &&
    SHA.test(run.head_sha), 'The completed run is not an eligible Dependabot CI run.');

  const head = run.head_sha;
  // GitHub can omit PR associations on the single-run endpoint even for same-repo PRs.
  const runs = await api(`actions/workflows/${source.id}/runs?event=pull_request&head_sha=${head}&per_page=1`);
  const latest = runs.workflow_runs?.[0];
  requireEligible(latest?.id === runId && latest.run_attempt === attempt && latest.pull_requests?.length <= 1,
    'The completed run is superseded or linked to multiple pull requests.');
  const linked = latest.pull_requests[0];
  let number = linked?.number;
  if (!linked) {
    // The list endpoint can omit the association too. Resolve by the exact repository-owned head.
    requireEligible(/^dependabot\/(github_actions|npm_and_yarn)\//.test(run.head_branch),
      'The completed run has no eligible Dependabot branch.');
    const query = new URLSearchParams({ state: 'open', head: `${repo.split('/')[0]}:${run.head_branch}`, base: branch, per_page: '2' });
    const pulls = await api(`pulls?${query}`);
    requireEligible(pulls.length === 1 && pulls[0].head?.sha === head,
      'The completed run does not match a unique open pull request.');
    number = pulls[0].number;
  }
  requireEligible(Number.isSafeInteger(number) && number > 0, 'The completed run does not identify an eligible pull request.');
  const [pull, jobs, liveBase] = await Promise.all([
    api(`pulls/${number}`),
    api(`actions/runs/${runId}/attempts/${attempt}/jobs?per_page=100`),
    api(`git/ref/heads/${branch}`),
  ]);
  const base = linked ? linked.base?.sha : pull.base?.sha;
  if (linked) {
    requireEligible(linked.head?.ref === run.head_branch && linked.base?.ref === branch &&
      linked.head?.repo?.id === repoId && linked.base?.repo?.id === repoId && linked.head?.sha === head,
    'The linked pull request changed after CI.');
  } else {
    requireEligible(Date.parse(pull.created_at) <= Date.parse(run.created_at),
      'The pull request was opened after the CI attempt began.');
  }
  requireEligible(pull.state === 'open' && pull.draft === false && pull.user?.id === BOT_ID &&
    pull.user?.type === 'Bot' && pull.user?.login === BOT && pull.head?.repo?.id === repoId &&
    pull.base?.repo?.id === repoId && pull.head?.sha === head && pull.head?.ref === run.head_branch &&
    pull.base?.ref === branch &&
    SHA.test(base) && SHA.test(liveBase.object?.sha), 'The Dependabot pull request changed after CI.');
  requireEligible(jobs.total_count === jobs.jobs?.length && successfulJobs(jobs.jobs, required),
  'The latest CI attempt must contain every required job with a successful conclusion.');

  const compare = await api(`compare/${base}...${head}`);
  requireEligible(verifiedBotCommits(compare, base, head),
    'The candidate must contain only verified Dependabot commits on the tested base.');
  const patch = dependencyPatch(compare.files, pull.changed_files, pull.head.ref);
  const notes = JSON.stringify({ title: pull.title?.slice(0, 250), body: pull.body?.slice(0, 7000) });
  return { repo, number, head, base, patch, notes, stale: liveBase.object.sha !== base };
}

export async function requestRebase(api, publisher, number, head) {
  const route = `issues/${number}/comments`;
  const marker = `<!-- aek-dependabot-rebase:${head} -->`;
  const body = `@dependabot rebase\n\n${marker}`;
  for (let page = 1; page <= 10; page += 1) {
    const comments = await api(`${route}?per_page=100&page=${page}`);
    if (comments.some((comment) => comment.body === body &&
        (comment.user?.login === 'github-actions[bot]' || ['OWNER', 'MEMBER', 'COLLABORATOR'].includes(comment.author_association)))) {
      return false;
    }
    if (comments.length < 100) {
      await publisher(route, 'POST', { body });
      return true;
    }
  }
  throw new Ineligible('The comment history is too large to check for an existing rebase request.');
}

function githubApi(repo, token) {
  return async (route, method = 'GET', body = undefined) => {
    const response = await fetch(`https://api.github.com/repos/${repo}/${route}`, {
      method,
      redirect: 'error',
      headers: {
        accept: 'application/vnd.github+json',
        authorization: `Bearer ${token}`,
        'content-type': 'application/json',
        'user-agent': 'aek-dependabot-review',
        'x-github-api-version': '2022-11-28',
      },
      body: body === undefined ? undefined : JSON.stringify(body),
      signal: AbortSignal.timeout(20_000),
    });
    if (!response.ok) throw new Error(`GitHub API ${method} failed for ${route} (${response.status}).`);
    return response.json();
  };
}

async function main() {
  const env = process.env;
  const repo = env.GITHUB_REPOSITORY;
  const repoId = Number(env.GITHUB_REPOSITORY_ID);
  const runId = Number(env.CI_RUN_ID);
  const attempt = Number(env.CI_RUN_ATTEMPT);
  const branch = env.DEFAULT_BRANCH;
  const workflow = env.CI_WORKFLOW;
  const required = JSON.parse(env.REQUIRED_JOBS);
  const phase = process.argv[2];
  if (!/^neuralsignal\/[a-z0-9-]+$/.test(repo) || !/^[\w.-]+$/.test(branch) ||
      !/^[\w.-]+\.ya?ml$/.test(workflow) || ![repoId, runId, attempt].every((id) => Number.isSafeInteger(id) && id > 0) ||
      !Array.isArray(required) || required.length === 0 || new Set(required).size !== required.length ||
      !required.every((job) => typeof job === 'string' && job.length > 0) || !env.GH_TOKEN) {
    throw new Error('Invalid Dependabot review configuration.');
  }

  const api = githubApi(repo, env.GH_TOKEN);
  const summary = (message) => appendFile(env.GITHUB_STEP_SUMMARY, `${message}\n`);
  try {
    const result = await candidate(api, { repo, repoId, branch, workflow, required, runId, attempt });
    if (phase === 'review') {
      const { patch, notes, number, head, base, stale } = result;
      const reviewPatch = stale ? '' : patch;
      const reviewNotes = stale ? '' : notes;
      await appendFile(env.GITHUB_OUTPUT, `patch=${reviewPatch}\nnotes=${reviewNotes}\nnumber=${number}\nhead=${head}\nbase=${base}\nstale=${stale}\n`);
      return;
    }
    if (phase !== 'merge') throw new Error('Unknown Dependabot review phase.');
    requireEligible(String(result.number) === env.EXPECTED_PR && result.head === env.EXPECTED_HEAD &&
      result.base === env.EXPECTED_BASE, 'The pull request or base changed after Claude reviewed it.');
    requireEligible(!env.PUBLISHER_TOKEN || RELEASE_REPOSITORIES.has(repo),
      'A separate publisher credential is limited to the release-enabled factory consumers.');
    requireEligible(!RELEASE_REPOSITORIES.has(repo) || env.PUBLISHER_TOKEN,
      'A separate publisher is required to start the repository’s push workflows.');
    const publisher = githubApi(repo, env.PUBLISHER_TOKEN || env.GH_TOKEN);
    const freshBase = await api(`git/ref/heads/${branch}`);
    if (result.stale || freshBase.object?.sha !== result.base) {
      const requested = await requestRebase(api, publisher, result.number, result.head);
      await summary(requested ? `Requested a new Dependabot revision for PR #${result.number}.` :
        `A rebase was already requested for the stale head of PR #${result.number}.`);
      return;
    }
    requireEligible(env.APPROVED === 'true', 'The current revision does not have Claude approval.');
    const merge = await publisher(`pulls/${result.number}/merge`, 'PUT', {
      sha: result.head,
      merge_method: 'squash',
    });
    if (!merge.merged) throw new Error('GitHub did not merge the approved dependency update.');
    await summary(`Merged Dependabot PR #${result.number} after CI and Claude approval.`);
  } catch (error) {
    if (!(error instanceof Ineligible)) throw error;
    await summary(`Manual review required. ${error.message}`);
  }
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  await main();
}
