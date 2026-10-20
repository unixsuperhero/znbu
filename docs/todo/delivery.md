# Delivery remaining work

[Delivery outline](../outline/delivery.md) records current systems and evidence. A recorded old verification log is not a new run, and code presence does not prove publication or runtime acceptance. [Original backlog](../sources/znbu/docs/todo.md).

<a id="b-22"></a>
## B-22 Complete feature inventory adoption and in-app review

Status: partial, stage 1 only · priority: p2 · size: L.

[Implemented generator/repository marks](../outline/delivery.md#b-22).

- Add the pre-commit regeneration hook so inventory changes appear with feature changes. Retain deterministic sorted output across two runs and coverage of every registry kind, command, exported struct and explicit concept.
- Establish every inventory ID in generated `mtm docs`; do not infer that the external inventory generator already provides runtime docs coverage.
- Decide verdict ownership: per machine in the store, repository review.yaml, or both. Preserve hashes and changed/unreviewed meaning. Cut is a deletion backlog, not automatic code deletion.
- Add the features store and Status(id) gating: o/O skip cut groupings; help/palette skip cut commands; config init still emits every action. Keep code until an explicit deletion.
- Add the Features page grouped by kind with k keep, x cut, u unreview, ? feature help; choose a free page letter. Help and palette expose an unreviewed glyph.
- Preserve review acceptance: an empty review file lists every ID; marking cut removes it from unreviewed; modifying its defining text returns it as changed. Seed a cut grouping in an end-to-end check and prove o/O never displays it in the title line. Stage1 hash tests do not close this gate.

<a id="b-26"></a>
## B-26 Establish release publication evidence

Status: verification-pending · priority: p2 · size: S.

[Implemented release/changelog baseline and local tags](../outline/delivery.md#b-26). Publication remains the maintainer's decision, not an action authorized by this documentation task.

- Record read-only remote evidence for an intended release tag and its annotated message, matching the committed changelog/version. Existing local annotated mtm v0.5.0/v0.6.0/v0.6.1 tags do not prove `git ls-remote` acceptance or release-script execution.
- Keep the canonical later contract explicit: Matomeru/mtm identity; origin plus vps2; no proxy priming/update hint; dry-run writes nothing; explicit --changelog-prompt writes the prompt; missing-entry non-dry exits 1 and writes it. These replace the original deck/vps2-only/dry-run-writing draft, not silently omit it.
- When publication is explicitly authorized, retain original observable acceptance adapted to the agreed contract: refuse a missing changelog entry, preserve clean-main/preflight/build gates, create an annotated version tag and establish it on intended remotes. Report a partial two-remote publication honestly because atomicity is per remote.

<a id="b-39"></a>
## B-39 Parallel isolated end-to-end runner

Status: open · priority: p2 · size: M. [Current runner](../outline/delivery.md#b-39).

- Run shell/Python suites in separate processes and outline cases or small groups with their own daemon/database. Use a bounded pool around four workers on vps2; PTY load is a measured constraint, not a reason for a host-wide lock.
- Run everything even if a case fails. Print one aggregate PASS/FAIL table listing every suite and case with status and duration. Exit with the number of failures, not only a generic nonzero code.
- A full vps2 run must finish under three minutes; the original desired range was roughly 1.5–2 minutes versus the observed 7.5-minute baseline.
- Two cases creating the same project name must pass together without seeing each other's rows. Keep test daemons uniquely named and separate from existing sessions.

Implemented targeted iteration and deduplicated full-suite execution [B-40](../outline/delivery.md#b-40) live in the outline.

<a id="b-71"></a>
## B-71 Adopt source documentation only after compatibility review

Status: open · priority: p2. [Selection and full review criteria](../outline/delivery.md#sourcereview), [Go tool decision](../go-code-review.md).

- Exercise the free browser on panes.Pane, prompts.QueuedPrompt, a private type, a command package and an interface with implementations. Compare actual signatures, fields/tags/embedding, comments and source links against the current source.
- Record coverage of package/module browsing, private declarations, dependencies, implementations and usages, revision/build context, and every loader/type error. Missing comments remain missing. Do not substitute an older compiler merely to get a clean report.
- Start with pkgsite plus go doc; add Golds only when its extra relationships are correct on the pinned Go version. Use gomarkdoc if a committed diffable reference is wanted. A maintainer-documented capability is not a verified result here.
- Only confirmed remaining gaps permit a custom view, using go/packages, go/ast and go/types rather than regex type inference.
- Keep private source private, servers loopback-only, tunnels explicit and launchers finitely bounded. Do not auto-open a desktop browser or leave an unbounded server as a check.

<a id="b-72"></a>
## B-72 Decide how to adopt the completed TUI research

Status: open · priority: p2. [Completed B-03](../outline/delivery.md#b-03), [full samples](../research/tui-design-samples.md), [topic index](../research/tui-design-samples.outline.md).

The research deliverable is done. Choose/dispose the remaining recommendations against actual UI needs without turning all alternatives into mandatory implementation. Preserve the evidence gaps for exact assign approval, target-scrollback composer, unstable sample images and unavailable authoritative article. Link chosen patterns to [B-29's per-page design/restyle/screenshot acceptance](forms.md#b-29), [forms research](../outline/forms.md#research) and [visible-state work B-60](forms.md#b-60). The two-input composer and recent page subsections have their own scoped owner evidence; they do not establish the whole visual pass.

<a id="b-73"></a>
## B-73 Finish the seven-step second-development-host plan

Status: partial, historical tooling/login/protocol baseline only · priority: p2.

[Canonical plan with every step and dependency](../plans/vps2-dev-host.md), [delivery baseline](../outline/delivery.md#vpsplan). Remaining acceptance includes all seven original steps, not merely remote build support:

1. Add Linux clipboard/open/open-with fallbacks while preserving Mac behavior and fixture error contracts.
2. Establish branch round-trip evidence between host-owned branches and fast-forward-only main.
3. Complete one small real vps2 agent task through edit/verification/commit/push with the user attached at least once.
4. Measure two overlapping suites, record load and precise PTY failures, and choose a narrow workload response only if evidence requires it.
5. Sweep only orphaned named test daemons under dead mtm-e2e temporary directories after force-kill; never touch the host daemon.
6. Burn down each named authorization/turn-capture/shared-navigation flake with five consecutive affected-suite passes.
7. Retain per-machine logins as the default; reconsider a shared Mac auth proxy only for a third machine, with the original policy/terms concern explicit.

No acceptance was run for this consolidation. Historical unit-test commands remain quoted in the preserved plan; current work follows the project verification policy and does not add unit tests.

<a id="b-76"></a>
## B-76 Complete packaged setup and supported-harness capture acceptance

Status: partial · priority: p2. [OMP source baseline and full contract](../outline/delivery.md#setup).

- Establish the supported capture-adapter list. The current setup item is OMP only; MCP launch configuration for Claude/Codex/opencode is not itself full request-to-final-answer capture. Other supported adapters must follow the same terminal-turn and packaging contract rather than requiring a separate inbox installation or manual hook copying.
- For the supported set, retain real isolated acceptance from a distributed binary with no source checkout: install, repeated install, status for missing/modified/conflicting/migration-required files, owned-only uninstall and rejection of unowned files/symlinks. Reuse existing setup coverage and record its evidence rather than treating source checks as passes.
- Establish a delivered request through final answer in history/reviews after reload, with the selected executable/data path and no duplicate legacy activity reporter. Rerun setup when those paths change. Preserve unrelated harness settings and user files throughout.
