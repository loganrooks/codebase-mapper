# Cross-Vendor Review Spec Contract

Status: initial generic contract

`REVIEW-SPEC.md` defines the review packet. The runner reads it to configure Claude Code launch, output verification, raw-log cleanup, and recovery.

The format is intentionally small YAML. Do not turn this into a broad review ontology without evidence from a real failure.

`review_type` is an open string, not an enum. The examples below are starter patterns only. If a packet needs a review type not listed here, name it plainly and put the real instructions in `PROMPT.md`.

## Minimal Spec

```yaml
review_id: 2026-05-08-example-review
review_type: <open-purpose-label>
runner: claude-code-cli
reviewer_requirement: cross_vendor
preferred_model: opus
writes_allowed: true
allowed_write_roots:
  - .planning/reviews/2026-05-08-example-review/
required_outputs:
  - OUTPUT.md
decision_required: false
```

Fields:

- `review_id`: stable id for the packet.
- `review_type`: open review-purpose label. The runner treats this mostly as data; prompts and required outputs carry the real semantics.
- `runner`: currently `claude-code-cli`.
- `reviewer_requirement`: `cross_vendor`, `non_current`, `external`, or a plain-language requirement.
- `preferred_model`: Claude model alias or id, for example `opus` or `sonnet`.
- `writes_allowed`: must be `true` for direct reviewer-written outputs.
- `allowed_write_roots`: directories the reviewer may modify.
- `required_outputs`: files that must exist and be non-empty after the run.
- `decision_required`: whether a disposition-style decision is expected.

## Optional Runner Fields

```yaml
permission_mode: auto
tools:
  - Read
  - Write
  - Edit
  - Bash
additional_read_roots:
  - .
raw_logs:
  retain_on_success: false
  retain_on_failure: true
soft_budget_guidance: "If the review is becoming too broad, write the strongest supported findings and explicit limitations instead of continuing indefinitely."
```

Defaults:

- `permission_mode: auto`
- `tools: [Read, Write, Edit, Bash]`
- `raw_logs.retain_on_success: false`
- `raw_logs.retain_on_failure: true`
- no hard `max_turns`
- no hard `max_budget_usd`

Hard limits may be declared explicitly for a cheap scratch probe, but they are not default review behavior:

```yaml
max_turns: 8
max_budget_usd: 1.00
```

Use hard limits sparingly; they can cut off a review before required artifacts are written.

## Pattern Notes

Use these as shape hints, not templates that must all be read or copied.

- Checkpoint or pass-claim review: set `decision_required: true`, declare the decision output files, and list `allowed_dispositions` if the packet has a finite disposition vocabulary.
- Architecture or design review: usually one `OUTPUT.md` or `REVIEW.md`; the prompt defines the architecture question and evidence set.
- Artifact or provenance audit: usually one `REVIEW.md`; the prompt names artifacts, provenance claims, and verification questions.
- Code or diff review: usually one `REVIEW.md`; the prompt names the diff base, changed files, or commands to inspect.
- Unknown future review type: choose a clear `review_type`, declare outputs, allowed write roots, and reviewer requirement; put all domain semantics in `PROMPT.md`.

## Example: Decision Review

```yaml
review_id: 2026-05-08-decision-review
review_type: pass_claim_checkpoint
runner: claude-code-cli
reviewer_requirement: cross_vendor
preferred_model: opus
permission_mode: auto
tools:
  - Read
  - Write
  - Edit
  - Bash
writes_allowed: true
allowed_write_roots:
  - .planning/reviews/2026-05-08-decision-review/
required_outputs:
  - CHECKPOINT.md
  - DISPOSITION.md
decision_required: true
allowed_dispositions:
  - accept
  - accept_with_blockers
  - revise
  - reject
disallowed_reviewer_model_families:
  - gpt-5
  - codex
raw_logs:
  retain_on_success: false
  retain_on_failure: true
```

For checkpoint reviews, the verifier expects disposition output to include a real reviewer model identity and an allowed disposition. It does not create or infer either value.

## Example: Open-Ended Review

```yaml
review_id: 2026-05-08-open-review
review_type: artifact_provenance_audit
runner: claude-code-cli
reviewer_requirement: cross_vendor
preferred_model: opus
allowed_write_roots:
  - .planning/reviews/2026-05-08-open-review/
required_outputs:
  - REVIEW.md
decision_required: false
```

The prompt decides what to inspect. The runner only manages execution and recovery.
