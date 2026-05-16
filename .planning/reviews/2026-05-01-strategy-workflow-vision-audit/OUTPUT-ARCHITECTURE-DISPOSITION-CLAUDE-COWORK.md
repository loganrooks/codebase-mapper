# Architecture Review Disposition

Reviewer: Claude (Cowork session, disposition role)
Date: 2026-05-01
Inputs: `OUTPUT-ARCHITECTURE.md` (Opus), `OUTPUT-ARCHITECTURE-CHATGPT.md` (GPT-5.5 Pro), `OUTPUT-ARCHITECTURE-CLAUDE-COWORK.md` (Cowork). Spot-checks performed against `cbm/cli.py`, `pyproject.toml`, `.research/run-phase-a-final-audit/`, `BUILD-LOG.md`, `VISION.md`, `docs/architecture.md`, `docs/contracts.md`, `.planning/STATE.md`, `.planning/CURRENT-PLAN.md`, `.codex/hooks.json`, `platform/codex/hooks.json`, `skills/`, and `git ls-files`.

This is a disposition, not a fourth review. It compares, meta-critiques, adjudicates, and recommends.

## Comparison summary

### Convergence (load-bearing agreements)

All three reviews agree on the following, and the code confirms each one:

1. The deterministic kernel is real, well-tested (`tests/test_cli.py` 1,800 lines against `cbm/cli.py` 4,525 lines, last reported 51 passing), and durable. Schemas, citation/freshness machinery, ledger append-only enforcement, gate composition, and run-directory layout are the protected core.
2. The runtime agent layer described in `VISION.md`, `RUNTIME-CONSTITUTION.md`, and `docs/architecture.md` Tier 2 does not exist in code. `skills/*.md` has seven prompt files; nothing in `cbm/` loads them (the only reference is `cbm/project_packs/agent_orchestration.json:11`, which points outward).
3. Several deterministic commands counterfeit agent output. `command_skeptic_review` (`cbm/cli.py:1344`), `review_dependency_graph` (`cbm/cli.py:1277`), `command_handoff` (`cbm/cli.py:3592`), `command_consult` (`cbm/cli.py:3362`), and `command_refine` produce artifacts stamped `produced_by: surface-mapper@0.1` / `skeptic@0.1` despite no agent running. The provenance is dishonest.
4. `cbm run` (`cbm/cli.py:4015`) is purely sequential in-process Python. No subprocess, no agent spawn. The name implies orchestration; the implementation does not deliver it.
5. The single load-bearing question is who launches the runtime agents — CBM (via subprocess) or an outer host platform.
6. The current fixture (`tests/fixtures/sample_repo/`, three files) is too small to demonstrate mapping adequacy; a small real benchmark (the open question names an MCP server) is required.
7. Hooks are useful adapter glue but should not be the source of correctness; CBM CLI validators are.
8. `docs/architecture.md` and `docs/contracts.md` describe a system that does not yet exist; the disjoint between as-built and as-designed needs to be made explicit.
9. The deterministic stand-ins — in their current form, stamped as if agents ran — should be either demoted, removed from `cbm run`, or relabeled.

### Divergences (real)

1. **What `cbm run` should become.** Opus: rename to `cbm baseline` or remove the `--mode` flag and stamp baseline-only. ChatGPT: keep the name, require `--backend deterministic|external|codex|claude` and add `run_completeness`. Cowork: keep the name, change the implementation under it via a producer registry mapping `artifact_type → producer`.

2. **Where subprocess management should live.** Opus prefers Option E — platform packs own the orchestrator, CBM owns the kernel + skill library; this rules out CBM owning a subprocess treadmill. ChatGPT prefers a hybrid: outer-agent orchestration immediately (`--backend external`), Codex/Claude subprocess backends later, all dispatched by `cbm run`. Cowork prefers Option D + structural surgery: producer registry inside the orchestrator, with backend choice (Codex CLI or Claude Code) gated on first verifying `codex exec` isolation semantics against `RUNTIME-CONSTITUTION.md` §17.

