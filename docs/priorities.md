# Unfinished work and value-first priorities

This is a recommendation based on the current [outline](outline.md), [canonical todo](todo.md), all ten outline/todo concept pairs, and the [source map](source-map.json). It is not a new implementation audit or a commitment to dates. Existing statuses, acceptance criteria and owners remain authoritative in the linked concept documents.

There are **39 unfinished Matomeru items** and **18 separate ecosystem groups with remaining work or decisions**. The optional third B-35 stuck-pane rule is listed separately, not reopened as mandatory work. EXT-001 through EXT-006 route to B-41 through B-45 and are not counted twice; B-42 and B-43 remain open while B-41, B-44, and B-45 are complete. Implemented and superseded work is excluded.

## Recommendation

Start with repeated interaction friction, then work on the shared creation workflow and trustworthy agent outcomes. Do not start with an embedded editor, a whole-app restyle, or the full Inventory designer if the goal is useful results quickly.

**[INFERENCE]** All value rankings and effort estimates below are judgments from documented scope, not measured development times. S means a bounded change to an existing workflow; M means coordinated state/UI work; L means a cross-cutting feature or substantial design decisions. Dependencies and real-code inspection can change the estimate. Old p1/p2 labels are preserved in source docs, but do not determine this order.

### Remaining small outcomes

