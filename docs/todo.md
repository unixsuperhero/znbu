# Todo

The one place to write down what deck should do next. Humans add items; agents on vps2 pick them up.
Finished items roll into the outline, so this file only ever holds open work.
[The outline](outline.md) stays the target design; an item here is work toward it and moves into the
outline's done list when it ships.

## How to use this file

- One item per `### B-nn` heading. Give it an ID, a status, a size and acceptance you could check from
  a terminal. Empty fields are fine; a title alone is a valid item.
- Status is one of `idea`, `ready`, `claimed`, `review`, `done`, `parked`. Only `ready` items may be
  claimed.
- An agent claims an item by setting `status: claimed` and `owner: <tuios agent id or name>` on a branch
  pushed to the vps2 hub, so two agents never take the same item. It flips to `review` with the branch
  name and the verification log path, and the human or the orchestrator moves it to `done`.
- Keep notes under the item, dated, newest last. Decisions go there, not in chat.
- Work the list top to bottom inside a priority. `p1` is tonight, `p2` is this week, `p3` is someday.
- Anything that changes existing behaviour (as opposed to adding new) ships behind a toggle on the
  settings page (B-21), default on or off as the item says; the Neovim input engine is the model case.
- Every record an agent or a check produces carries its provenance: `turn_id`, `session` + `window`,
  `task_id`, `project_id`, and for git things the commit, branch and PR. Turns, commits, PRs, documents,
  context items, notes, action items, captures. No item is done while one of its rows lacks them (B-28).

```js
Item = { id: "B-01", status: "ready", priority: "p1", size: "M",   // S < half a day, M a day, L more
         owner: "", branch: "", verified: "",                          // filled by the claiming agent
         acceptance: ["checkable statement", ...], notes: ["2026-10-19 …"] }
```

## p1 · tonight

### B-28 Provenance on every record: turn, pane, task, project, commit, PR

status: ready · priority: p1 · size: M · owner: · branch: · verified:

Cross-cutting. Every row that comes out of a turn or a check links back to where it came from, so a
PR can be traced to the turn that wrote its commits, the task that turn was on, and the project.
The outline's code unit already links commits and head moves to turns and branches to tasks; this
item makes the same fields mandatory on everything else.

```js
Provenance = { turn_id?, session, window, task_id, project_id, commit?, branch?, pr_url?, at }
// on: Review/Turn, Commit, PR, Document (B-11), ContextItem, Note (B-05), ActionItem (B-15),
//     Capture, Download? (no: a download has no turn), Schedule run (B-20)
```

- the store gets one `provenance` shape embedded in each of those tables, filled at write time from the
  pane's assignment and the open turn; CLI and MCP writes (B-12) fill it from the env-bound identity
- detail views show a `FROM` block: turn, pane, task › project, commit, PR, each a jump
- `deck trace <id>` prints the chain for any row id: PR → commits → turn → task → project

Acceptance:

- a commit made inside an agent turn shows the turn id and task in `deck code list`; the PR opened from
  that branch shows the same task and project; `deck trace <pr>` prints the chain
- a document reported through `document_report` and a context item extracted from the same turn carry
  identical `turn_id`, `task_id`, `project_id`
- the e2e provenance case asserts the fields on each table after one scripted turn

notes:
- 2026-10-19 "for turns, commits, prs, etc. make sure we track the turn, the tasks, project".

### B-25 Command palette opens in search mode

status: ready · priority: p1 · size: S · owner: · branch: · verified:

Today `:` (`palette`, normal mode) opens the modal navigating and `/` (`search`, modal mode) sets
`searching`; in `modalKeyAction` a searching modal closes on `esc` and `enter` leaves search and picks.
The palette is the one modal nobody navigates before typing, so open it searching.

```js
// openPalette() today:        modalState{ id: "palette", searching: false }
// with the setting on:        modalState{ id: "palette", searching: true, filterCursor: 0 }
Setting = { section: "palette", key: "open_in_search", value: true }     // B-21, default true
```

Keys with the setting on:

- `:` opens the palette with the filter focused and empty; the first keystroke filters, no `/` needed
- `ctrl+n` / `ctrl+p` (`option-next`/`option-previous`, modal mode) move the highlight while typing
- `enter` runs the highlighted command (`pick`), as after `/` today
- `esc` once leaves search, keeping the filter and highlight so `j`/`k` and the other modal keys
  work; `esc` again closes. This changes today's "esc while searching closes" for the palette only;
  other modals keep their behaviour
- `/` in navigation re-enters search with the cursor at the end of the filter, as today
- with the setting off, `:` behaves exactly as before

Build order:

1. `openPalette()` reads the setting and sets `searching` on the new `modalState`
2. `modalKeyAction` treats `esc` as leave-search when `d.id == "palette"` and `d.searching`
3. `scripts/e2e_outline.py` `palette()` stops sending `/` when the setting is on; the `palette-filter`
   `search_edit` case types straight after `:`

Acceptance:

- the e2e palette check types a letter right after `:` and sees ` / <letter>▏` in the filter line
  with the option list already narrowed
- `:` `foo` `esc` leaves the filter `foo` showing and `j` moves the highlight; a second `esc` closes
- `deck settings set --json '{"section":"palette","key":"open_in_search","value":false}'` then `:`
  opens with no filter line and `/` is needed, matching the current screenshots

notes:
- 2026-10-19 stub; expanded by a background agent the same day.

### B-21 Settings: a page plus per-service config areas, reachable by one key or one command

status: claimed · priority: p1 · size: M · owner: vps2 lane 2 · branch: · verified:

B-16 to B-20 need identity and preferences the user types once. They are rows in a `settings` table
keyed by section + key, read through the store like reminders (§6.9); config.toml (§6.10) only
supplies defaults and is never written by the app. Secrets (Slack, GitHub, Linear tokens) are never
stored: `gh` and the MCP servers carry their own credentials, and anything else comes from the
environment or the harness configs B-12 writes.

```js
Setting = { section: "identity"|"slack"|"github"|"linear"|"schedules"|"notify", key, value, updated }
// identity:  github_user ("instajosh"), slack_user, slack_user_id, name
// slack:     oncall_weeks (list of Monday dates), oncall_channels, oncall_group, watch_dms,
//            watch_mentions                                                        (B-16)
// github:    review_query, oncall_review_query, watch_interval_seconds (300),
//            my_prs_poll_seconds (300)                                             (B-17, B-18)
// linear:    enabled                                                               (B-19)
// schedules: default_timeout_seconds                                               (B-20)
// notify:    os_enabled (false), indicator_char                                    (B-15, B-18)
```

