# Panes, live mode, and reviews

[Remaining work](../todo/panes.md) · [Work and places](work.md) · [Shared forms and navigation](forms.md)

This document separates the implemented Matomeru baseline from target behavior. Code paths below are relative to the Matomeru repository. Commit and acceptance records are historical evidence, not checks performed during this consolidation. The committed `fff163c` baseline remains distinct from the subsequently owner-verified `e4cf07a` features.

<a id="daemon"></a>
## Daemon boundary and host identity

`internal/daemon` owns typed calls, subscriptions, presence, and pane streams. Its external contract is `tuios list-verbs`. Product units do not open a second terminal-control path. The retained event and start shapes are:

```js
Event = { seq, type, session, window, data }
StartAgentParams = { session, agent, name, cwd, prompt, ready_timeout }
```

The shell holds presence. Transcript readers receive the presence nonce rather than creating their own shell presence. The [event runner](architecture.md) owns event resume, resync, and bounded delivery.

A pane's identity includes host, session, and window. Local IDs remain raw. Remote IDs use `mtm-host://<escaped-host>/<kind>/<escaped-value>`. `internal/daemon/client.go`, `hosts.go`, and `stream.go` route an explicit host or a qualified target, reject conflicting hosts, and remove qualification before the remote call. Calls still dial the local tuios daemon. It opens a host connection using `open-host-connection`, with the host and SSH authentication socket. Matomeru does not independently dial a different daemon socket for every host.

Streams use the same route and qualify returned session/window identities again. `stream-pane` requires an explicit window. Columns and rows must be supplied together or both omitted. A nonzero size lease renews every ten seconds; a read-only stream does not acquire a size lease. Presence also supports a host route and nonce.

