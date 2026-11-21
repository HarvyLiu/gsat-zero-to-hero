# CLAUDE.md

Read docs/status.md first, then run git status and git log -5, and summarize before changing anything.

## Cost rules (owner, 2026-11-21)
- Research is FROZEN. Never read research/verified-2026-11-15.json whole (1.68 MB). Extract only the current subject's or chapter's entries with a short `python -X utf8` query into a slice file in the scratchpad, and give each writer agent only that slice. If a fact is not in the frozen research, flag it to the owner. No web search.
- Agents: writers on Sonnet (medium effort). Reviewers on Sonnet by default with a narrow scope: name the exact files and what to check. Never use Fable.
- Exceptions: new or edited lesson content may get up to 2 reviewers, and Opus is allowed for those. Site-code or UI changes get at most 1 reviewer, on Sonnet.
- Don't weaken correctness checks: source packs, harness `--strict`, and chapter content review stay.
- Checks: run tests and the harness only on what changed while iterating (`npx vitest run <dir>`, `verify_items.py <bank>`). Run the full suite and `npm run build` once before a commit. Run the site-wide link/href check once before a push.
- Visuals: check rendered pages with text/DOM checks first (scratchpad scan script, `javascript_exec`, `get_page_text`). Use screenshots only for visual changes: one phone-width check and one dark-mode check, at low scale.
- Batch independent tool calls into one message. Prefer one script over many small commands. Don't re-read files already in context.
- Keep reports short: ask agents for findings only (file:line, severity, fix), no recaps.
- Keep sessions short: one subject or one feature per session, and hand off through docs/status.md.
- Don't push unless the owner asks.
