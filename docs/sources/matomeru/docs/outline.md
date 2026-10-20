# Matomeru: outline

Target specification for Matomeru (`mtm`), synchronized with [the source outline](../../znbu/docs/outline.md). Project-specific decisions are recorded in section 10.

Phase 2 follow-ups, not needed for the first build: [upstream phase 2](../../znbu/docs/outline-phase2.md).

Conventions: shapes are js-style; `?` = optional; relationships read like Rails (`belongs_to`, `has_many`, `has_one`, `through`). `[ ]` marks a decision still open.

## 0. Rules every unit follows

- a unit = one package, one concept, its tables, its rules
- talks to others only via: command bus (writes), event runner (reads), narrow interfaces it was handed
- never imports a shell (`tui`, `cli`)
- never touches view state (selection, scroll, modal)
- every list read takes a `Scope`; a unit answers only the rows under it (`Scope{}` is everything)
- registers definitions (pages, commands, palette, groupings) with the registry at startup
- verified by e2e suites only; no unit tests

```js
Scope = { task_id, project_id }     // the pin: a task and its project; a unit filters by task subtree, else by project
Unit = { id, tables: [name], commands: [name], emits: [type], listens: [daemonType],
         pages: [id], palette: [id], cli: [spec] }
// Go: interface { ID() string; Register(*Registry) }
```

## 0b. How to build it

- design every TUI surface (rail, detail, page, modal, form, help) with the `/frontend-design` skill; a terminal is still a UI
- parallel subagents, one unit or page each; optimize for wall-clock speed
- subagents use `openai-codex/gpt-6.1-sol` through the ChatGPT login only; no Anthropic or paid API providers
- web UI removed for now (not used); nothing is built for `internal/web`
- commit after every green step; `scripts/e2e-all.sh` before the last commit

## 1. Orchestrator — `cmd/mtm`

- builds every unit in order, owns startup/shutdown
- startup order
  - store open → units built → registry filled → runner subscribe (union of `listens`) → taps → shells start
- shutdown
  - shells stop → runner `Start` done → handlers `Close` (history flushes)
- owns
  - command bus (§3)
  - event runner (§4, existing `events.Runner`)
  - store `Tx` (§2)
- subcommands: `tui`, `config`, `setup`, `update`, `version`, + generated `<unit> <command> --json`
- shared flags: `-socket -captures -data -auto-capture`
- reminders is an events-style unit with its own cancellable scheduler

```js
Wiring = { client, store, config?, registry, bus, runner,
           units: [work, prompts, context, history, reviews, captures, notes, reminders, panes],
           shells: [tui | cli] }
```

## 2. Store — `internal/store`

- one database, per-table repos, one transaction API
- backend: SQLite via modernc.org/sqlite; JSON rows in unit-owned tables
- units declare tables; store does not know fields
- `Tx(tables, fn)` — only touched tables saved
- history append-only, never rewrites other tables

```js
Table = { name, owner: unitId, key: "id", version: 1, migrate: { 0: "…" } }
Tx    = (tables: [name], fn: (t) => void) => error
t.<table> = { get(id), put(row), delete(id), all(), where(fn) }
```

- relationships
  - `Table belongs_to :unit`
  - `Store has_many :tables`

## 3. Command bus — writes

- synchronous dispatch table, not a queue
- every mutation = named command + json payload, handled by owning unit
- served by: TUI keys, `mtm <unit> <cmd> --json`
- one log line per dispatch: name, args hash, duration, error

```js
Command = { name: "unit.verb", args: {} }
Result  = { status: string, data: {} , error?: { code, message } }
Handler = (ctx, args) => Result
Bus     = { register(name, Handler), call(Command) => Result, list() => [name] }
```

## 4. Event bus — reads

- `events.Runner` unchanged: one daemon subscription, resume `after_seq`+`boot_id`, bounded queues (256), per-handler goroutine, `Resync` on `subscribed`/`gap`/overflow
- units also emit mtm events through it; mtm events never reach daemon

```js
DaemonEvent = { seq, type, session, window, data }
MatomeruEvent   = { type: "tasks.changed", source: "mtm", ids: [id], at }
Handler     = { Types(): [type], Handle(ctx, ev), Resync(ctx, bootID), Close?() }
Tap         = chan Event   // one per shell; never closes on reconnect
```

## 5. Registry — `internal/registry`

- definition tables; shells read, units write at register
- `All(kind)`, `Status(id)` (review marks from the inventory plan)
- kinds: page, action, palette, modal, grouping, form, feature
- generated from it, never hand-written: the docs of every struct, page, concept and action (`mtm docs`), `mtm list-actions` (bindings per mode + actions with no key), `mtm config init` (every value, with its default)
- help modal `?`: grouped overview plus one tab per mode; unbound actions listed last; `/` filters keys, action names, descriptions and groups
- `/` filters every list: rail, tasks, context, captures, downloads, documents, history, reviews, palette, help, any picker
- catalog modal: `Modal{ kind: "catalog", source: "registry.kinds" }`; picking a kind replaces the modal with that kind's list; the meta catalog is the catalog of catalogs; still one modal at a time

```js
Page           = { id, key, title, unit, rail: fnName, detail: fnName, keys: tableId, help: id, tick: bool,
                   scoped: bool }   // true: the page has scope/all modes (`S`), including tasks
PaletteCommand = { id, group, label, hint, key?, run: Command }
Grouping       = { id, levels: ["harness","project","top-task"] }
Modal          = { id, kind: "list"|"form"|"tree", source: sourceId, onPick: { replace: id } | { command } }
Form           = { id, submit: commandName, fields: [Field] }   // drawn by the forms.layout presentation (§7.1)
Field          = { name, label?, key: char, kind?: "assignment"|"destination"|"task"|"parent"|"project"|"directory"|"file"|"bool"|…,
                   source: sourceId, preview?: sourceId, add?: "task"|"project"|"session", parent?: fieldName, exclude?: fieldName,
                   required?: bool, options?: [string], unscoped?: bool, validate?: "number"|"json"|"required", type?, multi?: bool, hint? }
                 // kind: picks source, completion, path picker and validation; empty falls back to type, then source
                 // parent: picking this field sets that one to the record's ancestor of its kind; that one's value scopes this field's options
                 // exclude: never list that field's record or its descendants (a task is never its own parent)
                 // add: text matching no option is taken as the name of a new one, created on submit under the form's context
                 // key: the one highlighted char in the field's button; pressing it focuses the field
Action         = { name, mode, defaultKey, does, command? }   // does: prose; command: the bus command the key runs
```

- keys: a page's key comes only from `Page.key`; registering the page derives its `normal`-mode action (`{ name: page.id, defaultKey: page.key, does: "Show <title>" }`), so no other table declares page letters. An action's `does` is always prose and `command` names the bus command it dispatches; a key with no `command` is handled by the shell. Key resolution is one function over every registered action, config's own included: the override in `config.keys[mode][name]`, else `defaultKey`; any registered action can be remapped, and `mtm list-actions` and `mtm config init` list them all. Startup fails when two pages share a key or two actions in one mode share a default key (`Registry.Check`)

- relationships
  - `Page belongs_to :unit`
  - `PaletteCommand has_one :command`
  - `Form has_many :fields; Form has_one :command (submit)`
  - `Modal has_one :source; Modal may replace :modal`

### 5.1 Feature inventory (B-22 stage 1)

- `go run ./scripts/inventory > docs/inventory.json`: one `Feature` per page, command, action binding, palette entry, modal, grouping, form, registry kind, exported struct under `internal/` and `// feature: concept.<area>.<name>` comment, sorted by id; two runs are byte-identical
- registry kinds come from the mtm binary's own `mtm docs`, `mtm commands` and `mtm list-actions` (isolated home, `MTM_BIN` or a fresh build); go/ast only places each definition at its declaring literal and reads structs and concept comments
- `hash` covers the definition and its defining text (the key/value pair, composite literal or call around the literal); a mark made against another hash is `changed`
- `docs/review.yaml` holds the marks in YAML flow style (also JSON), `{}` today; `-review [-marks PATH]` prints `unreviewed<TAB>id` lines, then `changed<TAB>id`
- `scripts/e2e-inventory.sh` checks it in `e2e-all.sh`; stage 2 (store table, `Status(id)` gating, Features page) is not built

```js
Feature = { id: "action.reviews.mark", kind: "page"|"command"|"action"|"palette"|"modal"|"grouping"|"form"|"kind"|"feature"|"struct"|"concept",
            name, desc?, surfaces?: ["tui:reviews:r"], file, line, hash, fields?: [{ name, type, doc? }] }
Mark    = { [featureId]: { status: "keep"|"cut", on: "2026-10-19", hash, note? } }
```

## 6. Units

### 6.1 daemon — `internal/daemon` (unchanged)

- `Call`, `Subscribe`, `Presence`, `StreamPane`, typed verb wrappers
- contract = `tuios list-verbs`

```js
Event            = { seq, type, session, window, data }
StartAgentParams = { session, agent, name, cwd, prompt, ready_timeout }
```

### 6.2 panes — live pane registry

- one listing shared by every consumer (replaces 9 `panes.List` sites)
- `All()`, `ByID(window)`, emits `panes.changed`
- listens: `agent-state`, `window-closed`, `window-created`, `session-*`
- activity/transcript rendering stays here
- `HiddenTasks` moves out (needs store) → work unit

```js
Session = { name, attached, dir, branch, panes: [Pane] }
Pane    = { session, id, name, state, harness, foreground, cwd, message, blocked_by,
            is_agent, ready, needs_you, queued, unread, working, last_activity, idle_ms, stale }
```

- `Session has_many :panes`
- `Pane belongs_to :session`

### 6.3 work — projects, tasks, assignments

- tables: `projects`, `tasks`, `assignments`, `active`
- a project is a git repo
  - new project: pick an existing repo (the common case) or a folder, which the mtm turns into one with `git init`
  - on pick the mtm lists the repo's worktrees (`git worktree list`) into `trees`; the person picks the default
  - every new agent or terminal starts in the active project's chosen tree unless the form says otherwise; `Start(spec).cwd` defaults to it
  - `settings` per project: default tree, default harness, default preset
- the pin: the mtm is always pinned to one task; its project is the task's root project
  - `active` is one row and never empty once a task exists; `Scope` is derived from it
  - set through the project/task tree (`P`): one fully expanded tree of actual projects, tasks, and subtasks; no repeated `+ new` rows
    - `o` / `O` insert a draft task below the selected subtree / above the selected task; on a project, either inserts its first root task
    - `e` / `i` edit a task title or project name inline; `Escape` or `Enter` finishes the line and returns to navigation; empty new lines are dropped
    - new task lines support `Tab` / `Shift+Tab` nesting within the same project; existing task ownership is unchanged
    - `Ctrl+s` submits every insertion and rename together, preserves the pin, and closes only on success; validation or concurrent tree changes retain the draft with an error and write nothing
    - `Escape` in normal mode discards the entire draft without writes; navigation and line editing never persist changes
    - `Enter` on a clean task pins it; on a clean project it pins the first open task or creates one if needed; dirty drafts must be saved or discarded first
    - project creation and repository scanning remain palette actions with native filesystem pickers, not tree rows
    - `a` inserts a child at the end of the selected row (on a project, its last root task)
  - bulk-create tree (B-37; palette `Bulk create`, and `alt+m` / `+ add new…` in a form while `work.bulk_create` is on, the default): the same tree and draft, for adding only
    - opens holding every project, task and subtask, existing rows dim and read-only (never renamed, moved or deleted from here), the cursor on the form's parent or the pin
    - `o` / `O` add a sibling below the selected subtree / above the row; `a` adds a child; on a project `o` / `O` add a new project, since a top-level line is always a project
    - `Tab` / `Shift+Tab` nest and unnest new rows: a new project nests into the project above as its last root task, a new root task unnests into a project; children follow
    - `e` / `i` / `Enter` rename a new row; a new project is created by name with no repository, attached later through `Set project tree`
    - `Ctrl+s` saves every new project and task in one `work.apply-tree-draft` (`project_adds` first), says `Added N projects, M tasks`, and from a form restores it with the parked field set to the first new task; `Esc` in NORMAL discards
    - `work.bulk_create` off keeps the mass-add outline below; CLI: `mtm task tree`, `mtm task bulk-create --json '{revision, project_adds, adds, sibling_orders}'`
  - almost everything the UI shows is under the pin: panes in the rail, context, captures, history, reviews, queue, vim sessions, notes
  - not scoped: the project switcher, Assign, help, palette, and settings; the tasks/projects page follows its scope/all toggle
  - every scoped page has two modes: `scope` (rows under the pin, the default) and `all` (every row); `S` toggles, per page, and the title line reads `all` while it is on; the pin itself does not change
  - a pane assigned to another task is not in the rail; a count in the title line says how many are hidden
  - unassigned panes, terminals, and agents are excluded while scoped to a project or task; only ALL shows them, with black text on red, in the `No Task` group at the bottom
