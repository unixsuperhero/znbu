# Ecosystem concepts and recorded history

This page preserves ideas and reported behavior from products adjacent to Matomeru. It does not establish current implementation proof or approve these ideas for Matomeru. See the [ecosystem decisions and unfinished work](../todo/ecosystem.md).

## Product and evidence boundaries

- Znbu owns the canonical design and backlog; Matomeru owns its implementation. The Matomeru intake retains B-41 through B-45 rather than acquiring duplicate EXT backlog items.
- Ima/Now is the separate single-task completion product. Its task-as-mode, no-priority picker, Later locks, and deliberately absent pane list are not Matomeru defaults. The historical checkout name is Now and the published repository is `unixsuperhero/ima`.
- Thinktank is the historical project-registration/tooling context. Its Python tooling motivated a stack suggestion for Now, not a mandate for Matomeru.
- pstack is role/model setup tooling. Its historical model overrides and include choices do not configure this consolidation.
- mdoc is a publication destination for user stories, not the task app or a current serving guarantee.

A user request or goal describes intent. A historical assistant proposal describes an option. A historical assistant completion claim or checked source inventory records reported behavior only. The newer Ima inventory explicitly separates unadopted ideas, completed local work, and remaining decisions. No application acceptance suites, builds, or live integrations were run for this documentation change.

Source copies remain unchanged under [sources](../sources/), with originals and hashes recorded in the [source map](../source-map.json). Exact line links below retain mixed authorship and incomplete wording.

## Matomeru intake already owned by canonical domains

The first six external groups are references, not second backlogs. Competing cohesive-group and sparse-layer preset designs remain open in B-42. The newer editable-tree request remains separate from the completed Ima draft plugin.

