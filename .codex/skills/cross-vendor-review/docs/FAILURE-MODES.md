# Cross-Vendor Review Failure Modes

Status: initial catalogue

The runner treats Claude process success as necessary but not sufficient. The reviewer must write the declared outputs and remain inside allowed write roots.

## CLI And Auth

- `missing_cli`: `claude` is not on `PATH`.
- `unauthenticated_cli`: Claude exits or streams an auth/login error.
- `model_unavailable`: requested model is unavailable or rejected.
- `launch_failed`: command could not start or no raw stream was captured.

## Permission And Scope

- `permission_prompt_or_block`: the run stalls or reports permission denial.
- `wrote_outside_allowed_scope`: post-run git status or diff shows writes outside declared roots.
- `dirty_worktree_before_run`: checkpoint/pass-claim preflight sees a dirty tree without explicit allowance.
- `dirty_worktree_after_unexpected_files`: new files or modifications appear outside the allowed roots after run.
- `ambiguous_session`: no usable session name/id is available for explicit resume.

## Process And Stream

- `nonzero_exit`: Claude exits nonzero.
- `max_turns_or_budget`: final stream result reports max turns or max budget. These are supported for recovery but should not be default launch behavior.
- `malformed_stream_json`: stdout is not valid line-delimited JSON.
- `partial_expected_output`: required outputs exist but are empty or incomplete.
- `missing_expected_output`: required output file is missing or empty.

## Review Integrity

- `missing_reviewer_identity`: checkpoint/disposition output is present but has no actual reviewer model identity.
- `invalid_disposition`: disposition is not one of the spec's allowed values.
- `same_model_disallowed`: reviewer model matches a spec-declared disallowed model family.
- `fake_disposition_risk`: logs mention a disposition but the declared durable output does not contain it.

## Recovery Policy

For every failure:

- preserve raw logs;
- write `RECOVERY.md`;
- include captured files and expected output status;
- include a copy-ready explicit `--resume <session-name>` command only when safe;
- otherwise include a rerun command;
- do not synthesize final reviewer content from logs;
- do not fill reviewer identity, confidence, or disposition from the current agent.