- settings page on `E` (normal mode; `S` is scope-toggle, `M`/`W` are B-11's, `U` is B-09's, `J`/`K`
  are B-06's), listing every section with its keys and current values; `enter` on a row edits it
- `settings…` in the palette on every page lands on the settings page; `slack settings…`,
  `github settings…`, `linear settings…`, `schedules settings…` open that section
- on each service page `,` (free in every mode as of 2026-10-19) opens the page's own section as
  a form prefilled with the current values; forms use the shared form engine (`internal/ui/forms`), one field per
  key, list keys as multi-line fields, saving writes only the changed rows
- a required setting that is empty (github_user for B-17/B-18, slack_user_id and oncall_weeks for
  B-16) renders as a `needs: github username` line at the top of the service page, and the same
  row is highlighted on the settings page; the lookup that depends on it is skipped, not errored
- CLI: `deck settings list [--section identity]`; `deck settings set --json
  '{"section":"identity","key":"github_user","value":"instajosh"}'`; `deck settings init` writes
  every default from config.toml without overwriting a row that exists

Acceptance:

- `deck settings set` of identity.github_user makes the github page's `needs:` line disappear on
  the next refresh, and `deck github check` (B-17) runs instead of skipping
- `,` on the slack page opens a form prefilled with the stored oncall_weeks and channels; saving
  one field and reopening shows the new value and `updated` moved
- `settings…` from the panes page lands on the settings page with every section listed
- `deck settings list --section identity` prints only the identity rows as `section key value
  updated`, and `deck settings init` run twice leaves `updated` unchanged

notes:
- 2026-10-19 stub; expanded by a background agent the same day.

### B-12 Deck as an MCP server, configured into every agent deck starts

status: ready · priority: p1 · size: L · owner: · branch: · verified:

`deck mcp serve` speaks MCP over stdio from the same binary (Claude Code, Codex, OMP, opencode all
take a stdio command); an HTTP transport comes second only if a harness refuses stdio. One tool
registry, two transports, same handlers as the command bus (§3), so every tool is also a CLI command
and is recorded in history under the calling pane's task.

Agents started by deck (`prompts.start-agent`, `n a`) get the server configured for that harness
before the first prompt, scoped to the pane: the tool calls carry session + window, so deck knows who
is talking. See `~/bin/h-mcp` AGENT_TARGETS for every harness's config path and entry shape.

First tools, all thin wrappers over existing or planned commands:

```js
document_report   = { path, title?, kind?: "report"|"plan"|"review", summary? }   // → documents (B-11), owner = pane's task
task_list         = { scope?: "pin"|"all", status? }                               // → work.tasks
task_done         = { task_id, note? }                                             // → work.patch-task
task_note_add     = { owner: {kind, id}, text }                                    // → notes (B-05)
todo_list         = { priority?, status? }                                         // → B-13
todo_note_add     = { todo_id, text }                                              // research results land on the item
todo_claim        = { todo_id }                                                    // → B-13
action_item_create= ActionItem                                                     // → B-15
context_add       = { kind, text, task_id? }                                       // → context.extract
whoami            = {}                                                             // session, window, task, project, origin
task_status       = { task_id, expected_version, status, summary?, verification?, commit?, blocker? }
report_progress   = { message }                                                    // status line on the pane row
```

Learned from vaim (`~/work/ch/vaim/apps/server/src`):

- vaim mounts in-process SDK servers (`createSdkMcpServer` from @anthropic-ai/claude-agent-sdk) on
  `query({ mcpServers: { t3_app, t3_todo, t3_action_items, t3_context } })` per thread and mirrors
  the same specs as Codex `dynamicTools`; for non-SDK runtimes it injects `T3_PIPELINE_BASE_URL`,
  `T3_PIPELINE_THREAD_ID`, `T3_PIPELINE_TOKEN` into the agent env and `t3 pipeline-agent mcp` is a
  stdio JSON-RPC bridge that POSTs to loopback HTTP with the bearer token. Deck should do the env +
  stdio bridge variant: `DECK_SESSION`, `DECK_WINDOW`, `DECK_TASK_ID`, `DECK_TOKEN` in the pane env,
  `deck mcp serve` reads them, so an agent can never address another pane's task through arguments.
- identity is bound server-side at construction, never passed as a tool argument.
- task lifecycle worth copying: `set_status { item_id, expected_version, status, completion_summary?,
  verification?, commit?, blocker_reason? }` with an optimistic version check and evidence fields
  required on done, plus `reopen_item`; the minimal agent-facing trio is `report_progress { message }`,
  `complete_phase { summary?, resultJson? }`, `fail_phase { reason }`.
- documents: `create_document { title, markdown }` returns a stable id and route and auto-links the
  doc to the originating thread; `update_document { id, title, markdown }`; `list_documents`,
  `get_document`.
- notes: `create_action_item_note { action_item_id, text, important? }` and
  `create_action_item_context { label, content, important? }`, a one-shot "add a note to the thing I
  am on" with an important flag.
- `get_current_thread_action_item_origin {}` ("what spawned me") is the first tool an agent calls;
  deck's equivalent is `whoami {}` returning session, window, task, project, and the todo or action
  item that spawned the pane.
- skip from vaim: loops, tags, Slack/calendar/PR polling and typecheck-watcher tools; those belong to
  B-16 to B-20 as scheduled lookups, not agent tools.

Acceptance:

- `deck mcp serve` answers `initialize`, `tools/list` and `tools/call` over stdio; `deck mcp tools`
  prints the same list; a tool call from a deck-started Claude Code pane shows in `deck history list`
  with the pane's task
- an agent calling `document_report` on an md it wrote makes the file appear on the documents page
  within one refresh, unread-styled
- `task_done` from an agent flips the row and the TUI reflects it without a manual refresh
- outline gains §7.4 mcp as a shell over the bus, like the CLI

notes:
- 2026-10-19 requested with the action-item and slack work; a subagent is checking what
  `~/work/ch/vaim` exposes as tools so the first list can borrow from it.
- 2026-10-19 vaim survey folded in: env-bound identity, stdio bridge, versioned status with evidence, document auto-link.

### B-13 Todo unit and page: items that are not yet tasks

status: ready · priority: p1 · size: M · owner: · branch: · verified:

A todo is lighter than a task: no project required, no panes, a priority and free text, promotable
to a task. Agents browse todos for easy ones, do research and leave notes on them (through B-12), or
resolve them outright.

```js
Todo = { id, title, text, priority: "p1"|"p2"|"p3", status: "idea"|"ready"|"claimed"|"review"|"done",
         owner?: string, project_id?, task_id?, promoted_task_id?, created, updated }
```

- page under its own key (see the free letters in B-11), rows by priority then age; `enter` promotes to
  a task under the pin, keeping the notes; detail shows the notes (B-05) newest last
- commands `todos.add|patch|promote|claim|delete`, CLI `deck todo …`
- task status rule: a new task is `todo` unless the form assigns it to a pane or an agent at creation,
  then it is `active`
- this file (`znbu/docs/todo.md`) stays the human-facing list until the unit exists; a one-off
  import of it is part of this item

Acceptance:

- `deck todo add --json '{"title":"…","priority":"p2"}'` then `deck todo list` shows it; `promote`
  creates a task with the same title and moves the notes
- a task created from the form without a pane has status `todo`; one created by `n a` is `active`
- the import reproduces every B-nn item in this file with its status and notes

notes:
- 2026-10-19 asked for so agents can pick off easy items and pre-research the rest.

### B-14 MCP harvest and replay built into deck: read harness logs, catalog servers and tools, call them without an agent

status: ready · priority: p2 · size: L · owner: · branch: · verified:

`~/bin/h-mcp` already does this in Ruby (`harvest`, `harvested`, `template`, `calls`, `run`;
readers per harness in `~/bin/lib/h_mcp_harvest.rb`) but has never been used. Build the same into
deck so slack, glean, linear and github MCP servers the user is already authenticated with can be
called deterministically, without spending agent tokens.

- readers for Claude Code, Codex and OMP session logs (jsonl), run on a schedule and on demand
  (`deck mcp harvest`); each reader extracts: servers configured, their tools and input schemas,
  every tool call with its arguments, and the response for each call
- catalog tables: `mcp_servers`, `mcp_tools`, `mcp_calls` (args + response + harness + pane + at);
  `deck mcp servers|tools|calls|template SERVER TOOL`
- replay: `deck mcp call SERVER TOOL --json '{…}'` using the server's own transport and the auth the
  harness config holds; `--select path` into the response
- decision to make in the outline: tools become first-class handlers (generated request/response
  types per tool) or stay meta-info that commands and schedules can trigger. Start with meta-info;
  promote a tool to a handler only when a page depends on its shape (slack search, PR list)

What the logs on the Mac hold (surveyed 2026-10-19):

- `~/bin/lib/h_mcp_harvest.rb` has readers for codex, claude, opencode and omp; store is sqlite
  `~/.config/hiiro/hiiro.db` with tables `mcp_calls`, `mcp_harvest_files` (incremental by
  path+size+mtime), `mcp_tool_definitions`; templates aggregate observed argument shape, example
  args, declared input schema and a response parser per server/tool. Port these tables and the
  incremental file index, not the Ruby.
- Codex: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` and `~/.codex/archived_sessions/`; a call
  and its result are one record: `type=event_msg`, `payload.type=item_completed`,
  `payload.item.type=McpToolCall` with `server`, `tool`, `arguments`, `result{content[],isError}`,
  `status`, `duration`.
- Claude Code: `~/.claude/projects/**/*.jsonl`; call is an `assistant` record with
  `message.content[].type=tool_use` and `name=mcp__<server>__<tool>`; result is a `user` record
  with `tool_result` joined by `tool_use_id`, body in record-level `toolUseResult` else the block
  `content`; tool definitions come from `attachment` records (`deferred_tools_record.entries[]`,
  `prompt_snapshot.tools[]`) with `input_schema`.
- OMP: `~/.omp/agent/sessions/<cwd-slug>/<ts>_<id>.jsonl`; there are no direct `mcp__` toolCall
  records. MCP traffic is nested inside the `eval` REPL tool: result records
  `role=toolResult, toolName=eval` carry `details.jsonOutputs[].details{serverName, mcpToolName, ...}`.
  The omp reader must unwrap eval results; h-mcp's does not, so it has never harvested an OMP call.
- Counts on this Mac: claude 400 files / 672 MB, only 8 real MCP tool_use blocks (claude-in-chrome);
  codex 134 files, 371 calls (cua_repl 361, codex_app, codex_apps); omp 892 files / 933 MB, nested
  calls only (tuios_* and js). opencode: 1 db.
- No slack, glean, linear or github MCP call exists in any log on this Mac; glean appears only in
  permission-list text. Replay of those servers cannot be verified from logs.

Acceptance:

- on this Mac, `deck mcp harvest` finds the servers and tools present in existing Claude, Codex and
  OMP logs and lists call counts per tool; a subagent is confirming tonight what those logs contain
- `deck mcp template slack search` prints a filled-in example from a harvested call;
  `deck mcp call` on a server with a live session returns the parsed response

notes:
- 2026-10-19 the user has no MCP servers to test against right now; harvest from logs must work
  offline, replay is verified when a server is available.

### B-15 ActionItem unit, page and the one-character global indicator

status: ready · priority: p1 · size: M · owner: · branch: · verified:

Everything that needs the user's attention, from any source, in one place.

```js
ActionItem = { id, service: "slack"|"github"|"linear"|"agent"|"schedule", source_url, title, text,
               action_type: "pr-review"|"pr-status"|"oncall"|"mention"|"dm"|"thread"|"ticket"|"report"|other,
               category?: string, task_id?, project_id?, created, seen_at?, dismissed_at?,
               promoted_todo_id?, promoted_task_id?, extra: {} }
```

- commands `actions.create|seen|dismiss|promote` (to a todo or a task), CLI `deck action …`, MCP tool
  `action_item_create` (B-12); dedupe on service + source_url so repeated checks do not pile up
- page: unseen first, then undismissed, grouped by service; `enter` opens the url; `d` dismiss;
  `t` promote to todo; `T` to task
- the indicator: while any item is unseen, or seen but neither dismissed nor promoted, one bright
  character sits in the title line on every page (position fixed, next to the pin), with the count
  beside it when there is room. It is never cleared by looking at the page alone; items clear it
- OS notification on a new item is optional and off by default

Acceptance:

- `deck action create` twice with the same url makes one row; the title line shows the mark on every
  page; dismissing the last item removes it within one refresh
- the e2e case covers create, indicator, dismiss, promote to todo

notes:
- 2026-10-19 defined as the target for the slack, github, linear and scheduled checks below.

### B-16 Slack monitoring: mentions, DMs, threads, oncall channels, assessed into action items

status: ready · priority: p1 · size: L · owner: · branch: · verified:

Wanted by the morning. Two paths, both producing ActionItems (B-15); build the one that works
tonight and keep the other as the fallback:

1. MCP path: a scheduled lookup (B-20) calls the slack MCP through B-14's replay, searching for the
   username, DMs and threads the user is in; new messages since the last check are captured, then
   sent to an agent with a fixed prompt that answers only with action items (through
   `action_item_create`) or nothing
2. agent path: the scheduled prompt itself goes to an agent pane with the slack MCP attached; the
   agent searches, assesses and creates the action items

- there is no log fallback tonight: the 2026-10-19 survey found zero slack, glean, linear or github
  MCP calls in Claude, Codex or OMP logs on the Mac, so B-14 replay has nothing to learn from yet.
  Tonight's deliverable is path 2 (a scheduled prompt to an agent pane that has the slack MCP
  attached) plus the fixture-driven assessment; path 1 follows once one real call has been captured.
- slack page in deck with a settings section: oncall week (starts Monday, one or more weeks),
  channels to watch during oncall, the oncall user group or tag; during oncall, every message in
  those channels and every mention of the tag is captured and flagged; outside oncall, only
  mentions, DMs and threads the user is in
- captured messages are stored as context items of kind `slack` with the permalink, so the action
  item links straight to the thread

Acceptance:

- the agent-path prompt, run by hand against a pane with the slack MCP, produces at least one action
  item with a permalink; the captured call then seeds B-14
- with a fixture of captured messages (no live slack), the assessment prompt yields action items with
  the permalink as `source_url` and the indicator lights
- the settings persist in the store, `deck slack settings` prints them, and the oncall window
  changes which channels the next check queries
- a live run against the real slack MCP is verified the first morning it is available

notes:
- 2026-10-19 "i need this by the morning"; no MCP server is available to test tonight, so the fixture
  path and the agent-prompt path are what can be proven.

### B-17 PR review requests from GitHub, periodic through `gh`

status: ready · priority: p1 · size: S · owner: · branch: · verified:

- a schedule (B-20) runs one `gh` search for PRs with `@instajosh` as a requested reviewer
  (`review-requested:instajosh`, not team requests) and creates an ActionItem per new PR with
  `action_type: "pr-review"`; the dedupe key is the PR url
- during the oncall week (settings from B-16) the query widens: team review requests and PRs
  touching the oncall channels' repos; the exact oncall criteria are a setting, not code
- a follow-up schedule can ask an agent to review the PR and write an md report (B-11 documents),
  linked from the action item

Acceptance:

- `deck github check` creates action items for the PRs `gh search prs --review-requested=instajosh
  --state=open` returns, once each, and the indicator lights
- switching oncall on changes the query that runs next and the e2e case asserts both queries

notes:
- 2026-10-19.

### B-18 My PRs: open and drafts, watching, snooze until midnight, CI and status change alerts

status: ready · priority: p1 · size: M · owner: · branch: · verified:

```js
MyPR = { url, number, repo, title, draft, state, ci: "pending"|"pass"|"fail"|"unknown",
         checks: [{name, state, url}], reviews: [{who, state}], comments: int, last_change,
         watching: bool, snoozed_until?: midnight-local }
```

- a page or a section of the github page listing every open PR and draft authored by the user; `w`
  toggles watching, `z` snoozes until local midnight, after which the row returns
- watched PRs are polled every 5 minutes with one GraphQL request for all of them (`gh api graphql`
  with a nodes query on their ids), never one call per PR; the poll interval is a setting
- any change creates an ActionItem with `action_type: "pr-status"`: CI pending→pass, pass→fail, a
  new comment, a new review or approval, merged, closed, conflicts; the item names what changed
- the indicator (B-15) and, for watched PRs only, an OS notification

Acceptance:

- the list matches `gh pr list --author @me --state open` plus drafts; `w` and `z` persist across
  restarts; a snoozed row reappears after midnight in a clock-advanced test
- one poll of three watched PRs issues one `gh api graphql` call (asserted by counting invocations
  of a stub `gh` on PATH); a CI state change in the stub's next answer creates exactly one action item

notes:
- 2026-10-19; the single-call poll is to protect the API quota.

### B-19 Linear as a source of action items

status: idea · priority: p2 · size: S · owner: · branch: · verified:

Through the linear MCP (B-14 replay or an agent prompt): tickets assigned to the user, mentions,
state changes on watched tickets, into ActionItems with `service: "linear"`. Linear aggregates a lot
of this already but misses things, so it complements B-16 and B-17 rather than replacing them.

notes:
- 2026-10-19.

### B-20 Schedules: recurring prompts and lookups on an interval, results back through the MCP server

status: ready · priority: p1 · size: M · owner: · branch: · verified:

The reminders unit (§6.9) already runs a scheduler with intervals. Extend it so a schedule can be:

```js
Schedule = { id, title, interval: seconds, enabled, next, last,
             run: { kind: "prompt", target: StartSpec|window, text }          // send to an agent pane
                | { kind: "lookup", command: "github.check"|"slack.check"|"mcp.call", args: {} }
                | { kind: "command", name, args: {} },
             on_result?: { kind: "prompt", text }                               // what to do when a lookup finds something
           }
```

- a lookup that finds new rows creates ActionItems itself (B-15); a prompt run is sent to an agent
  with B-12 configured, so the agent reports back with `action_item_create` or `document_report`
  rather than text the deck has to parse
- `on_result` chains work: a found PR review request starts an agent that reviews the PR and writes an
  md report, linked from the action item
- every run is recorded in history with its duration and outcome; failures are visible on the
  reminders/schedules page and never repeat-notify the same occurrence (same rule as reminders)
- intervals are finite and bounded; a run has a timeout and the scheduler kills it

Acceptance:

- `deck schedule add --json '{"interval":300,"run":{"kind":"lookup","command":"github.check"}}'`
  runs within the interval, shows in `deck history list` with its outcome, and its action items carry
  the schedule id
- a prompt schedule starts the agent once per interval and never while the previous run's pane is
  still working

notes:
- 2026-10-19 the glue between B-16, B-17, B-18 and the agent side.

### B-08 Rail height budget: sections capped by percent, one-line rows, panes get most of it

status: ready · priority: p1 · size: M · owner: · branch: · verified:

Learned from tuios's own rail: `appearance.sidebar.sections` (default
`sessions:25,terminals,files:25,agents:34`) gives every section a percent share of the height, a
section scrolls inside its share, `appearance.sidebar.agent_rest_fold` (default `1h`) folds a resting
agent row to one line after a duration, and `appearance.sidebar.subagent_max_rows` caps the rows one
group may take. Deck's rail today lets the
review queue grow without limit and spends two lines on every row, so half the value takes all the
space.

- each rail section gets a percent cap of the rail height from config, with a default that hands the
  majority to the panes section (for example `review:25,panes:60,working:15`); a section scrolls
  within its share and shows `+N more` or a scroll mark, never pushes the next section down
- rows are one line unless the second line carries something the first does not; the rule for when a
  row earns a second line is written in the outline (for example: selected row, agent with a message,
  row that is stale) and applies to every page
- the panes section keeps the grouping headings from §7.1; headings count against the section's share

Acceptance:

- with 40 finished turns and 3 panes on a 40-row terminal, the review section takes at most its share
  and the panes are all visible; `j` inside the review section scrolls it
- a resting pane row is one line; a selected or messaging row is two; `deck config init` writes the
  default shares and the e2e layout case asserts both

notes:
- 2026-10-19 from the comparison with tuios's sidebar.

### B-09 Pane lifecycle in the rail: working at the bottom and locked, review at the top, rest in the middle

status: ready · priority: p1 · size: L · owner: · branch: · verified:

The rail becomes three sections that a pane moves through. Replaces the two-section rule in §7.1.

```js
RailSection = "review" | "panes" | "working"
Lifecycle   = submit prompt → "working" (bottom, locked, oldest first, newest at the very bottom)
            → turn ends → "review" (top; jumps to the bottom of that section; pronounced style:
              background colour and a glyph)
            → every accordion opened (= reviewed) → "panes" (middle), but only once the rail focus
              moves to a different pane
```

- working section: a pane goes there the moment its state turns working or any active state after a
  prompt (agents for sure; terminals after a command are undecided, see below). Rows are locked:
  moving the cursor over a locked row shows no preview, the detail says `press u to unlock`; `u`
  unlocks that row until focus leaves it, then it locks again on its own
- review section: one row per pane that produced review records, never one per turn. Focusing the row
  shows the review accordion (B-10) as the default detail, not the Screen tab; the pane's screen is
  still reachable through the tab bar (B-06)
- panes section: everything else, grouped as `o`/`O` say
- a pane with nothing left to review returns to the middle only after the user moves rail focus off
  it, so the row does not jump from under the cursor

Acceptance:

- submitting a prompt through `p` moves the row to the bottom section within one refresh, locked, and
  `j` onto it shows the unlock hint and no screen; `u` shows the screen; `k` away then `j` back shows
  the hint again
- `turn_end` moves the row to the top section with the review style; opening every accordion then
  moving to another row returns it to the middle; it does not move while focused
- order in the working section is submission time, oldest first; in the review section, finishing
  time, oldest first
- §7.1 rewritten for three sections; `history_review` and `shared_navigation` cases updated

Open before claiming: do terminals enter the working section after a command, or agents only.

Checked 2026-10-19 with `deck list-actions`: `u` is taken (half-page-up in normal, form, help and
modal modes). `U` is unbound everywhere, so the unlock key is `U` unless the outline picks another;
other free letters in normal mode are `b c f i t v x z` and `B E F I J K L M N Q V W X Y Z`.

notes:
- 2026-10-19 the human called this the important one.

### B-10 Review accordion: the detail for a pane with unreviewed turns

status: ready · priority: p1 · size: L · owner: · branch: · verified:

Modelled on tuios-deck's Turns tab (`~/proj/tuios-deck` README "The Turns tab", `internal/ui/turns.go`):
an accordion, one row per thing to review, oldest at the top, everything collapsed on open.

```js
Accordion     = { pane, rows: [TurnRow], context: [ContextItem], auto_reviewable_count }
TurnRow       = { turn_id, prompts: [Prompt], response, started_at, completed_at,
                  reviewed_at?, auto_reviewable: bool, starred: bool, project_id, task_id }
// several review records on one turn_id (steering prompts, one response) collapse into one TurnRow
```

- opening a row marks it reviewed; a row stays open until the accordion closes. All opened → the pane
  is reviewed and B-09 lets it leave the review section
- auto-reviewable: a turn that has later prompts after it was most likely read outside deck. Those
  rows get a different background, a line above the list names the key that marks all of them
  reviewed at once; the most recent turn is never auto-marked
- several review records with the same turn id are one row with all its prompts listed and the one
  response
- `*` (or the key the outline picks) stars a row for finding later; starred rows are listed first on
  the reviews page
- how tuios-deck keeps it stable (`internal/ui/turns.go`): rows have a stable id per source, expanded
  state is a map keyed by that id so a re-read never closes a row, a re-read is skipped when a
  fingerprint (count, last id, last body length) is unchanged, selection is re-found by id unless
  follow mode is on, `g` turns follow off and `G` on, `enter`/`space` toggle, `y` copies through
  OSC 52, `{`/`}` jump by group
- every row carries the project and task of the pane that produced it
- under the turn rows, the context items extracted from those responses, sorted and uniq'd, most
  recent first, auto-associated with the pane's project and task; starrable in place. A starred
  context item shows in the detail of the task it is directly on and of that task's direct parents
  (the parent task chain and the project), not of siblings or cousins

Acceptance:

- a pane with three finished turns opens an accordion with three collapsed rows, oldest first;
  `enter` on one marks only it reviewed (`deck review list` shows `reviewed_at`)
- two review records with one turn id render as one row; opening it marks both
- turns 1 and 2 of 3 are flagged auto-reviewable, the mass key marks exactly those two
- a context item extracted from turn 3 appears under the rows, starring it makes it appear in the
  detail of the pane's task and project, and in no sibling task
- the review page lists starred rows first

notes:
- 2026-10-19 defined together with B-09; B-09 owns the rail movement, this owns the detail.

### B-11 Documents page: starred docs, glow preview, live mode, unread theme

status: ready · priority: p2 · size: M · owner: · branch: · verified:

Reviewable documents already exist as review entries (§6.6: an md or html the agent wrote). Give them
a page and a star.

```js
Document = { id, path, kind: "md"|"html", written_by: { session, window, turn_id }, project_id,
             task_id, starred, read_at?, created }
```

- a documents page listing every agent-written document under the pin, starred first. Key to be
  chosen from the unbound uppercase letters (`B E F I J K L M N Q V W X Y Z` as of 2026-10-19;
  `U` is reserved by B-09); `M` for markdown or `W` for writings are the obvious candidates
- a starred document is also a context item on its direct parents, so it shows in the task's and
  project's detail (same parent rule as B-10) and in the context page
- highlighting an md row previews it in the detail through glow; html rows show the source or a text
  rendering. Installed glow is 3.0.0: `-t` TUI, `-l` line numbers (TUI only), `-p` pager, `-w` width,
  `-n` preserve new lines; there is no local-only flag. `glow -tln` is valid and means TUI with line
  numbers and preserved newlines. The read-only preview should render with `glow -w <detail width>`
  and the live mode should run `glow -tl <path>`
- `enter` goes live on the preview the same way as a pane: keys go to glow, `ctrl+a d` comes back
- until a document has been opened live once, its row uses an "unread" theme that stands out;
  opening live sets `read_at` and the row goes quiet

Acceptance:

- the page lists the two documents the `history_review` case writes, unread-styled; `enter` then
  `ctrl+a d` round-trips and the row is no longer unread
- starring one shows it in the owning task's detail and the project's detail, and on the context page
- `deck document list --task ID` returns the rows with `starred` and `read_at`

notes:
- 2026-10-19 asked for with the review lifecycle; glow must be present on the host for the preview.

### B-06 Pane detail: tab bar with a live Screen tab first, learned from tuios-deck

status: claimed · priority: p1 · size: L · owner: vps2 lane 1 · branch: · verified:

Today a pane row's detail opens on the transcript (`TRANSCRIPT · ] Turns`), so moving `j`/`k` down
the rail shows text that looks the same for every agent. Telling panes apart means `enter` into live
mode and `ctrl+a d` back out, for every pane. tuios-deck solved this: the main area is a tab bar and
the first tab is the pane's screen.

What to take from `~/proj/tuios-deck` (README "The deck page", "Live: typing into a pane";
`internal/ui/model.go` tabs, `view.go` detailLines, `live.go`):

- tabs `1 Screen · 2 Activity · 3 Transcript · 4 Turns`, drawn as a bar at the top of the detail with
  the pane's `session › name`, its assignment glyph and path, stale age and last message beside it.
  `1`–`4`, `[` `]`, `tab` / `shift+tab` switch from the rail or the detail; the bar brightens and
  underlines the shown tab when the detail has focus
- Screen is the default and is read-only: the pane's rendered screen from `capture-pane`, redrawn when
  the stream says the pane printed, with a one-second safety re-read; keeps the scroll unless
  following the bottom; `G` follows newest output again; `j`/`k` scroll a line with the detail
  focused, `J`/`K` half a page
- `enter` on a pane goes live, which is the same Screen tab with the keyboard routed to the pane:
  the only visual change is the live bar and the cursor. `ctrl+a d` drops the keyboard and the Screen
  stays. `ctrl+a j`/`k` go live on the next or previous rail pane without leaving
- the rail never changes shape between browsing and live; the detail is never full-screen except
  `ctrl+a z`
- the detail re-reads once a second and the list refreshes on daemon events; selection, tab and
  scroll survive both

Keep from the current deck: the review-queue rows in the rail, the transcript and turns content, the
leader semantics in §7.1, and the stream lease rules already in the outline.

```js
PaneDetail = { tab: "screen"|"activity"|"transcript"|"turns", follow: bool, scroll: int,
               live: { keyboard: bool, view: "normal"|"zoomed"|"fullscreen" } }