<a id="ext-001"></a>
- EXT-001, [Keep the chosen detail tab across row navigation, B-41](../todo/panes.md#b-41).
  Provenance: user requests: [Matomeru requests L4](../sources/hub/prompts/mtm-todo.md).

<a id="ext-002"></a>
- EXT-002, [Presets for cohesive field groups, with recent selections, B-42](../todo/agents.md#b-42).
  Provenance: user requests: [Matomeru requests L6-13](../sources/hub/prompts/mtm-todo.md).

<a id="ext-003"></a>
- EXT-003, [Sparse composable preset layers, B-42](../todo/agents.md#b-42).
  Provenance: user requests: [Matomeru requests L15](../sources/hub/prompts/mtm-todo.md).

<a id="ext-004"></a>
- EXT-004, [Projects page, completion categories, and research depth, B-43](../todo/work.md#b-43).
  Provenance: user requests: [Matomeru requests L20-41](../sources/hub/prompts/mtm-todo.md).

<a id="ext-005"></a>
- EXT-005, [Continuous Vim-like tree editing and renaming, B-44](../todo/work.md#b-44).
  Provenance: user requests: [Matomeru requests L47-59](../sources/hub/prompts/mtm-todo.md).

<a id="ext-006"></a>
- EXT-006, [Offer work completion when closing a pane, B-45](../todo/panes.md#b-45).
  Provenance: user requests: [Matomeru requests L63](../sources/hub/prompts/mtm-todo.md).

EXT-002 and EXT-003 intentionally share B-42. Neither the cohesive-group preset design nor ordered sparse layers wins by consolidation. EXT-005/B-44's rename request does not broaden Ima's draft plugin into a live task-database editor. EXT-006/B-45 is an offer to complete work, not an inference that closing a pane means done.

## Attention and work

Related Matomeru concepts: [work](../outline/work.md), [panes](../outline/panes.md), [forms](../outline/forms.md). Remaining Matomeru work: [work](../todo/work.md), [panes](../todo/panes.md), [forms](../todo/forms.md).

<a id="ext-007"></a>
### EXT-007: Central funnel and the task-as-now product purpose

The user describes Ima/Now as a single-task completion app. These goals do not replace Matomeru's pane and work-group model.



Source provenance: user goals: [Ima user goals L4-9](../sources/notes/ima/iwants.md), [Ima user goals L47-50](../sources/notes/ima/iwants.md), [Ima user goals L59-71](../sources/notes/ima/iwants.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L9-12](../sources/notes/ima/unfinished-work.md); user: [Original mixed-author conversation L8-13](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L24-28](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L62-87](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-007).

<a id="ext-010"></a>
### EXT-010: Attribute actions rather than prohibit activity

The newer Ima inventory clarifies the user's original task-gating language as attribution, not permission. It reports task links for app shell runs, prompts, and app-launched persistent agents, but explicitly excludes a general external action model.



Source provenance: user goals: [Ima user goals L25](../sources/notes/ima/iwants.md), [Ima user goals L38-43](../sources/notes/ima/iwants.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L11](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L71](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L84](../sources/notes/ima/unfinished-work.md); historical assistant proposal: [Original mixed-author conversation L111-115](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L145-146](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L165-166](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L625-626](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L664-665](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-010).

<a id="ext-011"></a>
### EXT-011: Time, effort, attention, context, event history, and task kinds

The user's broad time, effort, attention, and context ambition includes a raw event log as one option. The complaint about excessive flexibility is an unfinished sentence, not a design decision.



Source provenance: user goals: [Ima user goals L30-39](../sources/notes/ima/iwants.md); mixed user goals and assistant model: [Original mixed-author conversation L29-44](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L135-148](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-011).

<a id="ext-012"></a>
### EXT-012: Idle reset, breaks, overrun splitting, and attention

The user specifies three-minute idle and fifteen-minute no-break resets. The conversation proposes the five-minute child prompt, timestamp model, and external activity mechanisms. The newer inventory reports idle/overrun, CLI touches, and out-of-pane nudges complete in Ima. This is source-reported behavior, not fresh proof of each mechanism or a Matomeru default.

- User threshold, later reported complete: After more than three minutes idle, unset or put back the active task, return to the picker, and notify the person.
- User threshold, later reported complete: After more than fifteen minutes working with no one-minute break, reset the task and offer a smaller piece.
- Historical assistant split-prompt proposal/report: Historical proposed prompt asks for the smallest piece finishable in five minutes; answer becomes an active child and parent is split. Empty answer may simply put the task back.
- Historical assistant session model: Track task session start, last activity, and breaks with timestamps/durations.
- Historical assistant activity proposal: Activity may come from shell/editor touches and tuios pane events, not just TUI keys.
- Historical issue, later source-reported fixed: An idle nudge must reach the pane/OS when the TUI is hidden; background refresh itself is not activity.

Source provenance: user goals: [Ima user goals L31](../sources/notes/ima/iwants.md), [Ima user goals L54-57](../sources/notes/ima/iwants.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L12](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L88-90](../sources/notes/ima/unfinished-work.md); historical assistant proposal/claims: [Original mixed-author conversation L156-173](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L198-203](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L315-320](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L516-535](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-012).

<a id="ext-013"></a>
### EXT-013: Picker, one-task Now view, split/finish loop, and completion review

The historical assistant describes the picker/Now loop, then reports a first implementation. The later inventory reports the core, Review, and Find complete. Oldest-first within smallest-first was proposed; the implementation report says oldest-first open leaves only. Session clocks coexist with the finish-count metric.

- Historical assistant design/report: Now shows one active task, its children and a clock, without an open-task dashboard while active.
- Historical assistant design/report: One done key logs completion and immediately opens the picker; choosing is one action, shrinking is one sentence.
- Historical implementation report: Picker can create and activate typed text on Enter; filter tasks and activate the selected match.
- Historical implementation report: Offer a random task key, historically Ctrl+R.
- Competing proposal and implementation report: Picker has no priority field. Proposed oldest-first within smallest-first differs from the later reported implementation of oldest-first open leaves only; preserve both.
- Historical implementation report: Only open leaves are pickable; a parent disappears while its child is open and returns after child completion.
- Historical implementation report: Support done, split, put-back, and quit actions, historically d/s/u/Ctrl+Q.
- Historical design/report: Review shows done history and count per day; historical philosophy makes finish count the metric, not hours worked.
- Historical metric/timer distinction: The historical mockup nevertheless shows active/idle elapsed clocks. Preserve metric-versus-session-timer distinction rather than deleting clocks.

Source provenance: historical assistant proposal/claims: [Original mixed-author conversation L103-109](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L117-133](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L154-180](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L302-320](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L497-554](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L88-90](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-013).

<a id="ext-014"></a>
### EXT-014: Task-dependent whole-app theme

The user wants the task to determine the whole app theme. The assistant proposes deriving colors from task id. The newer inventory reports task theming complete in Ima, but does not establish the optional fleet announcement.

- User goal, later source-reported complete: The active task is the mode and determines the whole app theme.
- Historical assistant palette proposal: Historical proposal derives palette from task id and changes borders/bars on task switch.

Source provenance: user goals: [Ima user goals L37](../sources/notes/ima/iwants.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L12](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L88](../sources/notes/ima/unfinished-work.md); mixed user and assistant: [Original mixed-author conversation L40-42](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L196-203](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-014).

<a id="ext-017"></a>
### EXT-017: Responsive background work and uniform option navigation

The newer Ima inventory reports persistent-agent refresh preserving focus and reading state, and lists Ctrl+n/Ctrl+p option navigation among completed core behavior. Refresh is explicitly not user activity.

- Source-reported behavior or evidence: Background activity must not reset input, focus, selection, reading position, modal state, or current screen.
- Source-reported behavior or evidence: Every option list supports Ctrl+n and Ctrl+p, including a focused filter. Enter acts on the selected option.
- Source-reported behavior or evidence: A refresh is not evidence of user activity for idle tracking.

Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L13-14](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L44](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-017).

<a id="ext-020"></a>
### EXT-020: Projects, documentation encouragement, and automation decisions remain open

The newer inventory leaves projects, writing encouragement, multiplexer expansion, and automatic clipboard/pane capture open. Ima's grouping by task cwd and parent tasks does not settle Matomeru's separate Projects-page request.



Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L65-73](../sources/notes/ima/unfinished-work.md); user goals: [Ima user goals L26](../sources/notes/ima/iwants.md), [Ima user goals L39](../sources/notes/ima/iwants.md).

[Decisions and disposition](../todo/ecosystem.md#ext-020).

## Context and knowledge

Related Matomeru concepts: [knowledge](../outline/knowledge.md), [work](../outline/work.md). Remaining Matomeru work: [knowledge](../todo/knowledge.md), [work](../todo/work.md).

<a id="ext-009"></a>
### EXT-009: Generic selector and typed items with metadata

The user asks for a generic selector and typed metadata. The historical assistant proposes a universal item shape and filtered collections. That shape is not an approved replacement for Matomeru's domain records.



Source provenance: user goals: [Ima user goals L27-28](../sources/notes/ima/iwants.md); historical assistant proposal: [Original mixed-author conversation L135-152](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-009).

<a id="ext-015"></a>
### EXT-015: Noise capture, triage, extraction, links, and deduplication

The conversation proposes typed Noise, extraction provenance, and triage as task work, then reports capture and poller behavior. The newer inventory reports Noise and capture/extract/drop complete in Ima. Manual clipboard/pane source labels do not establish automatic ingestion.

- Historical capture design/report: Capture raw pasted text, transcripts, links, command-line input/stdin, clipboard-labelled text, and pane output without requiring structure.
- Historical assistant Noise model: Noise is a typed item with body, source, timestamp, optional source reference and deduplication key.
- Historical capture report: Capture supports explicit source/ref labels and piped stdin.
- Historical design/report, later source-reported complete: List open noise, extract a task, and drop noise. Keep both task-to-noise and noise-to-created-task links.
- Historical assistant triage proposal: Treat triage-noise as a task so processing the inbox itself earns completion.
- Historical deduplication report: Repeated polling/capture should not create duplicates; historical prose uses source ids or content hashes.
- Historical intake design/report: Show open noise count in picker header; intake waits for between-task review instead of interrupting the current task.
- Newer source boundary and conditional automation: Automatic clipboard/pane capture is explicitly conditional; source says capture -s labels are manual today.

Source provenance: mixed user request and historical claims: [Original mixed-author conversation L125-126](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L138-148](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L184-188](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L339-340](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L342](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L363-375](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L73](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L88](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-015).

<a id="ext-016"></a>
### EXT-016: Learn-for-later runs and locked motivations

The user's deferred-learning goal strictly forbids working on nice-to-have results until later. The assistant proposes locked motivations, but also proposes logged early promotion. The final suggestion returns to nothing from the learning pane being pickable today. The newer inventory reports Later locks complete, without resolving all policy alternatives.



Source provenance: user goals: [Ima user goals L76-79](../sources/notes/ima/iwants.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L12](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L88](../sources/notes/ima/unfinished-work.md); mixed user and assistant: [Original mixed-author conversation L91-95](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L142-144](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L190-194](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L675-678](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-016).

<a id="ext-018"></a>
### EXT-018: Domain vocabulary and distinct concept levels

The user's vocabulary lists distinct Git, GitHub, terminal, work, shell, and AI concepts. Repeated terms such as session and repository belong to different domains. The source spelling errors are preserved in the copied note.



Source provenance: user goals: [Ima user goals L83-119](../sources/notes/ima/iwants.md).

[Decisions and disposition](../todo/ecosystem.md#ext-018).

<a id="ext-019"></a>
### EXT-019: Dedicated to-know questions and answers

The newer inventory says to-know currently has only a kind/label. Question, answer, and state are a historical assistant sketch, not completed dedicated behavior.



Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L67](../sources/notes/ima/unfinished-work.md); historical assistant model: [Original mixed-author conversation L140-144](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-019).

<a id="ext-024"></a>
### EXT-024: Context matchers attach metadata from streams and events

The user leaves an unfinished matcher sketch over prompts, replies, and shell streams. The copied source retains the repeated NewTerminal entry and incomplete initialization phrase. No matcher grammar or initialization semantics were agreed.



Source provenance: unfinished user note: [Unfinished context-matcher note L1-20](../sources/notes/ima/ideas/context-matchers.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L79](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-024).

## Agent review and automation

Related Matomeru concepts: [agents](../outline/agents.md), [automation](../outline/automation.md). Remaining Matomeru work: [agents](../todo/agents.md), [automation](../todo/automation.md).

<a id="ext-021"></a>
### EXT-021: Task context pointers and terminal focus

The historical assistant separates physical pane/window, long-lived session, and task attribution. Remembered pointers, focus/spawn behavior, and title updates are proposals. Now deliberately avoids a pane list, unlike Matomeru.



Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L81](../sources/notes/ima/unfinished-work.md); historical assistant proposal: [Original mixed-author conversation L600-626](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L641-642](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L667-673](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-021).

<a id="ext-022"></a>
### EXT-022: External prompt/reply attribution and tuios event intake

The newer inventory distinguishes completed app-launched links and tuios activity/state noise from unbuilt arbitrary external attribution and proposed mail/pane intake. Historical event lists are proposals, not live coverage proof.



Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L71](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L79](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L82-84](../sources/notes/ima/unfinished-work.md); historical assistant proposal: [Original mixed-author conversation L611-637](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L643-665](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-022).

<a id="ext-023"></a>
### EXT-023: Automatic agent follow-up child tasks without spinner babysitting

The assistant proposes small read-reply/answer-agent children for inactive tasks and an inline message for the active task. The newer inventory explicitly says automatic child extraction is not built, despite completed app-launched attention.



Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L83-84](../sources/notes/ima/unfinished-work.md); historical assistant proposal: [Original mixed-author conversation L639-665](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-023).

<a id="ext-025"></a>
### EXT-025: Concise task/action/change walkthrough

The user's change-walker note asks for concise explanations of task/action/change and why, so the owner can shape outcomes. Its damaged lines are not an exact output-format specification.



Source provenance: unfinished, partially corrupted user note: [Unfinished change-walker note L3-10](../sources/notes/ima/ideas/change-walker.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L80](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-025).

<a id="ext-028"></a>
### EXT-028: Persistent task-scoped agents from the TUI, completed in Ima

The Ima inventory marks task-scoped persistent agents complete. Native tuios panes and durable run records preserve app-launched task links. Done/needs-input/error attention is distinct from automatic follow-up child tasks.

- Source-reported behavior or evidence: a opens a task-scoped launcher with inherited cwd, configurable interactive command, multiline prompt, and key/button submission.
- Source-reported behavior or evidence: Use native tuios panes that survive task switches and Now exit. Durable run records reconnect after restart. No worktree creation or custom agent supervisor is implied.
- Source-reported behavior or evidence: g lists task agents from Now or all agents from Picker normal mode. Details include original prompt, status, cwd, and bounded pane output.
- Source-reported behavior or evidence: o focuses the native pane. x asks before stopping only that pane; cancellation does not affect others.
- Source-reported behavior or evidence: Keep selection, reading position, Ctrl+n/p navigation and modal focus across background refresh.
- Source-reported behavior or evidence: App-launched done/needs-input/error transitions create deduplicated task-linked attention across watcher and polling. Find and Noise can open agent details.

Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L39-49](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-028).

<a id="ext-029"></a>
### EXT-029: Persistent-agent prerequisites and bounded recovery guarantees

The Ima inventory records commits and an isolated live Now/tuios OMP exercise. It states native CLI prerequisites, bounded output snapshots, and the non-restart-safe one-shot boundary. This is recorded verification, not an exercise performed for this consolidation.

- Source-reported behavior or evidence: Source reports commits 91a6480 and 572a596 and an isolated live Now/tuios OMP exercise of prompt delivery, switching, restart, output recovery, navigation, focus, cancelled stop, and isolated stop.
- Source-reported behavior or evidence: Requires tuios and an installed authenticated interactive agent CLI. Provider login, trust, and approval stay in its native pane.
- Source-reported behavior or evidence: Outside tuios, attach to dedicated now-agents session; focusing does not launch a terminal application.
- Source-reported behavior or evidence: Output is a latest bounded snapshot, not a continuous archive while Now is closed.
- Source-reported behavior or evidence: Existing :ask one-shot is not restart-safe; a is the persistent workflow.
- Source-reported behavior or evidence: Keep arbitrary external attribution and automatic child-task extraction separate from this completed app-launched scope.

Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L47-49](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-029).

