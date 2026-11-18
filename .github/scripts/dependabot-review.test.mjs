import assert from 'node:assert/strict';
import { test } from 'node:test';
import { candidate, dependencyPatch, requestRebase, structuredVerdict, summaryReason } from './dependabot-review.mjs';

const BASE = 'a'.repeat(40);
const HEAD = 'b'.repeat(40);
const NEXT = 'c'.repeat(40);
const WORKFLOW_FILE = '.github/workflows/ci.yml';
const BRANCH = 'dependabot/github_actions/actions/checkout-7';
const bot = { id: 49699333, login: 'dependabot[bot]', type: 'Bot' };
const repository = { id: 42 };
const base = { sha: BASE, ref: 'main', repo: repository };
const head = { sha: HEAD, ref: BRANCH, repo: repository };
const pull = {
  number: 166, base, head, user: bot, state: 'open', draft: false, changed_files: 1,
  created_at: '2026-01-01T00:00:00Z',
  title: 'Update checkout', body: '<details>Release notes for checkout</details>',
};
const file = {
  filename: WORKFLOW_FILE, status: 'modified', additions: 1, deletions: 1,
  patch: '@@ -5,2 +5,2 @@\n-      - uses: actions/checkout@v6\n+      - uses: actions/checkout@v7\n       - run: npm test',
};
const run = {
  id: 100, workflow_id: 10, path: WORKFLOW_FILE, run_attempt: 1, event: 'pull_request',
  conclusion: 'success', actor: bot, head_repository: repository, head_sha: HEAD, head_branch: BRANCH,
  created_at: '2026-01-01T01:00:00Z',
  pull_requests: [pull],
};
const jobs = [
  { name: 'lint', status: 'completed', conclusion: 'success' },
  { name: 'test', status: 'completed', conclusion: 'success' },
];
const comparison = {
  merge_base_commit: { sha: BASE }, behind_by: 0, ahead_by: 1, files: [file],
  commits: [{ sha: HEAD, parents: [{ sha: BASE }], author: bot, commit: { verification: { verified: true } } }],
};

function fixture(overrides) {
  const reads = {
    'actions/runs/100': { ...run, pull_requests: [] },
    'actions/workflows/ci.yml': { id: 10 },
    'pulls/166': pull,
    'pulls?state=open&head=example%3Adependabot%2Fgithub_actions%2Factions%2Fcheckout-7&base=main&per_page=2': [pull],
    'actions/runs/100/attempts/1/jobs?per_page=100': { total_count: jobs.length, jobs },
    [`actions/workflows/10/runs?event=pull_request&head_sha=${HEAD}&per_page=1`]: { workflow_runs: [run] },
    'git/ref/heads/main': { object: { sha: BASE } },
    [`compare/${BASE}...${HEAD}`]: comparison,
    ...overrides,
  };
  return candidate(async (route) => {
    assert.ok(route in reads, `Unexpected request ${route}`);
    return reads[route];
  }, { repo: 'example/test', repoId: 42, branch: 'main', workflow: 'ci.yml', required: ['lint', 'test'], runId: 100, attempt: 1 });
}

test('binds a genuine dependency patch to the tested revision and detects an advanced base', async () => {
  const ready = await fixture({});
  assert.deepEqual([ready.number, ready.head, ready.base, ready.stale], [166, HEAD, BASE, false]);
  assert.deepEqual(JSON.parse(ready.patch), [{ filename: WORKFLOW_FILE, patch: file.patch }]);
  assert.deepEqual(JSON.parse(ready.notes), { title: pull.title, body: pull.body });
  const stale = await fixture({ 'git/ref/heads/main': { object: { sha: NEXT } } });
  assert.equal(stale.stale, true);
  assert.equal(stale.base, BASE);
});

