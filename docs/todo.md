# Matomeru backlog

Znbu owns the canonical backlog. Each concept pairs its remaining acceptance with the [outline](outline.md); implemented work is indexed below but lives in the outline, not the active queue.

| Concept | Outline | Remaining work |
|---|---|---|
| Architecture: Unit boundaries, store, buses, registry, shells and design rules | [Design and current behavior](outline/architecture.md) | [Todo](todo/architecture.md) |
| Inventory: Tracked kinds, owned children and reusable cross-concept relationships | [Design and current behavior](outline/inventory.md) | [Todo](todo/inventory.md) |
| Work and repositories: Projects, tasks, assignments, trees, code and Git relationships | [Design and current behavior](outline/work.md) | [Todo](todo/work.md) |
| Panes and navigation: Terminal lifecycle, rail, pins, focus and directory selection | [Design and current behavior](outline/panes.md) | [Todo](todo/panes.md) |
| Forms and actions: Field editing, settings, common verbs and nested command palette | [Design and current behavior](outline/forms.md) | [Todo](todo/forms.md) |
| Agents and prompts: Harnesses, models, composer, dispatch, presets and AI subsections | [Design and current behavior](outline/agents.md) | [Todo](todo/agents.md) |
| Knowledge: Notes, context, captures, history, files and Vim | [Design and current behavior](outline/knowledge.md) | [Todo](todo/knowledge.md) |
| Automation: Actions, reminders, integrations, MCP and execution | [Design and current behavior](outline/automation.md) | [Todo](todo/automation.md) |
| Delivery and verification: Releases, VPS, inventories, visibility and research adoption | [Design and current behavior](outline/delivery.md) | [Todo](todo/delivery.md) |
| Related product ideas: Ima, Now, Thinktank, pstack, mdoc and shared ideas not automatically Matomeru scope | [Design and current behavior](outline/ecosystem.md) | [Todo](todo/ecosystem.md) |

## Working rules

