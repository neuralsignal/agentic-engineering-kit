import assert from "node:assert/strict";
import { execFileSync } from "node:child_process";
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { test } from "node:test";
import { createCandidate, hasRequiredGate, mergePlan, verifyPublicationBranch, verifyResolution } from "./upstream-sync.mjs";

const oldCwd = process.cwd();

function git(args, input) {
  return execFileSync("git", args, { input, encoding: "utf8" }).trim();
}

function index(files) {
  for (const [path, content] of Object.entries(files)) {
    const object = git(["hash-object", "-w", "--stdin"], content);
    git(["update-index", "--add", "--cacheinfo", `100644,${object},${path}`]);
  }
  return git(["write-tree"]);
}

function fixture(run) {
  process.chdir(mkdtempSync(join(tmpdir(), "upstream-sync-fixture-")));
  try {
    git(["init", "--quiet", "--object-format=sha1"]);
    git(["config", "user.name", "Sync fixture"]);
    git(["config", "user.email", "sync@example.invalid"]);
    const commit = (parent, files) => {
      if (parent) git(["read-tree", parent]);
      const tree = index(files);
      return git(["commit-tree", tree, ...(parent ? ["-p", parent] : []), "-m", "Fixture"]);
    };
    run(commit);
  } finally {
    process.chdir(oldCwd);
  }
}

test("an upstream ancestor needs no candidate", () => {
  fixture((commit) => {
    const upstream = commit(null, { "feature.txt": "upstream feature\n" });
    const base = commit(upstream, { "fork.txt": "fork feature\n" });
    assert.deepEqual(mergePlan(base, upstream), { state: "current" });
  });
});

test("a clean candidate retains both sides and rejects an extra change", () => {
  fixture((commit) => {
    const common = commit(null, { "shared.txt": "common\n" });
    const base = commit(common, { "fork.txt": "fork feature\n" });
    const upstream = commit(common, { "upstream.txt": "upstream feature\n" });
    const plan = mergePlan(base, upstream);
    assert.equal(plan.state, "clean");
    assert.equal(git(["show", `${plan.tree}:fork.txt`]), "fork feature");
    assert.equal(git(["show", `${plan.tree}:upstream.txt`]), "upstream feature");
    verifyResolution(plan, plan.tree);
    const candidate = createCandidate({ base, upstream }, plan.tree);
    assert.equal(createCandidate({ base, upstream }, plan.tree), candidate);
    assert.equal(git(["rev-list", "--parents", "-n", "1", candidate]), `${candidate} ${base} ${upstream}`);
    git(["read-tree", plan.tree]);
    assert.throws(() => verifyResolution(plan, index({ "extra.txt": "unexpected\n" })), /conflicted paths/);
  });
});

test("a repair must resolve exactly the recorded conflict", () => {
  fixture((commit) => {
    const common = commit(null, { "shared file.txt": "common version\n" });
    const base = commit(common, { "shared file.txt": "fork version\n" });
    const upstream = commit(common, { "shared file.txt": "upstream version\n" });
    const plan = mergePlan(base, upstream);
    assert.equal(plan.state, "conflict");
    assert.deepEqual(plan.conflicts, ["shared file.txt"]);
    assert.throws(() => verifyResolution(plan, plan.tree), /every recorded conflict/);

    git(["read-tree", plan.tree]);
    const malformed = index({ "shared file.txt": "<<<<<<< fork\nchange\n=======\nother\n>>>>>>> upstream\n" });
    assert.throws(() => verifyResolution(plan, malformed), /markers remain/);

    git(["read-tree", plan.tree]);
    const resolved = { "shared file.txt": "fork version\nupstream version\n" };
    verifyResolution(plan, index(resolved));
    assert.throws(() => verifyResolution(plan, index({ ...resolved, "unexpected.txt": "extra\n" })), /conflicted paths/);
  });
});

test("incoming workflow and agent-control paths require separate review", () => {
  fixture((commit) => {
    const common = commit(null, { "shared.txt": "common\n" });
    const base = commit(common, { "fork.txt": "fork feature\n" });
    const upstream = commit(common, {
      ".github/workflows/release.yml": "workflow\n",
      "plugin/AGENTS.md": "instructions\n",
    });
    const plan = mergePlan(base, upstream);
    assert.equal(plan.state, "review");
    assert.deepEqual(plan.paths, [".github/workflows/release.yml", "plugin/AGENTS.md"]);
  });
});

test("only an effective strict named check from GitHub Actions is accepted", () => {
  const check = "Checks passed";
  const gate = (strict, context, integrationId) => [{
    type: "required_status_checks",
    parameters: {
      strict_required_status_checks_policy: strict,
      required_status_checks: [{ context, integration_id: integrationId }],
    },
  }];
  assert.equal(hasRequiredGate([], check), false);
  assert.equal(hasRequiredGate(gate(false, check, 15368), check), false);
  assert.equal(hasRequiredGate(gate(true, "Different check", 15368), check), false);
  assert.equal(hasRequiredGate(gate(true, check, null), check), false);
  assert.equal(hasRequiredGate(gate(true, check, 15368), check), true);
});

test("a retry after an interrupted push accepts only the exact reverified branch and managed PR", () => {
  const bot = "upstream-sync[bot]";
  const former = "a".repeat(40);
  const candidate = "b".repeat(40);
  const body = `Merges upstream \`${"c".repeat(40)}\` into fork \`${"d".repeat(40)}\`.\n\nMode: conflict.\n\n<!-- upstream-sync:${former} -->`;
  const pr = { author: { login: bot }, baseRefName: "main", isCrossRepository: false, headRefOid: candidate, body };
  assert.equal(verifyPublicationBranch([pr], candidate, candidate, bot), pr);
  assert.throws(() => verifyPublicationBranch([pr], candidate, former, bot), /branch or body was changed/);
  assert.throws(() => verifyPublicationBranch([{ ...pr, body: `${body}\n\nMaintainer note` }], candidate, candidate, bot), /body was changed/);
  assert.throws(() => verifyPublicationBranch([{ ...pr, isCrossRepository: true }], candidate, candidate, bot), /not owned/);
  assert.throws(() => verifyPublicationBranch([{ ...pr, author: { login: "maintainer" } }], candidate, candidate, bot), /not owned/);
});
