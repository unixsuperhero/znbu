# Automation remaining work

[Automation outline](../outline/automation.md) records implemented behavior and its limits. Implemented B-12, B-15, B-17, B-18 and the two-rule B-35 baseline are not active backlog items. B-01 is superseded. [Original acceptance and historical notes](../sources/znbu/docs/todo.md) remain preserved.

<a id="b-16"></a>
## B-16 Complete Slack context capture and live monitoring

Status: partial · priority: p1 · size: L.

[Implemented baseline](../outline/automation.md#b-16) includes settings, oncall-dependent queries, deterministic fixture assessment and scheduled prompts. Remaining acceptance:

- Store captured Slack messages as context kind slack with the permalink and correct task/project ownership, or explicitly approve a change to that original contract. Preserve message dedupe and an action item's direct link to its thread; slack_messages alone does not close this requirement.
- Run the generated agent-path prompt by hand against an authenticated pane with Slack MCP. It must search mentions, DMs and participated threads, add oncall channels/tag only during the persisted Monday-start week window, and produce at least one permalink action item through action_item_create.
- Retain that real call to seed [B-14 harvest/replay](agents.md#b-14). Once replay exists, add the scheduled lookup path for messages since the last check; do not present fixture reads as external MCP replay.
- Verify the first available live Slack run separately from fixture results. Preserve fixture acceptance: captured-message assessment yields permalink source_url items and lights the indicator; settings survive restart, `mtm slack settings` prints them, and oncall changes the next query. Existing fixture evidence is recorded, not live evidence.

<a id="b-19"></a>
## B-19 Linear as a source of action items

Status: open · priority: p2 · size: S.

[Target and existing preference](../outline/automation.md#linear). Through Linear MCP using B-14 replay or an agent prompt, ingest tickets assigned to the user, mentions and state changes on watched tickets. Produce deduplicated ActionItems with service linear and source links. Linear complements Slack and GitHub monitoring rather than replacing them. A preference without ingestion is not implementation evidence.

<a id="b-20"></a>
## B-20 Supervise prompt schedule lifetime and complete report chaining

Status: partial · priority: p1 · size: M.

[Implemented scheduling baseline](../outline/automation.md#b-20) includes persisted definitions, run histories, bounded dispatch, overlap prevention, busy-pane skipping and on_result submission. Remaining acceptance:

- Supervise the launched agent turn after prompts.submit returns. The original timeout requirement says the scheduler kills an over-time run; bounding only dispatch/lookup does not satisfy it. Preserve target identity and record the terminal outcome without inventing delivery from a missing queue row. Coordinate with [queue outcomes B-63](agents.md#b-63) and [phase2 prompt correlation B-64](agents.md#b-64).
- Exercise a found GitHub review request that starts an agent, creates a Markdown review report through document_report and links the report back to the originating action item. Generic on_result prompt submission is only the implemented baseline. The optional B-17 automatic review follow-up is retained here without implying all GitHub checks must run a reviewer.
- Retain full original operational acceptance while extending it: a 300-second github.check lookup runs within its interval, appears in history with outcome, and its items carry schedule_id; prompts run at most once per interval and never while the previous target remains working; every run records duration/outcome and visible failure without repeat-notifying one occurrence. Intervals and timeouts remain finite and bounded.

<a id="b-75"></a>
## B-75 Complete the phase2 reminders management page

Status: open · priority: p3.

[Reminder delivery baseline](../outline/automation.md#reminders) is implemented; the original [phase2 plan](../outline-phase2.md) proposes a dedicated next-due-ordered page with t toggle, s snooze and e edit. Register it under the unit rather than adding a shell-specific page switch. Apply [unit-page scope rules](../outline/architecture.md#unitpages): S scope/all, read-only all mode except Assign, generated keys/help/palette and unit-ID ordering. Keep one reminder delivery loop and advance-before-delivery behavior. Establish which proposed management actions exist and verify only the remaining ones against a throwaway daemon.

<a id="b-77"></a>
## B-77 Settle the remaining MCP survey API proposals

Status: open, target decisions · priority: p2. [B-12 baseline and survey distinction](../outline/automation.md#b-12).

Retain these original alternatives without implying the whole vaim API was adopted:

- Caller origin: whoami also identifies the todo/action item that spawned the pane, analogous to get_current_thread_action_item_origin. Bind identity server-side, not from tool arguments, and settle the original no-other-pane-task security intent explicitly.
- Task lifecycle: set_status with expected_version/status/completion_summary/verification/commit/blocker_reason, evidence required on done, and reopen_item. Current task_status summary and optional version behavior is the baseline, not proof of every stronger survey constraint.
- Phase reports: report_progress plus complete_phase {summary?, resultJson?} and fail_phase {reason}.
- Documents: create_document {title, markdown} returns stable ID/route and links the originating thread; update_document {id,title,markdown}, list_documents and get_document. Current document_report reports an existing file instead.
- Action annotations: create_action_item_note {action_item_id,text,important?} and create_action_item_context {label,content,important?} preserve the one-shot add-to-current-item idea.

Choose the supported contract and link accepted gaps to the owning domain before implementation. The survey explicitly excluded agent-loop/tag/polling/typecheck-watcher tools; service monitoring remains schedules and units, not duplicated MCP orchestration.