- Keep stable `B-nn` identifiers. Add checkable acceptance, priority, owner, branch and verification evidence to each item.
- Coverage status (open, partial, verification-pending, implemented, superseded) describes implementation evidence. Execution state (idea, ready, claimed, review, parked) describes scheduling; consolidation does not promote an idea to ready. Only ready work may be claimed.
- Claim work with a named owner and branch pushed to the vps2 hub. Move it to review with the verification log; promote completed acceptance to its concept outline. Coordinate with existing owners rather than editing their implementation.
- Preserve dated decisions. Work in priority order: p1 is highest, p2 next, p3 deferred; old “tonight/this week” dates are historical, not new deadlines.
- Behavior changes retain the original settings-toggle requirement; [settings](outline/forms.md#b-21) documents the mechanism.
- Record provenance for produced rows; [B-28](todo/architecture.md#b-28) owns the remaining cross-unit gaps.
- Partial items link to implemented behavior and list only unfinished acceptance. Source-reported completion for adjacent products is not verified Matomeru behavior.

See [maintenance](maintenance.md) and [source coverage](sources/README.md). The [historical backlog](sources/znbu/docs/todo.md) preserves original priorities, owners, dates and wording.

## Item locations

This is a navigation index, not a second task list. Status and acceptance live in the linked concept document.

### Remaining Matomeru work

| Item | Coverage status |
|---|---|
| [B-02: Build application-owned shared-place messaging ](todo/work.md#b-02) | open |
| [B-05: Notes on almost any record ](todo/knowledge.md#b-05) | partial |
| [B-08: Budget rail height by section and compact resting rows ](todo/panes.md#b-08) | open |
| [B-13: Complete faithful backlog import ](todo/work.md#b-13) | partial |
| [B-14: offline MCP harvest, catalog, templates, and replay ](todo/agents.md#b-14) | open |
| [B-16: Complete Slack context capture and live monitoring ](todo/automation.md#b-16) | partial |
| [B-19: Linear as a source of action items ](todo/automation.md#b-19) | open |
| [B-20: Supervise prompt schedule lifetime and complete report chaining ](todo/automation.md#b-20) | partial |
| [B-22: Complete feature inventory adoption and in-app review ](todo/delivery.md#b-22) | partial |
| [B-23: optional embedded Neovim field engine ](todo/forms.md#b-23) | open |
| [B-26: Establish release publication evidence ](todo/delivery.md#b-26) | verification-pending |
| [B-27: Finish download notes and directory configuration ](todo/knowledge.md#b-27) | partial |
| [B-28: Complete cross-record provenance ](todo/architecture.md#b-28) | partial |
| [B-29: whole-app UI/UX design pass ](todo/forms.md#b-29) | open |
| [B-31: forms acceptance gaps ](todo/forms.md#b-31) | partial |
| [B-32: rich prompt presets and recorded questions ](todo/agents.md#b-32) | partial |
| [B-33: nested command palette ](todo/forms.md#b-33) | open |
| [B-34: complete the per-harness AI asset catalog ](todo/agents.md#b-34) | partial |
| [B-36: interchangeable palette styles ](todo/forms.md#b-36) | open |
| [B-39: Parallel isolated end-to-end runner ](todo/delivery.md#b-39) | open |
| [B-40: Targeted iteration and one final full suite ](todo/delivery.md#b-40) | open |
| [B-41: Keep the page's last explicitly chosen detail tab ](todo/panes.md#b-41) | open |
| [B-42: field-group presets, recent selections, and sparse layers ](todo/agents.md#b-42) | open |
| [B-43: Give projects their own knowledge and deliverables page ](todo/work.md#b-43) | open |
| [B-44: Continue insertion and rename existing records in the bulk tree ](todo/work.md#b-44) | partial |
| [B-45: Offer task or project completion when closing a pane ](todo/panes.md#b-45) | open |
| [B-46: Resolve the remaining directory-ranking acceptance ](todo/work.md#b-46) | partial |
| [B-48: Implement the full Place and observed Git model ](todo/work.md#b-48) | open |
| [B-49: Complete the noninterfering preview contract ](todo/panes.md#b-49) | verification-pending |
| [B-50: Establish the complete host-qualified pane inventory ](todo/panes.md#b-50) | verification-pending |
| [B-60: complete the UI-state visibility matrix ](todo/forms.md#b-60) | open |
| [B-63: durable queue and dispatch outcomes ](todo/agents.md#b-63) | open |
| [B-64: per-unit prompts and instruction-driven work ](todo/agents.md#b-64) | open |
| [B-70: Settle process ownership and remaining architecture choices ](todo/architecture.md#b-70) | open |
| [B-71: Adopt source documentation only after compatibility review ](todo/delivery.md#b-71) | open |
| [B-72: Decide how to adopt the completed TUI research ](todo/delivery.md#b-72) | open |
| [B-73: Finish the seven-step second-development-host plan ](todo/delivery.md#b-73) | partial |
| [B-74: Settle event-loop resilience, timers and mouse interaction ](todo/architecture.md#b-74) | open |
| [B-75: Complete the phase2 reminders management page ](todo/automation.md#b-75) | open |
| [B-76: Complete packaged setup and supported-harness capture acceptance ](todo/delivery.md#b-76) | partial |
| [B-77: Settle the remaining MCP survey API proposals ](todo/automation.md#b-77) | open |
| [B-90: Unit modal and unit-note management ](todo/knowledge.md#b-90) | open |
| [B-91: Dedicated Notes and Vim pages ](todo/knowledge.md#b-91) | open |
| [B-92: Complete the saved-editor management contract ](todo/knowledge.md#b-92) | partial |
| [B-100: Inventory kinds, identity, and interconnected relationships](todo/inventory.md#b-100) | open |

### Implemented or superseded Matomeru work

| Outline location | Status |
|---|---|
| [B-01: Superseded fleet orchestrator ](outline/automation.md#b-01) | superseded |
| [B-03: TUI research deliverable ](outline/delivery.md#b-03) | implemented |
| [B-04: help and effective binding reference ](outline/forms.md#b-04) | implemented |
| [B-06: Pane detail tabs ](outline/panes.md#b-06) | implemented |
| [B-07: Superseded mass-add outline ](outline/work.md#b-07) | superseded |
| [B-09: Rail lifecycle ](outline/panes.md#b-09) | implemented |
| [B-10: Review accordion and stars ](outline/panes.md#b-10) | implemented |
| [B-11: Documents ](outline/knowledge.md#b-11) | implemented |
| [B-12: MCP shell and agent identity ](outline/automation.md#b-12) | implemented |
| [B-15: Action items and global attention ](outline/automation.md#b-15) | implemented |
| [B-17: GitHub review requests ](outline/automation.md#b-17) | implemented |
| [B-18: Authored PRs and watch polling ](outline/automation.md#b-18) | implemented |
| [B-21: settings ](outline/forms.md#b-21) | implemented |
| [B-25: searchable palette ](outline/forms.md#b-25) | implemented |
| [B-30: Stale panes remain in their group ](outline/panes.md#b-30) | implemented |
| [B-35: Stuck-pane checks ](outline/automation.md#b-35) | implemented |
| [B-37: Adds-only bulk creation ](outline/work.md#b-37) | implemented |
| [B-38: Nested middle rail below the pin ](outline/panes.md#b-38) | implemented |
| [B-47: Git and GitHub inventories ](outline/work.md#b-47) | implemented |
| [B-61: Inferred launch defaults ](outline/agents.md#b-61) | implemented |
| [B-62: Two-input Prompt/Settings composer ](outline/agents.md#b-62) | implemented |

### Adjacent product ideas

See [ecosystem remaining work](todo/ecosystem.md) and [source-reported behavior and historical decisions](outline/ecosystem.md). These are not automatically approved Matomeru features.

### Former item anchors

<a id="b-37-bulk-create-tree-projects-tasks-and-subtasks-in-one-editable-tree"></a>
<a id="b-37"></a>
- [B-37: Bulk-create tree: projects, tasks and subtasks in one editable tree](outline/work.md#b-37) — implemented.
<a id="b-38-panes-rail-as-a-nested-tree-below-the-pin"></a>
<a id="b-38"></a>
- [B-38: Panes rail as a nested tree below the pin](outline/panes.md#b-38) — implemented.
<a id="b-35-replace-the-one-off-orchestrator-with-a-stuck-pane-check-that-raises-action-items"></a>
<a id="b-35"></a>
- [B-35: Replace the one-off orchestrator with a stuck-pane check that raises action items](outline/automation.md#b-35) — implemented.
<a id="b-31-forms-redesign-precise-modal-hierarchy-aware-replaces-the-top-8-lines-box"></a>
<a id="b-31"></a>
- [B-31: Forms redesign: precise, modal, hierarchy-aware, replaces the top-8-lines box](todo/forms.md#b-31) — partial.
<a id="b-32-preset-prompts-a-dedicated-start-with-preset-action-and-a-page-of-asked-questions"></a>
<a id="b-32"></a>
- [B-32: Preset prompts: a dedicated start-with-preset action and a page of asked questions](todo/agents.md#b-32) — partial.
<a id="b-33-nested-command-palette-styled-like-the-help-modal-sub-palettes-per-kind"></a>
<a id="b-33"></a>
- [B-33: Nested command palette: styled like the help modal, sub-palettes per kind](todo/forms.md#b-33) — open.
<a id="b-28-provenance-on-every-record-turn-pane-task-project-commit-pr"></a>
<a id="b-28"></a>
- [B-28: Provenance on every record: turn, pane, task, project, commit, PR](todo/architecture.md#b-28) — partial.
<a id="b-25-command-palette-opens-in-search-mode"></a>
<a id="b-25"></a>
- [B-25: Command palette opens in search mode](outline/forms.md#b-25) — implemented.
<a id="b-21-settings-a-page-plus-per-service-config-areas-reachable-by-one-key-or-one-command"></a>
<a id="b-21"></a>
- [B-21: Settings: a page plus per-service config areas, reachable by one key or one command](outline/forms.md#b-21) — implemented.
<a id="b-12-deck-as-an-mcp-server-configured-into-every-agent-deck-starts"></a>
<a id="b-12"></a>
- [B-12: Deck as an MCP server, configured into every agent deck starts](outline/automation.md#b-12) — implemented.
<a id="b-13-todo-unit-and-page-items-that-are-not-yet-tasks"></a>
<a id="b-13"></a>
- [B-13: Todo unit and page: items that are not yet tasks](todo/work.md#b-13) — partial.
<a id="b-14-mcp-harvest-and-replay-built-into-deck-read-harness-logs-catalog-servers-and-tools-call-them-without-an-agent"></a>
<a id="b-14"></a>
- [B-14: MCP harvest and replay built into deck: read harness logs, catalog servers and tools, call them without an agent](todo/agents.md#b-14) — open.
<a id="b-15-actionitem-unit-page-and-the-one-character-global-indicator"></a>
<a id="b-15"></a>
- [B-15: ActionItem unit, page and the one-character global indicator](outline/automation.md#b-15) — implemented.
<a id="b-16-slack-monitoring-mentions-dms-threads-oncall-channels-assessed-into-action-items"></a>
<a id="b-16"></a>
- [B-16: Slack monitoring: mentions, DMs, threads, oncall channels, assessed into action items](todo/automation.md#b-16) — partial.
<a id="b-17-pr-review-requests-from-github-periodic-through-gh"></a>
<a id="b-17"></a>
- [B-17: PR review requests from GitHub, periodic through `gh`](outline/automation.md#b-17) — implemented.
<a id="b-18-my-prs-open-and-drafts-watching-snooze-until-midnight-ci-and-status-change-alerts"></a>
<a id="b-18"></a>
- [B-18: My PRs: open and drafts, watching, snooze until midnight, CI and status change alerts](outline/automation.md#b-18) — implemented.
<a id="b-19-linear-as-a-source-of-action-items"></a>
<a id="b-19"></a>
- [B-19: Linear as a source of action items](todo/automation.md#b-19) — open.
<a id="b-20-schedules-recurring-prompts-and-lookups-on-an-interval-results-back-through-the-mcp-server"></a>
<a id="b-20"></a>
- [B-20: Schedules: recurring prompts and lookups on an interval, results back through the MCP server](todo/automation.md#b-20) — partial.
<a id="b-08-rail-height-budget-sections-capped-by-percent-one-line-rows-panes-get-most-of-it"></a>
<a id="b-08"></a>
- [B-08: Rail height budget: sections capped by percent, one-line rows, panes get most of it](todo/panes.md#b-08) — open.
<a id="b-09-pane-lifecycle-in-the-rail-working-at-the-bottom-and-locked-review-at-the-top-rest-in-the-middle"></a>
<a id="b-09"></a>
- [B-09: Pane lifecycle in the rail: working at the bottom and locked, review at the top, rest in the middle](outline/panes.md#b-09) — implemented.
<a id="b-10-review-accordion-the-detail-for-a-pane-with-unreviewed-turns"></a>
<a id="b-10"></a>
- [B-10: Review accordion: the detail for a pane with unreviewed turns](outline/panes.md#b-10) — implemented.
<a id="b-11-documents-page-starred-docs-glow-preview-live-mode-unread-theme"></a>
<a id="b-11"></a>
- [B-11: Documents page: starred docs, glow preview, live mode, unread theme](outline/knowledge.md#b-11) — implemented.
<a id="b-06-pane-detail-tab-bar-with-a-live-screen-tab-first-learned-from-tuios-deck"></a>
<a id="b-06"></a>
- [B-06: Pane detail: tab bar with a live Screen tab first, learned from tuios-deck](outline/panes.md#b-06) — implemented.
<a id="b-07-mass-add-outline-prefill-the-existing-tree-and-reuse-names-learned-from-tuios-deck"></a>
<a id="b-07"></a>
- [B-07: Mass-add outline: prefill the existing tree and reuse names, learned from tuios-deck](outline/work.md#b-07) — superseded.
<a id="b-03-gather-tui-design-samples-for-every-deck-screen-and-widget"></a>
<a id="b-03"></a>
- [B-03: Gather TUI design samples for every deck screen and widget](outline/delivery.md#b-03) — implemented.
<a id="b-01-orchestrator-agent-that-catches-agents-spinning-their-wheels"></a>
<a id="b-01"></a>
- [B-01: Orchestrator agent that catches agents spinning their wheels](outline/automation.md#b-01) — superseded.
<a id="b-41-keep-the-last-explicitly-chosen-detail-tab-while-navigating-a-page"></a>
<a id="b-41"></a>
- [B-41: Keep the last explicitly chosen detail tab while navigating a page](todo/panes.md#b-41) — open.
<a id="b-42-field-group-presets-recent-selections-and-composable-preset-layers"></a>
<a id="b-42"></a>
- [B-42: Field-group presets, recent selections and composable preset layers](todo/agents.md#b-42) — open.
<a id="b-43-give-projects-their-own-page-organized-around-what-needs-to-be-known-done-made-and-shared"></a>
<a id="b-43"></a>
- [B-43: Give projects their own page organized around what needs to be known, done, made and shared](todo/work.md#b-43) — open.
<a id="b-44-edit-the-bulk-create-tree-continuously-and-rename-existing-records"></a>
<a id="b-44"></a>
- [B-44: Edit the bulk-create tree continuously and rename existing records](todo/work.md#b-44) — partial.
<a id="b-45-offer-task-or-project-completion-when-closing-its-pane"></a>
<a id="b-45"></a>
- [B-45: Offer task or project completion when closing its pane](todo/panes.md#b-45) — open.
<a id="b-39-parallel-e2e-runner-a-database-per-case-about-four-at-once-one-report-at-the-end"></a>
<a id="b-39"></a>
- [B-39: Parallel e2e runner: a database per case, about four at once, one report at the end](todo/delivery.md#b-39) — open.
<a id="b-40-verify-with-targeted-cases-while-working-one-full-suite-only-at-the-end"></a>
<a id="b-40"></a>
- [B-40: Verify with targeted cases while working; one full suite only at the end](todo/delivery.md#b-40) — open.
<a id="b-36-command-palette-styles-several-interchangeable-looks-chosen-in-settings"></a>
<a id="b-36"></a>
- [B-36: Command palette styles: several interchangeable looks, chosen in settings](todo/forms.md#b-36) — open.
<a id="b-34-ai-page-harnesses-agents-skills-commands-marketplaces-mcps-learned-from-disk"></a>
<a id="b-34"></a>
- [B-34: AI page: harnesses, agents, skills, commands, marketplaces, MCPs, learned from disk](todo/agents.md#b-34) — partial.
<a id="b-29-uiux-pass-on-every-page-with-fable-51-and-the-frontend-design-skill"></a>
<a id="b-29"></a>
- [B-29: UI/UX pass on every page with Fable 5.1 and the frontend-design skill](todo/forms.md#b-29) — open.
<a id="b-22-feature-inventory-with-review-marks-growing-into-an-in-app-registry"></a>
<a id="b-22"></a>
- [B-22: Feature inventory with review marks, growing into an in-app registry](todo/delivery.md#b-22) — partial.
<a id="b-23-neovim-as-the-input-engine-behind-form-fields-behind-a-settings-toggle"></a>
<a id="b-23"></a>
- [B-23: Neovim as the input engine behind form fields, behind a settings toggle](todo/forms.md#b-23) — open.
<a id="b-26-changelog-and-release-script-in-the-tuios-deck-style"></a>
<a id="b-26"></a>
- [B-26: Changelog and release script in the tuios-deck style](todo/delivery.md#b-26) — verification-pending.
<a id="b-27-downloads-page-watch-downloads-newest-first-copy-absolute-paths"></a>
<a id="b-27"></a>
- [B-27: Downloads page: watch ~/Downloads, newest first, copy absolute paths](todo/knowledge.md#b-27) — partial.
<a id="b-05-notes-on-almost-anything-shown-in-the-detail-pane-of-every-page"></a>
<a id="b-05"></a>
- [B-05: Notes on almost anything, shown in the detail pane of every page](todo/knowledge.md#b-05) — partial.
<a id="b-04-help-modal-two-rows-shift-left-and-leak-border-glyphs"></a>
<a id="b-04"></a>
- [B-04: Help modal: two rows shift left and leak border glyphs](outline/forms.md#b-04) — implemented.
<a id="b-02-deck-owned-agent-messaging-shared-places"></a>
<a id="b-02"></a>
- [B-02: Deck-owned agent messaging (shared places)](todo/work.md#b-02) — open.
<a id="b-30-remove-the-stale-rail-group-on-the-panes-page"></a>
<a id="b-30"></a>
- [B-30: Remove the Stale rail group on the panes page](outline/panes.md#b-30) — implemented.
