# Agents, prompts, presets, and AI assets

[Remaining agent work](../todo/agents.md) uses the same concepts. Matomeru owns implementation; this document records current behavior and explicitly marked targets. Historical logs are recorded evidence, not checks performed during consolidation. The implementation owner reports five features completed and verified in commits `ec0d83a` and `e4cf07a`, pushed to main on origin and vps2. The parent observed those commits. Composer, defaults, ranked paths, and the implemented AI/Git/GitHub subset below use that newer evidence. This does not complete broader B-31, B-34, B-42, or UI-state acceptance.

<a id="prompts"></a>
## Prompt unit and launch flow

The prompts unit owns `prompt_presets`, `queued_prompts`, and `prompt_stashes`. Existing commands include `prompts.start-agent`, `prompts.new-terminal`, `prompts.queue`, `prompts.dispatch`, `prompts.add-preset`, and `prompts.stash`; changes emit `queue.changed` and `presets.changed`. It depends on the daemon, work target resolution, and panes. The TUI is one caller of the same command bus as the CLI and MCP.

The baseline preset is named text prepended once, with an optional cwd. The composer offers existing presets and `+ new preset…`. `Start(spec)` starts the agent, records its submission, and assigns its work target. Dispatch resolves a queued target; a new terminal can create its missing session. Results include readiness, blocker, prompt status, and explanatory notes rather than treating every created pane as a delivered prompt.

```js
Preset = { id, name, prefix, cwd, created }
QueuedPrompt = { id, text, preset, task_id, project_id, cwd, session, agent, window, created,
                 state?, daemon_id? }
StashedPrompt = { draft_id?, text, draft?, saved }
StartSpec = { host?, session, window?, agent, name, cwd, prompt, preset?, task?, project?,
              model?, thinking?, speed?, approval?, args?: [string], attach?: [path], ready_timeout? }
```

