# Automation and attention

[Automation todo](../todo/automation.md) contains only unfinished acceptance. The [original backlog](../sources/znbu/docs/todo.md) and [implementation outline](../sources/matomeru/docs/outline.md) preserve dated claims and alternatives. Historical suite paths below were recorded by earlier work, not run in this consolidation.

<a id="b-12"></a>
## B-12 MCP shell and agent identity

Status: implemented. `internal/mcp` owns no domain table. It exposes bus commands and registry sources through `mtm mcp serve`, a newline-delimited JSON-RPC 2.0 stdio server. Supported requests include initialize, ping, tools/list and tools/call; initialized notifications and empty resources/list and prompts/list are accepted. Known protocol versions are echoed, otherwise 2025-06-18 is selected. Protocol errors are JSON-RPC errors; tool failures have isError and a code/message result.

Identity is bound from TUIOS_SESSION and TUIOS_PANE_ID, with MTM_SESSION/MTM_WINDOW bridge overrides, not from tool arguments. Work resolves current pane ownership on each call so reassignment applies to the next call. Outside a pane, whoami reports bound:false; pane-bound tools reject no_pane. Stdio does not need the earlier proposed DECK_TOKEN. HTTP is deferred unless a harness cannot use stdio. Original vaim inspiration was environment-bound identity and a stdio bridge, not adoption of its loops, tags or provider polling tools.

```js
Identity = { session, window, task_id?, project_id?, cwd?, harness?, bound }
Tool = { name, description, inputSchema, command?, needs_pane }
Paths = { executable, data, socket? }
HarnessConfig = { harness, args?, file?, entry?, written }
```