- first run, no projects: the mtm asks for a list of dirs (`repo_roots`), scans them for git repos, and offers each repo as a project to create; the scan is repeatable from the palette
- inheritance: anything created with a parent takes the parent's task and project (a context item from an assigned pane, a note on a task, a queued prompt on a task, a subtask); the child stores no project of its own
- every task has a project: a root task stores `project_id`, a subtask inherits its parent's; there is no projectless task
  - `work.add-task`, `work.move-task`, `work.patch-task`, `work.mass-add` and `work.apply-tree-draft` reject a root task without a project
  - mass-add and the tree editor take the project from the selected row or the pin; with no projects at all, the tree editor says to add a project first
- themes
  - a project or task gets a random theme from the unassigned pool at creation
  - a theme counts as assigned while its owner is in a non-final state; final states: `done`, `skipped`
  - unassigned pane rows in ALL draw black on red, including selected rows and secondary lines
- rail row for a pane: first 4 chars of the project name in the project's theme, then the task title in the task's theme
- task edit (`e`): title, parent (fuzzy), status; normal form `ctrl+h` / `ctrl+l` walk the parent up / down; input mode uses `alt+h` for parent-up so `ctrl+h` remains Backspace
- rules owned here (today split ui/web)
  - `Resolve(window)` → task/project
  - `Target(task, project)` by id or name
  - assign new window
  - two-miss pruning, fed by `panes.changed`
  - themes: 16 colours, free-colour pool, glyph sections
  - snoozes, `easy`, status, `MoveTask`
  - `ProjectOf(task)` walks parents to root (subtasks store no project_id)
- commands: `work.add-project`, `work.patch-project`, `work.set-tree`, `work.pin`, `work.scan-repos`, `work.add-task`, `work.patch-task`, `work.move-task`, `work.assign`, `work.unassign`, `work.approve-assign`, `work.snooze`, `work.mass-add`, `work.tree-snapshot`, `work.apply-tree-draft`
- emits: `projects.changed`, `tasks.changed`, `assignments.changed`
- pages: tasks (`T`, scoped); modals: switch (`P`), task tree (`w`), Assign (`a`, global)
- task tree modal (`w`, from any item): the lineage of that item only
  - rows: the project, then each ancestor down to the item's task, then that task's own subtasks
  - siblings at every ancestor level are hidden; a hidden count on the ancestor row (`+19`) expands them on `l`, `h` folds again
  - never the whole project; the tasks page is for that

- Assign (`a`, or palette): a global inventory, independent of the active pin
  - assignable items include panes and agents, saved Vim sessions, context items, and notes, never tasks; historical captures, history, and reviews retain their recorded ownership
  - one row per canonical working directory, deduplicated and sorted; each row shows the containing Git repository, proposed new or existing project, and affected items
  - discovery is read-only: no projects, assignments, repositories, or worktrees are created
  - approve one row or all displayed eligible rows; approval creates or reuses one project per repository and assigns the displayed items
  - missing/non-Git directories and items without a working directory remain visible with a reason and an explicit existing-project picker
  - approval rechecks ownership and directory evidence; it never replaces an assignment made since preview or includes items discovered after approval
  - directory evidence uses canonical paths: `/tmp` and `/private/tmp` aliases do not invalidate approval, but a different resolved directory does
  - cancellation and completion preserve the current page and pin

```js
Project    = { id, name, theme: Theme, status, created, repo: path, trees: [Tree], default_tree: path,
               settings: { harness?, preset? } }
Tree       = { kind: "worktree"|"clone"|"dir", path, repo?, branch? }
Active     = { task_id, tree: path }                   // one row; project is ProjectOf(task)
Settings   = { repo_roots: [dir], stale_after, … }          // scan roots for first run and palette
Task       = { id, parent_id, project_id, title, position, theme: Theme, status, easy?, snoozed_until?, created, updated }
             // exactly one of parent_id / project_id is set; a root task always has a project
Assignment = { [window]: { session, task_id, project_id } }
Theme      = { color: ansiName, glyph }
AssignItem      = { kind, id, label?, session?, window?, cwd? }
AssignCandidate = { id, label, cwd?, repo?, tree?, project_id?, items: [AssignItem], reason? }
AssignApproval  = { candidate: AssignCandidate, project_id?: explicitExistingProject }
TreeDraft  = { revision, project_adds: [{ ref: "draft:p1", name }],          // new projects, no repository
               adds: [{ ref: "draft:1", title, parent_id, project_id }],     // project_id may be a project_adds ref
               task_renames: [{ id, title }], project_renames: [{ id, name }],
               sibling_orders: [{ parent_id, project_id, refs: [existingID, "draft:1"] }] }
```

- `Project has_many :tasks (top-level only)`
- `Task belongs_to :project (root only); Task belongs_to :parent (Task); Task has_many :subtasks`
- `Assignment belongs_to :pane (by window); belongs_to :task or :project`
- `Project has_one :theme; Task has_one :theme`
- `Project has_many :trees; Project has_one :default_tree (Tree)`
- `Active belongs_to :task; Active has_one :project (through task); Active has_one :tree`
- Tree draft submission uses a coherent snapshot revision and one transaction; stale revisions reject the entire draft. New child parent IDs may refer to earlier draft rows.
- Sibling `position` preserves above/below insertion after reopening; legacy rows retain created/ID ordering, ordinary creation appends, and touched draft sibling groups receive consecutive positions. Creation timestamps are not repurposed as ordering keys.

### 6.4 prompts — presets, queue, stash, dispatch, agent start

- tables: `prompt_presets`, `queued_prompts`, `prompt_stashes`, `prompt_launches`
- rules: apply preset (prefix once, cwd), queue target, `Start(spec)` (start agent, record submission, assign), `Dispatch(q)`, new terminal (create session if missing), status text (incl. `BlockedBy`, `PromptNote`)
- commands: `prompts.start-agent`, `prompts.new-terminal`, `prompts.queue`, `prompts.dispatch`, `prompts.add-preset`, `prompts.stash`
- emits: `queue.changed`, `presets.changed`
- modals: prompt modal (`p`), presets list, queue list
- composer: `p` shows multiline Prompt and Settings inputs; `tab` switches inputs, `enter` inserts a prompt newline or chooses a settings value, `ctrl+s` submits now, and `ctrl+q` queues
- queue reconciliation: a daemon-owned receipt is removed when its target definitively reports `window_not_found` or `session_not_found`, as when the daemon no longer lists the receipt. Saved unsent prompts remain; transport and other errors retain receipts and remain logged. Nothing is resubmitted automatically.
- composer completion: `@` paths, `/` skills and commands, attachments; an option that names a task or pane previews its recent scrollback beside the list
- a preset is a prefix prepended once plus an optional cwd; the composer offers the presets and `+ new preset…`
- launch forms list Host before Destination, Assignment and agent controls; host aliases include configured addresses, and the local daemon shows `TUIOS_HOST` only when its socket matches the current pane, otherwise its socket endpoint
- the prompt composer overrides the ordinary form layout; `alt+/` recalls advanced Host, Destination, Assignment, cwd, preset, attachment and approval fields, and `esc` returns to the two-input view
- Settings shows Harness, Model, Effort and Speed columns from real catalogs; fuzzy queries match values, not descriptions, with live weighted recall suffixes and visible searchable disambiguation tokens; selection stores the original value, not its token
- `prompts.launch-defaults` supplies both form seeds and backend defaults: explicit inputs and restored drafts precede focused-item evidence, scoped successful-launch modes, then project/preset/environment defaults; remote host histories and paths stay separate
- `prompt_launches` records successful terminal/agent settings without prompt text or attachments; queuing and ordinary activity do not count as launches; `_focus_window` supplies evidence without choosing an existing destination
- `work.directories` ranks canonical local repository/worktree and app-tracked directories without excluding unrelated projects; manual paths and the native directory picker remain available; remote hosts never receive local suggestions or local native picker results
- speed is harness-specific: Codex `fast` sets its fast service tier, Claude `normal`/`fast` sets session `fastMode`, and OMP exposes its documented OpenAI service tiers; model/account restrictions still apply, unsupported controls error, and existing-window sends cannot change speed
- `prompts.agents` lists all 24 bundled TUIOS harness IDs, not an installation guarantee; custom executable commands remain accepted; `prompts.models` reads installed OMP/OpenCode/Codex catalogs where available and falls back to the public models.dev text-model catalog with availability/compatibility explicitly unverified
- thinking and approval options are harness-specific; unsupported CLI controls report an error rather than sending invented flags; catalog subprocesses and HTTP reads have finite deadlines and do not run inference
- remote destinations use same-connection `open-host-connection` routing; remote session/window IDs are host-qualified in pane listings, queue receipts and assignments; remote launches do not use local MCP setup or local working-directory validation/defaults
- depends on: daemon, work (`Target`), panes

```js
Preset        = { id, name, prefix, cwd, created }
QueuedPrompt  = { id, text, preset, task_id, project_id, cwd, host, session, agent, window, name, model, thinking, speed, approval, args: [string], ready_timeout, created }
StashedPrompt = { draft_id?, text, draft?, saved }
StartSpec     = { host?, session, window?, agent, model?, thinking?, speed?, approval?, args?: [string], name, cwd, prompt, preset?, task?, project?, attach?: [path] }
```

- `QueuedPrompt belongs_to :preset; belongs_to :task or :project; belongs_to :pane (window)`
- `StashedPrompt belongs_to :draft`

### 6.5 context — items, extraction, actions

- table: `context_items`
- `Extract`, `Unwrap`, `Gather` from scrollback / activity / transcript / command-history
- actions: copy, insert, open, terminal (side effects: clipboard, opener processes)
- commands: `context.extract`, `context.patch`, `context.delete`, `context.insert`, `context.open`, `context.copy`
- emits: `context.changed`
- listens: `window-closed` (items outlive panes; nothing pruned)
- page: context (`C`); two scopes: the pane the mtm is on, and all
- an item inherits the task and project of the pane it came from, at extraction
- sortable (created first), filterable, groupable like the rail; actions: copy, insert, open, open with…
- `Item` gets its own type, no longer an alias of the store row

```js
ContextItem = { id, kind: "link"|"file"|"dir"|"pr"|"prompt"|"command", text,
                session, window, pane, project_id, task_id, starred, pinned, created }
Source      = { kind, session, window, pane, at }
Counts      = { scrollback, activity, transcript, history, total }
```

- `ContextItem belongs_to :pane (window); belongs_to :task or :project`

### 6.6 history + reviews

- table: `history` (append-only), `review_marks`
- history: `events.Handler`, batches live events → one insert a second
- harnesses/agents must capture turn-based information: one delivered user request through the agent’s final answer, not each model response or tool cycle
  - automatic continuations and retries keep the turn open; OMP completes on `agent_end` only when `willContinue !== true`, never on its lower-level `turn_end`
  - retain the full prompt and final response, stable turn and conversation IDs, harness, pane/session, start/completion timestamps, transcript reference, and final-message metadata; clipped activity summaries are not the archive
  - `history.capture-turn --json -` persists a start and then its completion as immutable, correlated records; repeated identical delivery is idempotent, conflicting reuse of an ID is rejected, and task ownership stays with the start
  - queued input is not a delivered request; steering delivered during an open turn belongs to that turn; aborted/error stops do not enter the completed review queue
- reviews: a view over history; only the mark is stored
  - packaged harness captures correlate prompt-submitted and response-completed by turn ID; uncorrelated native activity groups responses until the next prompt
  - `<task-notification>` prompt keeps turn open
  - listed when not awaiting and window subagent count == 0
