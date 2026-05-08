review_id: 2026-05-07-h1-minimum-useful-checkpoint
review_type: pass_claim_checkpoint
runner: claude-code-cli
reviewer_requirement: non_current
preferred_model: opus
permission_mode: auto
tools:
  - Read
  - Write
  - Edit
  - Bash
writes_allowed: true
allowed_write_roots:
  - .planning/reviews/2026-05-07-h1-minimum-useful-checkpoint/
additional_read_roots:
  - .
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
soft_budget_guidance: "This is a pass-claim checkpoint, not an open-ended audit. If review breadth grows, prioritize the nine questions in PROMPT.md and write explicit limitations."
