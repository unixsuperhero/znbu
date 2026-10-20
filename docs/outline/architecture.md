# Architecture

Current implementation and target decisions are separate below. Remaining work is in [architecture todo](../todo/architecture.md). Historical inputs are the [original design](../sources/znbu/docs/outline.md) and [implementation outline](../sources/matomeru/docs/outline.md). Source inspection is evidence, not a runtime check.

<a id="units"></a>
## Units and process ownership

A unit owns one concept, its tables, commands and rules. Units communicate through synchronous bus commands, event handlers and supplied narrow interfaces. They never import shells or own selection, scroll, modal or live view state. Units register declarative pages, forms, actions and read sources at startup.

[Inventory](inventory.md) is a first-class target category spanning tracked kinds and their relationships. It does not change unit ownership by itself; owned children, reusable links, and category-versus-unit boundaries remain [B-100](../todo/inventory.md#b-100) design work.

The executable is `cmd/mtm`. Construction opens storage, builds units, fills and checks the registry, registers handlers, then starts the runner and shell. Shutdown stops producers, drains events, flushes history and closes storage. One-shot CLI processes use the local runner before exit. Evidence: `cmd/mtm/wiring.go`, `internal/events/runner.go`. Attention units remain constructed through `internal/reminders/attach.go`; moving construction to the composition root is retained under [B-70](../todo/architecture.md#b-70).

The daemon boundary provides Call, Subscribe, Presence, StreamPane and typed verb wrappers; `tuios list-verbs` is the external contract. Its start-agent shape includes session, agent, name, cwd, prompt and ready_timeout. Domain units do not bypass it to drive terminal state. Every user-relevant transition also follows the [visible-state matrix](delivery.md#visibility): indicator, explanation and clearing rule, including failure/unknown states.

```js
Unit = { id, tables: [name], commands: [name], emits: [type], listens: [daemonType], pages: [id], palette: [id], cli: [spec] }
Wiring = { client, store, config, registry, bus, runner, units, shells: [tui | cli | mcp] }
```

<a id="store"></a>
## Store

SQLite via modernc.org/sqlite stores JSON rows in unit-owned tables. No speculative JSON-file backend is planned. Table declarations name owner, key, version and append-only policy. Redeclaration cannot silently change these. A table belongs to one unit; a store has many tables.

`Tx(tables, fn)` takes the write lock before mutations. `View(tables, fn)` is a deferred read transaction under WAL; Put and Delete reject writes inside it. Only listed tables are accessible. Observations use View; an actual pin repair uses Tx. Neither transaction may span daemon calls, git commands or process spawns. History is append-only. Evidence: `internal/store/store.go`, including WAL, busy timeout and transaction scope checks.

```js
Table = { name, owner: unitId, key: "id", version: 1, append_only? }
Tx = (tables: [name], fn: (t) => error) => error
// t.Get, t.Put, t.Delete, t.All operate only on declared transaction tables.
```

The original target declaration also carried `migrate: {0: migration}` callbacks by version. Current declarations reject incompatible metadata and application migration lives outside this Table shape. Whether to adopt declarative per-table callbacks or retain explicit application migrations remains [B-70](../todo/architecture.md#b-70); the target field is not silently claimed implemented.

<a id="bus"></a>
## Command bus

The bus is a synchronous dispatch table, not a queue. Mutations have `unit.verb` names and JSON payloads. TUI, concept-oriented CLI and MCP dispatch to the same handlers. A result has status, data and optional structured error code/message. Handlers run without the bus registry lock and synchronize their own mutable state. RegisterRead observations do not generate command history. Each dispatch logs name, argument hash, duration and error code, not private argument bodies. Mutation history carries identifiers rather than prompts or captured output. Evidence: `internal/bus/bus.go`.

```js
Command = { name: "unit.verb", args: {} }
Result = { status, data, error?: { code, message } }
Bus = { register(name, Handler), call(Command), list() }
```

<a id="events"></a>
## Events

`core.Event` has seq, type, source, session, window, boot_id, ids, at and JSON-compatible data. The typed envelope does not imply typed payloads: Data is currently `map[string]any`. Published events and their maps are immutable.

`events.Runner` maintains one daemon subscription, resumes with after_seq and boot_id, and has bounded 256-entry handler queues. Each handler has its own worker. Subscription, gap and overflow trigger Resync. Local mtm events never go to the daemon. Each shell gets a bounded tap that survives reconnect; a slow shell receives recent notifications. Shutdown drains queued work and locally emitted follow-on events. Evidence: `internal/core/core.go`, `internal/events/runner.go`.

```js
Handler = { Types(): [type], Handle(ctx, event), Resync(ctx, bootID), Close?() }
Tap = chan Event // one per shell; does not close merely because the daemon reconnects
```

<a id="registry"></a>
## Registry

Definitions include Page, Action, PaletteCommand, Modal, Grouping, Form and Feature. Units write definitions at registration; shells read them. Page contains id, key, title, unit, rail/detail source names, keys, help, tick and scoped. PaletteCommand contains id, group, label, hint, optional key and a bus Command. Grouping names ordered levels. Modal names kind, source and replacement modal or command on pick. Form owns Fields and one submit command. [Forms](forms.md) owns the complete Field contract.

Page.key is the sole declaration of page letters and derives a normal-mode action. Action.does is prose; Action.command names the bus mutation or is empty for shell-handled operations. Effective keys use config override then default. Duplicate page letters or same-mode default bindings fail registry checks. Generated `mtm docs`, `mtm commands`, `mtm list-actions`, catalogs and config init are not a substitute for [source documentation](delivery.md#sourcereview). `Status(id)` review gating is a [B-22 target](../todo/delivery.md#b-22), not completed registry behavior.

Page subsections are now owner-reported implemented and verified in e4cf07a. Each declares id/title/rail/detail/keys/help/scoped/tick; [ and ] switch subsections with independent selection, filters, scope and scroll. Reads are lazy and bound to the originating page/section request; only live subsections opt into ticks. Git/GitHub network inventories refresh explicitly rather than periodically. This scoped completion does not close Features gating or the phase2 page-per-unit target. [Owner evidence](delivery.md#effortpolicy).

Relationships: Page belongs to Unit; PaletteCommand has one Command; Form has many Fields and one submit Command; Modal has one source and may replace another Modal. Catalogs derive from registered kinds; picking a kind replaces the one current modal. Help and every list/picker support filtering. Help includes mode tabs and unbound actions rather than a second hand-maintained binding list.

<a id="coreconfig"></a>
## Core, config and scopes

Core owns IDs, millisecond timestamps, decoding, Event, Scope, ScopeSet and shared Provenance. Config owns `~/.config/matomeru/config`, effective key bindings and settings defaults. Config files are not the mutable settings database. Defaults include repository roots, stale duration and section/key values; application settings never rewrite those defaults.

The complete leaf provides shared slash-command and @-path completion to shells. The focus leaf provides an idle/activity clock; a full focus mode remains deferred rather than implied by that clock.

`Scope = {task_id, project_id}`. Work resolves the task subtree once into ScopeSet. Membership performs no I/O. Empty Scope means all. Registered reads receive scope explicitly; a scoped read excludes unassigned rows. The persisted active pin is one row per database shared across processes, not one per tuios session. CLI unqualified reads are all-mode reads. [Work](work.md) owns hierarchy, ownership and pin semantics. Evidence: `internal/core/core.go`, `internal/config/config.go`, `internal/work/scope.go`.

<a id="flows"></a>
## Cross-unit flows

Current baseline: start form → prompts.start-agent → daemon start-agent → work assignment → assignments.changed → shell reread. Turn end reaches history and autocapture through the runner, then reviews rereads completed turns. Closing a pane reconciles successful snapshots before pruning assignments. Pin changes update active and reread scope-mode pages; all-mode pages keep all rows. CLI task patches use the same bus and emit tasks.changed.

Target Place flows remain [work/code work](../todo/work.md#b-48), not shipped behavior: resolve task→parent→project Place; warn from WorktreeUse before starting another agent; prepend claims, dirty blame and branch context; record code messages under the sender task; broadcast heads-up before rebase. Turn or command completion refreshes worktree status and attributes dirty changes, commits and HEAD moves. A rewrite matches old commits by patch ID and retains superseded_by links. PR and CI refresh follow the branch. [Shared places](work.md#sharedplaces) owns claims and human-terminal delivery.

<a id="b-28"></a>
## B-28 Provenance baseline

Status: partial. `core.Provenance = {turn_id?, session?, window?, task_id?, project_id?, commit?, branch?, pr_url?, at}` is filled at write time by `internal/provenance`. Pane identity comes from TUIOS_SESSION and TUIOS_PANE_ID; assignment and open turn are supplied by registered lookups. The turn ID is the prompt history ID. Task-notification prompts do not open a new turn; post-turn writes retain pane ownership without inventing a turn.

History entries, context, notes, todos, captures' private metadata, reviews/marks, recorded commits and PRs carry provenance. `code.record-commit` records HEAD explicitly; `code.record-pr` derives ownership from the pane or newest branch commit. `mtm code trace --json '{"id":"…"}'` traces PR→commit→turn→pane→task→project and accepts supported row IDs, commit prefixes and ownership IDs. FROM blocks on context/history/capture/todo details are text, not jumps. Action items and schedule runs do not yet share the complete shape. [Remaining acceptance](../todo/architecture.md#b-28) preserves automatic attribution, document consistency and navigation gaps.

Evidence: `internal/core/provenance.go`, `internal/provenance/provenance.go`, `internal/history/code.go`, commit 322c11c. The [original B-28 notes](../sources/znbu/docs/todo.md) record `/root/proj/night/logs/lane-4-B-28.log`; this consolidation did not run it.

<a id="server"></a>
## Server target

Current CLI and TUI processes open the same database. View removes read-side write contention but does not create a single writer. The proposed long-lived server would own storage, daemon subscription and mail routing; TUI and CLI become Unix-socket clients and never open storage. This is an unresolved structural choice, not an implementation claim. [B-70](../todo/architecture.md#b-70) retains it.

<a id="unitpages"></a>
## Phase 2 unit pages

Target: every unit registers a page, scoped with S, all-mode read-only except Assign; page order follows unit ID without shell edits. Notes, reminders, prompts, Vim and panes retain their proposed management actions. [Knowledge unit notes](knowledge.md#unitnotes) preserves UnitModal, Struct, Relation, UnitNote and UnitPrompt shapes and notes→prompt→turn correlation. [Agents unit prompts](agents.md#unitprompts) owns queue management. Unfinished work is [B-90](../todo/knowledge.md#b-90), [B-91](../todo/knowledge.md#b-91), [B-64](../todo/agents.md#b-64) and [B-75 reminders](../todo/automation.md#b-75). Web remains deferred as a shell over bus/registry, not a second domain implementation.

<a id="eventloop"></a>
## Event-loop target decisions

The [original Bubble Tea comparison](../sources/znbu/docs/outline.md) was read against tuios's Bubble Tea v2.0.8, not Rust/ratatui herdr. Keep one model, Init/Update/View and rearmed commands per channel. Keep mutually exclusive modes, not more ShowX booleans. Help/focus/live gates have fixed priority. One modal plus one parked modal is sufficient until a real third layer requires an explicit stack. Every registered modal must be drawable and routable. Key and paste routing must stay equivalent; Escape may clear a notice without consuming the owner's key. Retain one post-handler settle point, not independent hooks per handler.

Targets still requiring decisions: earliest-deadline timer across detail/worktree/PR/reminder jobs, recoverable per-message panic handling, optional mouse support. Current detail refresh uses a thirty-second tick, not the old note's one-second tick. Mouse design records Hit rectangles during View and dispatches by z order in Update. Begin with clicks/wheel only and forward live-pane input through daemon commands; motion filtering is unnecessary until hover exists. Frame caching and a shared ProgramOptions abstraction are not required by the single-program architecture. [B-74](../todo/architecture.md#b-74) owns these decisions.

<a id="migration"></a>
## Migration record

The original sequence was: remove web; extract core helpers; move pruning; register definitions; derive pages; unify modal/source routing; introduce per-table Tx and append-only history; add bus/generated CLI; share panes snapshot; move wiring/reminder lifecycle to cmd. Its named gates were e2e-all without web, e2e.sh, help/palette, forms/stash, all storage suites, e2e-cli, history/review and final e2e-all respectively. Existing packages establish much of that structure, not proof that every old gate was run here. Remaining composition-root and server decisions stay in B-70. [Delivery](delivery.md) owns verification policy.

<a id="decisions"></a>
## Decision register

Resolved baseline: unit.verb names; SQLite only; explicit scoped reads; shared database pin; work-owned theme pool with random unused then least-used selection; shared daemon pane snapshot; mtm-owned Vim files; reminders' cancellable scheduler; typed envelope with map payload; local daemon host relay. Original alternatives are preserved in the [source outline](../sources/znbu/docs/outline.md).

Unresolved or newly requested alternatives: server ownership and payload typing in [B-70](../todo/architecture.md#b-70); remote git transport, worktree creation versus listing and dirty attribution in [B-48](../todo/work.md#b-48); shared-place human delivery and overlapping-claim warning versus refusal in [B-02](../todo/work.md#b-02); optional Neovim input engine in [forms todo](../todo/forms.md); mouse/deadline policy in B-74. Current relay behavior is [panes hosts](panes.md#daemon). The current shared text engine does not close the later optional Neovim proposal.
