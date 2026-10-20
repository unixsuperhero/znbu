# Matomeru outline

Znbu is the canonical design and backlog. This index replaces the oversized single-file outline; each concept keeps its current behavior, target design and remaining work together through links. **Target** and **open** sections are proposals, not shipped behavior.

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

The [project homepages target](outline/knowledge.md#project-homepages) proposes one running answer page per project alongside the existing Documents catalog. It is not implemented.

## Reading status

- Implemented behavior belongs in the concept outline, with evidence and limits.
- Partial implementations link to remaining acceptance criteria in the [todo](todo.md).
- Superseded proposals remain identified as history, not active tasks.
- Related ecosystem ideas retain their original product scope; they are not silently added to Matomeru.

See [source coverage](sources/README.md) for provenance and [maintenance](maintenance.md) for promotion rules. Historical acceptance is labeled; this consolidation does not rerun product acceptance.

## Former section locations

Old section anchors remain navigation links; their text now lives in concept documents.

<a id="modular-deck-outline"></a>
- [Modular deck: outline](outline/architecture.md)
<a id="0-rules-every-unit-follows"></a>
- [0. Rules every unit follows](outline/architecture.md)
<a id="0b-how-to-build-it"></a>
- [0b. How to build it](outline/architecture.md)
<a id="1-orchestrator--cmddeck"></a>
- [1. Orchestrator — `cmd/deck`](outline/architecture.md)
<a id="2-store--internalstore"></a>
- [2. Store — `internal/store`](outline/architecture.md)
<a id="3-command-bus--writes"></a>
- [3. Command bus — writes](outline/architecture.md)
<a id="4-event-bus--reads"></a>
- [4. Event bus — reads](outline/architecture.md)
<a id="5-registry--internalregistry"></a>
- [5. Registry — `internal/registry`](outline/architecture.md)
<a id="6-units"></a>
- [6. Units](outline/architecture.md)
<a id="61-daemon--internaldaemon-unchanged"></a>
- [6.1 daemon — `internal/daemon` (unchanged)](outline/panes.md)
<a id="62-panes--live-pane-registry"></a>
- [6.2 panes — live pane registry](outline/panes.md)
<a id="63-work--projects-tasks-assignments"></a>
- [6.3 work — projects, tasks, assignments](outline/work.md)
<a id="64-prompts--presets-queue-stash-dispatch-agent-start"></a>
- [6.4 prompts — presets, queue, stash, dispatch, agent start](outline/agents.md)
<a id="65-context--items-extraction-actions"></a>
- [6.5 context — items, extraction, actions](outline/knowledge.md)
<a id="66-history--reviews"></a>
- [6.6 history + reviews](outline/knowledge.md)
<a id="67-captures--files--autocapture"></a>
- [6.7 captures — files + autocapture](outline/knowledge.md)
<a id="68-notes"></a>
- [6.8 notes](outline/knowledge.md)
<a id="69-reminders"></a>
- [6.9 reminders](outline/automation.md)
<a id="610-config--internalconfig-unchanged"></a>
- [6.10 config — `internal/config` (unchanged)](outline/forms.md)
<a id="611-setup-complete-focus-unchanged-leaves"></a>
- [6.11 setup, complete, focus (unchanged leaves)](outline/architecture.md)
<a id="612-vim--neovim-sessions-as-deck-items"></a>
- [6.12 vim — neovim sessions as deck items](outline/knowledge.md)
<a id="613-code--directories-worktrees-branches-commits-prs-ci"></a>
- [6.13 code — directories, worktrees, branches, commits, PRs, CI](outline/work.md)
<a id="7-shells"></a>
- [7. Shells](outline/architecture.md)
<a id="71-tui--internalui"></a>
- [7.1 tui — `internal/ui`](outline/forms.md)
<a id="71a-lessons-from-tuioss-bubble-tea-use"></a>
- [7.1a Lessons from tuios's Bubble Tea use](outline/forms.md)
<a id="72-web--removed-for-now"></a>
- [7.2 web — removed for now](outline/architecture.md)
<a id="73-cli-new"></a>
- [7.3 cli (new)](outline/architecture.md)
<a id="8-flows-who-touches-what"></a>
- [8. Flows (who touches what)](outline/architecture.md)
<a id="9-migration-from-the-report-step--verify"></a>
- [9. Migration (from the report, step → verify)](outline/delivery.md)
<a id="10-open-decisions"></a>
- [10. Open decisions](outline/architecture.md)
