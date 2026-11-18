// The workflow runs this from its trusted checkout. Publication independently verifies the bundle.
import { spawnSync } from "node:child_process";
import { appendFileSync, mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

const branch = "main";
const candidateRef = "refs/heads/upstream-sync-candidate";
const syncBranch = "automation/upstream-sync";
const protectedPaths = [
  ".github", ".claude", ".mcp.json", ".gitmodules", ".gitattributes",
  ":(glob)**/AGENTS.md", ":(glob)**/CLAUDE.md", ":(glob)**/.mcp.json",
  ":(glob)**/.claude/**", ":(glob)**/.gitattributes",
];
const conflictMarker = /^(?:<{7,} |\|{7,} |={7,}$|>{7,} )/m;

function run(command, args, { env, allowed = [0] } = {}) {
  const result = spawnSync(command, args, { encoding: "utf8", env, maxBuffer: 16 * 1024 * 1024 });
  if (result.error) throw result.error;
  if (!allowed.includes(result.status)) {
    throw new Error(`${command} ${args[0]} failed (${result.status}): ${result.stderr.trim()}`);
  }
  return { output: result.stdout, status: result.status };
}

function git(...args) {
  return run("git", ["-c", "core.hooksPath=/dev/null", ...args]).output.trim();
}

function names(...args) {
  return run("git", args).output.split("\0").filter(Boolean);
}

function output(name, value) {
  appendFileSync(process.env.GITHUB_OUTPUT, `${name}=${value}\n`);
}

function summary(lines) {
  appendFileSync(process.env.GITHUB_STEP_SUMMARY, `${lines.join("\n")}\n`);
}

export function mergePlan(base, upstream) {
  if (run("git", ["merge-base", "--is-ancestor", upstream, base], { allowed: [0, 1] }).status === 0) {
    return { state: "current" };
  }
  const incoming = names("diff", "--name-only", "-z", `${base}...${upstream}`, "--", ...protectedPaths);
  if (incoming.length) {
    return { state: "review", paths: incoming };
  }
  const result = run("git", ["merge-tree", "--write-tree", "--name-only", "--no-messages", "-z", base, upstream], {
    allowed: [0, 1],
  });
  const [tree, ...files] = result.output.split("\0").filter(Boolean);
  const conflicts = [...new Set(files)].sort();
  if (!/^[a-f0-9]{40}$/.test(tree) || (result.status === 1) !== (conflicts.length > 0)) {
    throw new Error("Git merge did not report the expected tree and conflict paths.");
  }
  const protectedChanges = names("diff", "--name-only", "-z", base, tree, "--", ...protectedPaths);
  if (protectedChanges.length) {
    return { state: "review", paths: protectedChanges };
  }
  return { state: conflicts.length ? "conflict" : "clean", tree, conflicts };
}

export function verifyResolution(plan, candidateTree) {
  const changes = new Set(names("diff", "--name-only", "-z", plan.tree, candidateTree));
  if (changes.size !== plan.conflicts.length || plan.conflicts.some((path) => !changes.has(path))) {
    throw new Error("Repair must resolve every recorded conflict and change only conflicted paths.");
  }
  for (const path of changes) {
    const entry = git("ls-tree", candidateTree, "--", `:(literal)${path}`);
    if (entry && !/^100(?:644|755) blob /.test(entry)) {
      throw new Error(`Repair introduced an unsupported file type at ${JSON.stringify(path)}.`);
    }
    if (entry && conflictMarker.test(git("show", `${candidateTree}:${path}`))) {
      throw new Error(`Conflict markers remain at ${JSON.stringify(path)}.`);
    }
  }
  git("diff", "--check", plan.tree, candidateTree);
}

function fetchInputs() {
  const upstreamRepo = process.env.UPSTREAM_REPOSITORY;
  const forkRepo = process.env.GITHUB_REPOSITORY;
  if (!/^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/.test(upstreamRepo) || upstreamRepo === forkRepo) {
    throw new Error("Invalid upstream repository mapping.");
  }
  git("fetch", "--no-tags", "origin", `+refs/heads/${branch}:refs/remotes/origin/${branch}`);
  git("fetch", "--no-tags", `https://github.com/${upstreamRepo}.git`, `+refs/heads/${branch}:refs/upstream/${branch}`);
  return {
    base: git("rev-parse", `refs/remotes/origin/${branch}`),
    upstream: git("rev-parse", `refs/upstream/${branch}`),
  };
}

function prepare(stateDir) {
  const { base, upstream } = fetchInputs();
  if (git("rev-parse", "HEAD") !== base) {
    throw new Error("Fork main moved since checkout. Run again on the current main.");
  }
  const plan = mergePlan(base, upstream);
  const paths = plan.paths ?? plan.conflicts ?? [];
  summary(["## Upstream sync", `Fork: \`${base}\``, `Upstream: \`${upstream}\``,
    `Result: **${plan.state}**`, ...paths.map((path) => `- \`${JSON.stringify(path)}\``)]);
  output("state", plan.state);
  output("base", base);
  output("upstream", upstream);
  output("conflicts", JSON.stringify(plan.conflicts ?? []));
  if (process.env.DRY_RUN === "true" || !plan.tree) return;
  mkdirSync(stateDir, { recursive: true });
  writeFileSync(join(stateDir, "plan.json"), JSON.stringify({ ...plan, base, upstream }));
  git("read-tree", "--reset", "-u", plan.tree);
}

export function createCandidate(plan, tree) {
  const date = "@" + Math.max(...[plan.base, plan.upstream].map(
    (ref) => Number(git("show", "-s", "--format=%ct", ref)),
  )) + " +0000";
  return run("git", [
    "-c", "user.name=Upstream Sync", "-c", "user.email=upstream-sync@users.noreply.github.com",
    "commit-tree", tree, "-p", plan.base, "-p", plan.upstream,
    "-m", `Merge upstream main at ${plan.upstream}`,
  ], { env: { ...process.env, GIT_AUTHOR_DATE: date, GIT_COMMITTER_DATE: date } }).output.trim();
}

function finish(stateDir) {
  const plan = JSON.parse(readFileSync(join(stateDir, "plan.json"), "utf8"));
  if (git("rev-parse", "HEAD") !== plan.base) throw new Error("Conflict repair changed HEAD.");
  git("add", "--all");
  const tree = git("write-tree");
  verifyResolution(plan, tree);
  const candidate = createCandidate(plan, tree);
  git("update-ref", candidateRef, candidate);
  git("bundle", "create", join(stateDir, "candidate.bundle"), candidateRef, `^${plan.base}`, `^${plan.upstream}`);
  output("candidate", candidate);
}

function gh(...args) {
  return run("gh", args).output.trim();
}

export function hasRequiredGate(rules, status) {
  return rules.some(({ type, parameters }) =>
    type === "required_status_checks" && parameters.strict_required_status_checks_policy &&
    parameters.required_status_checks.some(({ context, integration_id }) =>
      context === status && integration_id === 15368));
}

function checkRules() {
  const repo = process.env.GITHUB_REPOSITORY;
  const status = process.env.REQUIRED_CHECK;
  const rules = JSON.parse(gh("api", `repos/${repo}/rules/branches/${branch}`));
  if (!hasRequiredGate(rules, status)) {
    throw new Error(`Set an effective strict GitHub Actions branch ruleset for '${status}' before publishing.`);
  }
  const { allow_auto_merge, allow_merge_commit } = JSON.parse(gh("api", `repos/${repo}`));
  if (!allow_auto_merge || !allow_merge_commit) {
    throw new Error("Enable GitHub auto-merge and merge commits before publishing.");
  }
}

const managedBody = /^Merges upstream `[a-f0-9]{40}` into fork `[a-f0-9]{40}`\.\n\nMode: (?:clean|conflict)\.\n\n<!-- upstream-sync:([a-f0-9]{40}) -->$/;

export function verifyPublicationBranch(prs, old, candidate, bot) {
  const [existing] = prs;
  if (prs.length > 1) throw new Error("Multiple open sync PRs exist.");
  if (!existing) return existing;

  const marker = managedBody.exec(existing.body?.trimEnd() ?? "")?.[1];
  if (existing.baseRefName !== branch || existing.isCrossRepository !== false ||
      existing.author?.login !== bot || existing.headRefOid !== old ||
      !marker || (marker !== old && old !== candidate)) {
    throw new Error("The open sync PR is not owned by the publisher or its branch or body was changed.");
  }
  return existing;
}

function publish(bundle) {
  const repo = process.env.GITHUB_REPOSITORY;
  const { base, upstream } = fetchInputs();
  if (base !== process.env.EXPECTED_BASE || upstream !== process.env.EXPECTED_UPSTREAM) {
    throw new Error("A ref changed after preparation. Run again to validate the new pair.");
  }
  const plan = mergePlan(base, upstream);
  if (!plan.tree) throw new Error(`Candidate failed publication revalidation: ${plan.state}.`);
  git("bundle", "verify", bundle);
  git("fetch", "--no-tags", bundle, `+${candidateRef}:${candidateRef}`);
  const [candidate, first, second, extra] = git("rev-list", "--parents", "-n", "1", candidateRef).split(" ");
  if (candidate !== process.env.EXPECTED_CANDIDATE || first !== base || second !== upstream || extra) {
    throw new Error("Invalid candidate SHA or merge parents.");
  }
  const tree = git("rev-parse", `${candidate}^{tree}`);
  verifyResolution(plan, tree);
  if (createCandidate({ base, upstream }, tree) !== candidate) {
    throw new Error("Candidate does not match the deterministic merge commit.");
  }
  checkRules();

  const prs = JSON.parse(gh("pr", "list", "--repo", repo, "--head", syncBranch, "--state", "open",
    "--json", "number,headRefOid,baseRefName,isCrossRepository,author,body"));
  const bot = `${process.env.APP_SLUG}[bot]`;
  const marker = (sha) => `<!-- upstream-sync:${sha} -->`;
  const ref = `refs/heads/${syncBranch}`;
  const old = git("ls-remote", "origin", ref).split(/\s/)[0];
  const existing = verifyPublicationBranch(prs, old, candidate, bot);
  if (!existing && old && old !== candidate) {
    git("fetch", "--no-tags", "origin", ref);
    if (run("git", ["merge-base", "--is-ancestor", old, base], { allowed: [0, 1] }).status !== 0) {
      throw new Error("The sync branch contains unmerged work without a bot-owned open PR.");
    }
  }
  const body = `Merges upstream \`${upstream}\` into fork \`${base}\`.\n\nMode: ${plan.state}.\n\n${marker(candidate)}`;
  if (old !== candidate) {
    git("-c", "credential.helper=", "-c", "credential.helper=!gh auth git-credential",
      "push", `--force-with-lease=${ref}:${old}`, "origin", `${candidate}:${ref}`);
  }
  if (existing && existing.body?.trimEnd() !== body) {
    gh("api", "--method", "PATCH", `repos/${repo}/pulls/${existing.number}`, "--raw-field", `body=${body}`);
  }
  const pr = existing ? String(existing.number)
    : gh("pr", "create", "--repo", repo, "--base", branch, "--head", syncBranch,
      "--title", "Sync upstream", "--body", body);
  gh("pr", "merge", pr, "--repo", repo, "--auto", "--merge", "--match-head-commit", candidate);
  summary(["## Upstream sync PR", pr, `Candidate: \`${candidate}\``]);
}

if (process.argv[1] && pathToFileURL(process.argv[1]).href === import.meta.url) {
  try {
    const [command, argument] = process.argv.slice(2);
    switch (command) {
      case "prepare": prepare(argument); break;
      case "finish": finish(argument); break;
      case "check-rules": checkRules(); break;
      case "publish": publish(argument); break;
      default: throw new Error("Expected prepare, finish, check-rules or publish.");
    }
  } catch (error) {
    console.error(error.message);
    process.exitCode = 1;
  }
}
