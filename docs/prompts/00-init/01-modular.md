---
seq: 1
type: 00-init
agent: modular
harness_model: claude-code / Fable 5.1 (subagents opus, sonnet)
target: inbox-451e6dcc / 07577614
cwd: ~/proj/tuios-deck/.dev/work/modular (branch modular off main)
sent_at: 2026-10-18 19:36
delivery: tuios start-agent --prompt
agent_state_at_send: idle (fresh pane)
steering_active_turn: false
notes: Paste sat in the input box; one Enter via send-keys submitted it. Outline given at commit b71bae4 (trees, no web, build rules).
---

You are in a git worktree of tuios-deck at /Users/unixsuperhero/proj/tuios-deck/.dev/work/modular on branch modular, cut from main. Read AGENTS.md first, then docs/plans/2026-10-18-modular-outline.md (the spec; follow it) and docs/reports/2026-10-18-modular-redesign.md (the reasoning behind it). Implement the whole outline on this branch, as fast as possible in wall-clock time.

Rules. Follow outline section 0b: use the /frontend-design skill for every TUI surface even though it is a terminal; fan out parallel subagents, one unit or page each, on opus or sonnet, never fable; delete internal/web and its suites first (migration step 0). Work only inside this worktree; never touch the main tree or other worktrees. Build with GOWORK=off. Keep the e2e suites green at every step and commit after each green step with conventional commits; never amend. Run scripts/e2e-all.sh before your final commit. Do not ask questions; decide, and record each open decision you settled in section 10 of the outline. When done, mail a summary with the commit range and the suite results to session inbox-451e6dcc, window e01e2e76-582c-436a-bf24-5056d7f13b18 with: tuios send-agent-message (see tuios --skill mail).
