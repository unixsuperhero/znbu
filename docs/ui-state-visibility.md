# UI state visibility

Requirements for [the outline](outline.md), not a claim that the application implements them. Source observations below come from the local redeck-astra working tree; it was changing during this audit. No runtime UI audit was performed for this documentation update.

## Terminal preview

Selecting a terminal, agent or running vim row reserves the bottom of the detail area for the actual terminal. Metadata and transcripts occupy the region above it. Preview is read-only; entering live mode remains a separate action.

- Normal terminal: show the recent scrollback tail together with the current screen, within bounded capture and display limits. Preserve meaningful spacing and supported colors. Identify truncation.
- Alternate-screen program, including neovim: show its current screen, not old shell output. Preserve layout; crop to the preview region without resizing the real terminal. Identify cropping.
- Show session, window and capture time in the preview header. Distinguish loading, current, cached, empty, closed and unavailable. A saved vim session without a live window says so; do not launch it to obtain a preview.
- Capture through the daemon boundary. A read-only subscription must not request a size lease. Bound request duration and retained bytes; cancel obsolete work and reject late responses whose selection identity no longer matches.
- Refresh only the selected target. Prefer events; any periodic fallback must preserve selection, filter, modal, scroll and keyboard focus. No input, focus change, terminal resize, acknowledgement or review mutation is allowed.
- Treat captured text as untrusted. Render supported terminal styles through the renderer; never pass clipboard, title, hyperlink or other terminal-control commands through to the user's terminal.
- On short terminals shrink metadata first. If a screen cannot fit, display an explicit too-small state instead of silently removing the preview. Preserve the help line.
- If refresh fails, a retained screen is labeled cached with its capture time and the error. Never show it as live or reuse another pane's image.

Acceptance scenarios to exercise on a uniquely named throwaway tuios daemon on VPS:

1. Print a unique line in a terminal, highlight its row and observe that line in the bottom preview without entering live mode.
2. Highlight an agent row: actual terminal output is visible even when transcript retrieval fails.
3. Open neovim in an isolated pane and observe its alternate screen, not the shell output before launch.
4. Delay capture A, select B, then finish A: B never displays A's screen. Close B during capture: show closed/unavailable, not a blank successful capture.
5. Compare target focus, input and terminal dimensions before and after selection and refresh; all remain unchanged. Keep a form open while output arrives; its input and selection remain intact.
6. Exercise empty output, narrow/short layout, Unicode, truncation, disconnect/reconnect and malicious escape sequences. Cached output has an age; fresh capture clears only the preview error.

## Indicator contract

Every user-relevant backend state has a cue on its object row or the global status area, and a plain-language explanation in detail/help. Internal locks, sequence counters and implementation-only bookkeeping need no independent badge; their user-visible consequences do.

- Indicators compose. Needs-input must not hide blocked; unread must not hide completion; working must not hide a queued prompt.
- Use stable ASCII labels and counts; color is supplemental. The shared legend is available in help and beside expanded details.
- Prioritize error/attention, then blocked/unknown, queue/unread, then activity. If width requires truncation, retain attention and show "+N statuses"; details still expose every state.
- Unknown is not zero, ready or success. Display the source and last observation when data is stale or unavailable.
- Clear indicators only when authoritative state changes or the defined acknowledgement occurs. Merely highlighting a row cannot mark work read or delivered.
- Use the same projection for terminal, agent and live vim rows. Persisted-only objects use the same vocabulary where applicable, without inventing live facts.

| Cue | Meaning | Detail must explain |
| --- | --- | --- |
| W / A / R | Working / awaiting / ready | Authoritative state, harness and last activity; show simultaneous flags where reported |
| ! / B | Needs attention / blocked | Reason, blocker and available user action |
| Qn | Queued prompts | Unique pending count, local versus daemon-owned state, target and any delivery uncertainty |
| Un / F | Unread items / finished unread | What is unread and what acknowledgement clears it |
| Sn / ~ | Active subagents / stale activity | Count; last activity and stale threshold |
| ? / E | Unknown / operation failed | Source, last successful observation, error and recovery action |
| Z / * / P | Snoozed / starred / pinned | Wake time or scope of the persisted setting |