```

Acceptance:

- selecting any pane row shows its actual screen within one second, without going live; two agents
  with the same name are distinguishable from the rail alone
- `1`–`4`, `[` `]` switch tabs from both the rail and the detail; the chosen tab persists per pane
  across refreshes and across re-selection
- `enter` then `ctrl+a d` leaves the detail on the Screen tab with the same scroll; the rail did not
  move or resize at any point
- outline §7.1 updated with the tab bar; the `shared_navigation` and live e2e cases assert the Screen
  tab and the detach round trip

notes:
- 2026-10-19 asked for after comparing with tuios-deck; this is the one the human called out as most
  important.

### B-07 Mass-add outline: prefill the existing tree and reuse names, learned from tuios-deck

status: ready · priority: p2 · size: M · owner: · branch: · verified:

The current mass-add (`alt+m` / `+ add new…`, outline §6.3 and §7.1) is a parked form where
`tab` / `shift+tab` nest new lines. tuios-deck's "Adding many at once" (README) is still a
plain outline but gets more right. Adopt:

- opens prefilled with every existing project (by name) and its tasks and subtasks nested beneath,
  drawn dim with their mark and status (`deck  ✓ done`), cursor on an empty line after them. The
  user sees where a new line lands and never retypes a parent
- existing names are reused, never duplicated: a line equal to an existing title under the same parent
  is the existing item, so new lines under it become its children. A top-level line may also name a
  task by path, `deck / command palette`, to add under it
- blank lines and `#` comments are skipped; the hint shows an example outline when the store is empty
- `ctrl+s` validates the whole outline first and refuses with the line number: indent under nothing,
  indent that jumps more than one level, odd spaces. Nothing is created on refusal; on success the
  status says `added N projects, M tasks` and the tasks page keeps its selection