Tools expose whoami; task_list with pin/all and status; task_done with task_id/note; task_status with expected_version/status/summary/verification/commit/blocker; task_note_add with owner/text; context_add with kind/text; document_report with path/title/kind/summary; report_progress with message; todo_list, todo_note_add, todo_claim; action_item_create. Task status uses the task updated stamp for optimistic checks, with zero skipping the check; done requires a summary and evidence becomes a note. Notes currently accept task/project owners; arbitrary-owner expansion is [B-05](../todo/knowledge.md#b-05). Context ownership follows the bound pane, ignoring a supplied task_id. Document reports require existing Markdown/HTML files and emit tool activity under the reporting task. Proposed document create/update/get APIs and complete_phase/fail_phase were survey alternatives, not shipped tools.

The original vaim survey also proposed caller origin (the todo/action item that spawned the pane), important notes/context on an action item, explicit reopen, phase completion/failure and document creation/update/read tools. These remain [API target decisions B-77](../todo/automation.md#b-77), not claims about current tools. The survey's security intent was to bind identity server-side and prevent task-identity spoofing through arguments; optional task IDs and stronger ownership/evidence requirements must be described explicitly when those APIs are settled.

Every MCP call records `mcp.<tool>` in history under its pane/task/project; the wrapped mutation also records its normal command entry. The server flushes history itself, so persistence does not depend on a running TUI. Live refresh uses harness tool_done activity plus best-effort pane status. `mtm mcp tools` matches tools/list; config/install/whoami provide CLI discovery.

Agent start preparation configures supported harnesses before the first prompt: Claude receives an mtm-owned --mcp-config file; Codex gets mcp_servers.mtm command-line settings; OMP merges mcpServers.mtm in its config while preserving other servers and respecting PI config directories; opencode merges a local mcp.mtm entry in its XDG config. The program basename after env selects the adapter. Unknown harnesses get no adapter, and configuration failure is visible without blocking agent start.

Evidence: `internal/mcp/server.go`, `tools.go`, `harness.go`, `cmd/mtm/mcp.go`, agent-prepare wiring; commits 75c2e1f and e6147c5. Recorded `mcp_server` case: `/root/proj/night/logs/lane-2-B-12.log`. That fixture evidence does not claim every live harness deployment was exercised.

<a id="b-15"></a>
## B-15 Action items and global attention

Status: implemented. Actions unify attention from Slack, GitHub, Linear, agents, schedules and other named services. Commands create, seen, dismiss, promote-to-todo/task, open and configure share the bus and CLI concept `mtm action`; MCP action_item_create calls actions.create.

```js
ActionItem = { id, service, source_url, title, text, action_type, category?, task_id?, project_id?, schedule_id?,
  created, updated, seen_at?, dismissed_at?, promoted_todo_id?, promoted_task_id?, extra: {} }
Indicator = { lit, count, unseen, mark }
```

Dedupe uses service+source_url. Repeats refresh text/title and report new:false; reopen explicitly un-dismisses. An item needs attention until dismissed or promoted. Seeing it never clears attention. Rows order unseen before seen before resolved, group by service and use newest-first order. Opening marks seen and opens HTTP(S) URLs. Todo promotion uses the todo unit; task promotion uses explicit ownership or the pinned task/project. Historical action_todos was transitional storage, not a second todo product.

The Actions page uses I; Enter opens, x dismisses, t promotes to todo, c promotes to task. The earlier d/T choices conflicted with shared navigation and Tasks. The global scoped header shows the attention mark on every page. Optional new-item OS notifications are off by default; failure is an event, not a failed create. New rows from another process appear on the next refresh. Dismissal of the last item clears the mark within a refresh.

Evidence: `internal/actions/actions.go`, `internal/ui/scoped_header.go`, commit 1971608. Historical action_items coverage checks duplicate URL, indicator, dismiss and todo promotion: `/root/proj/night/logs/lane-3-B-15.log`.

<a id="reminders"></a>
## Reminders

Reminders own a cancellable delivery loop and `reminders` table. Commands add, patch, delete and toggle accept finite recurring intervals. Due occurrences advance next before external delivery. Terminal/session and OS delivery are independent; one failure cannot repeatedly notify the same occurrence. Failure remains visible. This resolves the old question about an events-style cancellable unit, but does not imply a long-lived server exists.

```js
Reminder = { id, title, message, session?, interval: seconds, enabled, next, last, created }
ReminderEdit = { title?, message?, session?, interval?, enabled? }
```

Evidence: `internal/reminders/reminders.go`, `cmd/mtm/wiring.go`. Current management is a list modal opening the patch form, not a registered reminder Page. The phase2 next-due page with toggle/snooze/edit remains [B-75](../todo/automation.md#b-75), not established by the delivery loop.

<a id="b-20"></a>
## B-20 Schedule baseline

Status: partial. Schedules are a sibling of reminders, not an expanded reminder table. They own schedules and the last 500 schedule_runs. Commands add/patch/delete/toggle/run share `mtm schedule`; reads list/history/detail expose status and failures. Page Z uses Enter run-now and t toggle.

```js
Schedule = { id, title, interval: seconds, timeout: seconds, enabled, next, last, created, updated,
  run: {kind:"prompt", target:StartSpec|{window}, text}
     | {kind:"lookup", command, args:{}}
     | {kind:"command", name, args:{}},
  on_result?: {kind:"prompt", text, target?}, window?, last_run_id?, last_outcome?, last_error? }
RunRecord = { id, schedule_id, title, kind, started, finished, duration_ms,
  outcome:"ok"|"found"|"nothing"|"failed"|"timeout"|"skipped", summary, error?, window?, chained?, result?, manual? }
```

Intervals are positive and at most 30 days. Timeout defaults to 300 seconds and is at most 3600. The loop ticks every second, advances next before work, and excludes overlapping executions rather than queueing. Prompt dispatch remembers its pane and skips while it is working, awaiting or has subagents. Lookups receive schedule_id; returned found/new/items can trigger on_result. Commands execute through the bus. Every run emits schedules.ran and command-run history with duration/outcome; errors stay on the row and run list rather than repeatedly notifying.

The loop starts with the TUI; CLI run-now works independently. The dispatch deadline does not supervise or kill an agent turn after prompts.submit returns. Generic on_result prompt submission does not prove an end-to-end PR review report linked to its action item. [Remaining acceptance](../todo/automation.md#b-20) keeps both gaps. Queue state and phase2 turn correlation remain [agents work](agents.md#queueoutcomes) and [unit prompts](agents.md#unitprompts).

Evidence: `internal/schedules/schedules.go`, commit 2af9005. Recorded schedules case: `/root/proj/night/logs/lane-3-B-20.log`.

<a id="oncall"></a>
## Shared oncall window

`internal/oncall` owns oncall_settings, configure and settings read. Slack and GitHub share the same window instead of independent calendar logic.

```js
Oncall = { mode:"auto"|"on"|"off", start:"YYYY-MM-DD", weeks:1.., channels:[name], tag:"@oncall" }
// start is a local Monday. Auto is active in [start, start + weeks*7 days).
```

<a id="b-17"></a>
## B-17 GitHub review requests

Status: implemented. GitHub settings include user, personal extra review terms, oncall_query, oncall_repos and poll_interval. A personal check runs `gh search prs --review-requested=<user> --state=open --limit 100`, never substitutes team review requests. Only while oncall is active does a second configurable team/repository search run. A PR found in both queries is still one action, deduped by URL, with action_type pr-review and category review-requested or oncall. Schedule IDs pass through.

`github.install-schedule` installs one lookup at the configured interval and reuses its existing ID on repeat. gh calls have a 60-second deadline. gh_failed is visible in github_state.last_error and CLI state reads. Optional agent-review/report follow-up is a target through B-20, not a dedicated shipped workflow.

Evidence: `internal/github/github.go`, `internal/oncall/oncall.go`, commit 570bf6d. Recorded github_reviews fixture checks personal/oncall argv and action dedupe, not a live GitHub account: `/root/proj/night/logs/lane-3-B-17.log`.

<a id="b-18"></a>
## B-18 Authored PRs and watch polling

Status: implemented. `github.refresh-mine` requests all open authored PRs, retaining drafts. New rows begin unwatched with unknown CI; rows absent from refresh are marked closed. `github.watch` and `github.snooze` persist. Snooze defaults to next local midnight; the list hides until then without requiring a timer mutation.

```js
MyPR = { id:nodeID, url, number, repo, title, draft, state:"OPEN"|"MERGED"|"CLOSED",
  ci:"pending"|"pass"|"fail"|"unknown", checks:[{name,state,url}], reviews:[{who,state}],
  review_decision?, comments, mergeable?, last_change, watching, snoozed_until?, discovered, polled?, updated_at }
```

One GraphQL nodes query polls all watched, unsnoozed, open PRs; none means no call. It reads comments, the last 30 reviews and head status/check contexts. The first poll establishes a baseline. Later CI/comment/review/approval/merged/closed/conflict differences each produce one pr-status item naming the change; the occurrence URL fragment keeps separate changes distinct. Watched changes request OS notification. Poll interval defaults to 300 seconds with minimum 30. Page V uses Enter open, v watch and z snooze; w remains the tree key.

Evidence: `internal/github/prs.go`, commit bf40deb. Historical github_prs fixture covers three PRs in one call, one CI-change item, persistence and clock-advanced snooze: `/root/proj/night/logs/lane-3-B-18.log`. The concurrent owner's e4cf07a now adds AI/Git/GitHub subsections sharing canonical repository/branch sources, while preserving these Watched PR operations. [Owner-reported watched-action and live GitHub evidence](delivery.md#effortpolicy) is separate from the older fixture; no new run occurred here.

<a id="b-16"></a>
## B-16 Slack baseline

Status: partial. Slack settings, query generation, fixture capture/assessment and scheduled agent prompts exist. Outside oncall, relevant messages are mentions, DMs and participated threads; inside the window, every message in configured channels and every tag mention also qualifies. Classification orders oncall, DM, mention, thread, dropping unrelated messages.

```js
SlackSettings = { username, user_id?, watch_dms:true, watch_threads:true, fixture_path?, interval:300 }
Message = { id, channel, channel_id?, user, text, ts, thread_ts?, permalink, dm?, participants?,
  kind:"mention"|"dm"|"thread"|"oncall", reason, captured, assessed_at?, action_id?, schedule_id? }
```

Commands configure/capture/assess/check/open/install-schedule and reads settings/prompt/queries/messages/state/list expose the pipeline. The Slack page Q begins with settings/oncall summary, then newest captured messages. Permalinks are action source_url and dedupe keys. `slack.check` currently reads fixture_path, not live MCP replay. Agent-path install generates a fixed prompt from current queries and asks an MCP-equipped pane to answer only with action_item_create calls or nothing. The earlier survey found no Slack/Glean/Linear/GitHub MCP calls to seed replay, so no log fallback was claimed.

Captured messages live in slack_messages, not context kind slack. No authenticated live Slack MCP run is established. [B-16 remaining acceptance](../todo/automation.md#b-16) keeps context ownership/permalink, live-call and replay requirements. [MCP harvest](../todo/agents.md#b-14) is the replay dependency.

Evidence: `internal/slack/slack.go`, commit 4f58436. Recorded slack_monitoring fixture only: `/root/proj/night/logs/lane-3-B-16.log`.

<a id="linear"></a>
## Linear target

Only the disabled-by-default linear.enabled preference exists. [B-19](../todo/automation.md#b-19) retains assigned tickets, mentions and watched-state changes through MCP replay or an agent prompt, producing service:linear action items. Linear complements Slack and GitHub; it does not replace either.

<a id="b-35"></a>
## B-35 Stuck-pane checks

Status: implemented for two rules. `panes.stuck-check` is a stateless lookup over daemon agent_state_at. Same-state defaults to 1200 seconds in working with no commit in the pane cwd since then. Waiting-input defaults to 600 seconds in needs_input. It raises one action per pane/rule/state episode; dismissing silences that episode until state changes. Action extra contains rule/evidence/session/window/since; source_url is pane:// with rule and since.

```js
StuckRule = { id:"same-state"|"waiting-input", threshold:seconds }
StuckCheck = { schedule_id?, rules?:[StuckRule] }
StuckMatch = { session, window, name, rule, since, evidence, action_id, new }
```

Check for stuck panes runs once; Watch for stuck panes adds a 60-second schedule. Nothing is enabled by default. No Markdown ownership edits, mail loop or private state file remain. Evidence: `internal/panes/stuck.go`, removal commit 271da2c. The recorded stuck_check case tests duplicate suppression, commit suppression, waiting-input and dismissal; it was not rerun here.

The original repeat-failure proposal, the same file/tool command failing three times, is explicitly optional and unimplemented. It needs pane tail and harness meta.now; adopting it requires a separate decision, not declaring a third shipped rule or silently making it mandatory.

<a id="b-01"></a>
## B-01 Superseded fleet orchestrator

Status: superseded by B-35. The former always-on worker watcher detected long same-state/no-commit work, repeated failures, waiting input and size-based item overruns. It read tails/notes, sent one question by tuios mail, released repeated-plan workers back to ready with a dated note, answered only already-documented input questions, and wrote an overnight report. Its acceptance included progressing-worker safety, reading needs_input before keys, finite calls and daemon-restart survival. Those were the removed design, not current product requirements.

Historical thresholds were working for more than twenty minutes without a branch commit, the same file edit/command failure three times, needs_input beyond ten minutes, and item duration above ninety minutes for S or three hours for M. It was to send one mail within twenty-five minutes, release a looping worker within sixty, never interrupt slow progress, read input prompts before keys and report every touched item by morning. These retired acceptance numbers do not apply to B-35's action-only behavior.

The implementation existed in commit 956dcd5 and was removed with cmd/orchestrator, internal/orchestrator, its suite and todo Markdown-edit helpers. Original thresholds, ordered escalation and historical verification remain in [B-01 source](../sources/znbu/docs/todo.md). B-35 replaces autonomous intervention with visible action items; repeat-failure remains optional as stated above.