## Integration and tooling

Related Matomeru concepts: [panes](../outline/panes.md), [forms](../outline/forms.md), [agents](../outline/agents.md), [knowledge](../outline/knowledge.md), [automation](../outline/automation.md). Remaining Matomeru work: [panes](../todo/panes.md), [forms](../todo/forms.md), [agents](../todo/agents.md), [knowledge](../todo/knowledge.md), [automation](../todo/automation.md).

<a id="ext-008"></a>
### EXT-008: TUI, optional exact-parity web UI, and optional multiplexer

The user requests a modal TUI, makes web parity conditional, and questions whether a full multiplexer is needed. Neither the web UI nor another multiplexer is a commitment.



Source provenance: user goals: [Ima user goals L15-24](../sources/notes/ima/iwants.md), [Ima user goals L29](../sources/notes/ima/iwants.md); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L10](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L68](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L72](../sources/notes/ima/unfinished-work.md); user: [Original mixed-author conversation L19-20](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-008).

<a id="ext-026"></a>
### EXT-026: Durable Neovim task-entry plugin, completed in Ima

The 2026-10-17 Ima inventory marks the durable Lazy task-entry plugin complete. Durable pending text becomes tasks only on explicit apply. This is neither session-only scratch nor a live editor for existing task records, and is separate from Matomeru B-44 renaming.