- mass-add only adds: deleting a prefilled line deletes nothing, editing one renames nothing (the
  edited text is a new item). The hint says so
- line editing: `enter` splits and keeps the indent, `backspace` at line start joins, `ctrl+u` clears
  the line, `tab`/`shift+tab` indent and outdent without leaving the field, 14 lines visible with the
  cursor kept in view

Keep deck's rule that every root task needs a project (a bare top-level task line is a project, as in
tuios-deck, or is rejected; decide in the outline) and the one-parked-modal rule.

Acceptance:

- opening mass-add on a store with two projects and nested tasks shows them dim in the outline, and
  typing one indented line under an existing task creates exactly one task under it
- an invalid indent is refused with its line number and no row is written
- `deck task list` after a save shows the new rows in outline order with the right parents
- the `mass_add` outline case covers prefill, reuse, path lines, refusal and the status message

notes:
- 2026-10-19 "not great, but better than ours".

### B-03 Gather TUI design samples for every deck screen and widget

status: review · priority: p1 · size: S · owner: Claude Fable subagent (session_01Cg7zBUciGaMHsqweicyuGP) · branch: main (redeck-astra) · verified: file reviewed by the parent session; 55 samples, 73 unique links

Research only, no code. For each screen type and widget deck uses (dashboard rail + detail, two-line
rows and group headings, detail key/value blocks, fuzzy filter and palette, forms and pickers, prompt
composer, tree editor, help overlay, catalog browser, live mode, the history/reviews/captures/context/
tasks pages, status line and notices), collect 2 to 4 samples from popular TUI tools and the web with
links and a note on what deck could borrow. Output is `redeck-astra/docs/research/tui-design-samples.md`. It feeds a
later restyle item.

