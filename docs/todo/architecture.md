# Architecture remaining work

See [architecture](../outline/architecture.md) for current behavior and target rationale. Historical acceptance remains in the [original backlog](../sources/znbu/docs/todo.md) and [outline](../sources/znbu/docs/outline.md).

<a id="b-28"></a>
## B-28 Complete cross-record provenance

Status: partial · priority: p1 · size: M.

[Implemented baseline and evidence](../outline/architecture.md#b-28).

- Add the shared provenance shape to ActionItem and Schedule run rows. Keep downloads exempt because they have no turn.
- A document reported through document_report and context extracted from the same turn must have identical turn_id, task_id and project_id. Expose document provenance consistently.
- Establish automatic association for a commit made inside an agent turn and a PR opened from that branch, not merely explicit record-commit/record-pr fixtures. Code list must show the turn/task and PR ownership.
- Provide the promised bare `mtm trace <id>` entry point, or explicitly decide its replacement. Each FROM line must navigate to its turn, pane, task/project, commit or PR.
- The provenance end-to-end case must assert every applicable table after one scripted turn and retain valid PR→commits→turn→task→project chains. Historical coverage of some tables does not close all tables.

<a id="b-70"></a>
## B-70 Settle process ownership and remaining architecture choices

Status: open · priority: p2. [Server target](../outline/architecture.md#server), [decision register](../outline/architecture.md#decisions).

- Decide whether a single long-lived Unix-socket server owns storage, daemon subscriptions and agent mail, with no database access by TUI/CLI clients. Retain the current multi-process View/Tx design as the baseline, not proof of single-writer ownership.
- Complete composition-root migration by moving attention-unit construction/lifecycle from reminders/attach to cmd/mtm wiring. Preserve producer shutdown, event drain and history flush ordering.
- Decide whether typed event payloads are needed beyond the current typed envelope/map data. Do not describe current map payloads as typed variants.
- Settle the original PR-provider choice: gh only for the first build, or a provider interface with GitHub first. Existing gh monitoring is not evidence of a provider abstraction.
- Settle per-table versioned migrate callbacks from the original Table shape versus explicit application migrations. Preserve version/owner/key/append-only migration checks whichever design is chosen.
- Keep remote-host transport, theme ownership, pane snapshot and pin decisions explicit. Reopen only with a recorded requirement; rich Place/remote git and overlap-policy decisions remain [B-48](work.md#b-48)/[B-02](work.md#b-02) rather than duplicating acceptance here.
- Deferred web shell must reuse bus and registry if reinstated. Focus mode remains deferred with its original rules in the old deck TODO, not implemented by this consolidation.

<a id="b-74"></a>
## B-74 Settle event-loop resilience, timers and mouse interaction

Status: open · priority: p3. [Design constraints](../outline/architecture.md#eventloop).

- Choose earliest-deadline scheduling over detail/worktree/PR/reminder jobs or retain independent unit ticks with an explicit rationale.
- Decide per-message panic recovery: retain the model and show a visible error instead of exiting. Do not claim recovery before actual evidence exists.
- Check every registered modal is drawable/routable and paste follows key ownership. Preserve one modal plus one parked modal until a third layer justifies one stack.
- Decide keyboard-only versus clicks/wheel. If mouse is adopted, View records per-frame Hit rectangles with kind/x/y/z/w/h and row bounds; Update chooses the highest-z containing hit. Outside-click dismissal follows modal order. Begin with rail selection, tabs, detail scrolling and palette rows; live pane clicks forward through send-keys. Add motion filtering only for an actual hover feature.
- Escape notice dismissal must not consume another mode's key. Verify interaction, ordering and stale-layout behavior on isolated real daemon scenarios, not unit tests.