test('requires same-repository bot identity, matching workflow and complete successful latest CI', async () => {
  const jobRoute = 'actions/runs/100/attempts/1/jobs?per_page=100';
  const checks = [
    { 'actions/runs/100': { ...run, workflow_id: 11 } },
    { 'actions/runs/100': { ...run, head_repository: { id: 43 } } },
    { [`actions/workflows/10/runs?event=pull_request&head_sha=${HEAD}&per_page=1`]: { workflow_runs: [{ ...run, pull_requests: [pull, pull] }] } },
    { 'actions/runs/100': { ...run, event: 'push' } },
    { 'pulls/166': { ...pull, user: { ...bot, id: 7 } } },
    { 'pulls/166': { ...pull, head: { ...head, sha: NEXT } } },
    { [jobRoute]: { total_count: 2, jobs: [{ ...jobs[0], conclusion: 'skipped' }, jobs[1]] } },
    { [jobRoute]: { total_count: 1, jobs: [jobs[0]] } },
    { [jobRoute]: { total_count: 3, jobs } },
    { [`actions/workflows/10/runs?event=pull_request&head_sha=${HEAD}&per_page=1`]: { workflow_runs: [{ ...run, run_attempt: 2 }] } },
    { [`compare/${BASE}...${HEAD}`]: { ...comparison, commits: [{ ...comparison.commits[0], author: { id: 9 } }] } },
  ];
  for (const overrides of checks) await assert.rejects(fixture(overrides), { name: 'Error' });
});

test('recovers an omitted run association only for a unique PR at the exact tested head', async () => {
  const route = 'pulls?state=open&head=example%3Adependabot%2Fgithub_actions%2Factions%2Fcheckout-7&base=main&per_page=2';
  const noAssociation = { [`actions/workflows/10/runs?event=pull_request&head_sha=${HEAD}&per_page=1`]: { workflow_runs: [{ ...run, pull_requests: [] }] } };
  assert.equal((await fixture(noAssociation)).number, 166);
  await assert.rejects(fixture({ ...noAssociation, [route]: [pull, pull] }));
  await assert.rejects(fixture({ ...noAssociation, 'pulls/166': { ...pull, created_at: '2026-01-02T01:00:00Z' } }));
});

test('rejects moved or substituted action invocations, extra changes, and incomplete patches', () => {
  for (const patch of [
    file.patch.replace('actions/checkout@v7', 'outside/checkout@v7'),
    file.patch.replace('+      - uses:', '+        - uses:'),
    file.patch.replace('\n+      - uses:', '\n@@ -7,1 +7,1 @@\n+      - uses:'),
    `${file.patch}\n+      - run: curl example.invalid`,
  ]) {
    assert.throws(() => dependencyPatch([{ ...file, patch }], 1, BRANCH));
  }
  assert.throws(() => dependencyPatch([file], 2, BRANCH));
  assert.throws(() => dependencyPatch([{ ...file, patch: '' }], 1, BRANCH));
  assert.throws(() => dependencyPatch([{ ...file, filename: '.github/dependabot.yml' }], 1, BRANCH));
  const npm = 'dependabot/npm_and_yarn/plugins/test/minor-updates';
  assert.doesNotThrow(() => dependencyPatch([{ ...file, filename: 'plugins/test/package-lock.json' }], 1, npm));
  assert.throws(() => dependencyPatch([{ ...file, filename: 'plugins/test/index.ts' }], 1, npm));
});

test('requires an exact structured verdict and a display-safe reason', () => {
  assert.equal(structuredVerdict('{"verdict":"approve","reason":"Compatible version and successful CI."}')?.verdict, 'approve');
  assert.equal(structuredVerdict('{"verdict":"manual","reason":"Unsupported runner version."}')?.verdict, 'manual');
  for (const raw of ['', '[]', '{"verdict":"approve"}', '{"verdict":true,"reason":"OK"}',
    '{"verdict":"approve","reason":"<img>","extra":true}', '{"verdict":"manual","reason":"  "}']) {
    assert.equal(structuredVerdict(raw), null);
  }
  assert.equal(structuredVerdict('{"verdict":"approve","reason":"CI passed: compatible `input` — same contract."}')?.verdict, 'approve');
  assert.equal(summaryReason('`Quoted` <script>\n& another line.'), '`Quoted` &lt;script&gt; &amp; another line.');
});

test('requests one rebase per stale head and ignores a marker from an outsider', async () => {
  const calls = [];
  const comments = [{ body: `@dependabot rebase\n\n<!-- aek-dependabot-rebase:${HEAD} -->`, author_association: 'NONE' }];
  const read = async () => comments;
  const write = async (route, method, { body }) => {
    calls.push({ route, method });
    comments.push({ body, author_association: 'OWNER' });
  };
  assert.equal(await requestRebase(read, write, 166, HEAD), true);
  assert.equal(await requestRebase(read, write, 166, HEAD), false);
  assert.equal(await requestRebase(read, write, 166, NEXT), true);
  assert.deepEqual(calls, [{ route: 'issues/166/comments', method: 'POST' }, { route: 'issues/166/comments', method: 'POST' }]);
});