Acceptance:

- the file exists with a section per area, every link was actually fetched or returned by a search
- a closing "Patterns worth adopting" list and a "Not found" list

notes:
- 2026-10-19 started in the background by a subagent while the rest of the backlog is written.
- 2026-10-19 done, committed in redeck-astra. Not found: a public assign-flow sample with snapshot + approval, a composer showing the target pane's scrollback, stable images for Telescope/Textual/lazygit dialogs, an authoritative TUI design article. Waiting on the human to read it and move it to done.

### B-01 Orchestrator agent that catches agents spinning their wheels

status: ready · priority: p1 · size: M · owner: · branch: · verified:

An always-on agent in its own tuios pane on vps2. It watches every worker agent in its fleet, decides
whether each one is still making progress, and talks to the ones that are not. It never edits code.

What "spinning wheels" means, any one of these:

- same reported state for longer than 20 minutes while `working`, with no new commit on its branch
- the same file edited or the same command run three times with the same failure in the tail of the pane
- a `needs_input` prompt that has waited more than 10 minutes
- more than 90 minutes on one backlog item of size S, or three hours on M

What it does about it, in order:

1. reads the pane tail and the item's notes before saying anything
2. mails the worker one question through tuios mail: what it is trying, what blocked it, what it will try
   next. One message, then wait for the reply, no reply chains.