3. **Whether to split `cbm/cli.py`.** Cowork uniquely recommends splitting the 4,525-line monolith into `cbm/kernel/`, `cbm/commands/`, `cbm/orchestrator/`, `cbm/hooks/` so the kernel/agent/adapter boundary is visible at the file level. Opus and ChatGPT are silent on this.

4. **Run manifest as consumer contract.** ChatGPT uniquely proposes adding `run-manifest.json` as the machine-readable artifact list with schema versions, validation status, producer kind, and freshness. Opus and Cowork do not propose this.

5. **The coverage lie.** Opus uniquely identifies that `coverage.result.files_examined_directly` is set to `len(authorities)` in `coverage_block` (`cbm/cli.py:298`), where the authorities were never opened — only pattern-matched. The smoke run at `.research/run-phase-a-final-audit/surface-map.json` reports `files_examined_directly: 8`, and the Constitution defines this field as "files an agent or human opened and read." Cowork mentions coverage honesty in passing; ChatGPT does not catch it.

6. **Authority docs uncommitted.** ChatGPT uniquely catches that `VISION.md` and `RUNTIME-CONSTITUTION.md` are not in `git ls-files`. Verified: they exist in the working tree but were never committed on either local branch. Opus and Cowork cite them confidently as if committed.

7. **VISION revision as a live option.** Cowork uniquely puts "revising VISION downward to match the deterministic kernel" on the decision menu. Opus rejects pure-deterministic implicitly (Option A is dismissed). ChatGPT does not name it.

8. **Workflow drift as architectural signal.** Cowork uniquely reads `BUILD-LOG.md` (100 entries on 2026-05-01, all kernel-strictness slices) as evidence that the dev agent's slice-by-slice loop is itself an architectural problem — no slice's self-critique can ask the meta-question about VISION alignment. Opus reads the build log too but undercounts it ("~30 entries"); ChatGPT does not address it.

### Direct contradictions

- **BUILD-LOG count.** Opus: ~30 entries. Cowork: 100 entries. Cowork is correct (`grep -c '^## 2026-05-01' BUILD-LOG.md` → 100).
- **Authority doc commit status.** Opus and Cowork treat `VISION.md` / `RUNTIME-CONSTITUTION.md` as authoritative repo files. ChatGPT flags them as "not fetchable through the reviewed branch." ChatGPT is correct on commit status; Opus and Cowork are correct on working-tree content. Both observations matter — they describe different audiences (a working repo vs. a clone).

## Meta-critique per review

### `OUTPUT-ARCHITECTURE.md` (Opus)

**Evidence discipline — strong on the smoking-gun, sloppy on the inventory.** The forensic reading of `.research/run-phase-a-final-audit/surface-map.json` is the strongest single piece of evidence in any of the three reviews: line 6 carries `produced_by: surface-mapper@0.1`, line 32 reports `files_examined_directly: 8`, and the code path that produces both is identifiable down to `coverage_block` (`cbm/cli.py:298`) and `build_surface_map` (`cbm/cli.py:1071-1193`). All four citations verify exactly. But Opus also writes "BUILD-LOG.md has ~30 entries from 2026-05-01" — actually 100, off by 3.3×, suggesting Opus estimated rather than counted. And "command_skeptic_review (cbm/cli.py:1277-1354)" conflates `review_dependency_graph` (1277) with `command_skeptic_review` (1344). When line ranges matter, Opus is slightly imprecise.

**Framing — pushes back hard, lands on a sharp diagnosis.** "Mislabeled provenance is the central architectural defect" is the cleanest framing in any of the three reviews. It is upstream of every other confusion the project is trying to navigate. Opus does not echo `STATE.md` / `CURRENT-PLAN.md`. Independence is real here.