The original design requires this identity wherever an application record stores a pane, including assignments and provenance. The implemented relay and remote-agent listing do not prove that every remote terminal or every persisted pane reference meets that requirement. [B-50](../todo/panes.md#b-50) retains the unverified host-inventory contract. Rich host-specific directories and Git observations remain [Place work](work.md#places), not a consequence of a working relay.

Sources: [original daemon and pane unit design](../sources/znbu/docs/outline.md#61-daemon--internaldaemon-unchanged), [implementation outline](../sources/matomeru/docs/outline.md).

<a id="listing"></a>
## Shared pane listing and refresh

`internal/panes` shares one listing among consumers. It serializes refreshes and keeps sessions, a pane map, and stable IDs together. The original unit interface is `All()` and `ByID(window)`, with `panes.changed` as the consumer notification. Activity and transcript rendering belong to the pane unit. Stored assignment hiding belongs to work, not the daemon adapter.

The consolidated pane read model includes:

```js
Session = { host, name, attached, dir, branch, panes: [Pane] }
Pane = {
  host, session, id, name, state, state_at, harness, foreground, cwd,
  message, blocked_by, is_agent, ready, needs_you, queued, unread,
  working, awaiting, subagent_count, finished_unread,
  last_activity, idle_ms, stale,
  task_id, project_id, task_title, project_name, task_theme, project_theme, no_task
}
```

A session has many panes and belongs to a host. Cwd provides evidence for directory/worktree resolution; it does not turn a folder into a project. The richer `Pane has_one worktree` relation is a [Place target](work.md#places).

Output events update last activity without relisting every pane. Agent state, activity, messages, window/session lifecycle, command, attention, and host changes trigger semantic refresh. The shell's background page/detail fallback is thirty seconds. Output-only updates bypass expensive queue/status reads so a reminder or form notice is not immediately overwritten. Selection, filters, form input, and scroll survive refresh.

A pane without an activity timestamp uses its first observation as the age baseline. New output updates that baseline. Close/overflow reconciliation obtains two successful snapshots, bounded to at most three attempts with 100 ms waits. Assignment pruning depends on successful snapshots, not a transient failed list. See [assignment discovery and pruning](work.md#assignment-discovery-and-pruning).

`internal/panes/hosts.go` calls `list-host-sessions` and `list-host-agents` through the local relay with a fifteen-second bound. It qualifies remote agent host/session/window identities and includes remote state and cwd. A host explicitly reported stale or failed does not contribute fresh rows; previously known rows for that failed host remain marked stale. A top-level RPC failure is not evidence that the remote inventory is empty. Complete remote-terminal enumeration remains [B-50](../todo/panes.md#b-50).

The [shared status contract](forms.md) requires simultaneous flags, plain-text counts, reasons, and unknown/stale distinctions. A primary state alone is not acceptance of that target. [Preview acceptance](../todo/panes.md#b-49) also distinguishes current output from a cached image.

<a id="b-06"></a>
## B-06: Pane detail tabs

Status: implemented. A pane detail has **Screen**, **Activity**, **Transcript**, and **Turns**, in that order. The bar identifies the pane's session/name, assignment path and glyph, stale age, and last message. Review and persisted Vim rows have their own detail and do not receive a misleading pane tab bar.

`1` through `4`, `[`/`]`, and Tab/Shift+Tab switch pane tabs from the rail or detail. Detail focus makes the selected tab more prominent. Screen is the default for an ordinary newly selected pane until the page has an explicit tab choice. [B-41](#b-41) replaces the historical per-pane memory with page-level explicit selection.

Screen uses the actual `capture-pane` result rather than substituting an activity log or transcript. Selected output events request a new capture, with a one-second fallback. One capture runs at a time and at most one newer request waits. A late capture older than five seconds does not block the UI. Screen scroll remains where the user left it unless following the bottom; `G` resumes follow. With detail focused, `j`/`k` scroll a line and `J`/`K` move half a page.

Enter enters live Screen. Ctrl+a d returns to read-only Screen without changing the rail's shape. Selection, tab, and scroll survive refresh. This basic Screen implementation is not proof of every scrollback, safe-rendering, cached-state, and noninterference requirement in [B-49](../todo/panes.md#b-49).

Evidence: `internal/ui/model.go`, `internal/ui/pane_tabs.go`, and `internal/ui/live/live.go`; commits `09a4f22`, `48f451f`, and `3494216`; recorded `pane_tabs`, `shared_navigation`, and `create_jump` acceptance in the [preserved implementation outline](../sources/matomeru/docs/outline.md) and [original B-06](../sources/matomeru/docs/todo.md#b-06-pane-detail-tab-bar-with-a-live-screen-tab-first-learned-from-tuios-mtm). Those checks were not rerun here.

<a id="preview"></a>
## Target: read-only terminal preview

The retained target anchors an actual terminal preview at the bottom of the detail area, above help, for terminal, agent, and running Vim rows. Metadata and transcript can occupy the space above it but cannot displace the preview. A normal terminal includes the recent scrollback tail and current screen. An alternate-screen application shows its current layout, cropped without resizing the real pane. A saved Vim session without a live window says so and does not launch Vim to manufacture a preview.

The preview labels loading, current, cached, empty, closed, unavailable, and too-small states. Its header names session, window, and capture time. Failed refreshes can retain the same target's last image only with its age and error. Captured terminal text is untrusted; supported styles are rendered, while clipboard, title, hyperlink, and other terminal-control commands cannot execute in the user's terminal.

Read-only capture sends no input, changes no focus, requests no resize or size lease, and does not acknowledge reviews. Requests have duration and byte bounds, cancel obsolete work, and reject late results from another selection. Only the selected target refreshes. Refresh preserves selection, filter, modal, scroll, and keyboard focus. On a short terminal metadata shrinks first; the help line remains visible, and an impossible fit shows an explicit too-small state.

[B-49](../todo/panes.md#b-49) owns the unverified remainder and all six concrete acceptance scenarios. Source: [terminal preview requirements](../ui-state-visibility.md#terminal-preview).

<a id="live"></a>
## Live input, screen size, and pane creation

Live mode draws the pane inside the detail area under a live bar. It retains the rail. It does not make the Matomeru shell fullscreen. Tuios's own zoom/fullscreen actions apply to the target pane's session.

Ctrl+a is the live leader. The following key has these meanings:

| Chord | Result |
| --- | --- |
| Ctrl+a d | Detach to the shell. |
| Ctrl+a j / Ctrl+a k | Enter the next / previous rail pane without first leaving live mode. |
| Ctrl+a Z / Ctrl+a f | Zoom / fullscreen the target in its tuios session. |
| Ctrl+a Ctrl+a | Send a literal Ctrl+a. |
| Ctrl+a ? | Show live help. |
| Ctrl+a Esc | Cancel the leader. |

An unknown leader command is consumed and explained rather than sent to the pane. All nonleader input goes to the pane unchanged, including bare Esc and Ctrl+z. Neither is a shell escape. Config's `live` mode names the leader, detach, next/previous pane, zoom/fullscreen, and help bindings.

`internal/ui/live/live.go` owns one ordered, cancellable raw-input reader. The controller owns input, render, and pane switches. On a switch it releases the old stream lease with zero dimensions, stops the old stream, and closes its reader before acquiring the next target. Live stream dimensions are the measured detail columns and rows below the live/tab bar, not the full Matomeru terminal.

Zoom/fullscreen first wait for renderer acknowledgement of the target focus through a tuios `run-command`. A daemon `focus-window` response alone does not establish renderer focus. There is no guessed delay in place of that acknowledgement.

Pane creation uses the project's named tuios session for terminal, agent, and Vim launches. An explicit destination wins over that default. A pane is a terminal runtime target; a page is a Matomeru navigation view. These are not interchangeable terms.

Automatic placement requires at least eighteen rows per new pane and selects an empty workspace when the current one cannot fit it. If every workspace is occupied, creation refuses with an explanation because the native API cannot safely create the required workspace. It does not rearrange, resize, or otherwise mutate an existing workspace layout to force a fit. Explicit destination selection remains authoritative. Evidence: real PTY and SSH launch acceptance in `run.mu80sv9H`. Creation selects the new pane on Screen with follow enabled. CLI creation can supply explicit dimensions. Live-mode sizing is distinct from read-only preview's no-resize rule.

The six global creation bindings remain `n t`, `n a`, `n v` for quick terminal/agent/Vim creation, and `N t`, `N a`, `N v` for the corresponding prefilled forms. Quick creation does not open a form. Launch context comes from the highlighted pane/Vim row when applicable, otherwise the pin. Current launch behavior and the implemented defaults/composer are described in [agent launches](agents.md#launchdefaults); the full inherited Place and preflight-warning target remains [B-48](../todo/work.md#b-48). New panes must retain their assignment rather than briefly appearing as unassigned.

Sources: [original shell and live design](../sources/znbu/docs/outline.md#71-tui--internalui) and [implementation outline](../sources/matomeru/docs/outline.md). The earlier `fff163c` baseline was already verified in the prior implementation turn. The owner subsequently reports full TUI/live and SSH remote-launch checks for `e4cf07a`. These are owner-reported results. This consolidation ran no daemon.

<a id="b-09"></a>
## B-09: Rail lifecycle

Status: implemented. Panes has three sections, one list for navigation:

1. Review at the top contains one row per pane with unreviewed records, not one row per finished turn. It uses a pronounced review style. Standalone document-review rows retain their document workflow.
2. The middle contains all other panes under the current grouping or tree.
3. Working at the bottom contains working agents. Terminals running commands do not enter this section; commands are not agent turns.

Working rows are locked for browsing. Selecting one shows an unlock hint and does not capture its screen or build its review accordion. The tab bar remains. `U` unlocks the row until rail focus leaves it, then it locks again. Lowercase `u` retains half-page-up. Enter can still enter live mode on a locked row.

Working rows are oldest first, using first observation of working state when the daemon supplies no submission timestamp. The original submission-time rule remains the intended source ordering if that timestamp becomes available; the implementation does not invent one. Review rows are oldest first by the latest unreviewed finish for each pane. A finished agent moves to Review. Opening every accordion marks its records reviewed, but a fully reviewed pane stays in place while focused. It returns to the middle only after focus moves away. Starting new work moves it to Working immediately.

Document review is not the same as this focused-pane retention. Documents have their own open/read transition and a three-second off-cursor linger. Their content, star, and read state are documented under [documents](knowledge.md#b-11).

The sections have [B-08's independent percentage budgets](#b-08). B-09 defines membership and lifecycle; B-08 controls allocated height, compact rows, and scrolling.

Evidence: commit `ce5e679`; `internal/ui/rail_sections.go`, `internal/ui/render_panes.go`, and `internal/ui/pane_tabs.go`; recorded `rail_lifecycle`, `history_review`, and `shared_navigation` cases in the [implementation outline](../sources/matomeru/docs/outline.md). The [original lifecycle proposal](../sources/matomeru/docs/todo.md#b-09-pane-lifecycle-in-the-rail-working-at-the-bottom-and-locked-review-at-the-top-rest-in-the-middle) retains the earlier lowercase unlock and undecided terminal alternative as history, not current bindings.

<a id="b-10"></a>
## B-10: Review accordion and stars

Status: implemented. Turns presents a pane's review records as an oldest-first accordion. Rows begin collapsed. Multiple review records sharing the harness turn ID form one row with every prompt and response:

```js
Accordion = { pane, rows: [TurnRow|ContextRow], auto_reviewable_count, cursor, follow, expanded: { [row_id]: bool } }
TurnRow = { id, turn_id?, records: [review_id], prompts: [text], responses: [text],
  started_at, completed_at, reviewed_at?, auto_reviewable, starred, project_id, task_id }
ContextRow = { id, item: ContextItem, starred }
ReviewStar = { id: turn_id ?? review_id, starred_at }
```

Enter or Space opens/closes a row. Opening marks exactly that row's records reviewed. Expanded state is keyed by stable source identity, so a reread does not close opened rows or shift selection to an unrelated turn. Selection is found again by ID unless follow is enabled. `g` disables follow and moves to the beginning; `G` enables it and follows the newest row. The original proposal also suggested skipping rereads when a count/last-ID/last-body-length fingerprint is unchanged. That remains a retained optimization alternative, not a claim about the current `accordionLines` implementation, which rebuilds its rows.

With Turns detail focused, `j`/`k` move between accordion rows. `J`/`K` and PgDn/PgUp scroll the full expanded body so long responses can be read through their first, middle, and last lines. Real PTY evidence `run.AdYBNDbO` covers a 72-line response at 150x48 and 100x22; `run.ORperME4` records the earlier scoped proof.

A turn with later prompts is auto-reviewable and has a distinct background. The hint names `x`, which marks exactly the earlier auto-reviewable rows. The most recent turn is never mass-marked. `*` persists a turn star in `review_stars`; the Reviews page sorts starred rows first. `y` copies through `context.copy` and OSC 52. `{`/`}` move between the turn group and extracted context.

Extracted response context appears below turns, newest first, deduplicated by kind and text. Ownership comes from the producing turn's task/project. Context can be starred in place. A starred context item appears on its own task, that task's parent chain, and the project. It does not spread to siblings or cousins. The [context outline](knowledge.md#context) owns the reusable context model.

The acceptance case with two records sharing a harness turn ID uses records from different conversations. Duplicate IDs in one conversation are rejected. Grouping display records must not relax source identity or invent duplicate valid turns.

Evidence: commit `55c8f10`; `internal/ui/accordion.go`, `internal/reviews`, and `internal/context`; recorded `review_accordion` acceptance in the [implementation outline](../sources/matomeru/docs/outline.md). [Original B-10](../sources/matomeru/docs/todo.md#b-10-review-accordion-the-detail-for-a-pane-with-unreviewed-turns) preserves the complete proposal and recorded baseline.

<a id="b-38"></a>
## B-38: Nested middle rail below the pin

Status: implemented. `panes.rail_tree` defaults on. The middle section mirrors the [work tree](work.md#projecttask-tree-and-atomic-drafts) below the pin. Panes assigned directly to the pinned node lead under that node's name. A task pin then shows subtasks, a project pin shows its tasks, and ALL shows projects and descendants. Task order uses stored position. Ancestral headings preserve the full path and panes use their task's color. Headings are not selectable.

`z` folds the innermost relevant group. A folded heading uses `▸` and a pane count. Enter or `z` unfolds it and selects the first pane. `Z` folds the parent group. `{`/`}` jump by distinct task path. Filtering unfolds matching paths without losing the tree relation.

`o`/`O` continue to cycle grouping. Grouping zero is the nested tree; project, session, state, and task flat modes remain available. Review/Working lifecycle is independent of the middle section's tree.

Evidence: commit `a64d09f`; recorded `rail_tree`, `grouping_stale`, `pin_scope`, `rail_lifecycle`, `history_review`, and `shared_navigation` cases in [original B-38](../sources/znbu/docs/todo.md#b-38-panes-rail-as-a-nested-tree-below-the-pin) and the [implementation outline](../sources/matomeru/docs/outline.md). This is historical verification.

<a id="b-30"></a>
## B-30: Stale panes remain in their group

Status: implemented. Stale panes stay in their ordinary task/project group with a stale mark and age. There is no compulsory separate Stale bucket. `stale_after` and the **Close stale panes** palette command remain. The original rule that grouped every stale pane separately is superseded, not another current grouping requirement.

Evidence: commit `52961a5`; `internal/ui/model.go` and `internal/panes/panes.go`; [historical B-30 and its recorded acceptance](../sources/matomeru/docs/todo.md#b-30-remove-the-stale-rail-group-on-the-panes-page).

## Pane closure and work completion

Closing a pane removes a runtime target, not the work itself. [B-45](#b-45) defines the separate explicit completion choice.

<a id="b-08"></a>
## B-08: Rail height budgets and compact rows

Status: implemented. `panes.rail_review_percent`, `panes.rail_panes_percent`, and `panes.rail_working_percent` default to 25, 60, and 15. `mtm config init` emits those shares. Each accepts an integer from 1 through 100. Totals above 100 scale proportionally using the total as denominator; totals at or below 100 use 100. Headings count against their section. Empty or short Review and Working sections release unused space to Panes.

Each section retains an independent row offset. `+N more` and up/down markers identify overflow without pushing the next section offscreen. Group and tree ancestry stays visible within the middle viewport. Resting rows are one line across pages. A selected row adds a second line only for a nonempty summary. A live message adds its actual message as a second line whether selected or not. Staleness alone does not expand a row.

Recorded VPS PTY acceptance covers forty finished turns and three visible panes at forty rows, forty overflowing document rows, independent Working overflow, default/invalid config, and folds/pin. Moving within Review scrolls Review inside its budget.

Evidence: `/root/proj/redeck-astra-verification/runs/run.WJHFiPxy/verification.log`; artifacts `/tmp/mtm-e2e.CSpauN/outline-budget-*.txt`.

At fourteen rows, if the focused section cannot fit its heading and one row, an explicit `<Section> · rail too small for section budgets` message temporarily dedicates the available rail to that section. With only one row available, its label, warning, and selected row share that row. Normal-height budgets do not change. Final tiny-layout evidence: `run.1QOzlv21/verification.log`, artifacts `/tmp/mtm-e2e.4Fj981`.

The original duration-based resting fold and per-subagent cap remain historical alternatives, not extra current requirements. Sources: [original B-08](../sources/znbu/docs/todo.md#b-08-rail-height-budget-sections-capped-by-percent-one-line-rows-panes-get-most-of-it), [implementation-side copy](../sources/matomeru/docs/todo.md#b-08-rail-height-budget-sections-capped-by-percent-one-line-rows-panes-get-most-of-it).

<a id="b-41"></a>
## B-41: Keep the page's last explicitly chosen detail tab

Status: implemented. Explicitly choosing a tab sets the page's choice. Row navigation retains it rather than restoring a per-row tab or resetting to a default. Choosing another tab replaces that choice for subsequent rows. The rule applies to every tabbed page, including Panes. Automatic row-specific choices, including unreviewed-turn defaults, cannot override it. The former per-pane memory is historical, not the current contract.

Evidence: real VPS PTY acceptance `run.AdYBNDbO` and earlier `run.ORperME4`. Existing `pane_tabs` and `review_accordion` acceptance passed in `run.Rw8zJ3Z1`. Sources: [original B-41](../sources/znbu/docs/todo.md#b-41-keep-the-last-explicitly-chosen-detail-tab-while-navigating-a-page), [user request](../sources/hub/prompts/mtm-todo.md).

<a id="b-45"></a>
## B-45: Offer task or project completion after successful pane close

Status: implemented. Pane closure first requires confirmation and a successful close result. Only then does an associated task or project receive a separate completion offer. The default is No. Accepting marks the chosen owner done; declining leaves that owner's completion state unchanged while the pane remains closed. Cancelled or failed closure never offers completion. Closing a pane alone never implies work completion. Read-only selection and preview cannot mark work complete.

Evidence: real VPS PTY `run.AdYBNDbO` and earlier `run.ORperME4`. Sources: [original B-45](../sources/znbu/docs/todo.md#b-45-offer-task-or-project-completion-when-closing-its-pane), [user request](../sources/hub/prompts/mtm-todo.md).

Related broader terminal, multi-host, and collaboration ideas remain in the [ecosystem outline](ecosystem.md) and [ecosystem backlog](../todo/ecosystem.md).

