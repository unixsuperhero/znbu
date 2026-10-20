# Delivery, review and developer workflow

[Delivery todo](../todo/delivery.md) contains unfinished acceptance. This document distinguishes source inspection, earlier recorded verification and the concurrent implementation owner's reported checks. No application build, test, release or runtime check was run for this consolidation.

<a id="workflow"></a>
## Developer workflow

Matomeru owns implementation; znbu owns canonical product design and backlog. Use concept CLI commands instead of keystrokes or direct database writes. Discover payloads with `mtm commands` and `mtm help`; generated docs/actions/config share registry definitions. Units own domain logic; shells own presentation. Separate changing UI concerns from stable domain rules, and add an abstraction only when a second named use exists.

The implementation uses github.com/unixsuperhero/matomeru, Go 1.27.1, Bubble Tea v2 and Lip Gloss v2. Source build entry is `./cmd/mtm`. Default paths are `~/.local/share/matomeru/mtm.db`, its captures directory and `~/.config/matomeru/config`. Shared flags select socket, data, captures and autocapture. The earlier deck/redeck names in preserved notes are historical, not alternate commands.

Design every terminal page, rail, detail, modal, form and help area as a UI. Work is split by unit/page and commits follow completed verified steps. Conventional commits are used; no amending. Current implementation instructions select the OpenAI Codex model through the ChatGPT login rather than the upstream historical Anthropic defaults. This consolidation edits neither agent rules nor implementation code.

<a id="effortpolicy"></a>
## Minimum-effort policy and recent owner evidence

The implementation policy minimizes input: infer from focused records, scope, successful history and environment; offer editable defaults without overwriting an explicit choice. Paths retain fuzzy/manual entry and native pickers. Components may use different interaction styles. Page subsections do not depend on a two-pane layout, and Git/GitHub reuse canonical repositories/branches and ownership.

The concurrent owner reported five scoped features complete and verified in commits ec0d83a and e4cf07a: the policy, ranked directories, launch defaults, two-input fuzzy composer and AI/Git/GitHub subsections. Current `matomeru/docs/outline.md` describes those contracts. This replaces the earlier pending status only for that scope; it does not close all B-31 forms or B-34 agent/model ambitions. Owner-reported evidence includes run.8tnoOG3b composer, run.t7d5iNMS watched actions, run.uag5oacy TUI, run.0FUXkwfs AI and run.uMlaOO9N live GitHub, under `/root/proj/redeck-astra-verification/runs/`. The owner reported CLI, launch-default, all-five-layout, key/collision, header, provenance, SSH and real-100-PR checks. Those are not runs performed here. Native macOS picker behavior was not exercised on Linux and remains separate acceptance.

<a id="verification"></a>
## Verification baseline and safety

Builds and runtime verification use vps2 through `scripts/verify-vps.sh`, which copies current source including uncommitted edits into a fresh run.* snapshot. It excludes Git metadata, root binaries, database and environment files; newly required source directories must join its allowlist. Each run has separate compiler temporary files, layout/screen artifacts and verification.log; toolchains and caches are shared. Concurrent independent snapshots are allowed. Do not infer a host-wide lock from assumed resource limits.

Use only uniquely named throwaway tuios daemons. Never restart or mutate the host daemon or existing user sessions. Linux cannot prove macOS key handling, clipboard/open integration or native dialogs. Default outline runs include every case, so Linux native prerequisites are failures, not silently passed coverage. Report platform results separately. PTY scenarios wait for rendered mode/field and real capture-pane output; sleeps are not evidence. Shell fixtures replace provider inference, not terminal behavior.

MTM_VERIFY_TIMEOUT is a positive number of seconds. Use finite tool and remote deadlines; timeout exits 124 or 137 after the 15-second kill grace. More than 15 minutes requires a reason and explicit permission. SSH uses a 10-second connection timeout and server-alive checks. Evidence: implementation AGENTS.md and `scripts/verify-vps.sh`.

<a id="b-39"></a>
## B-39 Runner baseline