The [B-27 downloads directory setting](todo/knowledge.md#b-27) and [B-92 saved-editor forget command](todo/knowledge.md#b-92) remain small independent outcomes. Neither closes its entire parent item: download notes depend on B-05, and rich editor Place support depends on B-48.

### Completed quick wins

The previous recommendation is retained here as history, not active work. [B-41 explicit page tab](outline/panes.md#b-41), [B-45 close-time completion](outline/panes.md#b-45), [B-44 continuous tree editing](outline/work.md#b-44), [B-08 rail budgets](outline/panes.md#b-08), [B-13 complete import](outline/work.md#b-13), and [B-40 deduplicated full suite](outline/delivery.md#b-40) are implemented. Their outlines retain acceptance, provenance, and recorded real VPS evidence. Intended-store import follows the documentation snapshot and is not claimed as already performed here.

### Important remaining work


| Priority | Outcome | Value and sequencing |
|---|---|---|
| High product priority | [B-33: common verbs and nested creation palette](todo/forms.md#b-33) | Directly addresses discoverability and repeated form navigation. Full scope is L, not a label rename: shared commands, both navigation routes, back/filter preservation, directories and width acceptance. Resolve create/new wording and agent-choice order before implementing those branches. |
| High reliability priority | [B-63: truthful queue and dispatch outcomes](todo/agents.md#b-63) | Makes it clear whether a prompt is waiting, delivered, blocked, failed or unknown. Retains identity after partial failure and avoids duplicate launches. Do this before relying on more unattended automation; coordinate B-60's queue visibility rather than build a duplicate status model. |
| High repeated-use value | [B-42: grouped choices, recent selections and sparse presets](todo/agents.md#b-42) | Reduces repeated launch setup. Decide group/layer semantics once; existing fill-empty defaults do not implement ordered overwrite layers. This shares form work with B-33 but is not wholly dependent on finishing the palette. |
| High information value | [B-32: recorded preset questions and answers](todo/agents.md#b-32) | Makes prompts and answers retrievable instead of losing them in panes. Recording covers ordinary preset-bearing sends as well as ask. Needs reliable delivered-turn correlation. |
| Strategic design, then implementation | [B-100: Inventory, universal pins/stars and designer](todo/inventory.md#b-100) | Important to the product direction, but the whole feature is L. First settle shared identity and relationship boundaries; then deliver universal pinning and starring on that model. Do not equate existing task/project pinning with this requirement. Designer and broad type coverage stay in scope, not declared done by an early increment. |
| Cross-cutting information model | [B-05: notes on records](todo/knowledge.md#b-05) | High reuse across pages, but migration and ownership make it L. Align owner identity with Inventory rather than make a second incompatible record-reference model. The dedicated Notes page is not a prerequisite. |

If active remote work is a daily dependency, raise B-50's evidence check before expanding remote workflows. If unattended scheduled agents are used daily, raise B-20 turn-lifetime supervision alongside B-63. If Linear is used daily and access exists, B-19 becomes a relatively bounded integration candidate. Those conditions were not established by this document review.

### Verify before assuming more code is needed

- [B-31](todo/forms.md#b-31): exercise the original 80/200-column form acceptance. Keep its separate B-34 catalog dependency open. Do not rebuild the already-shipped forms/composer/defaults.
- [B-46](todo/work.md#b-46): decide current-cwd versus successful-launch frequency, then close the applicable picker evidence gap. Linux cannot establish macOS picker behavior.
- [B-49](todo/panes.md#b-49): run the six actual-preview scenarios and record any failures before estimating missing implementation.
- [B-50](todo/panes.md#b-50): prove remote terminals and host-qualified references, not just one successful remote agent launch.
- [B-26](todo/delivery.md#b-26): inspect publication evidence. This is not permission to tag or publish a release.

These checks can run independently of unrelated quick wins. Failed acceptance can move a reliability fix ahead of feature work.

### Large investments to sequence deliberately

B-23 embedded Neovim, B-29 whole-app design pass, B-36 multiple palette styles, B-48 full Place/Git attribution, B-02 shared-place collaboration, B-34 complete AI asset catalog, B-90/B-64 unit-meta workflows and the full B-100 designer remain valuable backlog. None should be sold as a quick win. B-36 follows the shared B-33 engine; B-02 depends on Place/delivery decisions; B-90/B-64 require coordinated note/prompt lifecycle. Do not build an application-server rewrite merely to clear an open architecture decision.

## Complete unfinished Matomeru list

Each row summarizes remaining scope; its link retains the full acceptance criteria. Partial means some behavior is already implemented. Verification-pending means the docs lack complete evidence, not that the feature is absent. Effort is an inferred estimate for the whole remaining item unless qualified.

### Panes

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-49](todo/panes.md#b-49) | verification-pending | Establish all noninterfering terminal/agent/Vim preview scenarios, stale/cached/error states, race handling, escape safety and unchanged target/input/dimensions. | M check; implementation unknown |
| [B-50](todo/panes.md#b-50) | verification-pending | Establish complete remote-terminal inventory and host identity through every stored/routed reference; prove stale-host recovery without incorrect pruning. | M check; implementation unknown |

### Work

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-02](todo/work.md#b-02) | open | Persistent shared-place claims/messages, peer routing, launch context and overlap warnings; depends on Place and unresolved server/delivery decisions. | L |
| [B-43](todo/work.md#b-43) | open | Dedicated Projects page with know/do/make/share and actual research at three answer depths, retained with its project. | L |
| [B-46](todo/work.md#b-46) | partial | Resolve current-cwd versus successful-launch frequency and explain the ranking; obtain platform-specific native-picker evidence where required. | S decision/evidence; chosen change may grow |
| [B-48](todo/work.md#b-48) | open | Full host-qualified multi-directory Place model, inherited launch location, observed Git/dirty blame/HEAD rewrites, branch/task/PR links and warnings. | L |

### Forms

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-23](todo/forms.md#b-23) | open | Optional embedded Neovim field editor, isolated buffers/undo, acknowledged rendering, bounded lifecycle/recovery and effective bindings. | L |
| [B-29](todo/forms.md#b-29) | open | Per-page design notes, agreed UI changes and before/after evidence across every page/modal; dispose research alternatives explicitly. | L for every-page notes, changes, and screenshots |
| [B-31](todo/forms.md#b-31) | partial | Prove form rendering at 80/200 columns; complete catalog-backed completion after B-34. Existing form redesign and composer are not pending rebuilds. | S evidence; catalog-dependent integration separate |
| [B-33](todo/forms.md#b-33) | open | Common create/new/edit/delete verbs plus nested verb-first and object-first palette routes, prefix/back/filter behavior, creation choices and width acceptance. | L for complete expanded acceptance |
| [B-36](todo/forms.md#b-36) | open | Several interchangeable palette presentations over one shared engine, selected in Settings; follows B-33. | M |
| [B-60](todo/forms.md#b-60) | open | Complete cross-domain UI-state matrix: simultaneous flags, reasons, ownership, queue/errors, histories, connection states and explicit entering/clearing behavior. | L |

### Agents

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-14](todo/agents.md#b-14) | open | Harvest offline MCP calls, normalize/catalog/template them and provide parameterized replay; retain safe source and result provenance. | L |
| [B-32](todo/agents.md#b-32) | partial | Rich prepend/append presets, record every preset-bearing delivered prompt, correlate answers and provide Questions page/CLI. | M |
| [B-34](todo/agents.md#b-34) | partial | Complete per-harness disk/config/plugin asset catalog, scanner schemas/provenance, symlinks and cross-harness navigation/search; existing AI subsections remain shipped. | L |
| [B-42](todo/agents.md#b-42) | open | Cohesive field-group choices, recent selections and ordered sparse preset layers with overwrite semantics; settle names/group-layer interaction. | M |
| [B-63](todo/agents.md#b-63) | open | Durable inspectable queue/delivery outcomes, correct counts/correlation and retained partial-failure target/draft identity; never infer delivery from disappearance. | M |
| [B-64](todo/agents.md#b-64) | open | Unit-note-generated prompts, scoped Prompts page, persisted dispatch/turn correlation and note completion/reopen lifecycle; coordinates with B-90. | L |

### Knowledge

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-05](todo/knowledge.md#b-05) | partial | Generic record-owned notes, migration, inherited ownership, detail CRUD and rail indicators across all requested record kinds. | L |
| [B-27](todo/knowledge.md#b-27) | partial | Expose downloads.dir in Settings, settle shared unread styling and add download-owned notes through B-05. | S for directory/theme completion; full closure depends on L B-05 |
| [B-90](todo/knowledge.md#b-90) | open | Per-unit shape/notes/prompts modal, generated relationships and unit-note CRUD/reopen/review lifecycle; coordinate prompt lifecycle with B-64. | L |
| [B-91](todo/knowledge.md#b-91) | open | Dedicated Notes and Vim pages with documented actions, scoped ordering and ALL restrictions. | M |
| [B-92](todo/knowledge.md#b-92) | partial | Saved-editor forget operation and remaining host/worktree-aware Place contract; managed Neovim panes already exist. | S for vim.forget; M for Place integration after its shared design exists |

### Inventory

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-100](todo/inventory.md#b-100) | open | First-class Inventory kinds/identity/owned children/shared links; composed or aliased primitives and user-defined designer; universal pins AND stars; contextual pinning remains optional. | L |

### Architecture

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-28](todo/architecture.md#b-28) | partial | Complete cross-record provenance, automatic commit/PR association, navigable FROM/trace and one end-to-end ownership chain. | L |
| [B-70](todo/architecture.md#b-70) | open | Resolve server/process ownership, typed payloads, migration/provider choices; move attention construction to composition root without speculative server rewrite. | M |
| [B-74](todo/architecture.md#b-74) | open | Resolve remaining event-loop recovery, timer noninterference and mouse-interaction policies and their acceptance. | L |

### Automation

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-16](todo/automation.md#b-16) | partial | Slack context ownership/permalinks, authenticated live acceptance and subsequent replay-based scheduled checks; fixtures are not live proof. | L |
| [B-19](todo/automation.md#b-19) | open | Linear issue lookup and deduplicated action items, including settings, errors and live integration acceptance. | S |
| [B-20](todo/automation.md#b-20) | partial | Supervise the actual scheduled agent turn through timeout/completion, not just dispatch; complete linked PR-review/report chaining. | M |
| [B-75](todo/automation.md#b-75) | open | Dedicated phase-2 Reminders management page and its actions/state; existing scheduler is not the missing feature. | M |
| [B-77](todo/automation.md#b-77) | open | Decide remaining MCP survey API proposals; do not treat optional proposals as implemented or mandatory integrations. | M |

### Delivery

| Item | Documented status | Remaining work | Effort |
|---|---|---|---|
| [B-22](todo/delivery.md#b-22) | partial | Feature inventory regeneration hook, runtime docs coverage, verdict ownership, Features page and keep/cut/status gating. | L |
| [B-26](todo/delivery.md#b-26) | verification-pending | Establish remote release/tag evidence and authorized publication acceptance; existing release machinery is not missing, and this assessment authorizes no release. | S |
| [B-39](todo/delivery.md#b-39) | open | Isolated bounded-concurrency E2E runner, aggregate every result, failure counts and demonstrated full-suite timing. | M |
| [B-71](todo/delivery.md#b-71) | open | Validate existing source-doc tools against real public/private/interface examples and compiler compatibility before adopting or building custom views. | S |
| [B-72](todo/delivery.md#b-72) | open | Choose/dispose completed TUI research recommendations; research is already done, adoption and unresolved decisions remain. | S |
| [B-73](todo/delivery.md#b-73) | partial | Finish all seven VPS development-host steps: platform actions, branch round-trip, real attached task, concurrent-load evidence, orphan cleanup, flake burn-down and auth policy. | L |
| [B-76](todo/delivery.md#b-76) | partial | Choose supported capture adapters and verify distributed-binary install/reinstall/status/owned-only uninstall plus delivered-request-to-final-answer capture. | M |

### Optional unimplemented decision outside the active count

[B-35's third repeat-failure rule](outline/automation.md#b-35) was explicitly optional and omitted. Decide whether detecting the same file/tool command failing three times is worth adding; the two existing stuck-pane rules stay implemented. This does not reopen the superseded fleet orchestrator.

### Inventory requirements added after its original todo checklist

The [Inventory outline](outline/inventory.md) is newer than B-100's detailed checklist. All of these belong to the unfinished B-100 scope:

- Every named inventory kind, with provider identity, todo items versus tasks, and the temporal examples retained.
- Owned children versus reusable shared links; one file/directory can serve multiple contexts without copies.
- Composed types and single-primitive aliases built from note, file, dir and address; reference remains a candidate.
- A user-facing inventory designer and creation of user-defined inventory items.
- Every built-in and user-defined item supports both pinning and starring.
- Contextual pinning is an optional proposal. Page type versus project/page instance is undecided; contextual starring was not requested.

## Separate ecosystem backlog

These 18 groups belong to adjacent Ima/Now/Thinktank/pstack/mdoc ideas or unresolved adoption decisions. Their presence is not approval to implement them in Matomeru. Effort for an adoption decision is not an estimate for building the entire associated product.

| Group | Documented status | What remains |
|---|---|---|
| [EXT-007: Central funnel and the task-as-now product purpose](todo/ecosystem.md#ext-007) | idea | Choose whether any central funnel/one-small-task completion workflow belongs in Matomeru. If pursued, show pick-finish-return and finishing-driven rather than timer-only switching, without permission/priority gates. Personal ambitions remain context, not acceptance imposed on a person. |
| [EXT-008: TUI, optional exact-parity web UI, and optional multiplexer](todo/ecosystem.md#ext-008) | idea | Decide whether web is pursued; only if chosen, require identical TUI/web actions and transitions. Compare launch/input-output capture with a new multiplexer, retaining no-new-multiplexer, herdr and tuios options and Go/Charm preference. Record exceptions to one abstraction level at a time. |
| [EXT-009: Generic selector and typed items with metadata](todo/ecosystem.md#ext-009) | idea | Choose shared selector independently from a universal typed item model. If adopted, retain type filters, distinct Now/Items/Noise scopes and parent-child/extraction links; do not replace Matomeru domain tables by implication. |
| [EXT-010: Attribute actions rather than prohibit activity](todo/ecosystem.md#ext-010) | idea | Define externally observed ask/run/write/read/split events with task, time and relevant pane identity. Choose no-active-task handling, preserving create-and-activate as an option rather than an implicit blocker. Demonstrate arbitrary external attribution separately from completed app-launched links; never gate when or why someone works. |
| [EXT-011: Time, effort, attention, context, event history, and task kinds](todo/ecosystem.md#ext-011) | idea | Select an actual use case before defining human time/effort/attention/context relationships or adopting raw event logs. Keep the incomplete flexibility complaint unresolved. Route dedicated to-know lifecycle to EXT-019 and writing interaction to EXT-020, not duplicate features here. |
| [EXT-013: Picker, one-task Now view, split/finish loop, and completion review](todo/ecosystem.md#ext-013) | source-reported-completed-with-open-decision | Only if reconsidering picker order, choose proposed smallest-first/oldest-first versus reported oldest-first open leaves. Do not relabel size ranking as shipped. |
| [EXT-014: Task-dependent whole-app theme](todo/ecosystem.md#ext-014) | source-reported-completed-with-open-decision | Decide whether starting Now announces active-task identity to tuios agents and allows addressed mail; establish it separately if adopted. |
| [EXT-016: Learn-for-later runs and locked motivations](todo/ecosystem.md#ext-016) | idea | Explicitly choose strict no-work-until-later versus logged conscious early promotion, preserving the stricter user request and final no-pickable-today suggestion. For the chosen policy establish a learn-about-X-for-Y run yielding linked title/why/unlock-time motivation items, Later read behavior and pre-unlock activation rules. |
| [EXT-018: Domain vocabulary and distinct concept levels](todo/ecosystem.md#ext-018) | idea | Map Git, GitHub, terminal, task/context, shell and AI terms to the relevant domains if adopted. Keep Git/GitHub repositories, terminal/agent sessions and pane/task concepts distinct, preserving original misspellings only as source links. |
| [EXT-019: Dedicated to-know questions and answers](todo/ecosystem.md#ext-019) | idea | Define question/answer/state lifecycle and completion meaning, then support storing/retrieving them. Keep separate from Matomeru B-43 research-depth work. |
| [EXT-020: Projects, documentation encouragement, and automation decisions remain open](todo/ecosystem.md#ext-020) | idea | Decide if first-class projects add value beyond cwd/parent tasks; do not import Matomeru B-43. Choose an actual documentation/writing encouragement interaction. Decide whether tuios/herdr integration needs additional multiplexer behavior, sharing EXT-008's decision. Decide whether to automate clipboard/pane capture; manual source labels do not prove automatic intake. |
| [EXT-021: Task context pointers and terminal focus](todo/ecosystem.md#ext-021) | idea | Choose session/window/pane/cwd pointer shape, first-activity recording and focus-versus-spawn behavior. If adopted, restore/create selected workspace and title without pane-equals-task semantics or per-pane productivity metrics; keep Now's no-pane-list design separate from Matomeru. |
| [EXT-022: External prompt/reply attribution and tuios event intake](todo/ecosystem.md#ext-022) | idea | Select tuios prompt/command-start/command-finish/agent-state/agent-activity/notification/attention events and prompt/tool/result/turn-end subtypes and their activity/attribution/noise mappings. Preserve external prompt/reply task and pane identity; capture mail/pane output with source references, treating mail as data not instructions. Establish working-pane nudges without counting background refresh as user activity; do not reopen already-completed generic CLI touches/hidden-pane nudges. |
| [EXT-023: Automatic agent follow-up child tasks without spinner babysitting](todo/ecosystem.md#ext-023) | idea | Choose active-task inline versus inactive-task read-reply/answer-agent child behavior for done and needs-input. Handle fan-out with separate small children linked to correct parent and pane; do not infer Slack/PR task meaning automatically. Share no-active-task prompt handling with EXT-010 without introducing permission gates. |
| [EXT-024: Context matchers attach metadata from streams and events](todo/ecosystem.md#ext-024) | idea | Choose source streams/events, matching rules, syntax, metadata schema and Context-to-ContextMatcher relationship. Explicitly resolve duplicate NewTerminal and incomplete initialization without rewriting the authoritative source into an agreed schema. If adopted, show matching prompts/responses/stdin/stdout/stderr/events attaching specified metadata. |
| [EXT-025: Concise task/action/change walkthrough](todo/ecosystem.md#ext-025) | idea | Choose trigger, explanation granularity and output format. If adopted, explain task/action/change and why concisely so the owner can direct outcomes without raw tool-call dumps; do not invent damaged source text. |
| [EXT-030: Standalone executable and release distribution backlog](todo/ecosystem.md#ext-030) | idea | Preserve/rebuild current macOS arm64 executable outside /tmp and record repeatable repository build/release workflow; historical artifact predates later plugin/navigation work. Choose license, dependency notices, supported OS/architectures and macOS signing/notarization policy before redistribution. Exercise selected platforms separately, address Mac open calls on Linux and document optional gh/h-mcp/agent CLIs/credentials as unbundled dependencies. Distinguish published source from packaged releases; publish artifacts only when requested. |
| [EXT-032: Slack via h-mcp and alternate server providers](todo/ecosystem.md#ext-032) | idea | Use an available authenticated slack/slack-no-dms/Glean/Runlayer provider to discover the actual tool and argument schema, recording selection/overrides rather than guessed candidates. Establish real message/thread lookup, permalink/source references, structured/text normalization and repeat-poll dedupe. For Glean establish owner handle/app:slack query requirements. Keep missing-catalog/fake-server results separate from live evidence and do not revert to superseded direct-token Slack transport. |

EXT-001–EXT-006 are already owned by B-41–B-45. Source-reported completed or historical groups are not active work; EXT-013 and EXT-014 retain only their open decisions. Optional future products are not prerequisites for the Matomeru sequence above.

## Completion and evidence rules

A small outcome under a broad item does not close that item. Keep untouched acceptance open and link shipped behavior into the outline. No product code was inspected or executed for this assessment; status comes from the canonical docs. Before implementing an item, check current code and coordinate its owner so newer work is not rebuilt. Validate changed behavior on vps2, using platform-specific evidence where required.