- Source-reported behavior or evidence: Capture completed Lazy-installable unixsuperhero/ima plugin exposed as require('now'), :Now, and :NowApply.
- Source-reported behavior or evidence: Open or reuse a dedicated split without replacing unsaved buffers. Enter creates task rows, Tab/Shift-Tab changes task/subtask nesting, normal Vim editing and undo remain.
- Source-reported behavior or evidence: Bindings are configurable or disableable and must not claim unrelated global keys.
- Source-reported behavior or evidence: Pending text lives in app-owned durable draft.json and survives Neovim restarts. Temporary means lifecycle, not an OS cache.
- Source-reported behavior or evidence: Explicitly apply the whole draft to real tasks with hierarchy and original cwd. Validate before publication, keep failed drafts, use batch receipt against duplicate retries.
- Source-reported behavior or evidence: This is neither session-only scratch nor a live task-database editor. General rename/reparent/delete APIs are not required by this plugin workflow.
- Source-reported behavior or evidence: Installation, durable draft path, apply/recovery behavior, and verification commands were requested in repository README.

Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L16-29](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-026).

<a id="ext-027"></a>
### EXT-027: Plugin evidence, publication, and durability limits

The Ima inventory records plugin commits, publication, installed configuration, real editor/storage exercises, and bounded durability claims. These are historical reported checks. This consolidation runs none of them and does not extend them to power loss or other versions.