These are display labels, not new daemon state values. Do not collapse arbitrary daemon states into this vocabulary: retain unfamiliar states in details and flag them as unknown to the renderer.

Example projection, not a replacement persistence schema:

```js
row = {
  kind: "agent", target: { session: "work", window: "agent-7" },
  badges: ["W", "Q2", "S1", "U1"],
  queue: { localSaved: 1, daemonWaiting: 1, uniquePending: 2 },
  preview: { state: "cached", capturedAt: "12:03:04", reason: "daemon disconnected" }
}
```

## Source-backed state inventory

Paths below are relative to the implementation repository, not znbu. “Observed” describes source, not exercised behavior. Required exposure is acceptance work, including any missing read-model fields.

| Area and source | Observed backend state or current exposure | Required visible result |
| --- | --- | --- |
| Pane lifecycle — internal/panes/panes.go; internal/ui/render_panes.go | State, Working, Awaiting, Ready; row uses a primary state fallback, details include flags | Shared primary state plus simultaneous flags; unknown when absent; closed target explicitly distinguished |
| Attention — same sources | NeedsYou, BlockedBy, Message; row currently chooses needs-you OR blocked | ! and B can coexist; detail shows blocker and message without opening logs |
| Queues — panes Queued; internal/prompts/prompts.go | Pane row shows daemon count; persisted QueuedPrompt separately has State, DaemonID, target and ownership | Qn includes locally saved prompts targeted to this pane; task/project queues expose untargeted prompts; do not duplicate a prompt after daemon acceptance |
| Dispatch — prompts StartResult and Dispatch | Outcome, Ready, BlockedBy, Reason, PromptStatus, PromptNote; partial start can retain a created target after error | Distinguish accepted, waiting, delivered when evidenced, blocked and failed; retain target identity and explain partial success |
| Queue reconciliation — internal/prompts/composer.go SyncQueue | saved becomes waiting; daemon receipt states are copied; absent receipt or closed target removes local row; other read failures retain it and return error | Never infer delivered from disappearance. Surface closed-target or unknown outcome and reconciliation failures; requires an outcome read model where current code only deletes/logs |
| Drafts and stashes — internal/prompts/prompts.go | StashedPrompt retains DraftID, text, draft and saved time; queued prompts are distinct | Stashed/draft marker, owner and saved time; distinguish unsent draft from queued prompt; do not count stashes as Qn |
| Unread/completion — panes; internal/reviews/reviews.go | Unread, FinishedUnread; row uses unread count OR finished-unread | Show unread count and completion independently; explain which review action clears each |
| Subagents — panes SubagentCount | Count available in pane details | Sn on the row, including when the parent awaits children; completion must not imply all children finished without evidence |
| Activity freshness — internal/panes/reads.go | LastActivity, IdleMS, Stale classification | ~ with age and threshold; distinguish idle activity from disconnected data source |
| Activity/transcript — internal/panes/detail.go | Activity entries include OK, kind, tool, target; TranscriptError; More, Reset, Untrusted pagination metadata | Tool failure, unavailable transcript, older/more content and reset visible; do not imply a complete history when partial; terminal preview remains independent |
| Terminal preview — internal/daemon/verbs.go and stream.go; internal/ui/view.go | Capture and stream APIs exist; current pane detail renders activity/transcript, vim detail renders metadata | Bottom terminal preview and explicit preview states specified above; this is a missing surface, not merely a different transcript label |
| Vim sessions — internal/vim/vim.go; internal/ui/view.go | Persisted session/path/cwd and running/closed state; vim rows do not share all pane indicators | Live vim rows inherit available pane indicators; closed/saved rows visibly lack a live preview. Buffer-modified state is not supplied by these fields: do not fabricate it |
| Ownership/scope — internal/panes/reads.go; internal/work/work.go | Task/project assignment, NoTask, hidden count, scoped filtering | No Task, owner, current task scope/all mode and hidden count visible; never present filtered absence as deletion |
| Task/project lifecycle — internal/work/work.go | Status; task Easy, SnoozedUntil, Position | Status label, easy marker and Z with wake time; child/group ordering clear; preserve status in all relevant lists |
| Tree edits and assignment — internal/ui/tree_edit.go; internal/work/assign | Draft edits, revision conflicts; assignment candidates and approval workflow | Unsaved, applying, failed/conflicted and committed distinguished; proposed ownership is not presented as already assigned |
| Reviews — internal/reviews/reviews.go and documents.go | Kind, Current, ReviewedAt, CompletedAt, TurnID; document changes can invalidate review | Unreviewed/reviewed, current/historical and turn/document distinguishable; changed document becomes visibly unreviewed; preview alone never acknowledges |
| History — internal/history | Turn start/completion; event tool, target and OK outcome | Running versus completed turn and failed tool outcome; unknown outcome is not success; source and timestamp in detail |
| Reminders — internal/reminders/reminders.go | Enabled, Interval, Next, Last; fired event can include notification_error or delivery_error | Enabled/disabled, next due and last attempt; failed notification/delivery remains inspectable after transient status text clears; schedule advancement is not proof of delivery |
| Context — internal/context | Item kind, Starred, Pinned; gathered warnings and source counts | Kind, * and P on rows; warnings and omitted/unavailable sources visible before submission, not silently dropped |
| Notes — internal/notes | Visible notes carry inheritance provenance and owner | Own/inherited note and source owner visible; effective context must not appear locally owned |
| Captures — internal/captures | Size, time, kind, ownership; preview truncation | Capture kind, owner, age and truncation; missing/unreadable source is an error, not empty content |
| Connection/event recovery — internal/events/runner.go; internal/ui/view.go | Reconnect/resync behavior; global syncing/status text exists | Connecting, disconnected, resyncing and current; visible error/reason and last success. Data retained during disconnect is marked stale; detailed signals may require a read-model addition |
| Commands/forms — registry/bus and internal/ui | Commands can fail, validation can reject and modal edits can remain uncommitted | Pending, validation failure, command failure and success visible at the affected object; retain unsaved input on failure; clear errors only on correction, successful retry or explicit dismissal |