The optional model/thinking/speed/approval fields above describe the current source contract. They are not a promise that every harness or model accepts every control. The richer target `place?: Place` associates host, directory, worktree, and branch with a launch and its turn; that belongs to the unfinished [Place design](work.md#places), not a completed source-control attribution system.

A queued prompt belongs to its preset, a task or project, and optionally a target pane. A stash belongs to a draft. Stash text and dynamic child fields survive reopening. An unsent stash is not a queued prompt and does not contribute to `Qn`. Attachments, `@` paths, `/` skills and commands, and a target object's recent scrollback belong in the composer contract. Full catalog-backed completion remains [B-34](../todo/agents.md#b-34).

Sources: [original prompts unit](../sources/znbu/docs/outline.md), section 6.4; [implementation prompts contract](../sources/matomeru/docs/outline.md), section 6.4. Code evidence for the baseline comes from `internal/prompts/prompts.go`, `composer.go`, and `register.go` in the backlog audit. The newer owner verification is recorded below, rather than inferred from the source outline.

<a id="quickstarts"></a>
## Quick starts and form starts

The target design retains paired quick/form starts for terminal, agent, and managed Vim panes on every page. The old proposal uses `n t`, `n a`, `n v` for immediate start and `N t`, `N a`, `N v` for a form. Effective configured actions are authoritative if bindings differ. New panes inherit a `NewSpec`, not a new set of ad hoc defaults.

A highlighted pane or Vim session supplies host, tuios session, task/project, place/cwd, and applicable harness/preset. Otherwise the pin supplies work ownership and the current tuios session, resolved place, and configured harness/preset. The form starts from the same values but allows edits and shows dirty/busy/branch/behind/PR/CI warnings. Assignment occurs before the start action returns, so a new pane does not briefly land in No Task. Implemented [default inference](#launchdefaults) adds launch-history evidence without replacing explicit inputs.

```js
NewSpec = { kind: "terminal | agent | vim", host, session, task_id, project_id,
            place, cwd, harness?, preset?, name?,
            warnings: [{ kind: "dirty | busy | branch | behind | pr | ci", text }] }
```

The full Place/warning target and quick-start refusal on conflicting path claims remain [work design](work.md#sharedplaces). This paragraph preserves the original design, not an assertion that all warning producers exist. Sources: [original TUI and flows](../sources/znbu/docs/outline.md), sections 7.1 and 8.

<a id="b-32"></a>
<a id="questionpresets"></a>
## B-32 basic presets and richer question presets

Status: partial. `internal/prompts/prompts.go` has `Preset` with id, name, prefix, cwd, and created time; `ApplyPreset` prepends once. This implements basic prompt-prefix selection, not the asked-question system. The implemented two-input composer is not `AskedPrompt` storage, question/answer capture, or a Questions page.

The remaining [B-32](../todo/agents.md#b-32) target adds prepend/append text, agent/ask kind, a preset-first ask action, full typed/sent provenance, answer capture on the delivered target turn's completion, and question management. Recording applies to every preset-bearing delivered prompt, including ordinary composer and start-agent sends, not only the ask action. The old proposal reserves `i` for ask, `Y` for Questions, and leaves `P` as switch. Those bindings require effective-config conflict review when implemented.

```js
QuestionPreset = { ...Preset, position: "prepend | append", text, kind: "agent | ask" }
AskedPrompt = { id, preset_id, typed, sent, session, window, turn_id, task_id, project_id,
                sent_at, answer, answer_turn_id, answered_at }
```

A brief example appends `Answer in 10 words or less, or if necessary 3 paragraphs or less.` Store typed text separately from the final sent text so preset application is auditable and cannot be applied twice. Sources: [original B-32](../sources/znbu/docs/todo.md#b-32-preset-prompts-a-dedicated-start-with-preset-action-and-a-page-of-asked-questions); [turn capture](knowledge.md#history).

<a id="fieldpresets"></a>
## Field-group presets and sparse layers

Status: open [B-42](../todo/agents.md#b-42). This is distinct from B-32 text/question presets and from inferred fill-empty defaults. Keep both user-approved ideas until their relationship and names are decided:

- Execution location groups host, repository, cwd, and worktree.
- Work assignment groups project and task.
- Agent profile groups harness/agent, model, and effort.
- Sparse layers may supply any subset of fields, without becoming fixed groups. Apply layers in order. Every supplied value overwrites the prior value, including an already populated field; omitted fields remain untouched.

```js
current = { host: "local", task: "Login", model: "model-a" }
layer = { host: "vps2", effort: "high" }
after = { host: "vps2", task: "Login", model: "model-a", effort: "high" }
```

Expose the one or two most recent selections as preset-like choices even when there is no saved preset. The names above are working terminology. Implemented `launchDefaults` fills inferred values; it does not implement this overwrite rule. Sources: [preserved request](../sources/hub/prompts/mtm-todo.md), lines 6–15; [original B-42](../sources/znbu/docs/todo.md#b-42-field-group-presets-recent-selections-and-composable-preset-layers).

<a id="b-61"></a>
<a id="launchdefaults"></a>
## Inferred launch defaults

Status: implemented in commit `e4cf07a`, with owner-reported VPS verification. `internal/prompts/defaults.go`, the `prompts.launch-defaults` source, and `prompt_launches` are implementation evidence. The owner reports launch-default, CLI, SSH remote-launch, stash, and full TUI/live acceptance. This consolidation did not rerun those checks.

The precedence is explicit inputs and restored drafts, then focused-item evidence, scoped successful-launch modes, and finally project/preset/environment defaults. `_focus_window` provides evidence without selecting an existing destination. Form seeds and backend launches use the same inference. A successful-launch record contains terminal/agent settings, not prompt text or attachments. Queuing and ordinary activity do not become launch samples.

Keep remote host history and path evidence separate. Remote launches route through same-connection `open-host-connection`; remote session/window IDs are host-qualified in pane lists, queue receipts, and assignments. Do not use local working-directory defaults/validation or local MCP setup for a remote launch. [Ranked local directory suggestions](work.md#rankedpaths) are documented separately, including canonical-path deduplication, unrelated-project discovery, manual input, and native-picker availability.

This implementation is not B-42's named field-group UI or ordered sparse-layer system. Source: [preserved prompts contract](../sources/matomeru/docs/outline.md), section 6.4; [ranked directory plan](../sources/matomeru/docs/plans/ranked-dir-suggestions.md).

<a id="b-62"></a>
<a id="composer"></a>
## Two-input Prompt/Settings composer

Status: implemented in commit `e4cf07a`, with owner-reported VPS verification. This is separate from the earlier verified generic [B-31 form baseline](forms.md#b-31). Recorded owner evidence includes `run.8tnoOG3b` for composer/settings/collision and all five destination layouts, `run.uag5oacy` for TUI, and stash/help/full live acceptance. Native macOS picker interaction was not exercised on Linux.

`p` shows a multiline Prompt and a Settings input. Tab switches between them. Enter inserts a prompt newline or accepts a settings value; `ctrl+s` sends now and `ctrl+q` queues. `alt+/` opens advanced Host, Destination, Assignment, cwd, preset, attachment, and approval fields. Escape returns to the two-input view rather than losing the prompt. This specialized composer overrides the ordinary form layout without creating a second input/key-binding system.

Settings displays Harness, Model, Effort, and Speed columns backed by catalogs. Fuzzy queries match option values rather than descriptions. Live weighted suffix recall and visible searchable disambiguation tokens help choose colliding labels; storage retains the original option value, never the display token. Host precedes Destination and Assignment in advanced launch forms. Aliases include configured addresses. The local daemon labels itself with `TUIOS_HOST` only when its socket matches the current pane; otherwise it shows its socket endpoint.

Source: `internal/ui/forms/prompt_composer.go`, launch-default wiring, and the [preserved implementation outline](../sources/matomeru/docs/outline.md), section 6.4. Commit `e4cf07a` and the newer owner verification, not the older form log, support this richer composer. Full `/` skill/command discovery remains [B-34](../todo/agents.md#b-34); rich ask records remain [B-32](../todo/agents.md#b-32).

<a id="modelcatalog"></a>
## Harness and model option provenance

Status: implemented option integration in `e4cf07a`, included in the owner-reported composer/CLI verification. Model availability and provider/account/harness compatibility remain explicitly unverified limits of the catalog, not a promise that every listed option runs. [B-34](../todo/agents.md#b-34) remains the broader disk/config/plugin inventory, not merely a model picker.

`prompts.agents` advertises the 24 bundled TUIOS harness IDs. Recognized commands are not proof of installation. Custom executable commands remain accepted. `prompts.models` prefers installed OMP, OpenCode, and Codex catalogs where available and uses the public models.dev text-model catalog as fallback. Preserve catalog origin and limits in the UI; a catalog listing does not establish provider access, model availability, account entitlement, or harness compatibility. Catalog reads have finite subprocess/HTTP deadlines and perform no inference.

Thinking, approval, and speed are harness-specific. Do not invent flags for an unsupported harness. Codex `fast` maps to its fast service tier. Claude `normal`/`fast` maps to session `fastMode`. OMP exposes documented OpenAI service tiers. Model/account restrictions still apply, and unsupported controls return errors. Sending to an existing window cannot change its launch speed. Host/harness/model dependency changes refresh only relevant options without erasing unrelated input or accepting stale async results.

The catalog is not a credential store and must not silently promise that a recognized ID will run. Preserve original identifiers through token disambiguation. Source: [preserved prompts source contract](../sources/matomeru/docs/outline.md), section 6.4. This consolidation did not call providers or test model/account combinations.

<a id="queues"></a>
<a id="queueoutcomes"></a>
## Queue, dispatch, stash, and outcome visibility

The implemented prompts unit persists queued prompts and stashes. The original design requires a queued prompt to appear in the queue list immediately, with separate send-now and queue-at-turn-end bindings. Dispatch can create a target, assign it, and still fail to deliver input. Never erase that partial target identity or silently start another agent on retry.

Source-observed `SyncQueue` behavior copies daemon receipt states, moves saved prompts to waiting after acceptance, removes a daemon-owned local receipt when the target definitively reports `window_not_found` or `session_not_found` or its receipt disappears, and retains it on transport/other read errors. It does not automatically resubmit. That deletion is not evidence of delivery. The required outcome/read model remains [B-63](../todo/agents.md#b-63).

Join local and daemon entries by delivery identity and host-qualified target, never prompt text. One local row with a `DaemonID` and its daemon entry is one prompt. If aggregate daemon counts cannot be correlated, label local and daemon counts separately instead of inventing an exact total. Untargeted prompts remain in their task/project queue. Stashes retain draft identity, text, dynamic form state, and save time; they are not queue receipts.

Visible outcomes distinguish accepted, waiting, evidenced delivery, blocked, failure, closed target, cancellation, and unknown. Missing receipt alone does not distinguish sent, cancelled, or discarded. Keep blocked reason, `PromptStatus`, `PromptNote`, readiness, target identity, and reconciliation errors inspectable after transient status text clears. Unknown is not success and is not a reason to resubmit.

Sources: [original prompt unit](../sources/znbu/docs/outline.md), section 6.4; [UI state inventory](../ui-state-visibility.md#queue-identity-and-transitions); source audit of `internal/prompts/composer.go`, `prompts.go`, and `SyncQueue`. The [shared visibility contract](forms.md#visibility) covers the rendered matrix and acknowledgement rules.

### Batch work queue integration

The [work-queue plan](../plans/queue.md) describes a separate `internal/queue` item/batch workflow, not the prompts unit's `queued_prompts` receipts. It is merged into main; real CLI, MCP, dispatch, and TUI acceptance passed on vps2 in `run.K14YL9XV` (28 seconds). [B-63](../todo/agents.md#b-63) retains the delivery-outcome gaps. The plan's original B-39 label does not change canonical [runner B-39](../todo/delivery.md#b-39).

Implemented portions include `queue_items`/`queue_batches`, repository-group claim, finish/release, bounded dispatch, pane-close release, rapid-add/mark/target TUI actions, and pane-bound MCP tools. The acceptance run exercised CLI group/finish/release, dispatch limits and closed-pane recovery, MCP claim/finish/history, and TUI rapid add/mark/target/finish. Dispatch uses `prompts.start-agent`; blank harness/session/cwd inherit ordinary launch defaults and requested rows/columns are forwarded. Existing prompt queues remain separate.

The remaining delivery gap is explicit: dispatch treats a returned window as started and does not use decoded `PromptStatus` as proof of prompt delivery or acknowledgement. Passing item/batch acceptance does not promote that target-created result to delivered.

The current session requirement supersedes the historical plan default. Explicit dispatch session wins, followed by nonblank configured `queue.session`; a blank queue session delegates to ordinary project-named launch defaults. A batch result or closed-pane release does not prove prompt delivery, cancellation, or receipt reconciliation.

<a id="aiassets"></a>
## AI assets and subsection navigation

Status: B-34 partial, with its subsection subset implemented in `e4cf07a` and owner-reported verified. `internal/ai/ai.go`, `skills.go`, and `sessions.go` add AI on `F` with Harnesses, Skills, Agents, and Sessions. These mean recognized harness commands, discovered local skill files with canonical paths, live agent panes with ownership, and observed conversations from recorded turns.

Observed Sessions group by host, harness, conversation, and event-time ownership. They are not a complete inventory of session files on disk. Recognized harnesses do not imply installed binaries. Local skill discovery is useful partial scope, not the original full persisted scanner.

Registry subsections use `[` and `]`, with independent filters, selection, scope, and scroll. Reads load lazily and refresh through `ctrl+r`; results belong to their page/section request. Only live subsections opt into ticks: AI Agents, AI Sessions, and Watched PRs. Mutation refreshes preserve selection, filter, and scroll without periodically rerunning Git/GitHub network inventories. [Git and GitHub inventory](work.md#gitcatalog) owns repositories/worktrees/remotes/branches/commits and live PR scope. Those adjacent pages do not complete AI asset discovery.

The unfinished [B-34](../todo/agents.md#b-34) target remains a per-harness disk/config/plugin scanner and a cross-harness skill view. Preserve all original kinds:

```js
Harness = { id: "claude-code", name, root: "~/.claude", config: [path], scanned_at }
Skill = { id, harness, name, description, path, source: "user | plugin:<name> | catalog", link_target? }
Agent = { id, harness, name, description, model?, tools: [name], path, source }
Command = { id, harness, name, description, path, source }
Plugin = { id, harness, name, version, marketplace, path, provides: { skills, agents, commands, mcps } }
Market = { id, harness, name, url, path }
MCP = { id, harness, name, transport: "stdio | http", command?, url?, scope: "user | project", path }
```

The original layout proposed `X` for a two-panel AI page and `W` for global skills. Implemented navigation uses `F` AI, `W` Git, and `V` GitHub. This is a navigation conflict to resolve explicitly while retaining cross-harness search, repeated section structure, and scanner acceptance, not grounds to silently drop them. Hook/config sections have no separate original schema but remain required inventory sections.

Source: [original B-34](../sources/znbu/docs/todo.md#b-34-ai-page-harnesses-agents-skills-commands-marketplaces-mcps-learned-from-disk); [implementation inventory contract](../sources/matomeru/docs/outline.md), section 6.15. Adjacent tool/plugin/context ideas beyond Matomeru remain in the [ecosystem design](ecosystem.md) and [ecosystem backlog](../todo/ecosystem.md). Owner-reported evidence includes `run.0FUXkwfs` for AI provenance, `run.uMlaOO9N` for live GitHub, `run.t7d5iNMS` for watched actions, page/subsection keys, canonical repository/branch sharing, and a real 100-PR comparison. These checks do not establish the full disk scanner.

<a id="harvest"></a>
## MCP harvest, catalog, and replay

Status: open [B-14](../todo/agents.md#b-14). The existing pane-bound MCP server is separate infrastructure, not a log harvester or external-server replay client. The target is deterministic use of authenticated servers such as Slack, Glean, Linear, and GitHub without agent inference.

Preserve log-derived server/tool definitions, input schemas, call arguments, responses, harness/pane/time provenance, and incremental file metadata. Templates combine observed argument shape, example arguments, declared input schema, and response selection/parser metadata. Start with tool catalog metadata that commands and schedules can invoke. Promote a tool to a typed first-class handler only when a page depends on its shape. [Automation](automation.md) depends on that distinction.

The 2026-10-19 source survey found Claude and Codex MCP calls and nested OMP eval results, but no real Slack, Glean, Linear, or GitHub MCP call. It recorded Claude 400 files/672 MB with eight real MCP tool-use blocks, Codex 134 files with 371 calls, OMP 892 files/933 MB with nested traffic, and one OpenCode database. Those are dated observations, not current counts or replay evidence. Offline harvest must stand alone. The Slack template/live replay acceptance requires an actual captured or live server call and cannot be claimed from the surveyed logs.

Source: [original B-14 log schemas, survey, and acceptance](../sources/znbu/docs/todo.md#b-14-mcp-harvest-and-replay-built-into-deck-read-harness-logs-catalog-servers-and-tools-call-them-without-an-agent). The old Ruby `~/bin/h-mcp` and `~/bin/lib/h_mcp_harvest.rb` are reference behavior, not code copied or exercised here.

<a id="unitprompts"></a>
## Per-unit prompt management and instructions

Status: target [B-64](../todo/agents.md#b-64). The phase-2 design adds a Prompts page with presets and queue side by side. Enter dispatches, `e` edits, Delete/drop removes, and `m` moves a prompt to a task. The original proposed `d` for drop must be reconciled with shared half-page navigation. Pages register under their unit id, use the shared scope/ALL toggle, and are read-only in ALL except assign.

The [unit modal and notes model](knowledge.md#unitnotes) provides Shape, Notes, and Prompts folds generated from registry/store data. Selected unit notes can build a prompt containing that unit's generated outline node, the numbered notes, and build instructions. The composer still permits presets, attachments, and edits. Its cwd defaults to the app's own source tree, not the active work pin.

Submission uses ordinary `prompts.start-agent` or `prompts.queue`. The unit prompt records target window, submission, and correlated turn. Only a `response-completed` for the delivered request after its `prompt-submitted` completes the linked notes. A `<task-notification>` does not end the turn. The review queue shows the resulting turn and the notes it closed. Reopening a note clears its prompt link and completion time.

```js
UnitPrompt = { id, unit, note_ids: [id], text, preset?, window?, submitted?, turn_id?, created }
```

`UnitPrompt` belongs to the unit and pane, has many notes, and has one history turn. The proposed `meta` unit owns `unit_notes` and `unit_prompts`; domain units do not own notes about themselves. [Knowledge](knowledge.md#unitnotes) retains the complete schemas, commands, lifecycle, and modal open decisions. Prompt design must still decide embedded outline text versus path link, one versus many prompts in flight per unit, and where the app repository tree is recorded. Generated [agent instructions](knowledge.md#agentinstructions) are input to prompts, not proof that this workflow exists.

Sources: [phase-2 plan](../outline-phase2.md), sections 1–3 and 5; [original build rules](../sources/znbu/docs/outline.md), section 0b. The phase-2 unit-modal `I` proposal conflicts with the current Actions key; no new key is declared shipped by this consolidation.

The user's newer [verb-first creation design](forms.md#commonverbs) adds a shared `new…` route to terminal, agent, Vim, prompt, project, task, and note creation. Agent harness/model/directory ordering and the illustrative prompt variants remain open design, not an implemented command taxonomy.