- Source-reported behavior or evidence: Requested edge coverage includes empty and mid-line Enter, subtree edits, root boundaries, undo/redo, split/window reuse, restart, failed apply/save, configurable keys, concurrent recovery ownership, and lost-response retry.
- Source-reported behavior or evidence: Record source-reported plugin commits 3924a01,4e48eeb,e678a8e; documentation e3612fc,2efe02c,e678a8e; publication to origin/main on 2026-10-17.
- Source-reported behavior or evidence: Installed GitHub plugin and Lazy lock were at 572a596, with both commands enabled; configured CLI is uv run --project ~/proj/now now because no standalone now is on PATH. Existing Neovim instances need restart.
- Source-reported behavior or evidence: Acknowledged asynchronous draft saves survive restart; a kill before save completion can lose the just-typed edit. Lifecycle flush and failed-save recovery require writable storage.
- Source-reported behavior or evidence: Source reports Neovim 0.12.3, injected filesystem failures, and real restart/application behavior, not physical power-loss or all OS/version testing.

Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L18](../sources/notes/ima/unfinished-work.md), [Ima inventory, 2026-10-17 L25-37](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-027).

<a id="ext-031"></a>
### EXT-031: Slack/GitHub sources feed the noise funnel

The historical conversation reports Slack/GitHub polling and source labels; the newer inventory lists both pollers complete in Ima. The direct Slack API history is superseded by the user's h-mcp request. Source-reported feature existence does not prove authenticated live coverage for every integration.