Status: open. `scripts/e2e-all.sh` prints status/time for each suite and existing suites isolate temporary data/daemons, but the runner is sequential and set -e stops after a failed suite. Outline cases share a harness run rather than four per-case workers. [Remaining acceptance](../todo/delivery.md#b-39) preserves per-case isolation, aggregate reporting and the under-three-minute goal.

<a id="b-40"></a>
## B-40 Targeted iteration and one final full suite

Status: implemented. `E2E_OUTLINE_CASES` selects only affected cases during iteration. The full runner invokes the outline suite once and no longer appends duplicate settings, palette search, MCP, actions, schedules, GitHub review/PR, Slack, tabs, create-jump, accordion, or rail-lifecycle invocations. Each outline case runs once in a full suite. The implementation AGENTS verification policy calls for one full suite at branch end before merge, not after every item. B-39 bounded parallelism and aggregate reporting remain separate unfinished work.

Recorded dispatcher evidence: `/root/proj/redeck-astra-verification/runs/run.neOHqj34/verification.log` compares the earlier 15 outline invocations and 67 dispatches for 53 unique cases with one invocation and 53 dispatches, each once. This predates the latest added cases. It proves dispatcher deduplication, not that every suite passes. The main agent owns the final full-suite run. This documentation task ran no local checks. [Original B-40 acceptance](../sources/znbu/docs/todo.md#b-40-verify-with-targeted-cases-while-working-one-full-suite-only-at-the-end) remains preserved.

Delivery verification stopped at the user’s explicit request after focused VPS proofs and Go vet passed. Broader runs exposed stale fixtures and reached their finite deadlines; no final all-green full-suite result is claimed. Native macOS picker selection remains unverified, with an explicit Linux skip rather than a pass.

<a id="b-22"></a>
## B-22 Feature inventory, stage 1

Status: partial. Stage 1 generates sorted `docs/inventory.json` from registry definitions, bus commands, exported Go structs and feature concept comments. Repository review marks compare defining-text hashes; no mark means unreviewed and a stale hash means changed. This is not the in-app Features page.

```js
Feature = { id, kind:"page"|"command"|"action"|"palette"|"modal"|"grouping"|"form"|"kind"|"feature"|"struct"|"concept",
  name, desc?, surfaces?, file, line, hash, fields?:[{name,type,doc?}] }
Mark = { [featureId]: {status:"keep"|"cut", on, hash, note?} }
```

IDs remain stable once written. Registry items come from the binary's own docs/commands/list-actions in an isolated home, using MTM_BIN or a fresh build. go/ast places source locations at declaring literals and extracts structs/comments; loop-generated entries may point at a nearby literal. This intentionally differs from the original runtime.Caller proposal. Struct IDs retain Go case, such as struct.store.Task, rather than silently lowercasing existing identities. YAML flow-style review.yaml is also JSON and needs no extra YAML dependency. Hashes cover defining text, not merely a symbol name. The concept marker shape is `// feature: concept.<area>.<name>`.

`go run ./scripts/inventory -review [-marks PATH]` lists unreviewed then changed. Evidence: `scripts/inventory/main.go`, `review.go`, committed inventory/review files, commit 9e7b76b. Recorded e2e-inventory checks deterministic output/review marks: `/root/proj/redeck-astra-verification/runs/run.wTMwj4fO/verification.log`. A regeneration hook, complete docs-ID coverage, verdict ownership, store-backed Status gating and in-app review remain [B-22](../todo/delivery.md#b-22).

<a id="b-26"></a>
## B-26 Changelog and release baseline

Status: verification-pending for publication acceptance. Changelog entries are newest first, one `## vX.Y.Z` plus date, with only changed concepts in this order: Store, CLI, Settings, Units, Pages, Modals, Forms, Actions and keybindings, Palette, Groupings, Rail and detail, Live mode, MCP, Events and recorders, Scripts and suites, Docs. Each change is one added/changed/removed/fixed line. Changed names now and before; removed names the replacement; fixed names the symptom. Use real names, help keys and functional defaults. Record a cross-concept change once and refer to it elsewhere. Derive entries from tag-to-HEAD log and diff, not a narrative.

`scripts/release.sh [patch|minor|major|vX.Y.Z] [--dry-run] [--changelog-prompt]` selects the newest semantic tag, or v0.0.0 if none. No source version constant is maintained. It requires a changelog entry, clean main and a nonexisting tag. It validates the real push destinations, including rewrites, permits only the Matomeru GitHub origin, preflights both origin and vps2 for ancestry/tag conflicts and atomic-push support, runs bounded build/vet/test through the VPS runner, creates annotated `mtm vX.Y.Z`, then pushes main+tag atomically per remote. Two remotes are not one global atomic transaction.

Dry-run changes nothing, including no prompt file. Explicit --changelog-prompt writes `.dev/changelog-prompt.md` without releasing; a non-dry missing-entry run also writes it and exits 1. The prompt contains AGENTS changelog rules, commits and file stats since the tag. There is no Go proxy priming or deck-update hint. These deliberate later rules replace the original vps2-only/deck-tag/dry-run-writes-prompt draft, while preserving publication acceptance as unfinished evidence.

Evidence: `scripts/release.sh`, CHANGELOG.md, AGENTS.md, commits f59adf6/0bb225d/a31b0b9. Earlier missing-entry/dry-run log: `/root/proj/redeck-astra-verification/runs/run.eXZQmt1e/verification.log`. Read-only local tag inspection during consolidation found annotated v0.5.0, v0.6.0 and v0.6.1 with `mtm` messages, plus nonrelease formsv2. Local tags are evidence of local annotated tags, not proof of remote publication or use of the release script. No tag was created, pushed or remotely checked here. [B-26](../todo/delivery.md#b-26) retains that distinction.

<a id="sourcereview"></a>
## Source documentation selection

The [full Go source review decision](../go-code-review.md) is the canonical selection record, not an installed service. Runtime registry docs describe actions/payloads; source review also needs packages, modules, internal/command packages, private declarations, fields/tags/embedding, methods/functions/constants/variables, comments/signatures, source locations, dependencies, implementations and type usages. Distinguish inferred relationships from declared ones. Missing comments stay visibly undocumented. Include revision, Go version and build context; loader/type errors must not masquerade as a complete report.

Selected order: pkgsite baseline browser plus go doc private-symbol inspection; evaluate Golds only against pinned Go compatibility and correct relationships; use gomarkdoc for committed diffable references if needed. pkgsite does not promise a complete private-symbol/usage graph. go doc -all -u/-src/-cmd is an inspection fallback, not a full explorer. Golds has richer relations/static HTML but maintenance/new-AST warnings and incomplete test-package analysis. gomarkdoc templates/check mode are snapshots, not an interactive relationship browser. Only confirmed remaining gaps justify a custom view using go/packages, go/ast and go/types, never regex type inference.

Review privately on local/VPS loopback, SSH tunnel if needed, no public private-source publication and no automatic desktop browser opening. Use bounded launchers; no unbounded server as verification. The adoption gate with representative panes.Pane, prompts.QueuedPrompt, private type, command package and implemented interface remains [B-71](../todo/delivery.md#b-71).

<a id="b-03"></a>
## B-03 TUI research deliverable

Status: implemented. [Canonical sample collection](../research/tui-design-samples.md) and [topic index](../research/tui-design-samples.outline.md) retain all twelve areas: dashboard, rows, detail, filters/palette, forms, composer, tree, help, catalogs, live, owned-content pages and status/themes. The original record reports 55 samples and 73 unique links, each fetched or search-returned, with borrowing notes, sketches, adoption patterns and missing evidence. Commits 41670da and 3492dc4 are the audit baseline. This consolidation did not refetch URLs.

Missing exact public examples include assign snapshot/approval and target-scrollback composer; stable images for some Telescope/Textual/lazygit views and an authoritative TUI design article were not found. Research is complete; adoption is not. [B-29](../todo/forms.md#b-29) owns per-page design/restyle/screenshots; [B-72](../todo/delivery.md#b-72) keeps evidence selection and still-unadopted alternatives without declaring every suggestion mandatory.

<a id="visibility"></a>
## Visible state review

The [UI state visibility matrix](../ui-state-visibility.md) is required acceptance, not a completed runtime audit. Every user-relevant state/transition needs a composable cue, explanation and clearing rule, including errors, unknown/stale data, queue uncertainty and partial success. Internal counters need no independent badge. [Forms visibility](forms.md#visibility) and [B-60](../todo/forms.md#b-60) own implementation/acceptance; [agents queue outcomes](agents.md#queueoutcomes) owns local-versus-daemon counts and uncertain delivery. Source documentation alone cannot establish visible behavior.

<a id="setup"></a>
## Packaged setup integration

The setup contract requires all hooks, extensions, helpers, scripts and configuration templates to live in the repository and distributed binary. Setup list/status/install/uninstall must work without a checkout or separate inbox install. Install materializes/configures owned files idempotently; status distinguishes missing, modified, conflicting and migration-required files. Uninstall preserves unrelated files/configuration and rejects unowned files/symlinks. OMP captures delivered request through final answer and replaces the older managed activity reporter to prevent duplicates. Record executable and selected data path, reload OMP after install and rerun setup when either path changes. Other adapters follow the same terminal-turn/packaging contract. These are retained target constraints from the [original outline](../sources/znbu/docs/outline.md), not a claim that every harness adapter was exercised here.

Current source baseline: `internal/setup/setup.go` embeds omp.ts, declares only the omp-activity item, stamps the selected executable/database, writes through an owned temporary file, detects modified/conflicting/migration-required content, refuses unowned files/symlinks and removes only recognized legacy reporters. This is narrower than claiming every harness has a packaged capture adapter. [B-76](../todo/delivery.md#b-76) retains remaining adapter/terminal-turn acceptance without reclassifying source inspection as runtime proof.

<a id="vpsplan"></a>
## Second development host

The [seven-step VPS plan](../plans/vps2-dev-host.md) preserves platform fallbacks, branch/sync protocol, first real development thread, measured concurrency, timeout-orphan cleanup, specific flakes and auth choice. [B-73](../todo/delivery.md#b-73) tracks all unfinished acceptance. Tooling/login and snapshot verification are existing evidence; they do not establish every plan step.

Adjacent auth/budget/routing ideas remain in [ecosystem](ecosystem.md) and [ecosystem todo](../todo/ecosystem.md), separate from Matomeru acceptance.