3. if the answer is a plan, let it run and check again at the next deadline; if the answer is the same
   plan as before, tell it to stop, commit what it has to its branch, write a dated note under the item,
   and release the item back to `ready`
4. answers `needs_input` prompts itself only when the question is one the backlog item already answers;
   otherwise leaves it and includes it in the morning report
5. writes a morning report to `znbu/docs/reports/<date>.md`: per item, status, branch, what shipped, what is
   stuck and why, and what needs the human

Acceptance:

- a worker agent stuck in a loop on a throwaway task gets one mail within 25 minutes and is released
  within 60, with the item back at `ready` and a note explaining why
- a worker that is slow but progressing is not interrupted
- the orchestrator never sends keys into a pane that is `needs_input` without reading the prompt first
- the morning report exists and names every item touched overnight
- it runs on vps2 with finite timeouts on every call and survives its own tuios daemon restart

Start from `tuios --skill fleet` and `tuios --skill recipes` (the conductor recipe), `tuios list-agents
--json`, `tuios subscribe` for state changes, and `tuios read-agent-messages` / `send-agent-message`.
Checkpoints (`tuios --skill checkpoints`) give it a per-turn diff to judge progress without reading the
whole pane.

notes:
- 2026-10-19 asked for so a batch of features can run on vps2 overnight without the human watching.

## p2 · this week

### B-29 UI/UX pass on every page with Fable 5.1 and the frontend-design skill

status: ready · priority: p2 · size: M · owner: · branch: · verified:

Run Claude Fable 5.1 with the `frontend-design` skill over each deck page and modal: dashboard rail +
detail, the tabs from B-06, the help modal, forms, the palette, the tree editor, the accordion from
B-10, documents, downloads, action items, settings. The brief is
`redeck-astra/docs/research/tui-design-samples.md` (B-03) and its "Patterns worth adopting" list.

```js
DesignNote = { page: "help-modal", path: "znbu/docs/design/help-modal.md",
               before: "ascii mockup", after: "ascii mockup",
               tokens: { colour_roles, borders, row_density, selected_row } }
```

- output is one design note per page under `znbu/docs/design/<page>.md` with before/after ASCII
  mockups and the exact style tokens: colour roles, borders, row density, selected-row style
- then the code changes, behind the settings toggle rule where they change existing looks (B-21)

Acceptance:

- every page has a design note under `znbu/docs/design/`
- the help modal fix from B-04 is included
- screenshots of before and after at 120 and 200 columns are attached under `docs/attachments`

notes:
- 2026-10-19 asked for after the design-sample research.

### B-22 Feature inventory with review marks, growing into an in-app registry

status: ready · priority: p2 · size: L · owner: · branch: · verified:

Port `~/proj/tuios-deck/docs/plans/2026-10-18-feature-inventory.md`: nobody can say which features
were reviewed or are worth keeping. Deck is ahead here: the registry (outline §5) already holds pages,
actions, palette commands, modals, groupings and forms as data (`deck docs`, `deck list-actions`, `deck
commands`), so stage 1 for those kinds is a registry dump; only two kinds need the go/ast program.

```js
Feature = { id: "grouping.cwd",            // <kind>.<name>, lower case, never renamed once written
            kind: "page"|"action"|"palette"|"modal"|"grouping"|"form"|"command"|"struct"|"concept",
            name, desc, surfaces: ["tui:o/O"], file, line, hash,     // hash: of the defining text
            fields?: [{ name, type, doc }] }                           // structs only
Mark    = { id, status: "keep"|"cut", on, note? }   // no mark = unreviewed; stale hash = "changed"
```

- free from the registry: page, action (one per mode), palette, modal, grouping, form; `command`
  from `bus.List()`; `file`/`line` via `runtime.Caller` at register time