**Blind spots.** Misses the uncommitted `VISION.md` / `RUNTIME-CONSTITUTION.md` issue. Misses the 4,525-line monolithic file structure. Misses the §17 isolation question for `codex exec`. Treats Option B as a "treadmill" without engaging Cowork's nuance that the answer depends on a verifiable empirical question.

**Recommendation specificity — high.** Concrete next step #2 is a single PR with named functions to edit. The `producer_class` enum proposal is a real schema design move. The first-platform-pack slice in #5 is concrete enough to execute without further design.

**Internal consistency.** Diagnoses provenance as the central defect; recommends Option E because it removes the false-provenance problem. Tightly consistent.

**AI-pattern failures — minimal.** Some option-table cells hedge. Otherwise tight.

### `OUTPUT-ARCHITECTURE-CHATGPT.md` (GPT-5.5 Pro)

**Evidence discipline — uneven.** The single best catch in this review is that `VISION.md` and `RUNTIME-CONSTITUTION.md` are not in `git ls-files`. This is real, important, and missed by both other reviewers. But the review otherwise has very few line citations, never reads `.research/` smoke artifacts, and doesn't drill into specific functions. Several claims are loose: "README.md describes schema version 1.1" is misleading — README has a "What's new in v1.1" *changelog* section and explicitly says "this v1.2 amendment." The drift ChatGPT names is real (changelog framing in the README) but the way it's stated reads as a flat factual error.

**Framing — partially echoes the planning docs.** Sentences like "demote hooks" and "hooks are now in tension with later planning docs" use vocabulary already present in `.planning/CURRENT-PLAN.md:47-50` and `STATE.md:85-94`. The diagnosis happens to be correct, but ChatGPT may have absorbed the framing rather than re-deriving it. The prompt asked reviewers not to ratify the current agent's framing; the tonal echo is the kind of evidence that suggests partial ratification.

**Blind spots.** Doesn't drill into `command_skeptic_review`'s hardcoded `competing_reading` — names "deterministic Skeptic" at high level only. Doesn't catch the `files_examined_directly` lie. Doesn't read smoke artifacts. Doesn't analyze `BUILD-LOG.md` for workflow patterns. Treats `VISION` / `RUNTIME-CONSTITUTION` as possibly-absent from the start, which is the right inference *for a clone of the committed branch* but constrains the rest of the analysis (ChatGPT cannot reason from VISION's text the way Opus and Cowork do).

**Recommendation specificity — medium-high.** `run-manifest.json` (with named fields) is concrete and is a real contribution. `cbm validate-run` as a missing primary validator is concrete. The backend flag spec is concrete. Some recommendations remain abstract ("Stop expanding deterministic feature surface").

**Internal consistency — solid.** Recommends a kernel-plus-producer architecture; the hybrid (Option 4) recommendation is consistent with the diagnosis. The five-option table is more of a tour than an adjudication, though.

**AI-pattern failures — multiple.** Disposition tags (Useful / Good / Best target / Promising) on each option read as hedging without commitment — premature evenhandedness in the form of structured tradeoff matrices that don't actually decide. Several "preserves X while allowing Y" sentences. Some "consider X / consider Y" recommendations. The Findings section uses aphoristic claims ("scattered across artifact schemas, CLI contracts, and hook notes") without specific evidence.

### `OUTPUT-ARCHITECTURE-CLAUDE-COWORK.md` (Cowork)

**Evidence discipline — strongest of the three on inventory and structure.** The grep counts verify exactly (100 BUILD-LOG entries; byte-identical hooks.json files; seven skill files with zero loads in `cbm/`; lines 1277-1342 for `review_dependency_graph`, 1344-1383 for `command_skeptic_review`, 3641-3654 for handoff template prose, 3592 for handoff start, 3749 for the second hardcoded `competing_reading`). One small overcount: "32 console scripts" should be 31 (`pyproject.toml:17-47` has 31 entries). Otherwise precise.

