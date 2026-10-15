---
name: workstream-orchestrator
description: Plan the execution order of a multi-task change set — decide which tasks can run in parallel and which must serialize — by building a dependency graph from write-sets, semantic dependencies, and shared-resource contention. Use when a user hands over 3+ tasks/fixes/features to implement and asks for prioritization, parallelization, concurrency analysis, an execution plan, or "what can run at the same time". Also use before spawning parallel subagents on one codebase.
---

# Workstream Orchestrator

Turns an unordered list of change tasks into a safe execution plan: parallel **waves** of independent tasks, separated by verification gates, with every serialization justified by a concrete contention or dependency.

The failure this prevents: spawning parallel workers that edit the same file, or running a global sweep (audit/polish/refactor) before the markup it must judge even exists. Both produce merge churn, lost edits, and rework that costs more than the parallelism saved.

## When to use

- The user supplies a backlog of fixes/features and asks you to prioritize or parallelize it.
- You are about to spawn two or more subagents that will write to one repository.
- A critique/audit produced N issues and you must decide the order to close them.

Do not use for a single task, or for tasks in unrelated repositories.

## The algorithm

### Step 1 — Inventory every task

For each task record five facts. Guessing here poisons the whole plan; read the code to confirm write-sets.

1. **Objective** — one sentence, the user-visible outcome.
2. **Write-set** — every file/directory the task will create, modify, or delete. Be exhaustive; include generated-adjacent files (tokens, CSS, config) and assets.
3. **Read-set** — files it depends on but does not change.
4. **Semantic dependency** — does this task consume another task's *output* as its input? (States before copy about those states; a component before the styles that target it; a token rename before consumers.) Name the producing task.
5. **Sweep class** — `scoped` (bounded write-set) or `global-sweep` (touches shared tokens, global CSS, or markup across many files: audits, polish passes, repo-wide refactors, dependency bumps).

### Step 2 — Build the edges

Three edge types. A task may only share a wave with tasks it shares **no** edge with.

- **Semantic edge** `X → Y`: Y consumes X's output. Always serialize, X first.
- **Contention edge** `X ↔ Y`: write-sets intersect on a real source file. Serialize; order so the task producing the more stable base runs first. *Generated* artifacts (build output, lockfiles both regenerate) are not contention.
- **Sweep edge** `everything → S`: a global-sweep task S must see the final markup of every task it judges, so every scoped task that writes markup S will touch gets an edge into S. Sweeps serialize among themselves and run last.

### Step 3 — Compute the waves

Wave 1 = tasks with no incoming edges. Wave N = tasks whose predecessors all sit in waves < N **and** whose write-sets are pairwise disjoint within the wave. Disjointness inside a wave is as mandatory as the edge rule: two tasks with no edge but a shared file still corrupt each other.

### Step 4 — Find the bottlenecks and say them out loud

Name the shared resources that forced serialization — typically the design-token/CSS file, shared shell components, app config, and the schema/migration layer. These are the project's true bottlenecks; the plan's job is to keep writers off them simultaneously, not to pretend they can be parallelized. Report:

- the **critical path** (longest edge chain) — this bounds total wall time, so shortening it matters more than widening any wave;
- the **contention list** — each shared file and which tasks fought over it;
- the **wave width** — how many workers each wave actually supports.

### Step 5 — Insert verification gates

Between every wave, run the cheapest check that proves the wave's writers didn't collide: typecheck/build, then a smoke test of the touched surface (test suite, or a rendered/visual check for UI). Parallel writers cannot see each other's edits, so the gate is what catches a wave that silently broke an invariant. Never chain two waves without one.

### Step 6 — Emit the plan

Output exactly this shape so it is executable as-is:

```
WAVE 1 (parallel): <task> [owns: files] ∥ <task> [owns: files]
  gate: <command / check>
WAVE 2 (parallel): ...
  gate: ...
WAVE n (serial):  <task> [owns: files]
  gate: ...
Critical path: A → B → C
Contention: <file> fought over by <tasks>; <file> by <tasks>
```

Then state, in one line each: why the parallel pairs are safe (disjoint write-sets, no semantic edge), and why each serialized pair could not be parallelized (name the edge type and the file or output).

## Hard rules

1. Never put two tasks that write the same source file in one wave. No exceptions for "different sections of the file" — editors collide at the file level.
2. Never parallelize a global-sweep with anything. It rewrites what others are mid-writing.
3. Semantic order beats file disjointness: even with disjoint write-sets, copy about a state ships after the state exists.
4. Cap a wave at the number of genuinely independent critical paths. Extra workers beyond that add coordination cost and zero throughput.
5. If two tasks conflict only through a file one of them will *delete*, the deleter runs first — the other task then edits a file that exists for a reason.
6. When a plan has only one wave, say so plainly: the tasks are coupled and parallelism was examined and rejected, not overlooked.

## Worked example (Dresroza landing, 2026-10-11)

Six critique fixes: `harden` (waitlist endpoint + real form states), `clarify` (success-card copy/echo/reset), `bolder` (mount thread stage, fix transparent PNG, author steps 3–4 art), `adapt` (pin edges + reduced motion), `audit` (contrast/palette sweep), `polish` (meta, assets, spacing/type sweep).

- Semantic: harden → clarify (copy describes the states harden builds); bolder → adapt (adapt fixes reduced-motion and pin behaviour around the stage bolder mounts).
- Contention: harden∩clarify on `App.tsx` + `SceneFinalCTA.tsx`; bolder∩adapt on `SceneHowItWorks.tsx` + `SceneHero.tsx`.
- Sweeps: audit and polish both rewrite `index.css` and component classes → all markup tasks edge into them; they serialize last.

Result:

```
WAVE 1 (parallel): harden [App.tsx, SceneFinalCTA.tsx, api/waitlist] ∥ bolder [SceneHero.tsx, SceneHowItWorks.tsx visuals, public/, src/three/]
  gate: tsc --noEmit && vite build && visual smoke of hero + form
WAVE 2 (parallel): clarify [SceneFinalCTA.tsx, App.tsx success path] ∥ adapt [SceneHowItWorks.tsx mechanics, index.css motion, SceneHero.tsx]
  gate: tsc --noEmit && vite build && reduced-motion + mobile smoke
WAVE 3 (serial):  audit [index.css tokens, component colour/border/shadow classes]
  gate: contrast re-measure on CTA + badges
WAVE 4 (serial):  polish [index.html, public/, spacing/type across components]
  gate: full build + re-run critique
Critical path: harden → clarify → audit → polish  (and bolder → adapt → audit → polish)
Contention: App.tsx + SceneFinalCTA.tsx (harden/clarify); SceneHowItWorks.tsx + SceneHero.tsx (bolder/adapt); index.css (audit/polish)
```

Two independent critical paths of equal length is what made wave 1 and wave 2 two-wide; nothing wider was safe.

## The dedicated agent

`workstream-planner` ships beside this skill as a read-only planning agent. For large backlogs (8+ tasks) or when the main context must stay free for implementation, delegate Step 1–4 to it: spawn it with the task list and repo path, and it returns the inventory, edges, waves, critical path, and contention list in the Step 6 shape. Verify its write-sets against the code before trusting them — a plan built on a guessed write-set is worse than no plan. For small backlogs, run the algorithm inline; spawning an agent to plan three tasks is overhead pretending to be rigor.
