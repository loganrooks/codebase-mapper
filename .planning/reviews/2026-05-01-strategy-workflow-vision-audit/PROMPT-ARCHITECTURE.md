# Prompt: Architecture and Product Shape Review

You are an independent architecture reviewer for the CBM project.

Read `SHARED-CONTEXT.md`, then inspect the repo as needed. Do not assume the current agent's diagnosis is correct. Do not assume hooks are either good or bad. Do not assume the deterministic CLI is either sufficient or misguided. Diagnose from evidence.

## Task

Review the current CBM product/execution architecture.

Address:

- What is the product boundary of CBM?
- How should another project or agent request codebase mapping information from CBM?
- What should `cbm run` mean?
- What artifacts should be produced, where should they live, and what contract should consumers depend on?
- Which parts of the current implementation are a durable kernel versus accidental scaffolding?
- What is the right relationship between deterministic commands, runtime agents, validation gates, hooks, and platform adapters?
- What are the plausible architecture options from here?
- What decision should be made before the next implementation slice?

Consider at least these options:

- CLI-only deterministic pipeline;
- CLI launching Codex/Claude subprocess agents;
- outer agent orchestrating CBM subagents while using CBM CLI as artifact/gate kernel;
- hybrid deterministic baseline plus runtime-agent backend;
- another option you think is better.

## Output

Write to `OUTPUT-ARCHITECTURE.md`.

Use this structure:

- Executive verdict
- Observed facts
- Architecture options
- Findings
- Recommended architecture
- Risks and tradeoffs
- Decisions required from the user
- Concrete next steps