- Historical source goal/report: Include Slack messages, threads, mentions, and direct messages as funnel sources.
- Historical source goal/report: Include GitHub review-request notifications, PR inbox, CI changes, and PR status/review-decision changes.
- Historical source labels: Preserve source labels cli,clipboard,pane,slack.message,slack.thread,github.review_request,github.pr_inbox,github.ci_status,github.pr_status.
- Historical GitHub implementation report: GitHub path uses authenticated gh, captures open requested-review PRs and unread PR notifications.
- Historical GitHub state-change report: Record first observed own-PR CI/review state silently, then produce noise only for subsequent changes.
- Historical polling design/report: Polling may run once per source or both, and loop with a configurable interval, historically 120 seconds. One failing source should not stop the others.
- Superseded Slack transport history: Slack original direct-API version searched mentions/thread replies and incoming DMs, starting DM history 24 hours back, but later h-mcp request superseded that transport.

Source provenance: mixed user requests and historical claims: [Original mixed-author conversation L215-217](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L325-340](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L342](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L365-400](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L88](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-031).

<a id="ext-032"></a>
### EXT-032: Slack via h-mcp and alternate server providers

The user explicitly changes Slack transport to h-mcp and names alternate providers. The assistant reports implementation but says real server catalogs were unavailable. Guessed tools and fake tests are not live Slack/Glean/Runlayer proof.



Source provenance: mixed user request and historical assistant claims: [Original mixed-author conversation L412-482](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-032).

<a id="ext-034"></a>
### EXT-034: Historical first-slice architecture and stack alternatives

The user approved the narrow first slice. Python/Textual and a plain-file store were the assistant's stack suggestion based on Thinktank's Python tooling; the transcript later reports a separate Now repository and JSONL replay. Thinktank registration is historical context, not a request for another repository.

- User first-slice approval: User approved the first slice: Now view, picker, done key, timers, with noise/learning/theming later.
- Historical assistant stack suggestion: Historical suggestion was Python/Textual because Thinktank was Python, with a JSONL/plain-file store.
- Historical assistant implementation report: Source reports append-only events.jsonl at ~/.local/share/now/ with state replay and activity file mtime touched by shell precmd/editor hook.
- Historical Thinktank registration report: Thinktank registration described a single-task TUI at ~/proj/now with notes ~/notes/proj/now; separate repository scaffold was historical work, not a request to create another today.

Source provenance: historical assistant proposal/claims plus user build approval: [Original mixed-author conversation L205-213](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L215-247](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L302-320](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-034).