**Framing — strongest pushback of the three.** Names the dev agent's slice-by-slice workflow as architecturally significant in itself: each slice's self-critique can only ask local questions, never the VISION-alignment question, so the build log accumulates kernel strictness while the runtime layer waits. This is a genuinely original framing. Explicitly puts "revising VISION downward" on the decision menu — the only review to do so.

**Blind spots.** Misses the uncommitted `VISION` / `RUNTIME-CONSTITUTION` issue (Cowork is reading from local working tree and explicitly skipped `SHARED-CONTEXT.md`). Misses the `files_examined_directly` coverage lie (mentions coverage honesty in passing; doesn't drill in). Skipping `SHARED-CONTEXT.md` is the right move for independence but means Cowork doesn't engage some of the explicit framings the prompt offered.

**Recommendation specificity — highest of the three on actionable next steps.** Producer-registry contract is specified concretely (`{ kind: "cli" | "agent", invoker, validator_chain }`). The `dev-fixture@x.y.z` provenance fix is a one-line-per-command change. The `codex exec` isolation verification step is itself the cheapest credible architectural research.

**Internal consistency.** Three diagnosed problems (missing runtime, counterfeit stand-ins, monolithic file structure) match three coupled solutions (producer registry, backend spike, file split). Tight.

**AI-pattern failures — minimal.** Some long-paragraph rambling. The "That is the bar" closing is mannered (and is a quoted echo of the prompt's closing line, which is mildly self-conscious). Few hedges.

**Independence under stress — strongest claim, sustained by the analysis.** Cowork explicitly states it didn't read other reviewers' outputs or `SHARED-CONTEXT.md`. The original framings (workflow drift, monolithic file structure, §17 isolation question) bear the claim out. Some risk of self-flattery from declaring independence; the substance survives the test.

## Adjudication of contested claims

**A1. How many BUILD-LOG entries?** Cowork: 100. Opus: ~30. **Verdict: Cowork.** `grep -c '^## 2026-05-01' BUILD-LOG.md` returns 100. The factual disagreement matters because it is load-bearing for Cowork's workflow-drift framing. With 100 single-day entries the local-optimization-treadmill diagnosis is hard to dismiss; with 30 it is still supportable but less stark.

**A2. Are `VISION.md` and `RUNTIME-CONSTITUTION.md` committed?** ChatGPT: not fetchable in the reviewed branch. Opus and Cowork: cited as if committed. **Verdict: ChatGPT on commit status; Opus and Cowork on content.** `git ls-files | grep -E '^VISION|^RUNTIME-CONSTITUTION'` returns nothing on either local branch (`main`, `phase-a-mvp-foundation`); the files exist only in the working tree. The correct disposition is: the content is real for any agent or reviewer with this working tree, but the project depends on uncommitted authority docs, which is itself a problem the user should fix.

**A3. The `files_examined_directly: 8` claim.** Opus uniquely catches this. **Verdict: Opus is correct and the defect is real.** `coverage_block` at `cbm/cli.py:298` sets `files_examined_directly` to its `examined` argument; `build_surface_map` at `cbm/cli.py:1168` calls `coverage_block(..., examined=len(authorities))`; and the authorities are pattern-matched filenames, not opened files. The smoke run reports `files_examined_directly: 8`, matching `len(authorities) == 8` for that run. Per `RUNTIME-CONSTITUTION.md` §15 (and §17 in current numbering, as the field is defined as files an agent or human opened directly), every interpretive claim referencing an authority in this set is undefensible. This is the strongest single piece of evidence that the deterministic kernel has stopped being a baseline and started being a substitute.

**A4. What should `cbm run` mean?** Opus: rename or re-scope. ChatGPT: keep the name, require `--backend`. Cowork: keep the name, dispatch through a producer registry. **Verdict: not contested at the level of substance.** All three want the same thing: `cbm run` should be the run lifecycle, and the producer of each artifact should be selectable / declarative. The synthesis is: keep `cbm run`, add a `--backend` flag (ChatGPT's user-facing knob), implement dispatch through a producer registry (Cowork's data structure), and ship platform packs that bundle backend + skills + hooks (Opus's distribution unit). This is one design, not three.

**A5. Where should subprocess management live?** Opus: in platform packs only. ChatGPT: in `cbm run`, gated by `--backend`. Cowork: in `cbm run`, gated by the producer registry, but pre-conditional on verifying `codex exec` isolation. **Verdict: empirically contingent.** The right answer depends on whether `codex exec` (or its analogues) provides the isolated-context subagent semantics that `RUNTIME-CONSTITUTION.md` §17 requires for the Skeptic. If it does, Hybrid (ChatGPT) and Producer Registry (Cowork) are equivalent in shape and CBM can host the orchestration. If it does not, then the Skeptic *must* run inside a host platform's native subagent system (Option E / Option C), and CBM's role for that producer is kernel-plus-skill-library only. The question is small, the test is reproducible, and the answer is unanswered. Cowork is right to make this the gating step.

**A6. Should `cbm/cli.py` be split?** Cowork: yes. Opus: silent. ChatGPT: silent. **Verdict: Cowork.** The 4,525-line monolith verifies; the kernel/agent/adapter dependency direction is correct in the code (no platform code is imported by `cbm/cli.py`) but invisible at the file level. Splitting the file is pure structural surgery with no functional payoff except making the architecture readable. The cheapest path is to couple the split to introducing the producer-registry dispatch — that work earns the boundary, then the boundary is made visible.

**A7. Producer registry vs. platform packs vs. backend flag.** **Verdict: not actually contested.** These are different framings of the same level of indirection. Producer registry is the data structure (Cowork). Platform packs are the distribution unit (Opus). Backend flag is the user-facing knob (ChatGPT). A coherent design has all three. The disagreement is presentational, not substantive.

**A8. What `produced_by` should say.** Opus: `cbm-baseline-surface@<v>` etc., plus a schema-level `producer_class` enum. ChatGPT: distinguish `deterministic_kernel` from `runtime_agent:<role>`. Cowork: `dev-fixture@x.y.z` for the templated stand-ins specifically. **Verdict: synthesizable.** The schema should grow a `producer_class` field (deterministic | agent | dev_fixture | human). Opus's enum design is the right granularity. Cowork's `dev-fixture` distinction is the right additional value because it separates "this baseline is honest about being deterministic" from "this is scaffolding output that exists for tests to depend on, not for real consumption."

## Actionable recommendations

Prioritized by leverage and reversibility. Highest-leverage and most-reversible items first.

**1. Fix the false-provenance lie now, in one PR, before any architecture decision.** Edit `cbm/cli.py`: change `produced_by` strings emitted by `command_surface` (1164), `command_authority_map` (via `build_authority_map`, 1220), `command_dependency_graph`, `command_verify_map`, `command_synthesis_index`, `command_skeptic_review` (1335, 1362), `command_trace_workflows`, `command_refine`, `command_approval_plan`, and `command_handoff` to honest strings. Recommended: `cbm-baseline/<role>@<version>` for honest deterministic outputs and `dev-fixture/<role>@<version>` for the templated stand-ins (skeptic, handoff card prose, refine, trace). Change `coverage_block` (`cbm/cli.py:292-303`) to set `files_examined_directly` to 0 by default, with `examined` populated only by paths an agent actually opened. Stop emitting the canned skeptic challenge with the hardcoded `competing_reading` (`cbm/cli.py:1294`, `cbm/cli.py:3749`); let unknown edges retain `claim_status: active` until a real Skeptic moves them.
   - *Rationale:* Adjudication A3, A8. All three reviews converge on this; Opus's evidence is decisive; the change is a single PR; leaving it unfixed corrupts every smoke artifact under `.research/`. No architecture decision is required to make this change.
   - *Falsification:* External reviewer reads any `.research/<run_id>/surface-map.json` and can tell deterministic-baseline from agent output by `produced_by` alone. `coverage.result.files_examined_directly` is 0 in all current artifacts. No artifact under `.research/` contains the phrase "The dependency graph should not be read as complete while unknown dependency edges remain unresolved" unless a real agent emitted it.

**2. Commit `VISION.md` and `RUNTIME-CONSTITUTION.md` to the repo.** `git add VISION.md RUNTIME-CONSTITUTION.md && git commit`. If the user does not want them committed, then `AGENTS.md`, `README.md`, `STATE.md`, and `docs/architecture.md` should stop referencing them as authoritative.
   - *Rationale:* Adjudication A2. ChatGPT's catch is real and important. The project's authority docs cannot be uncommitted while the code references them.
   - *Falsification:* `git ls-files | grep VISION.md` returns the file; cloning at HEAD includes it.

**3. Make the load-bearing decision: who launches runtime agents.** Pick one and write it into `.planning/STATE.md` as a single paragraph. Choices: (a) CBM owns subprocess management (Hybrid 4 / Option B); (b) host platform owns it, CBM is kernel + skill library + canonical platform pack (Option C / Option E); (c) producer registry inside CBM, with each entry choosing its own backend (Option D + E per Cowork). My adjudicated default: (c), because it is the synthesis (it is a kernel-internal data structure that supports both subprocess and outer-orchestrator producers per artifact); but (b) is correct if the answer to recommendation 4 below comes back wrong.
   - *Rationale:* Adjudication A4, A5, A7. The choice is the synthesis of all three reviews. The disagreement among reviews is presentational; the underlying design admits one resolution.
   - *Falsification:* `.planning/STATE.md` carries the decision. Subsequent slices either build a producer registry, or build a platform pack, but the next ten BUILD-LOG entries are coherent with one direction, not flailing between three.

**4. Verify `codex exec` isolation semantics before committing to it as a Skeptic backend.** Run a reproducible test: spawn a `codex exec` subprocess from inside an interactive Codex session and check whether the subprocess's context is isolated from the parent. Document the answer in `platform/codex/README.md`. If `codex exec` does not provide §17-compliant isolation, then the Skeptic backend cannot be CBM-launched Codex subprocesses, regardless of what the architecture decision says. The Surface Mapper backend can; the Skeptic must run inside the host platform's native isolated-subagent system.
   - *Rationale:* Adjudication A5. Cowork's question is the cheapest piece of architectural research that constrains the architecture decision in #3. Skipping it produces a decision made in the dark.
   - *Falsification:* `platform/codex/README.md` contains a reproducible test invocation and a yes/no answer. The architecture decision in #3 cites this answer.

**5. Stand up one real agent producer end-to-end on a real benchmark within two weeks.** Pick a small open-source MCP server (5-10k LOC, idiomatic Python). Pin its SHA in `tests/benchmarks/`. Wire one role (recommend Surface Mapper, since the deterministic version exists for diff comparison) through whatever backend was chosen in #3, with `skills/surface-mapping.md` loaded as system prompt and `--output-schema schemas/surface-map.schema.json` enforced on output. Verify the result passes `cbm gate-artifact` without templated patches; verify `coverage.files_examined_directly` reflects files the agent actually opened.
   - *Rationale:* Adjudications A3, A4, A5. All three reviews converge that the kernel cannot demonstrate VISION adequacy without a real agent run; the missing benchmark is the missing experiment. Two weeks is the timebox; if it slips beyond two weeks, the architecture decision in #3 should be re-evaluated.
   - *Falsification:* A `surface-map.json` exists under `.research/<run_id>/` for the benchmark repo, with `produced_by: <agent>@<version>` (not deterministic), citation-resolved at the benchmark SHA, validating against the kernel gates, with `coverage.files_examined_directly` matching files the agent actually opened. The deterministic version's output and the agent's output are diff-able; the diff has substantive interpretive content (different rationales, different challenge readings), not just whitespace.

**6. Add `--backend` and `run-manifest.json` to `cbm run`.** Even before #3 is fully resolved, ChatGPT's manifest proposal is a strict improvement. Add `--backend deterministic|external` immediately (the two implementations that exist). Add `run-manifest.json` to every run as the machine-readable artifact list with `schema_version`, `run_id`, `source_sha`, `goal`, `mode`, `backend`, `run_completeness`, artifact list with paths/types/schemas/validation status/freshness/producer, and the validation command used. Mark deterministic runs as `run_completeness: baseline_only`. Update `command_handoff` to reference the manifest.
   - *Rationale:* ChatGPT's unique contribution. Adjudication A4 makes `--backend` part of the synthesis; the manifest is the durable consumer-facing contract that does not depend on directory walking.
   - *Falsification:* `.research/<run_id>/run-manifest.json` exists for new runs. A downstream consumer can read the manifest and discover all artifacts, schemas, validation status, producer kind, and freshness without `find` or `ls`.

**7. Freeze kernel-strictness slices until #5 lands.** Cowork's workflow guard. Add a planning rule to `.planning/CURRENT-PLAN.md`: no merged slice that adds a new kernel-only gate, validator, or rejection rule until at least one real agent-produced artifact passes the existing gates on the benchmark repo (recommendation #5). Slices that directly support the runtime layer's introduction (producer registry, backend wiring, `--backend` flag, manifest) are exempt.
   - *Rationale:* Adjudication on workflow drift. With 100 BUILD-LOG entries on one day, almost all of them ratcheting kernel strictness, the dev agent's slice loop is itself feeding on the kernel's easy verifications. The architecture correction needs an explicit guard the per-slice self-critique cannot bypass.
   - *Falsification:* The next ten BUILD-LOG entries either advance the runtime layer, or are explicitly tagged as exemptions per the rule above. No new kernel-only gates merge until #5 has landed.

## Open questions for the user

These cannot be derived from evidence alone.

1. **Does the user want CBM to be a "type one command and walk away" tool, or a "kernel inside whatever agent session you're already in" tool?** This is the substantive value question behind the architecture decision. It points toward Hybrid 4 if the former and Option E if the latter. Recommendation 3 above defaults to the synthesis but the user's preference here is decisive when the synthesis fails to apply.

2. **Should `VISION.md` ship as committed authority, or remain a working-tree-only philosophical document?** ChatGPT's catch surfaces this. Committing it is recommended, but if the user wants it to remain a personal working document, then references to it from `AGENTS.md` and `README.md` should be removed or rewritten as "see local working notes."

3. **Which small MCP server (or comparable repo) becomes the first benchmark?** Already named as an open question in `STATE.md:103` and `CURRENT-PLAN.md`. Recommendation 5 timeboxes the answer to "before the runtime backend can be evaluated"; the actual choice (mcp-modelcontextprotocol-python? a specific server?) is the user's.

4. **Is "revising VISION downward" a live option?** Cowork puts this on the table. If the user is unwilling to invest in a runtime agent layer, the honest move is to revise VISION to describe what the deterministic kernel can deliver (a structural extractor + corpus + gates, not a hermeneutic instrument). I do not recommend this — VISION is the project's distinguishing commitment — but the question deserves an explicit yes/no, not silent attrition.

5. **What is the disposition policy for the live `.codex/hooks.json` in the repo root?** All three reviews flag the byte-identical duplicate at `.codex/hooks.json` and `platform/codex/hooks.json` as awkward. Either the root file is dogfood (document it in README as such, with a "do not copy this pattern to your project" note) or it should move to template-only. The user decides; the smell is real.

That is the disposition.
