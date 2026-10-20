# Work, projects, and places

[Remaining work](../todo/work.md) · [Panes and reviews](panes.md)

Matomeru's work unit owns projects, tasks, assignments, the active pin, and lightweight todos. A project's current repository/tree settings are narrower than the target Place model. The implemented Git inventories are also narrower than automatic attribution and shared-place collaboration. These designs remain separate below.

Implementation evidence names paths relative to the Matomeru repository. Historical verification is recorded evidence, not a check performed during this consolidation. The implementation owner reported the completed `e4cf07a` feature commit while this consolidation was in progress. Only its matching directory/inventory scope is promoted below.

## Projects, tasks, and the pin

The implemented records in `internal/work/work.go` have this shape:

```js
Project = { id, name, theme, status, created, repo, trees: [Tree], default_tree,
            settings: { harness?, preset? } }
Tree = { kind: "worktree"|"clone"|"dir", path, repo?, branch? }
Task = { id, parent_id, project_id, title, position, theme, status, easy?,
         snoozed_until?, created, updated }
Active = { task_id, tree }
Assignment = { window, session, task_id, project_id, assigned_at? }
Theme = { color, glyph }
```

A root task stores its project. A subtask stores its parent and inherits the root project, rather than duplicating `project_id`. Every task has a project. Creation, moves, mass-add, and tree-draft commands reject a projectless root. Startup adopts legacy projectless roots into `Unsorted`, creating that project without a repository when needed.

A project can already exist without a repository, notably after bulk creation. Its implemented location settings still describe one repository and a selected default tree. Explicit Add project can select an existing repository or initialize an explicitly chosen existing folder. Worktree discovery records `git worktree list`; Matomeru does not create worktrees. Attaching a repository to a pathless project is separate from naming the project.

The active pin is one persisted row per Matomeru database, shared by processes using that database. Once tasks exist, work maintains a nonempty pin and derives the project through the selected task. Tasks, panes, context, captures, history, reviews, queue, notes, and Vim sessions use the resulting scope. Each scoped page has its own scope/ALL toggle on `S`; changing it does not change the pin. Project switching, Assign, help, the palette, and settings remain global. The title shows the project, task, and hidden-pane count; ALL reports zero hidden panes.

Registered reads receive explicit `Scope`. Work resolves a task subtree into a `ScopeSet` once, then checks membership without I/O. Empty scope means all. Scoped content excludes unassigned panes, terminals, agents, and Vim sessions. ALL exposes them in `No Task`, with black text on red, including selected rows and secondary lines. Assignment removes a row from that group. The pin supplies defaults, not inferred ownership.

A child record created from an owned record inherits its task. Its project is resolved through that task. Notes distinguish own, parent, project, and descendant ownership. The task edit form changes title, parent, and status. Its ownership pickers offer all targets so a form can retarget across projects. In normal form mode `ctrl+h` and `ctrl+l` walk the parent. In input mode `alt+h` is parent-up because `ctrl+h` remains Backspace.

Work owns the theme pool. Creation picks randomly among unused themes. Owners in `done` or `skipped` do not reserve their theme. When every theme is used, selection is random among the least-used themes. The pane rail uses the first four project-name characters in the project's theme and the task title in the task's theme. This is the current decision, not the deterministic-color alternative in the design research.

The unit exposes project/task add and patch, `work.set-tree`, `work.pin`, `work.scan-repos`, `work.move-task`, `work.assign`, `work.unassign`, `work.approve-assign`, `work.snooze`, `work.mass-add`, `work.tree-snapshot`, and `work.apply-tree-draft`. Changes emit `projects.changed`, `tasks.changed`, `assignments.changed`, and `active.changed` as applicable. `Resolve(window)`, `Target(task, project)`, and `ProjectOf(task)` keep ownership rules out of the UI.