<a id="ext-035"></a>
### EXT-035: pstack role-model overrides and global include

The user requested pstack setup, dismissed the first questions, then selected skill-default role mapping and global inclusion. Other role mappings/include locations were offered alternatives. The assistant reports writing the override sheet. Those old model names are environment history, not authorization for this assignment.

- User setup request and recorded choice: User requested /setup-pstack, accidentally dismissed the questions, then chose skill-default role mapping and a global ~/.claude/CLAUDE.md include.
- Presented but unchosen alternatives: Record alternate choices presented: Fable every role, Sonnet workers/Opus judges, inherit parent; include globally, project-local Thinktank include, or do not wire. These were presented alternatives, not chosen goals.
- Historical assistant completion claim: Historical output says ~/.claude/pstack-models.md was written and included globally; rerunning setup overwrites the sheet.
- Historical environment constraint: Historical accepted session slugs were opus,fable,sonnet,haiku rather than stamped full model slugs. Preserve as old environment context, never apply them to this Sol-only research assignment.

Source provenance: historical user setup request/selection and assistant completion claim: [Original mixed-author conversation L250-253](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L273-300](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L330-337](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-035).

<a id="ext-036"></a>
### EXT-036: Publish user stories through mdoc

The user requested core-UX stories and publication through mdoc/openlink. The assistant reports repository and personal Markdown copies plus mdoc item 834. The missing render-preview tool and local URL are historical provenance, not current availability proof.

- User publication request: User requested a few core-UX stories, then a Markdown file opened with mdoc, then openlink.
- Historical assistant publication claim: Historical report points to repository docs/user-stories.md, ~/claude/docs/now-user-stories.md, mdoc item 834, and http://127.0.0.1:4387/items/834.
- Historical missing-tool boundary: Historical mdoc-render preview tool was missing; publication reportedly happened without that preview. Preserve provenance, not a claim those transient/local links still work.

Source provenance: user request and historical assistant completion claim: [Original mixed-author conversation L484-493](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt), [Original mixed-author conversation L571-589](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt).

[Decisions and disposition](../todo/ecosystem.md#ext-036).

## Packaging

Related Matomeru concepts: [delivery](../outline/delivery.md). Remaining Matomeru work: [delivery](../todo/delivery.md).

<a id="ext-030"></a>
### EXT-030: Standalone executable and release distribution backlog

The inventory reports an exercised macOS arm64 PyInstaller executable at a historical /tmp path, older than later plugin/navigation work. It reports source commits published to Ima origin/main, not release artifacts or current artifact existence.

- Source-reported source publication: Source says local Now project commits were published to unixsuperhero/ima origin/main on 2026-10-17; release artifacts remain separate.

Source provenance: inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L51-61](../sources/notes/ima/unfinished-work.md).

[Decisions and disposition](../todo/ecosystem.md#ext-030).

## Superseded rough edges

<a id="ext-033"></a>
### EXT-033: Preserve historical UX rough edges as resolved history

The newer Ima inventory supersedes the older assistant rough-edge list. CLI touches, hidden-pane nudges, Noise, Review, theming, and the broader listed core are source-reported complete. An older missing-feature claim does not reopen them.

- Source-reported behavior or evidence: Historical rough edges were CLI triage not touching activity, hidden-pane idle toast, no TUI Noise screen, no Review screen, and no per-task theme.
- Source-reported behavior or evidence: The newer unfinished-work inventory says these and TUI/CLI core, task/subtask storage, idle/overrun, CLI touches, out-of-pane nudges, capture/extract/drop, GitHub/Slack MCP pollers, task-attributed runs, tuios activity/state noise, Later locks, Review, Find, theming, and Ctrl+n/p navigation already exist.
- Source-reported behavior or evidence: Capture those as source-reported completed Ima behavior, not unresolved tasks and not proof of live integration coverage.

Source provenance: historical assistant report: [Original mixed-author conversation L556-569](../sources/notes/ima/ideas/fml-2026-10-15-180521-goal.txt); inventory updated 2026-10-17; source explicitly separates proposals from commitments: [Ima inventory, 2026-10-17 L86-90](../sources/notes/ima/unfinished-work.md).

[Disposition](../todo/ecosystem.md#ext-033).