- go/ast + go/doc (`scripts/inventory/`): `struct` for every exported struct under `internal/` with
  field docs; `concept` from `// feature: concept.<area>.<name>` comments on code that is not one symbol

Build order:

1. `scripts/inventory/`: registry dump plus the two ast extractors → `docs/inventory.json`, sorted by
   id, stable across two runs; a pre-commit hook regenerates it so its diff is the feature changelog
2. `docs/review.yaml` holds marks; `go run ./scripts/inventory -review` prints unreviewed, then changed
3. stage 2: `Status(id)` (§5) reads marks from a `features` store table; `o`/`O` skip cut groupings,
   palette and help skip cut commands, `config init` writes every action; code stays until deleted
4. Features page: rows by kind, `k` keep, `x` cut, `u` unreview, `?` opens the feature's help row;
   help and palette show a glyph on anything unreviewed. Page key from the free letters in B-11

Acceptance:

- `go run ./scripts/inventory | jq length` is equal on two runs and covers every registry kind plus
  structs and concepts; every id in it appears in `deck docs` output
- with an empty review file `-review` lists every id; marking one `cut` removes it; editing that
  feature's defining text brings it back as `changed`
- an e2e check seeding a grouping as cut asserts `o`/`O` never show it in the title line

Open before claiming (the plan's two questions): verdict per machine (store), per repo (`docs/review.yaml`)
or both? Should `cut` ever delete code? The plan says no: the cut list is the deletion backlog.

notes:
- 2026-10-19 stub; expanded by a background agent the same day.

### B-23 Neovim as the input engine behind form fields, behind a settings toggle

status: ready · priority: p2 · size: L · owner: · branch: · verified:

Port `~/proj/redeck-astra2/docs/plans/neovim-input-engine.md`: one app-owned headless Neovim
(`--embed --headless`, controlled profile, no user config, swap or network) behind the shared form
fields, vendored vim-rsi at `45540637` for Readline-style insert bindings, a Msgpack-RPC remote UI
drawn inside deck's field layout, one scratch buffer per live field (hidden buffers keep undo). Neovim
owns text, cursor, mode and undo; deck holds snapshots. Picker queries and filters stay on the shared engine.

```js
EditorSnapshot = { owner: "form-instance-42", field: "description", activation: 7, changedtick: 19,
                   lines: ["Prepare release", "Check migrations"],
                   cursor: { row: 1, byteColumn: 6 }, mode: "insert",
                   presentation: { cells: [], cursorCell: { row: 1, column: 6 } } }
// activation changes on focus, changedtick on text; events from closed forms are dropped
```

Setting `editor.engine = "shared"|"neovim"`, default `shared`, on the settings page (B-21); with
`shared` the current engine is untouched and no Neovim process starts. Neovim 0.11 is installed on
vps2, so the spike and every check run there through `scripts/verify-vps.sh`.

Build order (the plan's seven steps):

1. spike on vps2: buffer attach, remote UI redraw, completion, Visual block, key encoding,
   input-drain-before-read; record version, cold start and input-to-render latency
2. `internal/editor/`: pinned vim-rsi runtime with licence, deck init embedded, minimum version check
3. ordered RPC worker, finite deadlines, field identities, lifecycle, bounded shutdown, undo per field
4. presentation in the field box: cells, highlights, cursor, mode, command-line, messages, completion
5. migrate form editing: text, paste API, reads, acceptance; single-line fields reject newlines
6. keys: a configurable host action leaves editing for form navigation (Escape goes to Normal, never
   discards the form); mass-add through the same adapter; picker and filter callers kept deliberately
7. e2e cases in the existing suites; docs and outline updated only after behaviour is proven

Acceptance (from the plan's evidence table):

- counts, operators, text objects and dot-repeat produce the exact expected text after compound edits
- returning to a field retains its undo history; switching fields does not merge their undo stacks
- rapid input followed by save persists every completed edit before the accept action
- another form cannot be overwritten by stale events; after engine failure the last acknowledged
  draft remains recoverable
- save, cancel, field switching and native file or directory pickers remain reachable while editing

notes:
- 2026-10-19 stub; expanded by a background agent the same day.

### B-26 Changelog and release script in the tuios-deck style

status: ready · priority: p2 · size: S · owner: · branch: · verified:

Adopt the `## Changelog` and `## Commits and releases` sections of `~/proj/tuios-deck/AGENTS.md` and
the `CHANGELOG2.md` shape. `CHANGELOG.md` is a diff of deck between two tags, not a story: one entry
per release, newest first, `## vX.Y.Z — YYYY-MM-DD`, under it one `###` list per concept, only the
concepts that changed, in this fixed order adapted to deck (no Web page; Units and MCP are ours):

Store · CLI · Settings · Units · Pages · Modals · Forms · Actions and keybindings · Palette ·
Groupings · Rail and detail · Live mode · MCP · Events and recorders · Scripts and suites · Docs

```js
Line = { verb: "added"|"changed"|"removed"|"fixed", text }
// added: <thing> + the facts to use it (key, default, flag, path, unit)
// changed: <thing>, <now>; was <before>   removed: <thing> and its replacement   fixed: the symptom
```

Rules, copied: one line per change, no paragraphs or sentences that only explain; names in backticks;
a number only where it changes what the reader does; a key as the help shows it; a glyph quoted as the
character; a change spanning concepts is listed once under the concept met first and named from the
others; invisible internals go under Scripts and suites or nowhere; written from `git log <last
tag>..HEAD` and the diff. Both sections go into redeck-astra's `AGENTS.md` between `# Driving deck` and
`## Remote verification`; the commits one keeps conventional commits, no amending, `main` on `vps2`.

`scripts/release.sh [patch|minor|major|vX.Y.Z] [--dry-run] [--changelog-prompt]` ported with:

- remote `vps2` (the hub repo on that host) wherever tuios-deck's says `origin`; there
  is no GitHub remote, so the ahead/behind check and the pushes target `vps2/main`
- the proxy priming block and the `deck update` hint removed; nothing goes to proxy.golang.org
- kept: newest tag by semantic version (`v0.0.0` when none; the repo has no tag yet), refuse to tag a
  version with no `## vX.Y.Z` entry, write `.dev/changelog-prompt.md` from the AGENTS.md section plus
  commits and `--stat` since the last tag, clean-tree and `main` checks, `go build` + `go vet`,
  annotated tag `deck vX.Y.Z`; `.dev/` added to `.gitignore`

Acceptance:

- `--dry-run` with no matching entry prints `CHANGELOG.md has no entry for v0.0.1`, writes
  `.dev/changelog-prompt.md` with the rules and the commit list, tags nothing; without `--dry-run` it exits 1
- with a `## v0.0.1` entry committed, `scripts/release.sh` creates annotated tag `v0.0.1` and
  `git ls-remote vps2 refs/tags/v0.0.1` shows it; `git tag -n1 v0.0.1` reads `deck v0.0.1`
- `grep -c proxy.golang.org scripts/release.sh` prints 0

notes:
- 2026-10-19 stub; expanded by a background agent the same day.

### B-27 Downloads page: watch ~/Downloads, newest first, copy absolute paths

status: ready · priority: p2 · size: S · owner: · branch: · verified:

A page listing the files in `~/Downloads`, newest first, so a path just downloaded is one keypress
from the clipboard. A `downloads` unit watches the directory with `fsnotify` (new dependency) and
rescans on page open, so a missed event never leaves the list stale; subdirectories are one row each,
not walked; dotfiles hidden.

```js
Download = { path: "/Users/me/Downloads/report.pdf", name: "report.pdf", size: 18233,
             modified: "2026-10-19T21:04:11Z", seen: false, marked: false }
// seen persists in the store keyed by path + modified; marked is page state and clears on leave
```

- page key `L` (downLoads), proposed here from the free uppercase letters in B-11/B-21
  (`B F I L N Q V X Y Z` remain after E settings, M/W B-11, U B-09, J/K B-06); registered like every
  page with a rail row per file: name, size, age; detail shows the full path, size, modified and the
  `NOTES` section (B-05 owner kind `download`, id = path)
- rows sorted by `modified` descending; a new file inserts at the top without moving the selection
  (the refresh rule); unread style (the unread theme from B-11) until the row has been selected
  once, then `seen: true`
- `y` on a row runs `context.copy` with the absolute path; `space` toggles `marked`, shown with a
  glyph; `y` with any marks copies every marked path, one per line, in list order, and clears the
  marks. `context.copy` already requires `pbcopy` on PATH and reports to the status line otherwise
- `enter` opens the file with the OS opener (`open` on macOS, `xdg-open` elsewhere) through the
  existing context `open` action
- `downloads.dir` setting (B-21), default `~/Downloads`, so checks point the page at a temp dir
- CLI: `deck download list` prints `modified size seen path` newest first

Acceptance:

- touching two files in the `downloads.dir` temp dir while the page is open shows both within a
  second, newest on top, both styled unread; moving the selection onto one clears its unread style
  and `deck download list` shows `seen` for it only
- `y` on a row puts its absolute path on the clipboard (a `pbcopy` stub on PATH writes to a file the
  check reads); `space` on two rows then `y` writes both absolute paths, one per line
- `deck note add --json '{"owner":{"kind":"download","id":"<path>"},"text":"…"}'` shows under the
  row's detail `NOTES`

notes:
- 2026-10-19 stub; expanded by a background agent the same day.

### B-05 Notes on almost anything, shown in the detail pane of every page

status: ready · priority: p2 · size: L · owner: · branch: · verified:

Today a note belongs to exactly one task or project (outline §6.8). Open it up so a note can hang
off nearly any row deck shows, and so the page that lists those rows shows their notes in the
main-content area on the right, not in a modal.

```js
Note    = { id, text, owner: Owner, created, updated }
Owner   = { kind: "task"|"project"|"pane"|"context"|"capture"|"review"|"vim"|"reminder"|"prompt", id }
// pane notes key on session + window id, like captures, and stay readable after the pane closes
Visible = { note: Note, via: "own"|"parent"|"project"|"owner", owner: name }   // inherited marking stays
```

Pieces, in build order:

1. store + commands: polymorphic owner on `notes`, migration of the two existing columns into it,
   `notes.add|patch|delete` accept `owner`, `deck note list --owner kind:id`, visibility rules keep
   today's task/project inheritance and add "a row sees its own notes"
2. detail pane: every page's detail ends with a `NOTES` section for the selected row, newest last,
   inherited notes marked with `via`, wrapped to the detail width, scrolling with the rest of the
   detail; empty shows one dim line, never a blank gap
3. keys: add a note under the selected row from any page, edit and delete a note when detail focus is
   on it; the form is the existing notes textarea with the owner prefilled and shown in the title.
   `a` is taken by Assign and `n` by "create on this page", so pick the key in the outline first
4. the notes page from phase 2 §1 (by owner, inherited marked) can come after; it is not needed for
   the detail view

Acceptance:

- `deck note add --json '{"owner":{"kind":"pane","id":"<session/window>"},"text":"…"}'` works for every
  kind in `Owner`, and `deck note list --owner` returns it; unknown kinds are rejected with `invalid_args`
- on each of Panes, Tasks, Context, Captures, History, Reviews, the detail of a row with notes shows the
  `NOTES` section with the text, and the rail row carries a note count or glyph
- adding, editing and deleting from the detail keeps the selection and scroll (same rule as refresh)
- the `descendant_notes` outline case still passes and gains one assertion per new owner kind

Open before claiming: the key for "add note here"; whether a review note belongs to the turn or to the
history entry; whether a closed pane's notes surface anywhere besides history.

notes:
- 2026-10-19 asked for notes on "almost anything", displayed in the right pane on that item's page.
- 2026-10-19 repeated: notes can be added to almost anything; the downloads page (B-27), documents (B-11) and action items (B-15) are owners too.

### B-04 Help modal: two rows shift left and leak border glyphs

status: claimed · priority: p2 · size: S · owner: mac lane 5 · branch: night/lane-5 · verified:

Screenshot: [attachments/B-04-help-modal-alignment.png](attachments/B-04-help-modal-alignment.png),
deck on a wide terminal, `?` on the Panes page, filter `all`.

What is wrong, visible in the screenshot:

- two rows are one cell left of every other row, in both columns at once: the row holding `}` / `h`
  ("Fold tree or return to parent (also Left)") and the row holding `d` / `l` ("Expand tree or
  inspect option (also Right)"). The same rows show a stray `│` at the left edge of the modal and
  another just inside the right edge, so the row is being rendered one cell wider than the panel.
  Probable cause, unverified: those two right-column descriptions are the widest in their group and
  overflow the column by one cell, so the joined row breaks the border. Check the width measurement
  on a row whose description is exactly the column width.
- the description column starts at a different x in every group (PAGES at the key + 1 cell, MOVE
  padded to `shift+tab`, SHELL to `ctrl+r`, SELECTION to `delete`, FORM narrower again), so the two
  columns read as a ragged stack of tables rather than one. Decide whether descriptions align per
  column (one key width per column) or per group, and apply it everywhere; the approved reference is
  `images/help-good.png`.

Acceptance:

- no row in the help modal is offset from its neighbours and no border glyph appears inside a row, at
  80, 120 and 200 columns, for every tab filter
- descriptions line up according to the chosen rule, and the e2e help case asserts the rule on at
  least one wide and one narrow capture

notes:
- 2026-10-19 reported from a screenshot; not to be worked on yet.

## p3 · someday

### B-02 Deck-owned agent messaging (shared places)

status: idea · priority: p2 · size: L

Already designed in [the outline](outline.md) under the code unit, "shared places": the deck owns the
record (`PlaceMessage`, `Claim`) and the routing, tuios mail is only the transport, and every message
lands in history under the sender's task. Open decisions 598 (deck server) and 610 (messages to a human
terminal) gate parts of it. Split into claimable items when it comes up.

notes:
- 2026-10-19 the design was settled earlier today in the outline; this entry only tracks building it.

## Done

Move finished items here with their branch and the verification log path, then add the behavior to the
outline's done list.

### B-30 Remove the Stale rail group on the panes page
status: done · priority: p1 · size: S · owner: Claude Fable subagent · branch: main (redeck-astra ccbb1747662b2fb472efbf3b23ebf09feec80599) · verified: /root/proj/redeck-astra-verification/runs/run.gXZXXkHU/verification.log
Stale panes stay in their project/task group with the stale mark and age; the separate Stale group hid panes the user cared about. The stale_after setting and the close-stale palette command remain.
notes:
- 2026-10-19 done in the background on request.