Evidence: `internal/work/{work,scope,commands,repos,register}.go`, `internal/ui/{scoped_header,render_work}.go`, and the [preserved implementation outline](../sources/matomeru/docs/outline.md#63-work--projects-tasks-assignments). The broader [original work design](../sources/znbu/docs/outline.md#63-work--projects-tasks-assignments) remains the source for the [Place target](#places).

## Assignment discovery and pruning

Assign is a global inventory on `a`, also available from the palette. It previews panes and agents, saved Vim sessions, context items, and notes. It never assigns tasks to projects through cwd inference. Projects are ownership roots. Captures, history, and reviews retain recorded historical ownership rather than following a pane's current assignment.

Candidates are deduplicated and sorted by canonical working directory, not by individual item or repository. A row shows its containing Git repository, proposed existing or new project, affected items, and any unresolved reason. Discovery is read-only. It creates no project, assignment, repository, or worktree.

Approving one candidate or all displayed eligible candidates carries the exact displayed snapshot. Approval rechecks ownership and directory evidence. It must not overwrite an assignment made since preview or include newly discovered items. Several cwd rows in one repository reuse one project. `/tmp` and `/private/tmp` aliases resolve to the same evidence; a different resolved directory invalidates approval. Missing directories, non-Git directories, and items without cwd stay visible with a reason and an explicit existing-project picker. Assign never runs `git init`. Cancellation and completion preserve the page and pin.

```js
AssignItem = { kind, id, label?, session?, window?, cwd? }
AssignCandidate = { id, label, cwd?, repo?, tree?, project_id?, items: [AssignItem], reason? }
AssignApproval = { candidate: AssignCandidate, project_id?: explicitExistingProject }
```

Assignment pruning consumes the shared [pane snapshot](panes.md#listing). It requires two distinct successful snapshots started after the assignment was written. A queued older snapshot cannot delete a new assignment or override a pane known live in the current snapshot. Close and overflow recovery request two successful listings in at most three bounded attempts, allowing one transient split-list failure. Work resets its own observations before overflow reconciliation. This is event-triggered recovery, not an idle pruning poll.

Evidence: `internal/work/assign.go`, `internal/work/work.go`, `internal/panes/panes.go`, and the [recorded ownership decisions](../sources/matomeru/docs/outline.md#10-open-decisions).

## Project/task tree and atomic drafts

`P` opens the expanded project/task/subtask tree from any page. Only real records are selectable; there are no repeated `+ new` pseudo-rows. In the switch tree:

- `o` inserts below the selected task's subtree; `O` inserts above it. On a project, either creates its first root task. `a` inserts a child at the selected row's end.
- `e` or `i` edits a task title or project name. Enter or Escape finishes the line without saving. Empty new lines disappear.
- Tab and Shift+Tab nest only new task rows within the same project. Existing task ownership is unchanged.
- Ctrl+s submits all insertions and renames in one transaction. It preserves the pin and closes only on success. A validation error or stale tree revision keeps the draft and error, with no partial write.
- Escape in normal mode discards the whole draft. Navigation and line editing never persist changes.
- Enter on a clean task pins it. Enter on a clean project pins its first open task or creates one when needed. A dirty draft must first be saved or discarded.

Project creation and repository scanning remain separate palette actions, except for the explicit bulk-create policy below. The lineage modal on `w` shows the item's project, its ancestor task chain, its task, and that task's subtasks. It does not initially show the whole project. Ancestor rows show hidden sibling counts such as `+19`; `l` expands and `h` folds them.

```js
TreeDraft = { revision,
  project_adds: [{ ref: "draft:p1", name }],
  adds: [{ ref: "draft:1", title, parent_id, project_id }],
  task_renames: [{ id, title }], project_renames: [{ id, name }],
  sibling_orders: [{ parent_id, project_id, refs: [existingID, "draft:1"] }] }
```

Draft children can refer to earlier draft rows. Project additions precede task additions. Stable draft references avoid confusing two records with the same name. Sibling `position`, not a rewritten creation timestamp, preserves above/below placement after reopening. Legacy zero positions retain creation-time/ID order until a touched sibling group receives consecutive positions. Existing tasks are not reparented or reordered by draft insertion.

Evidence: `internal/work/tree.go`, `internal/ui/tree_edit.go`, and the [preserved tree contract](../sources/matomeru/docs/outline.md#63-work--projects-tasks-assignments).

<a id="b-37"></a>
## B-37: Bulk creation tree

Status: implemented. `work.bulk_create` defaults on. **Bulk create**, `alt+m`, and a form's `+ add new…` open the same tree draft as the `P` tree, not a separate field-form component. It opens every project, task, and subtask at the form's parent or pin. The historical adds-only restriction and dim read-only existing names are replaced by [B-44](#b-44).

`o` and `O` add siblings; `a` adds a child. On a project, sibling insertion creates a project because top-level lines are projects. Tab nests a new project into the preceding project as its last root task. Shift+Tab turns a new root task into a project with its children. A new project needs only a name, not a repository. **Set project tree** attaches one separately.

Ctrl+s runs one atomic `work.apply-tree-draft`, reports additions, and restores a parked form with the first new task selected. Escape in normal mode discards. CLI entry points remain `mtm task tree` and `mtm task bulk-create` with draft JSON. The [atomic tree contract](#projecttask-tree-and-atomic-drafts) retains revision/conflict handling.

Historical evidence: commit `e3f3780`, `internal/ui/tree_edit.go`, `internal/work/tree.go`, and `internal/settings/settings.go`. [Original B-37](../sources/znbu/docs/todo.md#b-37-bulk-create-tree-projects-tasks-and-subtasks-in-one-editable-tree) records `bulk_create`, `mass_add`, and `switch_creation` acceptance. Current behavior adds the B-44 proof below.

<a id="b-44"></a>
## B-44: Continuous insertion and existing-record renames

Status: implemented. Use `o` or `O` once, then enter several names separated by Enter without leaving insertion mode. Tab and Shift+Tab change the current line's nesting during editing. Multiline bulk lines retain their hierarchy. Vim-style draft navigation and name editing apply to existing projects and tasks as well as new rows.

Saving a rename preserves its primary key, assignments, and existing relationships. The same atomic draft-save and stale-revision conflict behavior applies to renames and additions; a failed save does not partially apply the draft. This explicitly replaces B-37's former existing-row protection, not superseded B-07.

Evidence: real VPS CLI/PTy tree runs `run.rn4oBZIK` and `run.nZi7OYaT`. Sources: [original B-44](../sources/znbu/docs/todo.md#b-44-edit-the-bulk-create-tree-continuously-and-rename-existing-records), [user request](../sources/hub/prompts/mtm-todo.md).


<a id="b-07"></a>
## B-07: Superseded mass-add outline

Status: superseded by [B-37](#b-37), not active default-flow work. `work.bulk_create` off still selects the legacy mass-add outline. The original proposal wanted all existing projects and nested tasks prefilled dim, with status marks and an empty line after them. Equal names under the same parent would reuse the existing record; a top-level task path such as `project / task` could select an existing parent.

Its remaining historical details were blank/comment skipping, an empty-store example, line-numbered rejection of orphan indentation, jumps greater than one level, and odd spaces before any write. It requested outline-order insertion, a count of projects/tasks added, and unchanged Tasks selection. Deleting or editing a prefilled line would neither delete nor rename the original record. Enter would split with the current indent, Backspace at line start would join, Ctrl+u would clear, and Tab/Shift+Tab would change indent without leaving the field. Fourteen visible lines would keep the cursor in view. Root lines had to become projects or be rejected, never create projectless tasks; B-37 chose projects. The one-parked-modal rule still applies.

These are preserved design alternatives, not a claim that every legacy outline behavior was implemented. They do not authorize rebuilding the default flow or retaining the old prohibition on renaming as a requirement of B-44. Evidence: the [full B-07 source](../sources/znbu/docs/todo.md#b-07-mass-add-outline-prefill-the-existing-tree-and-reuse-names-learned-from-tuios-deck) and `bulkCreateOn` in `internal/ui/tree_edit.go`.

<a id="b-13"></a>
## B-13: Lightweight todos and promotion

Status: implemented. The Todo unit exists in `internal/work`, alongside the work transaction and pin. A todo needs no project or pane. It carries free text, priority, notes, and optional ownership, and can be claimed, researched through the [agent interface](agents.md), resolved, or promoted into a task. Canonical index/directory import now preserves the complete backlog and its dispositions.

```js
Todo = { id, external_id?: "B-nn", title, text, priority: "p1"|"p2"|"p3",
  status: "idea"|"ready"|"claimed"|"review"|"done"|"parked"|"superseded", owner?, project_id?, task_id?,
  promoted_task_id?, notes: [string], created, updated }
Promoted = { task: Task, todo: Todo }
Import = { path, imported, updated, ids }
```

The global Todos page uses `B`. Rows sort with done last, then by priority and age. Detail shows text and notes oldest to newest. Enter promotes; `n` adds, `e` edits, and Delete asks before removal. `todos.add`, `todos.patch`, `todos.claim`, `todos.promote`, `todos.delete`, and `todos.import` emit `todos.changed`. Patch can append a dated note. Claim accepts only `ready`, sets `claimed` and owner, and otherwise returns `not_ready`. CLI commands use `mtm todo …`; `mtm work todos list` reads the same table.

Promotion chooses explicit `parent_id`, then explicit root `project_id`, then the todo's own task/project, then the pin. Without a destination it returns `invalid_args`. It copies the title, moves text followed by notes into the new task's own notes in order, sets `done`, `promoted_task_id`, and `task_id`, and refuses repetition with `already_promoted`. A new task defaults to `todo`; creation with a pane, or a later `work.assign`, makes it `active` and records that change in history. `done` and `skipped` remain the final states. The `new_task_status` setting defaults to `todo`; the historical environment-only fallback is not the canonical settings interface.

Import accepts the canonical `docs/todo.md` index or its containing directory, follows the split concept locations, and preserves all 66 B identifiers. It preserves each title, priority, status, body, and notes rather than importing only the older fixture. Parked and superseded records retain their dispositions instead of becoming active ideas. Repeating an import upserts by B identifier without duplicate records; existing notes and ownership are retained under the import contract. Unknown statuses are not silently recast as idea. Completed identities remain completed.

Recorded real VPS CLI evidence: `run.GsYNEfhn` covers all 66 IDs and repeat import. The intended application-store import subsequently returned `imported: 66, updated: 0`; the CLI read-back contained 23 open, 13 partial, 3 verification-pending, 25 implemented, and 2 superseded records. All six quick-win IDs retain implemented status. The approved disposition of each imported item is recorded in the canonical index and source map.

Historical baseline evidence remains commit `059ba80`, `internal/work/todos.go`, and `internal/work/commands.go`. The [implementation source](../sources/matomeru/docs/outline.md#17-b-13-todo-unit-and-page-items-that-are-not-yet-tasks) records original ordering, errors, claim, promotion, notes, activation, and fixture repeat-import acceptance. [Original B-13 acceptance](../sources/znbu/docs/todo.md#b-13-todo-unit-and-page-items-that-are-not-yet-tasks) remains preserved.

The [todo metadata and dispatch plan](../plans/todo-dispatch.md) extends this implemented baseline. Per-item source file/line, stored size, structured export, directory setting, marked dispatch, and orchestrator preset acceptance remain in the [work backlog](../todo/work.md#todo-dispatch). The plan is not evidence that those extensions exist, and does not justify rewriting canonical index import.

## Projects as knowledge and deliverables

Target, not implemented: the dedicated Projects page has one selected project and makes that project's running short-answer document its main content. It shows questions and concise answers in one place, with links to full reports and source turns. The existing things to know, do, make, and share categories organize related project work without replacing the running answers. Selecting a project on this page establishes project-page context only while this page is open. In this target design, "scoped to a project" and "pinned to a project" mean being on that project's page, not filtering every other page through a persistent task pin. Task ownership and explicit project filters for CLI reads remain distinct. Leaving the page does not silently keep its project as a filter for Panes, Documents, or other global pages. [B-43](../todo/work.md#b-43) owns the page and navigation. [Project-page content and agent contributions](knowledge.md#project-homepages) own the answer flow. The current database-wide task pin and project/task tree are implemented behavior, not this target. Related research and reusable knowledge ideas belong in the [ecosystem outline](ecosystem.md) and [ecosystem backlog](../todo/ecosystem.md).

<a id="rankedpaths"></a>
## Ranked directory suggestions

Status: partial. The directory catalog is implemented in commit `e4cf07a`, with owner-reported VPS verification. The [ranked-directory plan](../plans/ranked-dir-suggestions.md) preserves the original request to collect agent/terminal cwds and sort by frequency as well as the richer implemented ranking. [B-46](../todo/work.md#b-46) retains only the frequency-policy difference and native-picker evidence boundary.

`internal/work/directories.go` gathers canonical existing local directories from the current value, focused evidence, successful launches, project repositories/trees, pane and Vim cwd, context, presets, queue/stashes, recorded history, configured repository roots, process cwd, and home. It deduplicates paths but retains unrelated-project candidates. Context improves ranking rather than filtering the entire candidate set away. Remote-qualified evidence is not used as a local filesystem path, and selecting a remote destination returns no local suggestions. Manual typing and native picking remain available. Linux verification did not exercise the native macOS picker.

Ranking prioritizes current input, focused target, scoped successful launches, scoped project/preset evidence, other tracked evidence, repository discovery, process cwd, and home. Within a rank it uses launch frequency, then recency, then path. Ordinary activity and queued prompts are inventory, not successful-launch samples. This is not identical to counting how often cwds occur among current panes. That difference remains an explicit [B-46 decision and acceptance item](../todo/work.md#b-46), not an inferred acceptance of a changed request. Launch-default precedence belongs to [agent defaults](agents.md#launchdefaults), not the directory catalog.

<a id="gitcatalog"></a>
<a id="b-47"></a>
## B-47: Git and GitHub inventories

Status: implemented. Commit `e4cf07a` supplies the shared repository/branch inventory subset. Its owner reported VPS subsection, watched-action, provenance, and real hundred-PR comparison verification. Reported runs include `run.t7d5iNMS`, `run.0FUXkwfs`, and `run.uMlaOO9N`. These are owner evidence, not checks performed by this documentation change. [Remaining richer work](../todo/work.md#b-48) stays open.

`internal/gitcatalog` and registry subsections define Git on `W` with Repositories, Worktrees, Remotes, Branches, and Commits. GitHub on `V` reuses the exact repository and branch sources, then offers live Pull Requests and the existing Watched PRs operations. [AI on `F`](agents.md#aiassets) is a related implemented subsection page, not a complete disk catalog.

Repository identity is the canonical common Git directory. Worktrees share that identity; independent clones do not. Branch identity includes the full ref. Recorded commit provenance joins by repository and SHA. A fork's head branch is not a branch of the base clone. Live commits are capped at the newest 100 per repository across refs. Live GitHub reads request up to 100 PRs in all states per hosted repository through authenticated `gh`, retaining clone identity and project/task links.

The read contracts are `mtm git <repos|worktrees|remotes|branches|commits> list` and `mtm github <repos|branches|inventory-prs> list`, with explicit `--project` or `--task` scope. Existing GitHub review-request and watched-PR commands remain separate behavior. Subsections have independent selection, filter, scope, and scroll, load lazily, and refresh with Ctrl+r. Results belong to their page/section request. Only live subsections opt into ticks, including AI Agents, AI Sessions, and Watched PRs. Mutation refresh preserves selection/filter/scroll. Background ticks do not rerun Git/GitHub network inventories. Subprocesses are read-only, have finite deadlines, show errors, and never interpret remote cwd as a local path.

Evidence: `internal/gitcatalog/{catalog,inventory,github}.go`, `internal/ui/subsections.go`, `cmd/mtm/wiring.go`, commit `e4cf07a`, and the [preserved implementation outline](../sources/matomeru/docs/outline.md), sections 6.15 and 7.1. These inventories do not establish automatic dirty attribution, head-move recording, patch-ID rewrite tracking, inherited Place, messages, or claims. Explicit commit/PR record-and-trace provenance is a separate existing baseline; see [B-28](../todo/architecture.md#b-28). Broader repository and collaboration ideas remain in the [ecosystem outline](ecosystem.md) and [ecosystem backlog](../todo/ecosystem.md).

<a id="places"></a>
## Target: projects independent from repositories

The retained target is broader than `Project.repo`, `trees`, and `default_tree`. A project is named work, not a repository or folder. It can have zero directories, several repositories, plain directories, or a shared library also attached to another project. Naming a project must not infer it from a path. A project without directories still holds tasks. Native picking, repository scanning, and the CLI attach directories afterwards.

A directory is host plus canonical path. The same path on two hosts is two directories. A directory inside Git is `repo`; a plain directory is `dir`, has one implicit worktree equal to itself, and no branch. A project chooses a default directory and a default worktree for each directory.

A task may set a Place. Missing values inherit from its parent, then project defaults. `Active.place` records the resolved result. Agent, terminal, and Vim launches use that place's host and worktree path unless explicitly overridden. The edit form exposes directory, worktree, and branch, with blank meaning inherit. First-run `repo_roots` becomes a host/directory list. Scanning proposes directories; the person names projects and attaches repositories, with one project per repo as the default offer rather than a domain identity.

```js
ProjectTarget = { id, name, theme, status, created, dir_ids: [id], default_dir?: id,
  settings: { harness?, preset?, worktree: { [dir_id]: worktree_id } } }
Place = { host, dir_id, worktree_id?, branch? }
ActiveTarget = { task_id, place: Place }
TaskTarget = { ...Task, place?: Place }
SettingsTarget = { repo_roots: [{ host, dir }], stale_after, worktree_poll, pr_poll }
```

This is an explicit target, not the current schema. [B-48](../todo/work.md#b-48) tracks the cutover and related source-control behavior. Existing directory suggestions and the active Git catalog must not be used to close it.

<a id="gitattribution"></a>
## Target: observed Git state and attribution

The original code-unit design owns `dirs`, `worktrees`, `branches`, `commits`, `head_moves`, `prs`, `claims`, and `place_messages`. Work owns the work; this unit owns where it happens and the observed code state. The original Code-page proposal used `D`, which is now Panes. The active Git `W` and GitHub `V` subsections are the current navigation proposal. Their verification must resolve presentation without dropping the richer data requirements.

Git and `gh` run on the directory's host through its tuios daemon. Unreachable hosts leave rows `unknown`, never `clean`. The target refreshes `git worktree list` explicitly, every `worktree_poll` interval with a 30-second default, and after a turn or command in the repository. This target polling policy is distinct from the active catalog's lazy/manual reads. Every observation has an age. `WorktreeUse` derives current panes from cwd, task, and working state and is never stored as independent truth.

Dirty attribution records every observed cause since the prior observation, newest first. A turn produces a turn reference; a terminal command produces a history reference; nothing observed produces `unknown`, never a guess. The blame list clears on clean, while history retains both transitions. Branches retain upstream, ahead/behind, and commits seen since first observation. A bound branch links dirty changes, commits, and PRs to a task. If branch ownership and the turn's recorded task disagree, both are shown rather than silently choosing one.

Every HEAD change produces a `HeadMove`. Graph ancestry distinguishes commit and merge; loss of reachability identifies rewrite, and branch changes identify checkout. After rebase, amend, reset, or squash, patch IDs relate old commits to replacements through `superseded_by`, preserving turn-to-commit links and old SHAs in history.

For upstream branches, the target reads `gh pr view --json` and `gh pr checks` on turn completion and at `pr_poll`, default two minutes. A PR has one aggregate CI state and a per-check list. Missing `gh`, offline access, and rate limiting yield `unknown` with a reason. A PR context item links to the same record, not a second PR identity.

```js
Dir = { id, host, path, kind: "repo"|"dir", remote?, default_branch?, created, observed }
Worktree = { id, dir_id, path, branch_id?, head, main, dirty: Dirty|"clean"|"unknown", observed }
Dirty = { since, files, blame: [Blame] }
Blame = { kind: "turn"|"command"|"unknown", turn_id?, history_id?, host?, window?, task_id?, at }
WorktreeUse = { worktree_id, host, window, task_id?, working }
Branch = { id, dir_id, name, upstream?, ahead, behind, head, task_id?, observed }
Commit = { dir_id, sha, branch_id, subject, author, at, blame?, task_id?, superseded_by? }
HeadMove = { id, worktree_id, from, to, kind: "commit"|"merge"|"rewrite"|"checkout", at, blame? }
PR = { id, dir_id, branch_id, number, url, title, base,
  state: "draft"|"open"|"merged"|"closed", head, ci: CI, task_id?, observed }
CI = { state: "pending"|"passing"|"failing"|"unknown", reason?, checks: [{ name, state, url }], observed }
```

Directories relate many-to-many to projects and own worktrees, branches, and PRs. Worktrees own head moves and derived uses. Branches own commits and a PR and optionally bind a task. Blame links a turn or command history entry to its event-time task. PR ownership follows its branch. A historical turn stores its Place so the task, turn, dirty change, and commit can be traced in both directions.

The target code view is scoped, grouped by directory, with a worktree row showing branch, short HEAD, dirty state and blame, agents present, PR state, and CI. Detail lists head moves and commits with turns/tasks. Enter on a PR opens it. Polling cannot move selection, scroll, filters, or modals, and stale rows say so.

Target commands are `code.attach-dir`, `code.detach-dir`, `code.scan-repos`, `code.refresh`, `code.bind-branch`, `code.unbind-branch`, and `code.link-pr`. Emitted changes cover directories, worktrees, branches, and PRs. Window creation/closure and history turn/command completion drive observations. A turn end records history with Place, refreshes the worktree, records dirty/HEAD changes, refreshes PR/CI, and updates readers. A human command follows the same path with command blame. These are [B-48 requirements](../todo/work.md#b-48), not an assertion that the existing explicit provenance recorder implements them.

Launch forms display the resolved Place and nonblocking warnings for dirty changes with blame, another working agent, wrong bound branch, branch behind its base, a merged/closed PR, or failing CI. Quick `n a`, `n t`, and `n v` still launch immediately, showing warnings in status and on the row. The agent launch/composer rules live in [Agents](agents.md#composer).

Unresolved target choices remain explicit: remote Git through the host daemon versus direct SSH; GitHub-only `gh` versus a provider interface; list-only worktrees versus task-created branches/worktrees; attribution of all observed causes versus only active panes. Current Matomeru does not create worktrees. [B-48](../todo/work.md#b-48) cannot close by silently choosing a narrower design.

<a id="sharedplaces"></a>
<a id="b-02"></a>
## B-02: Target shared places, claims, and messages

Status: open. No application-owned `PlaceMessage`/`Claim` persistence and routing implementation was found in the code audit. Existing tuios mail and task/project notes are not this feature.

Two panes share a place when they use the same worktree, or the same branch in different worktrees. Matomeru owns recipient discovery and persisted records; tuios mail is transport addressed by host, session, and pane. It never types message text into the target terminal. Each message records its Place, named paths, text, originating turn, recipients, and per-recipient delivery outcome, and appends history under the sender's event-time task.

The six kinds are `claim`, `release`, `heads-up`, `handoff`, `question`, and `answer`. A claim names paths being edited. Release ends that claim. Heads-up precedes a commit, rebase, branch switch, or migration. Handoff records what is done and what remains. Questions and answers can use `reply_to`. A claim also exists as a worktree row, visible on the code view, in launch forms, and to later agents. Release, turn completion, or pane closure ends it.

```js
Claim = { id, worktree_id, host, window, task_id?, turn_id?, paths: [path], text?, since, until? }
PlaceMessage = { id, kind: "claim"|"release"|"heads-up"|"handoff"|"question"|"answer",
  from: { host, session, window, task_id?, turn_id? }, place: { worktree_id?, branch_id? },
  to: [{ host, session, window }], paths?: [path], text, reply_to?, at,
  delivered: [{ window, at, error? }] }
Preamble = { place: Place, others: [{ window, task_id?, working, claims: [Claim] }],
  dirty?: Dirty, head, branch, pr?: PR, commands: { claim, release, handoff, ask } }
```

The standard launch preamble names other panes and tasks, working/idle state, open claims, uncommitted paths with blame, branch/HEAD and PR state, and exact claim, release, handoff, and ask commands. It tells agents to claim before editing and send heads-up before a head move. Humans see the same information on pane rows and detail; quick start shows the summary in status.

Overlapping claims, a head move during another pane's open turn, or a commit touching another pane's claims warn on both rows and name both turns. Claims are warnings, not locks. The original alternative of refusing quick start on overlap remains a decision, not an undocumented change to this default.

Target commands are `mtm code message --json '{kind, worktree_id|branch_id, paths?, text}'`, `mtm code claim`, `mtm code release`, and `mtm code place --window W`. Commands emit `claims.changed` and `place_messages.changed`. Claims relate to worktree, pane, optional turn, and task; messages relate to sender, worktree or branch, recipients, optional parent message, and one history entry. The heads-up before a rewrite is retained with the resulting head move so another agent can explain why its base changed.

A proposed [long-lived application server](architecture.md#server) would deliver directly to connected pane clients and persist the row in the same operation, retaining mail for unreachable clients. That server is not current behavior. Delivery to a human terminal still needs a choice between tuios mail, an application notification, or both. [B-02's remaining acceptance](../todo/work.md#b-02) keeps these dependencies and choices visible. Adjacent cross-agent coordination ideas remain in the [ecosystem outline](ecosystem.md) and [ecosystem backlog](../todo/ecosystem.md).

The complete original schemas, relationships, warnings, and flows are preserved in the [original code-unit design](../sources/znbu/docs/outline.md#613-code--directories-worktrees-branches-commits-prs-ci) and [original flow descriptions](../sources/znbu/docs/outline.md#8-flows-who-touches-what). They are consolidated here as target requirements, not replaced by those source links.