- `Turns(window)`, `Mark(id)`
- commands: `reviews.mark`, `reviews.unmark`
- emits: `history.changed`, `reviews.changed`
- pages: history, reviews, Turns tab
- history is a timeline of everything the mtm manages: prompt submitted, response completed, command run, session start, subagent start/stop, assignment, task status change, capture written, reminder fired
- review queue: a turn is listed only after it finishes, in finishing order, oldest at the top, newest at the bottom; it lives in the top section of the mtm rail (§7.1), not only on its own page
  - highlighting an entry previews it in the detail area and does not mark it reviewed
  - giving the detail area focus (`l` or `right`) on an entry marks it reviewed; `r` toggles the mark by hand either way
  - a reviewed entry stays in the mtm rail while highlighted and leaves it 3s after the cursor moves off it; the reviews page still lists it
  - a reviewable document (an md or html the agent wrote) is an entry too, once it exists
  - documents with equal timestamps order by path

```js
HistoryEntry   = { id, kind, at, observed, source, source_id, session?, window?, summary, detail, turn?: HarnessTurn }
HarnessTurn    = { id, harness, conversation_id, session, window, prompt, response?,
                   started_at, completed_at?, transcript_path?, response_message? }
Review         = { id: promptHistoryId, turn_id?, session, window, pane, harness, prompt, response,
                   responses: [ReviewResponse], output?, started_at, completed_at, reviewed_at }
ReviewResponse = { id, at, text }
ReviewMark     = { [historyId]: reviewedAtMs }
```

- `Review belongs_to :pane (window); has_many :responses (HistoryEntry); has_one :mark; has_one :output (Capture, -turn)`
- `HistoryEntry belongs_to :pane (window)`

### 6.7 captures — files + autocapture

- folder: `~/.local/share/matomeru/captures`
- autocapture: `events.Handler`, writes `-turn` / `-cmd` on turn or command end
- terminal snapshots supplement the structured harness turn records in history; they do not replace the full prompt and final answer
  - packaged turn snapshots link to their review by session, window ID, and turn ID, not an exact timestamp or a mutable pane name
- `List`, `Read`, `Dir` (no store import)
- commands: `captures.capture`, `captures.delete`
- page: captures

```js
Capture = { name, path, size, modified, session, pane, window?, turn_id?, kind: "turn"|"cmd"|"" }
```

- `Capture belongs_to :pane (session+pane name)`

### 6.8 notes

- table: `notes`
- visible notes: a parent and a child see each other's; a task sees its own, its ancestors', its descendants' and its project's
- commands: `notes.add`, `notes.patch`, `notes.delete`

```js
Note        = { id, text, task_id, project_id, created, updated }   // exactly one id set
VisibleNote = { note: Note, via: "own"|"parent"|"child"|"project", owner: name }
```

- `Note belongs_to :task or :project`

### 6.9 reminders

- table: `reminders`
- loop delivering due reminders → becomes events-style unit with its own goroutine (step 9)
- commands: `reminders.add`, `reminders.patch`, `reminders.delete`, `reminders.toggle`
- a due reminder shows in the terminal and as an OS notification

```js
Reminder     = { id, title, message, interval: seconds, enabled, next, last, created }
ReminderEdit = { title?, message?, interval?, enabled? }
```

### 6.10 config — `internal/config` (unchanged)

- `~/.config/matomeru/config`, key action table generated from config definitions, `Binding(mode, action)`
- registry reads `Action` from here

```js
Config = { keys: { [mode]: { [action]: key } }, … }
Action = { name, mode, default, does, command? }   // see §5: overrides apply to every registered action
```

### 6.11 setup, complete, focus (unchanged leaves)

- setup: `Items()` table and CLI `mtm setup` (list), `mtm setup status`, `mtm setup install`, `mtm setup uninstall`
  - every required external setup asset (hooks, extensions, scripts, helpers, configuration templates) must be stored in this repo and embedded in the distributed binary; setup must work without a source checkout or a separate inbox installation
  - install materializes and configures the packaged files; no manual hook copying or shell edits are required for harness turn capture
  - installation is idempotent; status identifies missing, modified, conflicting, and migration-required files; uninstall removes owned files only, preserving unrelated configuration and rejecting unowned files/symlinks
  - the OMP integration captures delivered requests through final answers; setup records the installing executable and selected `-data` database, and replaces the older managed mtm activity reporter so completions are not duplicated
  - reload/restart OMP after installation; rerun setup if the mtm executable or database location changes; other harness adapters must follow the same terminal-turn and packaging contract
- complete: slash commands, `@` paths; shared by shells
- focus: idle/activity clock

### 6.12 vim — neovim sessions as mtm items

- a vim session is listed on the mtm pages beside panes, with the same rail row format
- opening neovim starts it in the active project/task's tree; a form may pick another tree
- commands: `vim.open`, `vim.list`
- sessions are discovered from mtm-owned metadata and session files

```js
VimSession = { id, name, path, project_id, task_id, cwd, created }
```

- `VimSession belongs_to :project; VimSession belongs_to :task (optional); belongs_to :tree`

### 6.13 downloads — `internal/downloads`

- lists the entries of the downloads directory, newest first by modification time; subdirectories are one row each and are not walked; dotfiles are hidden; a missing directory is an empty list
- directory: `MTM_DOWNLOADS_DIR`, default `~/Downloads`; it becomes the `downloads.dir` setting when the settings page (B-21) lands
- the tui watches the directory with fsnotify and emits `downloads.changed`; every read rescans, and opening the page reloads, so a missed event never leaves the list stale
- seen state persists in the `downloads_seen` table keyed by path + modified, so a file replaced under the same name is unread again
- commands: `downloads.seen`, `downloads.open` (OS opener: `open` on macOS, `xdg-open` elsewhere; the path must be an entry of the directory); source `downloads.list`; CLI concept `download` (`mtm download list` returns rows newest first)
- page `L` Downloads: rail row is the name (`✓` when marked) and `size · age`, prefixed `new ·` and styled unread until the row has been selected once; detail shows path, size, modified and state
  - `y` copies the absolute path through `context.copy`; `space` toggles a mark; `y` with marks copies every marked path, one per line, in list order, and clears the marks; marks are page state and clear when the page is left
  - `enter` opens the selected entry with `downloads.open`
  - new files insert at the top without moving the selection
  - notes on a download (B-05 owner kind `download`) wait for B-05

```js
Download = { id: path, path, name, size, modified: "2026-10-19T21:04:11Z", dir?, seen }
```

### 6.14 documents — `internal/documents`

