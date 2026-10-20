# Agent and prompt work

[Current agent behavior and target design](../outline/agents.md). This file retains only unfinished acceptance. The newly verified owner implementation of [launch defaults B-61](../outline/agents.md#b-61) and [two-input composer B-62](../outline/agents.md#b-62) belongs in the outline. It does not close rich question presets, field-group layers, complete AI discovery, or queue outcome requirements. Historical and owner-reported checks were not rerun during consolidation.

<a id="b-14"></a>
## B-14 offline MCP harvest, catalog, templates, and replay

Status: open. Priority: p2. Size: L. [Design and survey limits](../outline/agents.md#harvest). The existing MCP server is not a harvester or external-server client.

Port the behavior and data model of `~/bin/h-mcp` and `~/bin/lib/h_mcp_harvest.rb`, not the Ruby implementation. Read Claude Code, Codex, and OMP JSONL logs on demand and on a schedule through `mtm mcp harvest`. Preserve configured servers, tools, declared input schemas, every call's arguments, its response, and harness/pane/time provenance. Retain OpenCode's database reader as the additional surveyed source rather than losing it when implementing the three required readers.

Use server, tool, and call catalogs (`mcp_servers`, `mcp_tools`, `mcp_calls`) plus an incremental `mcp_harvest_files` index by path, size, and mtime and tool definitions equivalent to `mcp_tool_definitions`. Templates aggregate observed argument shape, example arguments, declared schema, and response parser/selection. Commands include `mtm mcp servers`, `tools`, `calls`, `template SERVER TOOL`, and `call SERVER TOOL --json '{…}' --select path`.

Preserve each real log shape:

- Codex roots are `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl` and `~/.codex/archived_sessions/`. A complete call/result can be in one `type=event_msg`, `payload.type=item_completed`, `payload.item.type=McpToolCall` record. Read `server`, `tool`, `arguments`, `result.content[]`, `result.isError`, `status`, and `duration`.
- Claude roots are `~/.claude/projects/**/*.jsonl`. Assistant `message.content[]` entries with `type=tool_use` and `mcp__<server>__<tool>` join user `tool_result` by `tool_use_id`. Prefer record-level `toolUseResult`, otherwise block `content`. Definitions come from attachment `deferred_tools_record.entries[]` and `prompt_snapshot.tools[]` with `input_schema`.
- OMP roots are `~/.omp/agent/sessions/<cwd-slug>/<ts>_<id>.jsonl`. There need not be a direct `mcp__` toolCall. Unwrap `role=toolResult`, `toolName=eval`, `details.jsonOutputs[].details` with `serverName`, `mcpToolName`, and associated result metadata. The old Ruby reader missed these nested calls.

Replay uses each server's own transport and harness-configured authentication. Start with catalog metadata that commands/schedules can trigger; generate typed first-class handlers only when a page depends on a tool's shape. Never treat permission-list text as a captured call or require provider inference for offline harvest.

Acceptance:

- On the surveyed Mac inputs, harvest finds the servers/tools and reports per-tool call counts from Claude, Codex, and nested OMP logs. Repeated harvest uses the incremental index without duplicating calls.
- `mtm mcp template slack search` prints a filled example from a real harvested Slack call once one exists. `mtm mcp call` against a live authenticated server returns the parsed response and honors response selection.
- Offline harvesting works without a live server. Keep replay acceptance separate when no server is available. The dated survey found no Slack, Glean, Linear, or GitHub call, so those logs cannot prove their templates or replay.

Source: [original B-14](../sources/znbu/docs/todo.md#b-14-mcp-harvest-and-replay-built-into-deck-read-harness-logs-catalog-servers-and-tools-call-them-without-an-agent). Adjacent generic tool-catalog ideas remain in the [ecosystem backlog](ecosystem.md).

<a id="b-32"></a>
## B-32 rich prompt presets and recorded questions

Status: partial. Priority: p1. Size: M. The implemented [basic prefix/cwd preset](../outline/agents.md#b-32) is the baseline. The two-input composer does not supply question/answer persistence.

Extend `prompt_presets` with `position: prepend | append`, `text`, and `kind: agent | ask`. Existing rows migrate/read as prepend plus their old prefix, kind agent. Apply the preset once with a blank-line separator: prepend is preset text then typed text, append is typed text then preset text. Keep typed and sent text separately.

```js
Preset = { id, name, prefix, cwd, created, position: "prepend | append", text, kind: "agent | ask" }
AskedPrompt = { id, preset_id, typed, sent, session, window, turn_id, task_id, project_id,
                sent_at, answer, answer_turn_id, answered_at }
Action = { name: "ask", mode: "normal", key: "i" }
Page = { id: "questions", key: "Y", rail: "prompts.asked", detail: "prompts.asked-detail" }
```

Add `prompts.ask` and registry CLI `mtm prompt ask`/`mtm prompt asked`. The normal ask action opens a preset-first composer, then text. `+ new preset…` creates a preset; `form.add-preset` gains position. Keep `P` as switch. The proposed `i` and `Y` require effective-binding conflict review, not a silent semantic change.

On the target pane's correlated turn end, history's final assistant message fills answer, answer turn, and answered time in the original `asked_prompts` row. A later unrelated turn or task-notification must not become the answer. The Questions rail lists newest first with typed text, preset name, pane, and answered/waiting state. Detail shows sent text and answer. `/` filters typed and answer text. Retain all turn/pane/task/project provenance.

Record every preset-bearing delivered prompt with its correlated answer, including ordinary composer and start-agent sends, not only `prompts.ask`. All entry points share this recording contract; the basic preset and verified composer remain implemented baselines.

Acceptance:

- `mtm list-actions` shows ask in normal mode on the agreed key, originally `i`.
- For preset `brief` with append text `Answer in 10 words or less, or if necessary 3 paragraphs or less.`, `mtm prompt ask --json '{"preset":"brief","text":"what is 2+2","window":"<id>"}'` creates a row whose sent text ends with that preset text exactly once.
- After the corresponding agent turn completes, the same row has a nonempty captured answer and its turn/time provenance.
- A prepend preset places its text before typed text.
- Deliver preset-bearing prompts through ordinary composer and start-agent flows as well as ask; each records typed/sent text and captures only its correlated target-turn answer.
- A real PTY opens Questions on the agreed key, originally `Y`, and sees the question in the rail and answer in detail.

Source: [original B-32](../sources/znbu/docs/todo.md#b-32-preset-prompts-a-dedicated-start-with-preset-action-and-a-page-of-asked-questions). New prompt variants such as question, reference document, researcher, and designer are examples in the [shared new-command design](../outline/forms.md#commonverbs), not a closed taxonomy that replaces this acceptance.

<a id="b-34"></a>
## B-34 complete the per-harness AI asset catalog

Status: partial. Priority: p2. Size: L. The [implemented subset](../outline/agents.md#aiassets) is AI on `F` with recognized Harnesses, local Skills, live Agents, and observed-conversation Sessions, committed in `e4cf07a` with owner-reported verification. Keep only the remaining original scanner/catalog scope here. Git/GitHub sharing and subsections do not satisfy that scope.

Add a persisted disk/config scanner with `ai.scan`, startup/on-demand scans, one scanner per harness, and tables for the [original asset shapes](../outline/agents.md#aiassets). Read frontmatter name/description and preserve model/tools where present. Inventory agents, skills, commands, plugins, marketplaces, MCPs, hooks, and configuration, rather than limiting discovery to live panes and current skill completion.

Retain every original scan root and configuration source. Counts below are the 2026-10-19 source survey, not fixed current acceptance totals:

- Claude Code: `~/.claude/skills` (391 entries in the survey), `agents` (32), `commands` (20), `hooks`, `rules`, and `settings.json`; plugin `installed_plugins.json`, `known_marketplaces.json`, `marketplaces/claude-plugins-official`, and `cache/claude-plugins-official/*`; MCPs from `~/.claude.json` `mcpServers` and per-project `.mcp.json`.
- Codex: `~/.codex/config.toml` `[mcp_servers.*]`, skills, `hooks.json`, `AGENTS.md`, and plugin caches `claude-cowork`, `claude-plugins-official`, `openai-bundled`, `openai-curated-remote`, and `openai-primary-runtime`.
- OMP: `~/.omp/agent/config.yml`, skills, extensions, `keybindings.yml`, `~/.omp/plugins/package.json`, and `~/.omp/marketplaces.json`.
- Other roots: `~/.gemini/settings.json` and skills; `~/.cursor/mcp.json`, skills, agents, and plugins; `~/.config/opencode/opencode.json`, skills, and plugins; `~/.agents/skills` and agents; `~/.pi/agent`.
- User catalog symlink targets: `~/proj/ai-tools/catalog/{skills,agents,commands,hooks,extensions}`. Preserve both source path and canonical/link target rather than erasing symlink provenance.

Preserve a per-harness navigation view with the same section names and selected-list/detail behavior. Detail shows path, source, frontmatter, and initial file lines; Enter opens the real file in managed Neovim. Preserve a cross-harness skill search. The old `X` AI/`W` Skills key proposal conflicts with current `F` AI/`W` Git/`V` GitHub; resolve keys/layout explicitly without dropping required discovery or search.

The composer `/` completer and [B-33 skills sub-palette](forms.md#b-33) read the resulting catalog, not a separate manually entered inventory. MCP records retain stdio/http transport, command/URL, user/project scope, and config path. Plugin records retain marketplace/version and provided assets. Catalog model availability/compatibility limits remain visible and are not installation guarantees.

Acceptance:

- After `mtm ai scan`, a skill list filtered to `claude-code` has the same count as the actual matching `~/.claude/skills/*/SKILL.md` files under the scanner's stated scope. The old 391 survey count is not hard-coded.
- The MCP list includes `tuios` from `~/.claude.json` when that config is present.
- A real PTY opens the agreed AI navigation and sees every scanned harness with the same section names.
- Cross-harness `/ tuios` skill search returns more than one harness where the scanned fixtures/files contain them.
- A symlinked skill displays `link_target` under the user's catalog.

Source: [original B-34](../sources/znbu/docs/todo.md#b-34-ai-page-harnesses-agents-skills-commands-marketplaces-mcps-learned-from-disk). Do not reopen the verified subsection implementation merely to retain this broader acceptance.

<a id="b-42"></a>
## B-42 field-group presets, recent selections, and sparse layers

Status: open design. Priority: p2. [Design and overwrite example](../outline/agents.md#fieldpresets). Basic prefix/cwd presets and inferred launch defaults are related inputs only. Neither is this feature.

Find names for cohesive execution-location, work-assignment, and agent-profile concepts and make each easy to set. Working groups are host/repository/cwd/worktree; project/task; harness/agent/model/effort. Preserve both groups and sparse layers as compatible alternatives until their relationship and terminology are decided. A layer can supply any subset, not only one predefined group.

Acceptance:

- Set each cohesive group without editing every constituent field.
- With no saved preset, offer the one or two most recent selections as preset-like choices.
- Apply multiple sparse layers in order. Every supplied field overwrites its earlier value, including nonempty values. Omitted fields keep their values.
- For current `{host: local, task: Login, model: model-a}` and layer `{host: vps2, effort: high}`, preserve task/model and replace host while adding effort. Fill-empty-only behavior fails this criterion.
- Keep groups and layers compatible while names and relationships remain undecided.

Sources: [original B-42](../sources/znbu/docs/todo.md#b-42-field-group-presets-recent-selections-and-composable-preset-layers); [preserved user request](../sources/hub/prompts/mtm-todo.md), lines 6–15.

<a id="b-63"></a>
## B-63 durable queue and dispatch outcomes

Status: open. This identifier preserves the unnumbered queue-outcome requirements in the [UI-state inventory](../ui-state-visibility.md#queue-identity-and-transitions). [Current queue behavior and target](../outline/agents.md#queueoutcomes) distinguish receipt reconciliation from delivery evidence. The verified new composer does not prove all these outcomes exist.

- A newly queued prompt appears immediately in the queue list. Send-now and queue-at-turn-end remain distinct actions.
- Join persisted prompts and daemon receipts by delivery identity plus host-qualified target, not text. Count a local row with `DaemonID` and its daemon entry once. When correlation is impossible, display separate local/daemon counts rather than a false exact total. Untargeted prompts stay in the task/project queue.
- Add an inspectable outcome model where `SyncQueue` currently deletes or logs. Distinguish accepted, waiting, evidenced delivery, blocked, failed, closed target, cancelled, and unknown. Disappearance alone never means delivered.
- A start returning a window followed by error retains created-target identity, readiness, blocker, reason, `PromptStatus`, and `PromptNote`. Retrying must not silently launch a second agent.
- Closed targets are not successful delivery. A missing receipt alone does not distinguish sent/cancelled/discarded. Transport/reconciliation failures retain the local record and an inspectable error; no automatic resubmission.
- Stashes/drafts expose owner and saved time, stay unsent, preserve dynamic child edits, and never contribute to queue count. Existing stash support is the baseline, not work to rebuild.

Acceptance exercises local saved → daemon waiting without double count, blocked plus needs-you, partial dispatch failure, closed target, missing receipt, and reconciliation read failure. Assert rendered outcome, target identity, retained draft, and clearing behavior, not just backend fields or log text. Link these scenarios into [B-60](forms.md#b-60)'s complete visibility matrix.

<a id="b-64"></a>
## B-64 per-unit prompts and instruction-driven work

Status: open phase-2 target. [Design](../outline/agents.md#unitprompts), [unit-modal schemas and lifecycle](../outline/knowledge.md#unitnotes), and [unit-note CRUD B-90](knowledge.md#b-90) define the boundaries. Knowledge owns notes/modal CRUD; this item owns prompt construction, dispatch, turn correlation, and the Prompts page.

- Register a scoped Prompts page under the unit id, showing presets and queue side by side. Enter dispatches, `e` edits, drop removes, and `m` moves a prompt to a task. ALL is read-only except assign. Resolve the original `d` drop proposal against shared half-page navigation rather than taking over a motion silently.
- Build a prompt from selected unit notes. Include the generated unit shape/outline node, notes as a numbered list, and build instructions. Open the ordinary composer so presets, attachments, and edits still apply.
- Default cwd to the app's own repository tree, not the current pin. Decide whether that tree is recorded in settings or as an app project.
- Submit through `prompts.start-agent` or `prompts.queue`. Persist `UnitPrompt {id, unit, note_ids, text, preset?, window?, submitted?, turn_id?, created}` in the proposed meta unit's `unit_prompts` table. Mark selected notes prompted with their prompt id only at the defined submission transition.
- Correlate history `prompt-submitted` to the later `response-completed` for that delivered request/window. Attach the turn, complete linked notes with done time, and show the notes closed by the turn in review. `<task-notification>` does not end the request, and an unrelated later turn does not complete these notes.
- Reopening notes clears their old prompt link and completion time through knowledge's meta commands. Preserve generated [agent instruction context](../outline/knowledge.md#agentinstructions) rather than hand-writing an independent copy in each unit.

Acceptance covers selection → generated body → edited composer → immediate start and queued start → correlated completed turn → linked done notes/review → reopen. Persist relationships across restart. Keep the open decisions visible: embed generated outline text versus link by path, one versus multiple in-flight prompts per unit, app repo-tree location, and the unit-modal key (`I` versus `ctrl+i`, with `I` already used by Actions). These are undecided, not implementation facts.

Source: [phase-2 design](../outline-phase2.md), sections 1–3 and 5. Other dedicated unit pages stay with their owners rather than becoming duplicate acceptance here.