### Queue identity and transitions

Join persisted prompts to daemon receipts by delivery identity and target, not text. A local record with a DaemonID and its daemon entry represent one prompt. If the available aggregate count cannot be correlated, label local and daemon counts separately rather than publish a falsely exact total. A prompt without a window belongs in its task/project queue until assigned.

A dispatch returning a window followed by an error is partial success, not a reason to silently start another agent. A closed target is not successful delivery. An absent queue receipt alone does not distinguish sent, cancelled or discarded: the UI needs an authoritative outcome or must display unknown. The current SyncQueue deletion behavior therefore needs more than a renderer change to meet this contract.

### Coverage and verification

For each state above, implementation must record its source, read-model field, row/global cue, detail explanation, entry transition, clearing transition and a reproducible E2E scenario. New states extend this inventory in the same change. Backend-only errors that currently disappear into logs need an inspectable outcome, not a guessed badge.

Exercise at least: saved → daemon waiting without double counting; blocked plus needs-you; unread plus finished; active subagents; dispatch partial failure; closed target; missing receipt; reconciliation read failure; stale activity versus disconnected source; snooze/wake; draft conflict; changed document review; reminder delivery failure; context warning; truncated capture. Assert the rendered cue and its clearing behavior, not just the backend field.

Run interactive verification on VPS using isolated throwaway tuios daemons, never the daemon hosting the user's pane. Every tool invocation and shell command has an enforced finite timeout; over 15 minutes requires a reason and explicit permission first. This documentation change does not mark those application acceptance scenarios passed.