- the md and html files agents wrote, read through the reviews unit's document listing (§6.6, `reviews.List`, kind `document`); the unit owns only their state in `documents_state`: `starred`, `read_at`, the context item a star made, the glow pane live mode reuses
- commands: `documents.star` (toggles, or `starred` sets), `documents.read`, `documents.open`; sources `documents.list` (scoped, starred first then newest) and `documents.preview`; CLI concept `document` (`mtm document list --task ID` returns rows with `starred` and `read_at`)
- a star adds a `document` context item on the document's task through `context.add`, so it shows on the context page and in the `STARRED CONTEXT` block of the task's detail and of its parent tasks' and project's detail (the context scope rule: an item shows on its own task and that task's parents, never on siblings); unstarring deletes it
- page `M` Documents, scoped: rail row is the name (`★` when starred) and `kind · age`, prefixed `new ·` and styled unread until opened live once
  - detail renders md through `glow -w <detail width>`; html, or a host without glow, shows the source
  - `*` stars; `y` copies the path; `enter` runs `glow -tl <path>` in a pane of the document's session (`mtm` when that session is gone), sets `read_at` and goes live on it like a pane: keys go to glow, `ctrl+a d` comes back to this page; the pane is reused on the next `enter` while it lives

```js
Document = { id: "document:<sha256>", path, name, kind: "md"|"html", session, window, pane, harness,
             task_id, project_id, starred, read_at, created }
```

### 6.15 AI and Git inventories — `internal/ai`, `internal/gitcatalog`

- AI (`F`) has Harnesses, Skills, Agents and Sessions subsections; harnesses are recognized commands, not installation claims; skills reuse structured local completion discovery with canonical file paths; agents retain live pane ownership
- AI Sessions are observed harness conversations from recorded turns, grouped by host, harness, conversation and event-time ownership; they are not a complete on-disk harness session inventory
- Git (`W`) has Repositories, Worktrees, Remotes, Branches and Commits; GitHub (`V`) shares the exact repository and branch sources, then adds live Pull Requests and the existing Watched PRs operations
- repository identity is the canonical common Git directory; worktrees share it, independent clones remain distinct; branch IDs include the full ref, and recorded commit provenance joins by repository and SHA
- live commits show the newest 100 per repository across refs; live GitHub PRs show up to 100 in all states per hosted repository through authenticated `gh`, retaining canonical clone IDs and project/task relationships; fork heads are not conflated with base-repository branches
- `mtm git <repos|worktrees|remotes|branches|commits> list`, `mtm github <repos|branches|inventory-prs> list`, and `mtm ai <harnesses|skills|agents|sessions> list` use explicit `--project` or `--task` scope; existing GitHub command/read contracts remain available
- Git and GitHub errors remain visible; read-only subprocesses have finite deadlines, never use remote cwd as a local path, and do not mutate repositories

## 7. Shells

### 7.1 tui — `internal/ui`

- keeps: `Model` as view state only (selection, scroll, modal slot, page, live)
- loses: domain logic (→ units), page enum (→ registry `Page`), closures over Model in forms (→ `Field.source`)
- one modal slot; `replace` or close; mass-add is the one parked modal
- shared list navigation applies to the rail, pages, modals, trees, palette, help, pickers, and autocomplete suggestions
  - normal mode: `j` / `k` move one item; `h` / `l` switch areas or fold / expand tree nodes
  - `d` / `u` move half a visible page; `ctrl+f` / `ctrl+b` move a full visible page
  - `g` / `G` jump to the first / last item; Home, End, PageUp, PageDown, and arrows remain available
  - `{` / `}` jump to the first item of the previous / next contiguous section; lists without sections jump to their first / last item
  - `ctrl+n` / `ctrl+p` move through items or autocomplete suggestions, including while typing
- text inputs use readline: `ctrl+a` / `ctrl+e` move to the current line start / end; `ctrl+f` / `ctrl+b` move one character; `ctrl+h` backspaces
  - printable keys remain text in input mode, including Vim motion letters and braces; readline takes priority over form and list actions
  - text buffers, filter queries, and pasted input share cursor-aware editing; live mode retains its own forwarding rules below
- forms: one engine (`internal/ui/forms`), drawn by the layout the setting `forms.layout` names (B-31, [design](plans/forms-redesign.md)); the next form opened uses a changed value, no restart
  - layouts: `list` (default: every field a row with its value, full width), `split` (field list left, the focused field's editor and options right), `modal` (centred panel over the dashboard), `inline` (the list in the detail area beside the rail; full width under 100 columns), `box` (the pre-B-31 compact form in the top eight lines with tab cycling, kept for compatibility); a layout is presentation only and one file implementing `Layout`
  - a form shows a title with the mode, a status line (the focused field's full value and hint, `new: <text> under <parent>`, `cleared: <child> not under <parent>`, or `! error`), one row per field `› t  label  value  path`, the focused field's options or editor under its row, and a key line
  - normal mode (`form-list`): `j` / `k` move the field cursor, `g` / `G` first / last; a field's letter edits it (letters skip `j k g G u d h l i c ' / ?`); `1`–`9` move the cursor to the Nth field; `'` labels every field and the next key edits it; `enter` / `i` / `/` edit the cursor field; `c` clears it and edits; `ctrl+s` submit; `esc` close
  - input mode: `tab` / `shift+tab` next / previous field; `ctrl+n` / `ctrl+p` move options; `enter` picks (or ends a one-line text) and returns to normal on the next field in list layouts; BOX keeps same-field input after picking until `esc`; selecting a parent can instead focus its new child
  - completion is fuzzy and ranked (exact, prefix, word, substring, subsequence over label, path and id), the current value first; moving through options previews the option's object: the rail selects it, the detail shows it
  - `alt+/` opens optional fuzzy field search from normal or input mode in every layout; `ctrl+n` / `ctrl+p` move matches, `enter` edits the selected field, and `esc` cancels; direct field shortcuts and focused value search remain available
  - field labels and value options show `‹suffix›` recall hints, recomputed as the query changes with the same matcher as filtering; `‹enter›` means unique, and `␠` means type a space, requiring the preceding character to end a word
  - hint search minimizes typing cost: repeating the previous key costs half another key, while every repeat still consumes a separate character; all eligible competitors participate, including offscreen values; `‹…›` marks unresolved hints when the bounded search cannot find a unique suffix
  - linkage is declared on fields: picking a child sets its `parent` field to the child's ancestor of that kind (a task sets the project to its root project); an explicitly chosen parent limits the child's options to records under it, direct children first, and clears a child outside it; a pinned default parent only sorts its children first
  - a task, project or parent field with no exact (case-insensitive) match shows `+ new <kind>: <text>` last and creates it on submit, parents first: the typed text is the name; a new task goes under the form's parent (the pinned task, or the field's chosen parent), a new project is a new project; the status reads `new: <text>` so it is never a surprise
  - required fields carry `*` in every layout; empty required values use a bold error style and `missing required`, while filled required values remain emphasized; validation checks the effective edited value and still applies numeric/JSON rules
  - explicit `assignment` fields replace task/project or parent/project pairs with one searchable project/task tree; selecting a task inherits its root project and does not open another field; selecting a project adds and focuses an optional Task field
  - explicit `destination` fields replace window/session pairs; Host comes first in launch forms, and a selected window inherits its host and session; `add: "session"` allows a selected or newly named session to open an optional Window/name field; a blank child creates a window, a matching child selects an existing window, and unmatched text names a new window; assignment-only destinations omit `add` and accept existing windows only, including windows outside the current task pin
  - leaving input mode or moving focus commits unmatched assignment text as a new project name and focuses its optional Task field; each newly named task adds/focuses a Subtask field, stopping at the first blank; typing and canceling create no work records
  - `alt+f` switches hierarchical options between tree and flat; flat rows keep their ancestry inline; filtering keeps matching descendants with ancestor context
  - `alt+c` cycles boolean and option values with wraparound; `alt+o` opens labeled choice mode; letters select a value, multi-letter labels address large lists, Enter confirms a shorter ambiguous label, and Escape cancels the chooser; arrows, Home/End and PageUp/PageDown navigate without consuming labels; cycle and letter choice show the committed value in normal mode unless a parent expands into a child input; these actions are remappable in normal and input modes
  - new work records use stable `draft:` references rather than names and save through one `work.apply-tree-draft` transaction, parents first; inline projects may have no repository, and duplicate task names remain distinct; only resolved command fields reach the final command
  - prompt drafts retain dynamic child rows and their text; asynchronous choices, file picks and completions use stable field identities; host/harness/model dependency changes reload relevant sources without resetting unrelated inputs
  - `+ add new…` or `alt+m` opens the bulk-create tree (§6.3) over the parked form for more than one item; with `work.bulk_create` off, the mass-add outline, where `tab` / `shift+tab` change nesting
  - delete confirmation defaults to `y`; `esc` closes the palette so `ctrl+p` can move up in it
- modal input library: every modal and form runs on one engine; a config of modes, bindings (key → action) and actions (action → method on the object); fed keys one at a time, it tracks the mode and the object
  - the shared modal input engine handles text; Neovim is a managed session, not an embedded form dependency
- the first shell row reserves the center for a bright, bold project glyph/name and task title; action-item count sits at the left, page scope/ALL and hidden-pane count at the right; the second row holds the application name and page tabs, and the dashboard starts on row three
- the pin is centered against terminal display columns with one-column edge padding and gaps; long labels and corner indicators truncate without wrapping; ALL reports zero hidden panes; `P` opens the switch modal from any page
- mtm rail layout (see [upstream annotated rail](../../znbu/docs/images/mtm-rail-annotated.png)): two sections, one list for `j`/`k`
  - top: the review queue, finished turns and documents under the pin, oldest first; focus on the right (`l`/`right`) marks the entry reviewed, preview does not
    - a reviewed entry lingers while highlighted and leaves the rail 3s after the cursor moves off it
  - bottom: active panes, agents and terminals still working or waiting, grouped as `o`/`O` says; ALL includes `No Task` last, scoped views exclude unassigned items
  - a pane moves from the bottom to the top when its turn ends, and back when a prompt is sent
- help line (last row): the bindings that apply to the current mode and the highlighted row, not a fixed list; `F1` / `?` open the full help modal
  - help matches the [approved reference](../../znbu/docs/images/help-good.png): centered `Keys` panel, thin border, readable headings, muted pink keys and aligned descriptions over the dashboard
  - wide terminals show two columns with separated groups; narrow terminals use one column; descriptions wrap instead of truncating
  - descriptions align per column: one key width per column, the widest key of any group in that column, so every group in a column starts its descriptions at the same x
  - every row keeps both borders in place at 80, 120 and 200 columns for every tab; displayed text drops Unicode variation selectors (U+FE0E/U+FE0F) because terminals disagree on their width, which shifted rows and leaked the border into the modal when an emoji pane title sat behind it
  - `tab` / `shift+tab` cycle overview and mode filters; `/` searches; navigation and section jumps select shortcuts; `enter` inspects the effective action
  - the footer shows selection and scroll position with a close hint; compact layouts retain the close hint; Escape restores the dashboard without changing its selection
  - help uses effective bindings, including remaps and the configured live leader; unbound actions remain searchable
- mtm page keys: `h` / `l` move between rail and detail; `{` / `}` jump by group (`No Task` is one); `o` / `O` cycle the grouping; `w` the task tree modal (lineage only, see §6.3); `e` edit
- stale panes: no activity past `stale_after` marks the row stale; it stays in its own group; a palette command closes them
- pages dispatch through registry: `keys`, `rail`, `detail`, `helpLine`
- pages may declare registry subsections; `[` / `]` switch subsections with independent filters, selection, scope and scroll; pane detail tabs retain their existing bindings
- subsection reads load lazily and refresh with `ctrl+r`; async results belong to their page/section request, and only live subsections opt into ticks (AI Agents, AI Sessions and Watched PRs); mutation refreshes preserve selection/filter/scroll without periodically rerunning Git/GitHub network inventories
- forms may declare a seed source; asynchronous defaults apply only to untouched values and recompute when their launch context changes
- live mode: `enter` on a pane goes live; the live screen draws in the detail area under a live bar, the rail stays; never full-screen on the mtm side
  - `ctrl+a` is the leader; the key after it is a command; every other key goes to the pane untouched, including `esc`
  - `ctrl+a d` detach (back to the mtm) · `ctrl+a j` / `ctrl+a k` next / prev pane · `ctrl+a Z` / `ctrl+a f` zoom / fullscreen the pane inside tuios (its own session, not the mtm) · `ctrl+a ctrl+a` types a literal ctrl+a · `ctrl+a ?` keys · `esc` after the leader cancels it
  - bindings live in config under mode `live`: leader, detach, next_pane, prev_pane, zoom_pane, fullscreen_pane, help
  - never a bare key as the exit: no held `esc`, no `ctrl+z`; the pane's program owns those
  - one input goroutine in order; `stream-pane` for the size lease and frames; `capture-pane` is the screen
- presence held by shell; transcript reader takes nonce as arg

```js
ViewState = { pin: Scope, all: { [pageId]: bool }, page: pageId, sel: { pane?: window, task?: id, ctx?: id }, scroll: { [pageId]: n },
              modal?: { def: Modal, state }, parked?: modal, confirm?, live?, status, filter?: query }
InputLib  = { modes: [name], mode: name, bindings: [{ mode, key, action }],
              actions: { [action]: (object, key) => void }, object }     // feed(key) → runs the bound action, may switch mode
```

### 7.2 web — removed for now

- not used; delete `internal/web`, `scripts/e2e-web.sh`, `scripts/wscheck`
- reinstate later as a shell over the bus and registry

### 7.3 cli (new)

- `mtm <unit> <command> --json '{…}'` generated from bus `list()`
- reads: `mtm <unit> list` per table
- one subcommand per concept (project, task, context, prompt, reminder, note, capture, vim), each mirroring its unit's commands, so an agent can drive the mtm; AGENTS.md says so
- `mtm list-actions`, `mtm config init`, `mtm docs` from the registry

## 8. Flows (who touches what)

- start agent from TUI
  - key → `Form form.start-agent` → submit `prompts.start-agent` → bus → prompts unit → daemon `start-agent` → `work.assign` (tx: assignments) → emit `assignments.changed` → shells re-read
- pane closes
  - daemon `window-closed` → runner → panes unit → `panes.changed` → work unit miss counter (2 misses → prune, tx: assignments) → `assignments.changed`
- turn ends
  - daemon `agent-activity` → runner → history (batch insert) + autocapture (file) → `history.changed` → reviews page re-reads `Turns`
- switch pin
  - `P` → full project/task tree → clean `Enter` → `work.pin` → tx: active → `active.changed` → every scoped page, including Tasks, re-reads with the new `Scope`
  - `P` → draft line edits / `o` / `O` insertions → `Ctrl+s` → `work.apply-tree-draft` → one transaction for names, tasks, and sibling order; pin unchanged
- cli patch task
  - `mtm work patch-task --json` → bus → tx: tasks → `tasks.changed` → TUI re-reads

## 9. Migration (from the report, step → verify)

0. delete `internal/web` and its suites → e2e-all minus web
1. `internal/core`: move the duplicated helpers out of ui → e2e.sh
2. pruning into core → e2e.sh
3. registry: pages/palette/groupings/modals/actions → e2e-help.py, palette checks
4. pages from table → e2e.sh page switches
5. one modal slot + field sources → e2e.sh forms, e2e-prompt-stash.sh
6. store per-table `Tx`, history append-only → every suite (seed helper updated once)
7. command bus + generated cli → new e2e-cli.sh
8. panes registry unit + `panes.changed` → e2e.sh, e2e-history.sh, e2e-review.py
9. wiring to cmd/mtm, reminders as unit → e2e-all

## 10. Open decisions

- [x] Preserve the repository module and paths: github.com/unixsuperhero/matomeru, Go 1.27.1, Bubble Tea v2, Lip Gloss v2, and SQLite only. No web UI or speculative JSON backend.
- [x] Workers use openai-codex/gpt-6.1-sol through the ChatGPT login, overriding the upstream model defaults.
- [x] The active pin is one persisted row per mtm database, shared by processes using that database. Its project is resolved through the task. Tasks follows the same per-page scope/all toggle as other owned content.
- [x] Scope is an explicit argument at registered read boundaries. Work resolves a subtree once into a ScopeSet; row membership checks perform no I/O. Empty Scope means all.
- [x] Projects record all discovered git worktrees and a selected default. Matomeru may initialize an explicitly chosen existing folder as a repo, but never creates a git worktree. Legacy tree paths migrate without filesystem mutation.
- [x] New project/task themes are randomly selected from the unused pool. Owners with done/skipped status do not reserve themes. Work owns the pool.
- [x] Commands retain unit.verb names. Concept-oriented CLI verbs are registry metadata over the same command bus. Registry types and definitions generate docs, actions, catalogs, and command discovery.
- [x] All modals/forms use a shared mode/key/action engine. Text stays in that engine; Neovim is not embedded into forms. Native OS pickers remain available for every filesystem field.
- [x] Panes uses one shared daemon snapshot. Scoped reads exclude unassigned items without exception; ALL includes them. Project switching and Assign remain global so hidden items can be found and assigned.
- [x] Child records store task ownership without duplicating the inherited project. Descendant notes use via=child; parent/own/project labels remain distinct.
- [x] Captures retain ownership in private file metadata beside the capture. Files without ownership metadata remain readable in all mode without guessing a current pane assignment.
- [x] Neovim session metadata and session files are mtm-owned, beside the selected database. Opening a session uses the active tree unless explicitly overridden.
- [x] A due reminder advances its schedule before external delivery. OS and session notices are independent; failures remain visible without repeatedly notifying the same occurrence.
- [x] Event envelopes are typed Go values with JSON-compatible payloads. Command history records command names and identifiers, not private argument bodies. Read-only commands do not generate command history.
- [x] TUI dispatch logs and worker slog diagnostics append to a private mtm.log beside the database, never to the terminal. One-shot CLI commands drain local events before exit. Shutdown stops producers, drains events, flushes history, then closes storage.
- [x] Live mode retains one ordered raw-input reader. Capture-pane supplies detail content; stream-pane supplies frames and the detail-sized lease. Remote zoom/fullscreen stays in the target tuios session.
- [x] Before remote zoom/fullscreen, live mode sends run-command FocusWindow with the selected pane UUID and waits for the renderer reply. The daemon-only focus-window reply does not acknowledge renderer focus. Both actions then use the renderer command path without timing delays.
- [x] Unknown leader commands are consumed with a visible status. Double leader forwards its literal key; leader followed by Escape cancels. Bare keys never detach.
- [x] Run builds and verification on the registered VPS through `scripts/verify-vps.sh`; independent runs execute concurrently in separate snapshots with uniquely named throwaway tuios daemons. No blanket host-wide verification lock. Local execution requires explicit permission; never use existing host sessions. Linux checks do not prove macOS-specific behavior.
- [x] Completed turns remain reviewable when a later prompt starts; only unfinished turns and turns awaiting subagent completion are excluded. Highlighting previews without marking; focusing the detail marks reviewed, and r toggles the mark.
- [x] A reviewed queue entry stays in the mtm rail while highlighted and leaves it three seconds after the cursor moves away. The reviews page keeps listing it.
- [x] Every task has a project. Root tasks store `project_id`; subtasks inherit it. Creation, moves, mass-add and tree drafts reject a root task without a project. Legacy projectless root tasks are adopted at startup by a project named `Unsorted`, created without a repository when none exists. Pathless legacy projects can attach an explicitly selected repository.
- [x] When the theme pool is exhausted, choose randomly among the least-used themes. Panes with no activity evidence begin aging at their first observation; streamed output refreshes that baseline without relisting.
- [x] Ownership pickers (project, task, parent, and project tree) offer all targets so forms can retarget across projects. The pin supplies defaults and the parent for newly typed tasks; content pickers retain their scope. Selecting a task first derives its project unless the user explicitly selected a conflicting project.
- [x] Background page/detail status refresh runs every thirty seconds. Raw output updates cached activity but bypasses shell notification queues and status reads, so it cannot displace reminder notifications. Semantic daemon events and live frames remain immediate. Refresh retains the active form, selection, and scroll.
- [x] Assignment pruning requires two distinct successful snapshots started after the assignment was written. Queued older snapshots cannot delete a newer assignment or override a pane known live in the current shared snapshot.
- [x] Close and overflow recovery reconcile two successful pane snapshots, allowing one transient split-list failure in three bounded attempts. Work requests overflow reconciliation after resetting its own observations so earlier dropped events cannot leave a closed assignment stuck. This is event-triggered, not an idle polling loop.
- [x] Assign groups by canonical cwd rather than item or repository. Multiple cwd rows in one repository reuse one project. Approval carries the exact displayed candidate snapshot, not a wildcard.
- [x] A task has no cwd. Assign offers panes, Vim sessions, context items and notes, never tasks; it does not infer ownership from the active pin. Projects themselves are ownership roots, not records assigned to another project.
- [x] Non-Git directories remain unresolved until an existing project is selected. Assign never calls git init; explicit Add project retains that separate capability.
- [x] Shared normal-mode list actions use the upstream Vim motions. Delete moves from `d` to the Delete key; mass-add moves from `ctrl+b` to `alt+m` in both form modes.
- [x] Readline is intrinsic text editing in the shared engine, like arrows and Backspace. In form input, parent-up uses `alt+h`; `ctrl+h` always erases text. Normal form parent-up retains `ctrl+h`. Keep `ctrl+h` distinct from `backspace` in configuration: Bubble Tea decodes raw BS as Ctrl+h and DEL as Backspace.
- [x] Lists share index movement and section boundaries. Page distances derive from visible rows, including group headings and multiline entries; section jumps select group starts and clamp at boundaries.
- [x] Forms with option lists reserve configured motion keys and display alternate field accelerators. Pure text forms retain field shortcuts. Native OS dialogs retain platform navigation.
- [x] `P` edits one initially expanded project/task tree. Only real rows are selectable; creation and repository scans stay out of the tree. `o/O` insert task siblings below/above, `e/i` rename, and Escape returns to navigation without saving. On a project row, insertion creates its first root task.
- [x] Tree edits remain an in-memory draft until Ctrl+s submits one atomic transaction. Escape in normal mode discards the draft. Saving retains the pin; clean Enter pins an existing row. A revision conflict retains the draft and error without partial writes.
- [x] Persist task sibling positions separately from timestamps. Draft insertion may nest new tasks, but does not reparent or reorder existing tasks. Legacy zero positions retain created-time/ID order until an insertion normalizes that sibling group.

## 11. Build and command reference

Requires Go 1.27.1.

```sh
go build -o mtm ./cmd/mtm
./mtm
./mtm docs
./mtm list-actions
./mtm config init
./mtm commands project
./mtm help task
./mtm task list --project PROJECT_ID
```

Use `-socket`, `-data`, and `-captures` to select the daemon and local data. Defaults remain `~/.local/share/matomeru/mtm.db`, `~/.local/share/matomeru/captures`, and `~/.config/matomeru/config`.

Default page keys are `D` mtm/panes, `T` tasks, `C` context, `H` history, `R` reviews, `A` captures, and `L` downloads. `P` opens the task/project switcher; `a` opens global Assign; `S` toggles scope/all for the current scoped page. `?` or `F1` opens generated help. `mtm list-actions` is the complete effective key reference, including unbound actions.

Forms open in normal mode. A field's letter enters input mode on that field; Escape returns to normal before closing the form. `forms.layout` picks where the form draws (`list` by default; `box` keeps the top eight lines with the dashboard below). Native path pickers remain available through the configured picker binding.

Lists use `j/k`, `d/u`, `ctrl+f/b`, `g/G`, and `{` / `}` for section navigation. Delete uses the Delete key. In text inputs, `ctrl+a/e` reach line edges, `ctrl+b/f` move the cursor, and `ctrl+h` erases a character; `ctrl+n/p` navigate suggestions. Use `alt+m` for mass-add.

`P` opens the full tree without creation rows. Use `o/O` to insert, `e/i` to edit, Escape to return to navigation, and Ctrl+s to save the complete draft. Escape again discards it. Add project and repository scan remain in the palette.

Live mode uses the configured leader, initially Ctrl+A: d detaches, j/k switch panes, Z/f act inside tuios, ? shows keys, repeated leader sends the literal leader, and Escape after the leader cancels. Bare Escape and all non-command input belong to the pane.

CLI reads default to all rows; `--task` and `--project` supply explicit scopes. Mutations use the same command bus as the TUI. Empty creation targets use the active pin where the unit supports a target. See generated command help for actual payload fields.

## 12. End-to-end verification

```sh
# Linux-compatible cases; context/open-with and native_picker require macOS.
scripts/verify-vps.sh env E2E_OUTLINE_CASES=repo_discovery,pin_scope,assign,switch_creation,compact_forms,mass_add,form_jump,form_child_parent,form_parent_scope,form_create,form_layout_toggle,lineage,grouping_stale,catalogs_help,shared_navigation,readline,prompt_composer,history_review,descendant_notes,reminder_delivery,vim_sessions,downloads bash scripts/e2e-all.sh

# Only when local verification is explicitly authorized:
E2E_OUTLINE_CASES=context,native_picker bash scripts/e2e-run.sh outline
```

The VPS runner snapshots current source and runs `scripts/e2e-all.sh` with an enforced timeout, without a shared verification lock. Independent runs can overlap; each has its own compiler temporary directory, screen/layout artifacts and log. Suites build the executable, isolate data and uniquely named throwaway tuios servers, verify their sockets differ from existing sessions, and stop those servers afterward. Shell fixtures replace provider inference. Live input and rendering use an external PTY and actual capture-pane readback. Acceptance covers scope, Assign, repositories, forms, navigation, readline, catalogs, timeline, and Neovim. ANSI capture verifies black-on-red unassigned rows. Native macOS dialogs and platform-specific key handling require separately authorized macOS verification; Linux results do not prove them.

Without an explicit case selection, `scripts/e2e-all.sh` includes every outline case. On Linux, native macOS cases fail their prerequisites rather than silently passing or being skipped. Report the Linux and macOS results separately; both are required for complete platform coverage.

## 13. B-21 settings: a page plus per-service config areas

- unit `internal/settings`: table `settings`, one JSON row per section + key, read through the store like reminders (§6.9); config (§6.10) supplies defaults under `settings.defaults` and is never written by the app
- secrets are never stored here: `gh` and the MCP servers carry their own credentials; anything else comes from the environment or the harness configs B-12 writes
- the schema (`settings.Definitions`) declares type, default, hint and the `needs` label of every known key; unknown section.key pairs are accepted and stored with a stable shape (whole numbers → int64, lists → []string)
- a required setting that is empty reports `needs: <label>`; `settings.needs` lists them so a service page can show a `needs: github username` line and skip the lookup that depends on it, never error
- commands: `settings.set { section, key, value }` (strings are coerced to the declared type: `true`/`false`, integers, one list entry per line or comma), `settings.save { section, …keys }` (writes only the rows whose value changed; `updated` moves only on those), `settings.unset { id | section, key }` (restores the default), `settings.init` (stores every default without touching an existing row, so running it twice leaves `updated` unchanged)
- emits `settings.changed`
- sources: `settings.list` / `settings.detail` (effective rows: default overlaid with the stored row; honour `--section`), `settings.sections`, `settings.needs`, `settings.definitions`
- Go readers for other units: `Get`, `String`, `Bool`, `Int`, `List`
- page `settings` on `E` (normal mode), not scoped: every section with its keys and current values, one row per key; `enter` or `e` edits the row through `form.settings.set`, `Delete` restores the default after confirmation, `,` opens the row's section form
- `,` (`settings-section`, normal mode) on a page whose id or unit names a section opens that section's form prefilled with the current values; elsewhere it lands on the settings page
- forms: `form.settings.set` and one `form.settings.<section>` per section (shared form engine, one field per key, list keys as multi-line fields); submitting a section form calls `settings.save`, so only the changed rows are written
- palette: `Settings…` lands on the settings page from every page (`ui.page`); `<section> settings…` opens that section's form; `Set a setting`; `Write default settings`
- CLI: `mtm settings list [--section identity]`, `mtm settings needs list`, `mtm settings set --json '{"section":"identity","key":"github_user","value":"instajosh"}'`, `mtm settings save --json '{"section":"slack","oncall_group":"@oncall"}'`, `mtm settings unset --json '{"id":"notify.os_enabled"}'`, `mtm settings init`; `--section` is a generic read filter carried as `core.ListFilter`

```js
Setting    = { id: "section.key", section, key, value, updated }
Definition = { section, key, type: "text"|"bool"|"number"|"list", default, hint?, required?: label }
View       = { ...Setting, type, default, stored, required, needs?, hint?, title, status, text }   // effective row
Need       = { section, key, needs }
// sections: identity (name, github_user*, slack_user, slack_user_id*), slack (oncall_weeks*, oncall_channels,
//   oncall_group, watch_dms, watch_mentions), github (review_query, oncall_review_query, watch_interval_seconds,
//   my_prs_poll_seconds), linear (enabled), schedules (default_timeout_seconds), notify (os_enabled, indicator_char),
//   palette (open_in_search)        // * required
```

- verified by the `settings` outline case (`scripts/e2e-all.sh` suite "B-21 settings")

## 14. B-25 command palette opens in search mode

- `:` opens the palette with the filter focused and empty (`modalState{ id: "palette", searching: true, filterCursor: 0 }`); the first keystroke filters, no `/` needed; `ctrl+n` / `ctrl+p` move the highlight while typing and `enter` runs the highlighted command
- `esc` once leaves search for the palette only, keeping the filter and the highlight so `j` / `k` and the other modal keys work; `esc` again closes. With nothing typed yet `esc` closes at once, as before. Other modals keep closing on `esc` while searching
- `/` in navigation re-enters search with the cursor at the end of the filter; `/` typed into an empty palette filter while searching is ignored, since it is the search key
- the behaviour is behind `palette.open_in_search` (B-21 settings table, default on): `mtm settings set --json '{"section":"palette","key":"open_in_search","value":false}'` restores the old opening, navigating with no filter line until `/`
- `openPalette()` reads the setting through the `settings.list` source each time; an unreadable setting keeps the default
- e2e: the shared `palette()` helper sends `/` only when the palette opened without a filter line; the `palette-filter` readline case types straight after `:`; verified by the `palette_search` outline case (`scripts/e2e-all.sh` suite "B-25 palette search")

## 15. B-12 mtm as an MCP server (§7.4 mcp: a shell over the bus, like the CLI)

- `internal/mcp` is a shell, not a unit: it owns no table and dispatches through the command bus and registry sources, so every tool is also a CLI command and every call lands in history
- `mtm mcp serve` speaks MCP (newline-delimited JSON-RPC 2.0) over stdio: `initialize` (echoes a known client protocol version, else 2025-06-18), `notifications/initialized`, `ping`, `tools/list`, `tools/call`, empty `resources/list` and `prompts/list`; protocol mistakes are JSON-RPC errors, tool failures are results with `isError` and a `code: message` text
- identity is bound server-side at construction from the pane's environment (`TUIOS_SESSION` + `TUIOS_PANE_ID`; `MTM_SESSION` / `MTM_WINDOW` override for bridges and tests) and never read from tool arguments; the pane's task, project, cwd and harness are resolved through `work.Resolve` on every call, so a reassignment applies to the next call; outside a pane `whoami` reports `bound: false` and pane-bound tools refuse with `no_pane`
- every tool call writes one `command-run` history entry `mcp.<tool>` with the pane's session, window, task and project; the wrapped bus command adds its own entry as usual
- the history entry is written by the server process itself, so it survives with no TUI running; the live reload comes from the harness's own hooks, which report the MCP call as `tool_done` activity (the daemon only emits an `agent-state` event on a state change, not on a new message); after a mutation the server also flushes history, waits for its own document entry, and puts a short message on the pane row (`set-agent-state working`), best effort
- tools: `whoami {}`, `task_list { scope?: "pin"|"all", status? }` (→ `work.tasks`), `task_done { task_id?, note? }` (→ `work.patch-task` + `notes.add`), `task_status { task_id?, expected_version, status, summary?, verification?, commit?, blocker? }` (optimistic check against the task's `updated`; `done` requires a summary; evidence is saved as a note), `task_note_add { owner?: {kind, id}, text }` (→ `notes.add`), `context_add { kind?, text }` (→ `context.extract` with text; refuses text without an item), `document_report { path, title?, kind?, summary? }` (an existing `.md`/`.html`; emits a `tool_done` activity with the file so the reviews unit lists it as a document under the pane's task, which is where documents live until B-11 lands), `report_progress { message }` (→ daemon `set-agent-state`)
- passthrough tools over units that merge later are listed only while their bus command exists: `todo_list` / `todo_note_add` / `todo_claim` (`todo.list`, `todo.note-add`, `todo.claim`, B-13) and `action_item_create` (`actions.create`, B-15); their names are provisional until those units register
- `mtm mcp tools` prints the same list as `tools/list`; `mtm mcp whoami` prints the bound identity; `mtm mcp config [HARNESS]` prints the server entry (this binary with `-data` and `-socket`, then `mcp serve`) and what a harness needs; `mtm mcp install HARNESS` writes it; errors are structured like the CLI's
- agents started by mtm (`prompts.start-agent`, the composer) get the server configured for their harness before the first prompt, through a prepare hook on the prompts unit; the start result's status says `mtm MCP server configured for <harness>`; a failure is reported there and never blocks the start
  - `claude`: a mtm-owned file `<data dir>/mcp/claude-mtm.json` passed as `--mcp-config`, so no user or project config is touched
  - `codex`: `-c mcp_servers.mtm.command=… -c mcp_servers.mtm.args=[…]` on the command line
  - `omp`: `mcpServers.mtm` merged into `~/.omp/agent/mcp.json` (`PI_CODING_AGENT_DIR` / `PI_CONFIG_DIR` honoured); other servers and keys are kept
  - `opencode`: `mcp.mtm` (type local) merged into `$XDG_CONFIG_HOME/opencode/opencode.json`
  - the harness is the program's base name after any `env` prefix; an unknown harness gets nothing
- the pane env is enough for identity, so no token is needed over stdio; an HTTP transport is a later step only if a harness refuses stdio

```js
Identity      = { session, window, task_id?, project_id?, cwd?, harness?, bound }
Tool          = { name, description, inputSchema, command?: busCommand, needs_pane }
Paths         = { executable, data, socket? }
HarnessConfig = { harness, args?: [string], file?, entry?, written }
```

- verified by the `mcp_server` outline case (`scripts/e2e-all.sh` suite "B-12 mcp server")

## 16. B-35 Stuck-pane check — `panes.stuck-check`

Replaces the B-01 fleet orchestrator (`cmd/orchestrator`, `internal/orchestrator`, removed). The stuck rules are a lookup of the panes unit that the schedules unit (§20) runs on an interval; every match is an action item (§19). No markdown parsing, no mail loop, no state file.

```js
StuckRule  = { id: "same-state" | "waiting-input", threshold: seconds }   // defaults: same-state 1200, waiting-input 600
StuckCheck = { schedule_id?, rules?: [StuckRule] }  →  { found: newItems, new: bool, items: [StuckMatch] }
StuckMatch = { session, window, name, rule, since, evidence, action_id, new }
ActionItem = { service: "mtm", action_type: "stuck", source_url: "pane://<session>/<window>?rule=<id>&since=<state_at>",
               title: "Stuck: <pane> (<rule>)", task_id?, project_id?, extra: { rule, evidence, session, window, since } }
```

- `same-state`: an agent pane in `working` since the daemon's `agent_state_at` for at least the threshold, with no commit in its cwd since then (`git log -1` in the pane's cwd)
- `waiting-input`: an agent pane in `needs_input` for at least the threshold
- panes report `state_at` (Unix ms the agent entered its state); the check is stateless, so `mtm panes stuck-check` from the CLI and the schedule agree
- one item per pane, rule and state episode: a repeat folds into the same item (`new: false`); dismissing it silences that pane until its state changes, which gives a new `since` and so a new item
- palette: `Check for stuck panes` runs it once; `Watch for stuck panes` adds the schedule `Stuck panes` (lookup, every 60 s); nothing is scheduled until then
- the third rule of the old orchestrator (the same tool call failing three times) is not carried; it needs the pane tail and harness `meta.now`

### Verification

`E2E_OUTLINE_CASES=stuck_check bash scripts/e2e-run.sh outline`: an agent pane held `working` past a one-second threshold with no commit raises exactly one item on two runs; a commit after it entered the state raises none; a `needs_input` pane raises a `waiting-input` item; a dismissed item stays dismissed on the next run.

## 17. B-13 Todo unit and page: items that are not yet tasks

A todo is lighter than a task: no project required, no panes, a priority and free text, promotable to a task. Agents browse todos for easy ones, research them and leave notes, or resolve them outright. The unit lives in `internal/work` (table `todos`, owner `work`) so it shares the work transaction, the pin and the task creation path; the shared parser of `znbu/docs/todo.md` is `internal/todomd`, used by the import here.

```js
Todo     = { id, external_id?: "B-nn", title, text, priority: "p1"|"p2"|"p3", status: "idea"|"ready"|"claimed"|"review"|"done",
             owner?, project_id?, task_id?, promoted_task_id?, notes: [string], created, updated }
Promoted = { task: Task, todo: Todo }
Import   = { path, imported, updated, ids }
```

- page `todos` on `B`, title Todos, not scoped: rows by status (done last), then priority, then age; the rail shows title and status, the detail shows the fields, the text and the notes newest last
  - `enter` promotes the selected todo to a task under the pin, keeping the notes; `n` adds, `e` edits, Delete removes with confirmation; the todo page is listed with the other pages in help and `mtm list-actions`
- commands `todos.add`, `todos.patch` (fields, or `note` to append one dated line), `todos.claim` (only a `ready` todo, sets `claimed` and the owner, else `not_ready`), `todos.promote`, `todos.delete`, `todos.import`; emits `todos.changed`
- CLI concept `todo`: `mtm todo add|patch|claim|promote|delete|import --json '{…}'`, `mtm todo list`; `mtm work todos list` reads the same table
- promote: the task takes the todo's title; it goes under `parent_id`, else as a root task of `project_id`, else under the todo's own task or project, else under the pinned task; with nothing to promote into it fails with `invalid_args`. The todo's text and then each note become notes of the new task, in order, through the notes unit's writer (work never imports notes); the todo closes as `done` with `promoted_task_id` and `task_id`; a second promote fails with `already_promoted`
- task status rule: a new task is `todo` unless a pane or agent is assigned to it at creation, then it is `active`; `work.assign` moves a `todo` task to `active` and records the status change in history like any other. `todo` joins the offered statuses; `done` and `skipped` stay the only final states. The rule changes existing behaviour (new tasks were `open`), so it is toggled by the setting `new_task_status` (default `todo`); until the settings page (B-21) lands the toggle is the environment variable `MTM_NEW_TASK_STATUS` read at startup, e.g. `MTM_NEW_TASK_STATUS=open` keeps the old default
- import: `mtm todo import --json '{"path":"…/todo.md"}'` upserts one todo per `### B-nn` item keyed by the item id: title, body text, priority (unknown → `p2`), status (`parked` or unknown → `idea`), owner and notes; a second import updates in place and reports `updated` instead of `imported`. `znbu/docs/todo.md` stays the human-facing list; the repository's `docs/todo.md` copy is what the e2e imports

### Verification

The outline case `todos` (`scripts/e2e-todos.sh`, also inside the full outline suite) checks: add without a project, list order by priority then age, invalid priority and status rejected, a dated note appended by patch, claim and the `not_ready` refusal, promote under the pin with the text and notes moved onto the task as own notes in order, `already_promoted`, an explicit project promoting to a root task, the `todo` status for a task created without a pane and `active` once a pane is assigned, the import of the checked-in `docs/todo.md` reproducing every item's title, status, priority and notes with a second import updating in place, and the page on `B` with `/` filtering and `enter` promoting the selected row.

## 18. B-28 Provenance on every record: turn, pane, task, project, commit, PR

Cross-cutting. Every row that comes out of a turn or a check links back to where it came from, so a PR can be traced to the turn that wrote its commits, the task that turn was on, and the project.

```js
Provenance = { turn_id?, session, window, task_id, project_id, commit?, branch?, pr_url?, at }   // core.Provenance
// embedded as `provenance` on: history Entry (turns and every activity row), context Item, Note, Todo, Capture (in its
// private metadata file), Review (turns and documents), ReviewMark, Commit, PR
Commit     = { sha, repo, branch, message, author?, at, provenance }      // history unit, table commits
PR         = { url, repo?, branch, title?, state, at, provenance }         // history unit, table prs
Trace      = { id, kind, chain: [{ kind: "pr"|"commit"|"turn"|"pane"|"task"|"project"|…, id, label? }] }
```

- filled at write time by `internal/provenance`: session and window default to the env-bound pane (`TUIOS_SESSION`, `TUIOS_PANE_ID`) so CLI and MCP writes made from an agent's pane carry it; task and project come from the pane's assignment when the row names none; the turn is the pane's turn in progress; commit and branch come from the pane's tree. The two lookups are registered at startup, the open turn by history and the pane owner by work, so no unit imports another to stamp its rows
- the turn id is the history id of the turn's prompt entry, the same id the review queue lists; history keeps a per-pane open-turn cache fed by prompt and completion entries and primed from the store; a `<task-notification>` prompt does not open a new turn
- commits and PRs: `code.record-commit { sha?, repo?, branch?, message?, session?, window?, task_id? }` records HEAD of the repo (default: the pane's tree) with the open turn, pane, task and project; `code.record-pr { url, branch?, repo?, title?, state?, … }` links a PR to its branch and takes task, project, turn and commit from the pane, else from the newest recorded commit on that branch. `mtm code list` prints both tables; `mtm code record-commit|record-pr --json`; a git `post-commit` hook or the agent itself calls record-commit (the full code unit of the upstream outline §6.13, with head moves and PR polling, is still open)
- `mtm code trace --json '{"id":"…"}'` prints the chain for any id: a PR url → its commits on that branch → turn → pane → task → project; a commit sha or unique prefix, a turn id, any note, todo, context item or history id with a provenance, a task or a project. `mtm trace <id>` as a bare subcommand belongs in `cmd/mtm` (lane 2) and is an alias of this read
- detail views show a `FROM` block (turn, pane, task › project, commit, PR) on context items, history entries, captures and todos; the jumps from each line are open
- documents reported by B-12's `document_report` get their provenance from the reporting pane like any other write; documents derived from tool calls carry the tool entry's provenance today

### Verification

The outline case `provenance` (`scripts/e2e-provenance.sh`, also inside the full outline suite): a scripted turn on an assigned pane is its own provenance and records the tree's commit and branch; a note, a todo, a context item, a capture and a commit written from inside that pane during the turn carry the identical turn, pane, task and project; `mtm code list` shows the commit's turn and task; a PR recorded from the branch carries the same task and project, with or without a pane; `mtm code trace` prints PR → commit → turn → task → project in order and traces a note id, failing `not_found` otherwise; the completed turn in the review queue carries it; a write after the turn ends has the pane and task but no turn; a document written by a tool call and a con…

## 19. Action items — `internal/actions` (B-15)

Everything that needs the user's attention, from any service, in one table, plus the one-character global indicator.

- table: `action_items`; `action_settings` (one row, `notify`); `action_todos` (stub todos until the todos unit, B-13, is wired; its import migrates them)
- commands: `actions.create` (dedupe on `service` + `source_url`: a repeat refreshes title/text and reports `new: false`; `reopen: true` un-dismisses), `actions.seen`, `actions.dismiss`, `actions.promote` (`to: "todo"|"task"`), `actions.promote-todo`, `actions.promote-task`, `actions.open`, `actions.configure`
- reads: `actions.list` (rows: unseen first, then seen, then resolved; by service, newest first), `actions.detail`, `actions.indicator`, `actions.settings`, `actions.todos`
- CLI concept `mtm action …`; MCP `action_item_create` (B-12) maps onto `actions.create`
- attention: an item needs attention while it is neither dismissed nor promoted; seeing it (opening, `actions.seen`) never clears it
- promote to todo calls `todos.add` when the bus has it, else writes `action_todos`; promote to task calls `work.add-task` under the pinned task, else the pinned project, unless `parent_id`/`project_id` is given
- `actions.open` marks the item seen, then hands `source_url` to `open`/`xdg-open` (http(s) only)
- OS notification on a new item: `actions.configure {"notify": true}`; off by default; failures are events, never command errors

```js
ActionItem = { id, service: "slack"|"github"|"linear"|"agent"|"schedule"|identifier, source_url, title, text,
               action_type: "pr-review"|"pr-status"|"oncall"|"mention"|"dm"|"thread"|"ticket"|"report"|"other",
               category?, task_id?, project_id?, schedule_id?, created, updated, seen_at, dismissed_at,
               promoted_todo_id?, promoted_task_id?, extra: {} }
Indicator  = { lit, count, unseen, mark: "●N" | "" }
```

- page `actions` (`I`): rail rows `title` / `state · service · action_type`; detail shows service, type, state, URL, stamps, a `FROM` block (schedule, task, project) and the text
  - page keys are registered as registry actions in mode `actions`: `enter` open, `x` dismiss, `t` promote to todo, `c` promote to task (`d`/`T` from the item text clash with half-page-down and the Tasks page, so the free letters are used)
  - `Enter` on any page whose unit registered an `<keys>.open` action dispatches it (shared `pageOpen` in the shell)
- the indicator: the shell reads `actions.indicator` on every reload and appends `mark` to the Actions tab title, the first tab after the pin, so it shows on every page at a fixed position; the title line itself belongs to lane 1's `view.go` and gains a dedicated slot when that merges. Items created from another process (CLI, agent) appear on the next reload: an event, `ctrl+r`, or the 30 s tick
- wiring: `cmd/mtm` is owned by lane 2 tonight, so `reminders.New` builds and registers the actions unit through `internal/reminders/attach.go`; lifting it into `cmd/mtm/wiring.go` is the merge step
- e2e: `action_items` in `scripts/e2e_attention.py` (joined to the outline matrix)

## 20. Schedules — `internal/schedules` (B-20)

Recurring prompts, lookups and commands on an interval, every run recorded, a prompt chained onto a lookup that found something. The reminders unit (§6.9) keeps its own loop; schedules is a sibling unit with the same advance-before-run rule.

- tables: `schedules`, `schedule_runs` (the last 500 runs)
- commands: `schedules.add`, `schedules.patch`, `schedules.delete`, `schedules.toggle`, `schedules.run` (run now, synchronous, returns the run record)
- reads: `schedules.list` (rows with a `status` line: kind · every N · next in / due / off / running · last outcome), `schedules.history` (newest first), `schedules.detail`
- CLI concept `mtm schedule …`; `mtm schedules history list` for the run history

```js
Schedule  = { id, title, interval: seconds (≤ 30 days), timeout: seconds (default 300, ≤ 3600), enabled, next, last, created, updated,
              run: { kind: "prompt", target: StartSpec | { window }, text }
                 | { kind: "lookup", command: "github.check"|"slack.check"|…, args: {} }
                 | { kind: "command", name, args: {} },
              on_result?: { kind: "prompt", text, target? },
              window?: last prompted pane, last_run_id?, last_outcome?, last_error? }
RunRecord = { id, schedule_id, title, kind, started, finished, duration_ms,
              outcome: "ok"|"found"|"nothing"|"failed"|"timeout"|"skipped", summary, error?, window?, chained?, result?, manual? }
```

- the loop ticks every second; a due schedule advances `next` before it runs, so a failure never repeats the same occurrence; a schedule already running is skipped, never queued; every run gets a context deadline of `timeout` seconds
- prompt: `prompts.submit` with the target (a pane `window`, else StartSpec fields that start an agent) and the text; the pane of the last run is remembered, and the next run is `skipped` while that pane is working, awaiting, or has subagents
- lookup: the command receives its args plus `schedule_id`, so the items it creates carry the schedule id; it reports `found: N`, `new: bool` or `items: […]`; `found` chains `on_result` as a prompt run
- command: any bus command with args
- every run emits `schedules.ran` and a `command-run` event with source `schedules`, summary and outcome, so `mtm history list` shows it; failures show on the row (`last_error`) and in the run list, with no notification
- page `schedules` (`Z`): `enter` runs now, `t` toggles; the detail shows the definition, next/last, the prompt or lookup, the last error and the last ten runs
- flat form fields (`kind`, `text`, `command`, `window`) build `run` for the palette form; the CLI passes `run` directly
- wiring: hosted by `internal/reminders/attach.go` like §19 until `cmd/mtm` merges; the loop starts with the TUI, so `mtm schedule run` is the CLI path and prompt runs from the CLI need a refreshed pane list
- e2e: `schedules` in `scripts/e2e_attention.py`

## 21. GitHub review requests — `internal/github`, `internal/oncall` (B-17)

- `internal/oncall`: the window shared by the slack and github checks. Table `oncall_settings`; command `oncall.configure`; read `oncall.settings` (adds `active` and `until`); CLI `mtm oncall configure`, `mtm oncall list`

```js
Oncall = { mode: "auto"|"on"|"off", start: "YYYY-MM-DD" (a Monday, local), weeks: 1.., channels: [name], tag: "@oncall" }
// active: mode on → true, off → false, auto → start ≤ now < start + weeks·7d
```

- `internal/github`: tables `github_settings`, `github_state`, `github_prs` (B-18); commands `github.check`, `github.configure`, `github.install-schedule`; reads `github.settings`, `github.state`, `github.queries` (the argv the next check runs); CLI `mtm github check|configure|install-schedule`, `mtm github state list`, `mtm github queries list`

```js
GitHubSettings = { user: "instajosh", review_query: "extra gh search terms", oncall_query: "team-review-requested:org/team …",
                   oncall_repos: ["org/repo"], poll_interval: 300 }
CheckResult    = { found, seen, items: [url], oncall, queries: [[argv]] }
```

- `github.check` runs `gh search prs --review-requested=<user> --state=open --limit 100 --json …` (never team requests), plus, while oncall is active, a second search built from `oncall_query` and `repo:` terms for `oncall_repos`; the criteria are settings, not code
- every PR becomes `actions.create {service: github, source_url: url, action_type: pr-review, category: review-requested|oncall}`; the PR url is the dedupe key, so a repeated check reports `found: 0`; a PR in both searches is one row; the schedule id flows through the lookup args
- `gh` runs with a 60 s deadline; a failure is the structured error `gh_failed` and is written to `github_state.last_error`, visible to the page and `mtm github state list`
- `github.install-schedule` adds the `github.check` lookup schedule once, at `poll_interval`; running it again returns the existing id
- a follow-up schedule that asks an agent to review a PR and write a report is `on_result` on that schedule (§20), linked from the item once documents (B-11) exist
- e2e: `github_reviews` in `scripts/e2e_attention.py` with a PATH `gh` stub that records argv and answers from a fixture

## 22. Slack monitoring — `internal/slack` (B-16)

Mentions, DMs, threads the user is in, and during the oncall window every message in the oncall channels and every mention of the tag, captured and assessed into action items (§19) whose `source_url` is the permalink.

- tables: `slack_settings`, `slack_messages` (captured messages, deduped on permalink), `slack_state`
- commands: `slack.configure` (username, DMs, threads, interval, fixture path, and the oncall fields forwarded to `oncall.configure`), `slack.capture` (store and classify messages), `slack.assess` (one `actions.create` per unassessed message), `slack.check` (the lookup: read, capture, assess), `slack.open`, `slack.install-schedule`; reads `slack.settings` (also `mtm slack settings`), `slack.prompt` (also `mtm slack prompt`), `slack.queries`, `slack.messages`, `slack.state`, `slack.list`
- CLI concept `mtm slack …`

```js
SlackSettings = { username, user_id?, watch_dms: true, watch_threads: true, fixture_path?, interval: 300 }   // + oncall: §21 Oncall
Message       = { id, channel, channel_id?, user, text, ts, thread_ts?, permalink, dm?, participants?,
                  kind: "mention"|"dm"|"thread"|"oncall", reason, captured, assessed_at?, action_id?, schedule_id? }
Queries       = { oncall, username, terms: ["@user", "dms", "threads", tag?], channels: [oncall channels while active], tag? }
```

- two paths, both ending in `actions.create`
  1. MCP path: a lookup schedule runs `slack.check`; tonight it reads the captured messages from `fixture_path` (no slack, glean, linear or github MCP call has been captured yet, so B-14 replay has nothing to learn from); once one real call is captured the fixture reader is replaced by the replay
  2. agent path: `slack.install-schedule` adds a prompt schedule whose text `slack.prompt` generates from the current queries; the prompt tells the agent (a pane with the slack MCP attached) to answer only with `action_item_create` calls or nothing
- the fixed assessment (`classify`): inside the window, a message in an oncall channel or mentioning the tag is `oncall`; a DM is `dm`; `@username` (or `<@user_id>`) is `mention`; a reply in a thread whose participants include the user is `thread`; everything else is dropped, so the oncall window changes which channels the next check keeps
- `slack.check` records `slack_state` (captured, found, oncall, channels, last error) and fails with `slack_failed` when the source is missing
- page `slack` (`Q`): the first row is the settings summary (`@user · oncall on/off · channels`) whose detail shows the window and the last check; then the captured messages, newest first, `kind · channel · new|assessed|action`; `enter` opens the permalink
- open: captured messages are kept in `slack_messages`, not as context items of kind `slack`, because the context unit has no add command tonight; adding one (or B-28's provenance pass) moves them
- e2e: `slack_monitoring` in `scripts/e2e_attention.py`; a live run against the real slack MCP is verified the first morning it is available

## 23. My PRs — `internal/github` (B-18)

The user's open PRs and drafts, watched ones polled in one request, every change an action item.

- table `github_prs`; commands `github.refresh-mine`, `github.poll`, `github.watch`, `github.snooze`, `github.open`; reads `github.list` (open rows, snoozed hidden), `github.prs` (every row), `github.detail`; `github.install-schedule {"which": "mine"|"poll"}` adds each lookup once at `poll_interval`

```js
MyPR = { id: node id, url, number, repo, title, draft, state: "OPEN"|"MERGED"|"CLOSED", ci: "pending"|"pass"|"fail"|"unknown",
         checks: [{name, state, url}], reviews: [{who, state}], review_decision?, comments, mergeable?, last_change,
         watching, snoozed_until?: local midnight (ms), discovered, polled?, updated_at }
```

- `github.refresh-mine`: one `gh search prs --author=@me --state=open --limit 100 --json …` (drafts included, `isDraft` kept); new rows start unwatched with `ci: unknown`; rows the search no longer returns are marked `CLOSED` and leave the list
- `github.poll`: every watched, unsnoozed, open PR in one `gh api graphql -f query=… -F ids[]=…` nodes query (comments count, last 30 reviews, the head commit's status rollup and check contexts); never one call per PR; no watched PR means no call
  - the first poll of a PR is its baseline; afterwards each difference is one `pr-status` item whose title names the change: `ci` (`pending → pass`, `pass → fail`, …), `comment` (n new), `review`, `approval`, `merged`, `closed`, `conflicts`; `source_url` is `url#<kind>-<poll ms>` so each change is its own row; the item asks for the OS notification (`notify: true` on `actions.create`) because the PR is watched
- `github.snooze` without `until` hides the row until the next local midnight; the list compares `snoozed_until` to now, so the row returns on its own
- page `github` (`V`): rows `repo#n title` / `draft? · ci state · n approved|reviews · n comments · conflicts? · watching`; `enter` opens, `v` toggles watching, `z` snoozes (the item text's `w` is the tree key)
- the poll interval is `github_settings.poll_interval` (default 300 s, minimum 30)
- e2e: `github_prs` in `scripts/e2e_attention.py`: three watched PRs, one `gh api graphql` argv with all three ids, a CI change in the stub's next answer creating exactly one item, persistence across a restart, a snoozed row returning when its time passes

## 24. B-06 — Pane detail: tab bar with a live Screen tab first

Supersedes the pane-row detail and the live-mode drawing rules in §7.1; the leader semantics, the stream lease rules and the review-queue rows stay.

- a pane row's detail is a tab bar: `1 Screen · 2 Activity · 3 Transcript · 4 Turns`, drawn at the top of the detail with the pane's `session › name`, its assignment (project glyph and name › task), its directory, `stale <age>` when stale and the last agent message beside it; the shown tab is bright and underlines when the detail has focus
- Screen is the default tab and is read-only: the pane's rendered screen from `capture-pane` (visible, ANSI kept, control sequences stripped), truncated to the detail width; it follows the bottom until the user scrolls up, `G` follows newest output again; a pane taller than the detail shows its bottom rows while following
- the Screen tab redraws when the daemon's `output` stream says the pane printed (the shell subscribes to `output` for the selected pane only; one capture in flight, one queued) and re-reads once a second as a safety net; a capture older than five seconds never blocks the next one
- keys on the panes page while a pane row is selected, registered as `panes`-mode actions by the panes unit: `1`–`4` pick a tab, `[` / `]` previous / next tab, `tab` / `shift+tab` cycle tabs instead of toggling focus, `J` / `K` scroll the detail half a page; with the detail focused `j` / `k` scroll a line, `g` / `G` jump to the top / follow the bottom
- the chosen tab is remembered per pane for the life of the shell: it survives refreshes, daemon events and re-selection; a pane not yet visited opens on Screen
- Activity shows the pane header fields and the activity log; Transcript the header and the transcript (or why it is unavailable); Turns the header and the finished turns under the pin
- `enter` on a pane goes live on the same Screen tab with the keyboard routed to the pane: the tab bar stays, the live bar appears under it, and the pane gets a size lease for the rows below both; `ctrl+a d` drops the keyboard and the detail rests on the Screen tab with its scroll; `ctrl+a j` / `ctrl+a k` go live on the next / previous rail pane without leaving
- the rail never changes width or selection between browsing and live; the detail is never full-screen except through `ctrl+a Z` / `ctrl+a f` inside tuios
- review and vim rows keep their own detail (no tab bar)
- creating a pane shows it: when the shell dispatches `prompts.start-agent`, `prompts.submit`, `prompts.new-terminal` or `vim.open` it switches to the Panes page first, measures the Screen tab body (the detail column by the dashboard rows under the tab bar, with no modal) and sends it as `cols` / `rows`; the unit creates the window, then sizes its PTY to that area with the daemon's `resize` verb (a session created on the way is born at that size; a failed resize is noted, never fatal); when the result arrives the shell selects the resulting pane's row (the new one, or the existing pane a composer prompt went to) on its Screen tab, following output, so the program is laid out for exactly the area it is shown in. The CLI takes the same `cols` / `rows` and leaves the size alone when they are absent

```js
CreateSpec = { ...StartSpec | TerminalSpec | OpenSpec, cols?: int, rows?: int }   // the shell fills cols/rows from screenArea()
PaneJump   = { session, window, tries }                                           // selected on the Panes page once its row arrives
PaneDetail = { tab: "screen"|"activity"|"transcript"|"turns", follow: bool, scroll: int,
               live: { keyboard: bool } }
Screen     = { id: selection, lines: [ansi line], err?, pending, since, dirty }   // one per shell, for the selected pane
```

Verification: `E2E_OUTLINE_CASES=pane_tabs,shared_navigation,create_jump bash scripts/e2e-run.sh outline` and `bash scripts/e2e-run.sh live`; `scripts/e2e-all.sh` runs the `B-06 pane tabs` suite; `create_jump` proves the Panes-page jump, the selected row and the PTY size of a terminal and of Neovim created from the shell and the CLI.

## 25. B-10 — Review accordion: the detail for a pane with unreviewed turns

The Turns tab of §24 is the accordion. A pane whose finished turns include an unreviewed one opens on it (the tab is then remembered for the pane); every other pane opens on Screen. B-09 decides which rail section such a pane sits in; this section owns only the detail.

```js
Accordion  = { pane, rows: [TurnRow | ContextRow], auto_reviewable_count, cursor: row id, follow: bool, expanded: { [row id]: bool } }
TurnRow    = { id: "turn:" + (turn_id ?? record id), records: [review id], prompts: [text], responses: [text],
               started_at, completed_at, reviewed_at?, auto_reviewable, starred, project_id, task_id }
ContextRow = { id: "context:" + item id, item: ContextItem, starred }
ReviewStar = { id: turn_id ?? review id, starred_at }           // table review_stars, unit reviews
```

- rows are the pane's review records grouped by harness turn id (a record without one is its own row), oldest at the top, all collapsed when the accordion opens; several records with one turn id are one row that lists every prompt and every response
- the accordion opens when the detail reaches the pane and closes when the detail leaves it; expanded state is a map keyed by row id, so a re-read of the records never closes a row; the cursor is re-found by id, `g` turns follow off, `G` turns it on
- with the detail focused: `j` / `k` and the shared motions move the cursor, `{` / `}` jump between the turn group and the context group, `enter` / `space` toggle the cursor row, `y` copies its prompts and responses through `context.copy`, `*` stars it, `x` marks every auto-reviewable row reviewed; `x` also works from the rail while the tab shows
- opening a row marks each of its records reviewed (`reviews.mark`); nothing is marked by showing the tab or moving the cursor
- auto-reviewable: an unreviewed row with later turns after it, which most likely was read outside mtm; such rows take a darker background and a line above the list names the mass key and the count; the most recent turn is never auto-reviewable
- stars: `reviews.star` / `reviews.unstar` take a review id or a turn id and store the star under the row's key; `reviews.list` reports `starred` and `starred_at`; the reviews page and the review queue show `★` and the reviews page lists starred rows first, finish order inside each group
- every row carries the task and project captured with its prompt (falling back to the pane's assignment) and shows them when expanded
- under the turns, `CONTEXT · from this pane`: the context items whose sources include this pane, newest first, one row per kind and text; `*` on one toggles `context.patch { starred }` in place
- a starred context item shows under `STARRED CONTEXT` in the detail of the task it is on and of every direct parent (the task chain and the project); the tasks page reads `context.list` under the row's scope, which is that subtree, so siblings and cousins never see it
- keys registered by the panes and reviews units: `*` star (modes `panes` and `reviews`), `x` mark auto-reviewable (`panes`)

Verification: `E2E_OUTLINE_CASES=review_accordion bash scripts/e2e-run.sh outline`; `scripts/e2e-all.sh` runs the `B-10 review accordion` suite. Two records with one turn id come from two conversations reporting the same harness turn id, the only path `history.capture-turn` allows.

## 26. B-09 — Pane lifecycle in the rail: working at the bottom and locked, review at the top, rest in the middle

Replaces the two-section rail rule in §7.1 ("mtm rail layout … two sections"). The leader semantics, grouping (`o`/`O`), `No Task` last and the help line stay.

```js
RailSection = "review" | "panes" | "working"
PaneRow     = Pane & { _section: RailSection, _review_count?, _review_at?, _review_prompt?, _working_since? }
Lifecycle   = prompt submitted → agent state working → "working" (bottom, locked, submission order, newest at the very bottom)
            → turn ends → "review" (top, finish order, pronounced style ● and a background)
            → every accordion row opened → "panes" (middle), once the rail focus has moved to another row
```

- the rail is one list for `j`/`k` with three sections, top to bottom: `─ Review ─`, the panes groups `o`/`O` choose (`No Task` last), `─ Working ─`; `{` / `}` treat the review and working sections as groups
- working: a pane is there while its agent state is `working` (agents only; a terminal after a command stays in the middle, its command is not a turn). Order is the time the shell first saw the pane working, oldest first. Rows are locked: the detail keeps the tab bar but shows `Locked while the agent works … press U to unlock`, no screen is captured and no accordion drawn; `U` unlocks that row until the rail focus leaves it, then it locks again on its own
- review: one row per pane with at least one unreviewed, non-document review record under the pin (never one row per turn); the row keeps the pane's label and adds `N turns to review · <latest prompt>` on its second line; ordered by the latest unreviewed finish time, oldest first, so a pane that just finished lands at the bottom of the section. Document reviews stay their own rows in this section with the open / `r` flow and the three-second linger of §6.6. Focusing a pane row shows the accordion of §25; the Screen tab stays reachable through the tab bar
- panes: everything else, grouped as `o`/`O` say; a pane whose latest turn finished no longer disappears from the rail
- a pane whose last unreviewed turn was just opened stays in the review section while the rail focus rests on it (`reviewSticky`) and drops to the middle on the next `j`/`k`/jump, so the row never moves from under the cursor; moving to working happens at once, even while focused
- key registered by the panes unit: `U` unlock (`panes` mode); `u` remains half-page-up

Verification: `E2E_OUTLINE_CASES=rail_lifecycle,history_review,shared_navigation bash scripts/e2e-run.sh outline`; `scripts/e2e-all.sh` runs the `B-09 rail lifecycle` suite. The cases drive the agent state through `set-agent-state` because a prompt sent with `p` only reaches the pane; the harness reports `working`.

## 27. B-38 — Panes rail as a nested tree below the pin

The middle section of the panes rail (§26) nests panes as project › task › subtask. It is grouping 0 while `panes.rail_tree` is on (the default); `o` / `O` cycle on to the four flat groupings (project, session, state, task) and back. Off, `o` / `O` cycle the flat groupings only.

```js
PaneRow = Pane & { _tree_path: ["project:p1", "task:t1", "task:t2"], _tree_names: ["mtm", "forms", "layout"], _tree_pos: 7 }
FoldRow = { _kind: "fold", id: "task:t2", _fold_name: "layout", _fold_count: 3 }   // id is the folded path below the pin
```

- the tree starts one level below the pin: pinned to a task, its subtasks are the top level; scoped to a project, its tasks; `S` (ALL) starts at projects
- panes assigned to the pinned node itself lead the tree under the node's name; every other pane sits under one heading per level of its path, indented by level, in tree order (task position), siblings by heading
- a row in the tree names the pane in its task's colour; the headings carry the project and task
- `z` folds the selected row's innermost group into one row `▸ <name>` with `N panes folded`; `z` or `enter` on a fold row unfolds and selects its first pane; `Z` folds one level up; folding is per page state, not stored
- `{` / `}` jump between groups, one per distinct path; review and working keep their places above and below the tree; a filter shows every match unfolded
- keys registered by the panes unit: `z` fold, `Z` fold-up (`panes` mode)

Verification: `E2E_OUTLINE_CASES=rail_tree bash scripts/e2e-run.sh outline`. The outline matrix sets `panes.rail_tree` off for the legacy cases (`E2E_RAIL_TREE=true` runs them with the tree); `rail_tree` turns it on for itself.
