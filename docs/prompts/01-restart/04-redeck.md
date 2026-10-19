---
seq: 4
type: 01-restart
agent: redeck
harness_model: claude-code / Fable 5.1
target: inbox-451e6dcc / db52c28e
cwd: ~/proj/redeck (reset to 5c964a2)
sent_at: 2026-10-18 20:12
delivery: claude argv (prompt as the positional argument); two earlier typed attempts stalled
agent_state_at_send: idle (fresh pane)
steering_active_turn: false
notes: Same as seq 2 plus the clean-room rule. Reported done 20:3x: e2e-all green.
---

Greenfield project. /Users/unixsuperhero/proj/redeck is a fresh git repository holding one file, docs/outline.md: the complete spec of a Go program named deck, a terminal dashboard that drives the tuios daemon over its JSON verb socket. Build it, as fast as possible in wall-clock time.

Clean-room rule: this project is built from docs/outline.md alone. Never read, search, list, copy or reference any directory outside /Users/unixsuperhero/proj/redeck except the Go module cache, and never look for or at other projects on this machine; if the outline leaves something unspecified, decide it yourself and record it in section 10. Read docs/outline.md fully first. It describes the target system; where it says unchanged or today or names a migration step, there is nothing yet, so build the target directly, in the dependency order of section 9. Section 0b holds the build rules: use the /frontend-design skill for every TUI surface even though it is a terminal; fan out parallel subagents, one unit or page each, on opus or sonnet, never fable; no web UI. tuios is on PATH; tuios list-verbs --json is the daemon contract and tuios --skill all its documentation; verify end to end against throwaway daemons (tuios --server NAME ... and kill-server), never the daemon this pane runs in. Go module github.com/unixsuperhero/redeck, Bubble Tea v2 (charm.land/bubbletea/v2, charm.land/lipgloss/v2), sqlite via modernc.org/sqlite. Commit after every working step with conventional commits; never amend. Do not ask questions; decide, and record each open decision you settled in section 10 of the outline. When done, mail a summary to session inbox-451e6dcc, window e01e2e76-582c-436a-bf24-5056d7f13b18 with: tuios send-agent-message (see tuios --skill mail).
