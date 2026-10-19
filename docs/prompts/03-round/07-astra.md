---
seq: 7
type: 03-round
agent: astra
harness_model: omp / openai-codex gpt-6-astra:high
target: redeck-astra / 7593f7e1
cwd: ~/proj/redeck-astra
sent_at: 2026-10-18 20:31
delivery: tuios ask-agent (first attempt 20:28 failed: --from named a pane of another session)
agent_state_at_send: done (idle after round 1)
steering_active_turn: false
notes: Context at 78% of 272K when sent. Reported done ~20:38: live leader and embedded detail.
---

Round 2, two changes. docs/outline.md section 7.1 (live mode) was rewritten; read it first and build exactly that.

1. Live mode keys. Replace the held-esc exit, ctrl+z zoom and ctrl+f fullscreen. ctrl+a is the leader; the key after it is a command; every other key, esc included, goes to the pane untouched. ctrl+a d detaches back to the deck, ctrl+a j / ctrl+a k move to the next / previous pane, ctrl+a Z / ctrl+a f zoom / fullscreen the pane inside tuios (its own session, not the deck), ctrl+a ctrl+a types a literal ctrl+a, ctrl+a ? shows the keys, esc after the leader cancels it. The live bar shows these. Bindings live in config under mode live: leader, detach, next_pane, prev_pane, zoom_pane, fullscreen_pane, help. Never a bare key as the exit.

2. Live layout. The deck page is already two panes: the rail on the left and the detail area on the right. Enter on a pane loads the live screen into that right detail area under a live bar; the rail stays visible and keeps working after ctrl+a d. The live pane is never full-screen on the deck side: delete the deck-side zoom and fullscreen view modes. The stream-pane lease is sized to the detail area.

Keep the e2e suites green, extend e2e for live mode (enter, a key reaching the pane, ctrl+a d, ctrl+a j), commit each green step, never amend, same subagent model rule (openai-codex only). Mail the summary to the same inbox as before when done.
