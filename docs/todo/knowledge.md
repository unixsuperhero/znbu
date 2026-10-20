# Remaining knowledge and file work

The [knowledge outline](../outline/knowledge.md) records current behavior, schemas, and target decisions. This backlog contains only unfinished acceptance. B-11's implemented Documents core lives [in the outline](../outline/knowledge.md#b-11); its missing turn provenance stays in [B-28](architecture.md#b-28), not a second Documents implementation item. Historical verification logs below are recorded evidence, not checks performed for this consolidation.

<a id="project-homepages"></a>
## Project homepages

status: open · source: [project homepages target](../outline/knowledge.md#project-homepages)

- Persist one homepage path per stable Matomeru project ID and expose a project-scoped lookup to agents. Reuse the mapped page across project renames and worktrees.
- Resolve the contribution's project from explicit project or inherited task ownership, then an explicitly assigned pane, then a unique canonical repository match. Never borrow another pane's global pin. If ambiguous or unassigned, retain the contribution for assignment without writing to a guessed page.
- Provide a project-owned contribution command that accepts an idempotency ID, question or request, short answer, date and source links. Serialize concurrent writes to that project's Markdown page; retrying the same ID must produce exactly one section without losing another agent's section.
- Show or open the project homepage as the first short-answer destination while preserving the Documents list and chronological artifact index for full reports.

<a id="b-05"></a>
## B-05: Notes on almost any record

status: partial · priority: p2 · size: L

[Implemented baseline and target schema](../outline/knowledge.md#b-05). Task/project notes, hierarchy visibility, add/patch/delete commands, and todo-promotion note transfer already exist. The audit found only task/project ownership in `internal/notes/notes.go`, task-only note detail loading in `internal/ui/model.go:486`, and no download `NOTES` block. Those features do not satisfy arbitrary-owner notes.

### Remaining contract

1. Replace the two owner columns with `owner: { kind, id }` and migrate existing notes without losing IDs, text, timestamps, provenance, or task/project inheritance. Keep child notes distinguishable from parent notes with `via=child`.
2. Support every original owner kind, `task`, `project`, `pane`, `context`, `capture`, `review`, `vim`, `reminder`, and `prompt`. Include the later explicit additions, download, document, and action item. Settle their exact command kind names rather than omitting those owners because the first schema predates them.
3. Make `notes.add`, `notes.patch`, and `notes.delete` accept the owner contract; expose `mtm note list --owner kind:id`. Reject an unknown kind with `invalid_args`. A row sees its own notes while task/project inheritance remains unchanged.
4. Key pane notes by session plus stable window ID, keep them readable after closure, and settle how closed-pane notes are found outside history. Decide whether review notes belong to the stable turn or a history entry before implementing that owner identity.
5. End each page's selected-row detail with `NOTES`, newest last, inherited notes labeled by `via`, wrapped to detail width, and scrolled with the rest of the detail. Empty notes show one dim line, not an unexplained blank gap. The Panes, Tasks, Context, Captures, History, and Reviews pages must all show the text and a note count or glyph in the rail. Downloads, Documents, and Action Items must also display their explicitly requested owned notes.
6. Add a selected-row note action on every applicable page. Choose and document its binding before implementation; `a` is already Assign and `n` already means create on the page. Use the existing notes textarea with the owner prefilled and shown in the title. Detail focus permits edit/delete on a note without opening a separate notes-list modal.
7. Preserve the selected record and scroll during note add/edit/delete and later refresh. The detail is the ordinary right-hand content area, not a modal substitute.

### Remaining acceptance

- `mtm note add --json '{"owner":{"kind":"pane","id":"<session/window>"},"text":"…"}'` and owner-filtered listing work for every supported kind. Unknown kinds return `invalid_args`.
- Each named page shows its selected row's notes and a rail marker. Inherited notes retain their labels and task/project visibility. A closed pane's note remains retrievable by its stable owner identity.
- Detail add/edit/delete preserves selection and scroll. Empty, wrapped, and inherited notes meet the display contract above.
- The existing `descendant_notes` acceptance still holds and gains one assertion per new owner kind. No task/project behavior is dropped during the migration.
- The download-specific example, `mtm note add --json '{"owner":{"kind":"download","id":"<absolute path>"},"text":"…"}'`, appears under that entry's detail. This also closes the notes part of [B-27](#b-27).

The [dedicated Notes page, B-91](#b-91), can come later. It is not a prerequisite for these detail requirements. Notes about a unit's implementation are separate [meta unit notes, B-90](#b-90), not another arbitrary record owner added by implication.

Sources: [B-05 design, build order, acceptance, and open decisions, lines 1518-1561](../sources/znbu/docs/todo.md#b-05-notes-on-almost-anything-shown-in-the-detail-pane-of-every-page), [original task/project notes, lines 335-346](../sources/znbu/docs/outline.md#68-notes), and [implementation-era child-note label, lines 383-394](../sources/matomeru/docs/outline.md#68-notes). Evidence baseline: Matomeru `internal/notes/notes.go:19,181,202`, `internal/ui/model.go:486`, and `internal/ui/render_downloads.go`.

<a id="b-27"></a>
## B-27: Finish download notes and directory configuration

status: partial · priority: p2 · size: S

[Implemented downloads behavior](../outline/knowledge.md#b-27) already covers watcher/rescan, newest-first listing, hidden dotfiles, nonrecursive directory rows, per-modification seen state, selection-safe inserts, clipboard copies, marks, OS open, and CLI rows. Do not reopen that implemented scope as another page build.

### Remaining acceptance

- Define `downloads.dir` in the existing settings system, defaulting to `~/Downloads`, and make the unit use it. The current `MTM_DOWNLOADS_DIR` constructor value is not the requested setting. Use a temporary configured directory for acceptance rather than the user's Downloads. Preserve the application's chosen setting/default precedence instead of adding a second convention.
- After the setting is wired, the original acceptance still holds using that setting: create two files while the page is open, see both within one second newest first and unread, select one, and see only that modification marked seen in `mtm download list`. The known implementation is the baseline; this setting change must not bypass its watcher or rescan behavior.
- Implement owner kind `download`, keyed by the absolute path, through [B-05](#b-05). A note added with `mtm note add --json '{"owner":{"kind":"download","id":"<absolute path>"},"text":"…"}'` appears in the row's `NOTES` detail section.
- Use the same unread theme contract as Documents, or settle and record the source's explicit local-style departure. The historical implementation used local bold styling plus `new ·` while the shared unread theme was absent. Preserve the visible distinction until a row is selected, including when a new modification makes the same path unread again.

The implemented clipboard contract remains one absolute path for `y`, or all marked paths one per line in list order, followed by clearing marks. A missing `pbcopy` remains a visible failure. `downloads.open` is the established cross-platform opener; reverting to context's macOS-only `open` action is not required to match obsolete command wording.

Sources: [B-27 including its explicit not-done notes acceptance, lines 1474-1516](../sources/znbu/docs/todo.md#b-27-downloads-page-watch-downloads-newest-first-copy-absolute-paths) and [implementation-era directory and state contract, lines 442-456](../sources/matomeru/docs/outline.md#613-downloads--internaldownloads). Evidence: Matomeru `internal/downloads/downloads.go`, `internal/ui/render_downloads.go`, and no `downloads.dir` definition in `internal/settings`. The recorded historical run `/root/proj/redeck-astra-verification/runs/run.85RFtc62/verification.log` covers the implemented downloads case but explicitly does not establish notes support or the missing setting.

<a id="b-90"></a>
## B-90: Unit modal and unit-note management

status: open · source: phase-2 unit modal and unit notes

This ID preserves unfinished knowledge work that had no B ID. It does not replace B-05. [The complete UnitModal, Struct, Relation, UnitNote, and UnitPrompt schemas and lifecycle](../outline/knowledge.md#unitnotes) are canonical. [B-64](agents.md#b-64) owns prompt construction, dispatch/queue integration, and turn correlation. Both remain linked to the [phase-2 plan](../outline-phase2.md).

### Remaining acceptance

- Register a `meta` unit that owns `unit_notes` and `unit_prompts`, so a domain unit does not store notes about itself. Preserve unit identity and the schema relationships: a note belongs to a unit and optionally a prompt; a prompt has selected notes, a pane/window, and one history turn.
- Open the current page's unit modal with a documented binding and any unit's modal with `unit: <id>` in the palette. Resolve `I` versus `Ctrl+i`; do not silently choose a binding that conflicts with another action.
- Render three folds, shape, notes, and prompts, from registry/store data. Shape includes structs, field names/types/JSON tags/docs, explicit relationships, commands, emitted/listened event types, and pages. Structs start collapsed to their names. Use the existing source-documentation path and [B-71 adoption gate](delivery.md#b-71), not hand-written parallel type definitions or inferred authoritative prose.
- Provide unit-note add/edit/delete through `meta.add-note`, `meta.patch-note`, and `meta.delete-note`, and `Space` selection in the notes fold. Preserve `open`, `prompted`, and `done` states, prompt linkage, created time, and optional `done_at`.
- Provide `meta.reopen-note` and `o` to return a note to `open` while clearing `prompt_id` and `done_at`. Emit `unit_notes.changed` and `unit_prompts.changed` for their corresponding writes.
- Display the completed prompt's linked unit notes when that turn is opened for review. Notes become done only through the correlated completed turn defined by B-64, not on submission or an intermediate model/tool response. Task notifications and continuing agent runs must not close the notes.
- Retain all UnitPrompt fields in the fold, including selected note IDs, editable text, optional preset, window, submission, stable turn link, and creation time. The fold must not erase multiple in-flight prompt records if that alternative is chosen.

Decisions shared with [B-64](agents.md#b-64) remain explicit: embed the generated outline text or link its path; allow one or many prompts per unit in flight; record the app repository tree in settings or an app-named project. The workflow's default cwd is the app's own repo, not the active pin. The outline retains all alternatives until a decision is recorded.

Source: [phase 2, unit modal, schemas, commands, lifecycle, and decisions, lines 17-61 and 70-75](../outline-phase2.md). Generated runtime reference and source-level documentation remain distinct in [instruction context](../outline/knowledge.md#agentinstructions).

<a id="b-91"></a>
## B-91: Dedicated Notes and Vim pages

status: open · source: phase-2 page-per-unit work

The original phase-2 plan gives each unit a page even when its rows already appear elsewhere. Preserve the two knowledge-owned pages here. Prompt pages remain with [B-64](agents.md#b-64); other units stay in their own domains.

### Remaining acceptance

- Register a Notes page with rows grouped by owner and inherited notes visibly marked. In scope mode, `e` edits, `d` deletes, and `a` adds under the pin. Use the common note model, not a separate page-only store. This is later work than B-05's cross-record detail and is not needed to finish that item's detail UI.
- Register a Vim page listing saved editor sessions. `Enter` focuses a running session or restores a closed session; `d` forgets a session through [B-92](#b-92). Keep running/closed state and ownership visible.
- Give both pages the existing scoped/all behavior with `S`, and make all mode read-only except assignment, as the phase-2 plan specifies. Retain the pin when switching modes.
- Set `Page.unit` correctly and derive ordering from unit ID, so another unit page appears without editing a central page switch. Use registry-provided page keys and palette commands rather than hard-coded duplicate routes.

Baseline: [task/project notes](../outline/knowledge.md#b-05) already appear in task detail, and [Vim sessions](../outline/knowledge.md#editorvim) already have a palette and resume modal. Neither constitutes its own phase-2 page. Source: [phase 2, page-per-unit contract, lines 5-15](../outline-phase2.md).

<a id="b-92"></a>
## B-92: Complete the saved-editor management contract

status: partial · source: original Vim unit target

[Current editor behavior and both schema versions](../outline/knowledge.md#editorvim) record the implemented direct `nvim` launch, app-owned session discovery, save/restore, active-tree default, explicit directory override, stable pane identity, running-session focus, and closed-session retention. These are not new implementation tasks.

### Remaining acceptance

- Add the original `vim.forget` command for a saved editor session and connect the later Vim-page forget action in [B-91](#b-91). The current unit exposes `vim.open` and `vim.list` but not forgetting. Record whether forgetting removes only metadata or its owned session file as well; the source does not settle that deletion detail.
- Integrate the original `place: Place` relationship when the shared [place design](../outline/work.md#places) is implemented. Opening uses the active task's resolved host/directory/worktree/branch, and the form may choose another existing worktree. Retain the record linking the saved session to the project, optional task, worktree through place, and living pane. The current cwd/tree-only metadata is not evidence of host/worktree-aware place handling.
- Keep session-file save/restore and stable session identity across that integration. An unrelated pane running Neovim remains a terminal; it must not become an app-owned session merely because its command is `nvim`.

The app-owned directory versus Neovim-owned discovery question is settled by the implementation's app-owned metadata/files beside the database. Do not reopen discovery or scan global Neovim sessions. Worktree creation is not part of this item. Optional Neovim-backed form input remains [B-23](forms.md#b-23), not a fallback implementation of session management.

Sources: [original Vim commands, place relationship, and session behavior, lines 381-395](../sources/znbu/docs/outline.md#612-vim--neovim-sessions-as-deck-items), [implementation-era session contract, lines 429-440](../sources/matomeru/docs/outline.md#612-vim--neovim-sessions-as-mtm-items), and [settled app-owned metadata decision, lines 609-610](../sources/matomeru/docs/outline.md#10-open-decisions). Evidence: Matomeru `internal/vim/vim.go` and `internal/vim/register.go`.

<a id="relatedknowledgework"></a>
## Work tracked with related concepts

- Document turn provenance, write-time ownership across record kinds, automatic commit/PR association, and navigable `FROM` links remain [B-28](architecture.md#b-28). The Documents page and manually recorded code chains do not close them.
- History's rich `HarnessTurn.place`, Git-aware timeline events, dirty attribution, and rewrite continuity remain with [work's Git attribution design](../outline/work.md#gitattribution) and its linked todo. The [implemented Git catalog](../outline/work.md#gitcatalog) and [observed AI conversation inventory](../outline/knowledge.md#observedconversations) are distinct completed scope in owner-reported commit `e4cf07a`; they do not close that richer target.
- [Whole-app research adoption, B-72](delivery.md#b-72), and the page design pass own [knowledge-page proposals](../outline/knowledge.md#knowledgepagedesign), including history columns, review glyphs/badges, light theme, split layout, command log, and capture position display.
- [Context matchers](ecosystem.md#ext-024), [change walker](ecosystem.md#ext-025), and [deferred learning](ecosystem.md#ext-016) remain external adjacent ideas. Their requirements are not duplicated as B-90-series work, and source-reported Ima behavior is not Matomeru implementation evidence.
