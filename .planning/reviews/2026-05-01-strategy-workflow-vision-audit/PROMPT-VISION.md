# Prompt: Vision Quality Review

You are an independent reviewer of `VISION.md` as a project-shaping artifact.

Read `SHARED-CONTEXT.md`, then inspect `VISION.md` and any supporting docs needed to judge how the vision affects implementation quality. Do not assume the vision is good because it is authoritative. Do not assume implementation drift proves the vision is bad. Diagnose carefully.

## Task

Review `VISION.md` on two fronts:

1. Did ambiguity, overbreadth, missing operational detail, or rhetorical framing in the vision contribute to implementation or planning problems?
2. Even if it did not cause current issues, how could the vision be improved to produce better code, better codebase structure, better development workflow, and better verification discipline?

Address:

- Is the vision clear enough to guide implementation decisions?
- Does it distinguish destination, roadmap, architecture, runtime behavior, and developer workflow clearly enough?
- Does it give the right pressure against false understanding and overclaiming?
- Does it accidentally encourage overbuilding, excessive artifact machinery, or phase drift?
- Are the graduation criteria measurable and useful?
- Are any parts too aspirational to guide engineering?
- Are any important product/deployment assumptions missing?
- What changes, if any, would make `VISION.md` more useful without weakening its ambition?

## Output

Write to `OUTPUT-VISION.md`.

Use this structure:

- Executive verdict
- Strengths of the vision
- Ambiguities or failure modes
- Possible contribution to current drift
- Improvements to guide implementation quality
- Improvements to guide workflow and verification
- Recommended edits or sections
- Questions requiring user decision
