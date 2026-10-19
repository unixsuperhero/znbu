# Modular deck: outline

Working outline of the redesign in [the modular report](../reports/2026-10-18-modular-redesign.md). Nested lists, shapes, relationships. Fill in details under each node.

Phase 2 follow-ups, not needed for the first build: [outline-phase2.md](outline-phase2.md).

Conventions: shapes are js-style; `?` = optional; relationships read like Rails (`belongs_to`, `has_many`, `has_one`, `through`). `[ ]` marks a decision still open.

## 0. Rules every unit follows

- a unit = one package, one concept, its tables, its rules
- talks to others only via: command bus (writes), event runner (reads), narrow interfaces it was handed
- never imports a shell (`tui`, `cli`)
- never touches view state (selection, scroll, modal)
- every list read takes a `Scope`; a unit answers only the rows under it (`Scope{}` is everything)
- registers definitions (pages, commands, palette, groupings) with the registry at startup
- verified by e2e suites only; no unit tests
- every user-relevant state and transition has a visible indicator, explanation, and clearing rule; follow the [UI state inventory](ui-state-visibility.md), including failures and unknown state, not just the happy path
- source documentation must support reviewing packages, structs, fields, methods and relationships; use the [Go documentation tool decision](go-code-review.md) alongside runtime registry documentation

```js
Scope = { task_id, project_id }     // the pin: a task and its project; a unit filters by task subtree, else by project
Unit = { id, tables: [name], commands: [name], emits: [type], listens: [daemonType],
         pages: [id], palette: [id], cli: [spec] }
// Go: interface { ID() string; Register(*Registry) }
```

## 0b. How to build it

- design every TUI surface (rail, detail, page, modal, form, help) with the `/frontend-design` skill; a terminal is still a UI
- parallel subagents, one unit or page each; optimize for wall-clock speed
- subagent models: opus or sonnet only; never fable
- web UI removed for now (not used); nothing is built for `internal/web`
- commit after every green step; `scripts/e2e-all.sh` before the last commit

## 1. Orchestrator — `cmd/deck`

- builds every unit in order, owns startup/shutdown
- startup order
  - store open → units built → registry filled → runner subscribe (union of `listens`) → taps → shells start
- shutdown
  - shells stop → runner `Start` done → handlers `Close` (history flushes)
- owns
  - command bus (§3)
  - event runner (§4, existing `events.Runner`)
  - store `Tx` (§2)
- subcommands: `tui`, `web`, `config`, `setup`, `update`, `version`, + generated `<unit> <command> --json`
- shared flags: `-socket -captures -data -auto-capture`
- [ ] does reminders become an events-style unit here (step 9)

```js
Wiring = { client, store, config?, registry, bus, runner,
           units: [work, code, prompts, context, history, reviews, captures, notes, reminders, panes],
           shells: [tui | cli] }
```

## 2. Store — `internal/store`

- one database, per-table repos, one transaction API
- SQLite only; no JSON-per-table backend
- units declare tables; store does not know fields
- `Tx(tables, fn)` — only touched tables saved; begins with the write lock
- `View(tables, fn)` — a deferred read transaction; in WAL mode it takes no write lock, so a reader in one process never waits on `busy_timeout` behind another process and never holds a writer back; `Put` / `Delete` fail inside it
  - every observation (`inspect`, scope, target, tree snapshot, the pin when it needs no repair) is a `View`; only mutations and an actual pin repair are a `Tx`
  - nothing holds either kind of transaction across a daemon call, a git command or a process spawn
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
- served by: TUI keys, `deck <unit> <cmd> --json`
- one log line per dispatch: name, args hash, duration, error

```js
Command = { name: "unit.verb", args: {} }
Result  = { status: string, data: {} , error?: { code, message } }
Handler = (ctx, args) => Result
Bus     = { register(name, Handler), call(Command) => Result, list() => [name] }
```

## 4. Event bus — reads

- `events.Runner` unchanged: one daemon subscription, resume `after_seq`+`boot_id`, bounded queues (256), per-handler goroutine, `Resync` on `subscribed`/`gap`/overflow
- units also emit deck events through it; deck events never reach daemon

```js
DaemonEvent = { seq, type, session, window, data }
DeckEvent   = { type: "tasks.changed", source: "deck", ids: [id], at }
Handler     = { Types(): [type], Handle(ctx, ev), Resync(ctx, bootID), Close?() }
Tap         = chan Event   // one per shell; never closes on reconnect
```

## 5. Registry — `internal/registry`

- definition tables; shells read, units write at register
- `All(kind)`, `Status(id)` (review marks from the inventory plan)
- kinds: page, action, palette, modal, grouping, form, feature
- generated from it, never hand-written: the docs of every struct, page, concept and action (`deck docs`), `deck list-actions` (bindings per mode + actions with no key), `deck config init` (every value, with its default)
- help modal `?`: one tab per mode, the unbound actions listed last, `/` filters
- `/` filters every list: rail, tasks, context, captures, history, reviews, palette, help, any picker
- catalog modal: `Modal{ kind: "catalog", source: "registry.kinds" }`; picking a kind replaces the modal with that kind's list; the meta catalog is the catalog of catalogs; still one modal at a time

```js
Page           = { id, key, title, unit, rail: fnName, detail: fnName, keys: tableId, help: id, tick: bool,
                   scoped: bool }   // true: the page has the scope/all modes (`S`), including tasks
PaletteCommand = { id, group, label, hint, key?, run: Command }
Grouping       = { id, levels: ["harness","project","top-task"] }
Modal          = { id, kind: "list"|"form"|"tree", source: sourceId, onPick: { replace: id } | { command } }
Form           = { id, submit: commandName, fields: [Field], box: "top" }   // drawn in the top ~8 lines, content pushed down
Field          = { name, key: char, source: sourceId, preview?: sourceId, add?: "task"|"project", multi?: bool, hint? }
                 // add: text matching no option is taken as the name of a new one, created on submit under the form's context
                 // key: the one highlighted char in the field's button; pressing it focuses the field
Action         = { name, mode, defaultKey, does }     // from config/keys.go today
```

- relationships
  - `Page belongs_to :unit`
  - `PaletteCommand has_one :command`
  - `Form has_many :fields; Form has_one :command (submit)`
  - `Modal has_one :source; Modal may replace :modal`

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
- a pane lives on a tuios host; `local` is the deck's own daemon, other hosts are the registered ones (`tuios hosts`); a pane is identified by host + session + window everywhere the deck stores a window
- `cwd` is what the code unit (§6.13) uses to tell which worktree a pane is in and whether an agent is working there

```js
Session = { host, name, attached, dir, branch, panes: [Pane] }
Pane    = { session, id, name, state, harness, foreground, cwd, message, blocked_by,
            is_agent, ready, needs_you, queued, unread, working, last_activity, idle_ms, stale }
```

- `Session has_many :panes; Session belongs_to :host`
- `Pane belongs_to :session; Pane has_one :worktree (by cwd, through code)`

### 6.3 work — projects, tasks, assignments

- tables: `projects`, `tasks`, `assignments`, `active`
- a project is a real piece of work people do, named by what it is for; it is not a repo and not a folder
  - a project has zero or more directories (§6.13): repos and plain dirs, each on a tuios host; most projects have one, a product with a frontend repo, a backend repo and a shared library has three
  - new project: a name; directories are attached afterwards from a native picker, the repo scan or the CLI, never inferred from a path; a project with no directory still holds tasks
  - a repo directory has worktrees; the project picks one default directory and a default worktree per directory
  - a place (`Place`) is host + directory + worktree + branch; a task may pin its own place, a subtask inherits its parent's, and the project's defaults fill whatever is missing
  - every new agent or terminal starts in the resolved place unless the form says otherwise; `Start(spec).cwd` and `Start(spec).host` default to it; the code unit warns when the place is dirty, busy or on the wrong branch
  - `settings` per project: default directory, default worktree per directory, default harness, default preset
- the pin: the deck is always pinned to one task; its project is the task's root project
  - `active` is one row and never empty once a task exists; `Scope` is derived from it
  - set through the project/task tree (`P`): one fully expanded tree of actual projects, tasks, and subtasks; no repeated `+ new` rows
    - `o` / `O` insert a draft task below the selected subtree / above the selected task; on a project, either inserts its first root task
    - `e` / `i` edit a task title or project name inline; `Escape` or `Enter` finishes the line and returns to navigation; empty new lines are dropped
    - new task lines support `Tab` / `Shift+Tab` nesting within the same project or unassigned group; existing task ownership is unchanged
    - `Ctrl+s` submits every insertion and rename together, preserves the pin, and closes only on success; validation or concurrent tree changes retain the draft with an error and write nothing
    - `Escape` in normal mode discards the entire draft without writes; navigation and line editing never persist changes
    - `Enter` on a clean task pins it; on a clean project it pins the first open task or creates one if needed; dirty drafts must be saved or discarded first
    - project creation, directory attachment and repository scanning remain separate palette actions with native filesystem pickers, not tree rows
  - almost everything the UI shows is under the pin: panes in the rail, context, captures, history, reviews, queue, vim sessions, notes
  - not scoped: the project switcher, Assign, help, palette, and settings; the tasks/projects page (`T`) follows its scope/all toggle
  - every scoped page has two modes: `scope` (rows under the pin, the default) and `all` (every row); `S` toggles, per page, and the title line reads `all` while it is on; the pin itself does not change
  - in `scope` mode, panes outside the selected project or task are not in the rail; the hidden count includes unassigned panes
  - unassigned panes, terminals, agents, and vim sessions are hidden whenever the UI is scoped to a project or task; only `all` mode shows them, in a `No Task` group at the bottom; a pane leaves that group the moment it is assigned
- first run, no projects: the deck asks for a list of dirs (`repo_roots`, each on a host), scans them for git repos, and offers each repo as a directory; the person names the projects and attaches repos to them, one project per repo by default; the scan is repeatable from the palette
- inheritance: anything created with a parent takes the parent's task and project (a context item from an assigned pane, a note on a task, a queued prompt on a task, a subtask); the child stores no project of its own; a subtask also inherits its parent's place unless it sets one
- themes
  - a project or task gets a random theme from the unassigned pool at creation
  - a theme counts as assigned while its owner is in a non-final state; final states: `done`, `skipped`
  - an unassigned pane uses the red/black theme (black text on a red background) in the rail's `No Task` group, visible only in `all` mode
- rail row for a pane: first 4 chars of the project name in the project's theme, then the task title in the task's theme
- task edit (`e`): title, parent (fuzzy), status, place (directory, worktree, branch; blank inherits); `ctrl+h` / `ctrl+l` walk the parent up and down so a task can be added under any node from anywhere
- rules owned here (today split ui/web)
  - `Resolve(window)` → task/project
  - `Target(task, project)` by id or name
  - assign new window
  - two-miss pruning, fed by `panes.changed`
  - themes: 16 colours, free-colour pool, glyph sections
  - snoozes, `easy`, status, `MoveTask`
  - `ProjectOf(task)` walks parents to root (subtasks store no project_id)
- commands: `work.add-project`, `work.patch-project`, `work.set-default-place`, `work.pin`, `work.add-task`, `work.patch-task`, `work.move-task`, `work.assign`, `work.unassign`, `work.snooze`, `work.mass-add` (directories and the repo scan are `code.*`, §6.13)
- emits: `projects.changed`, `tasks.changed`, `assignments.changed`
- pages: tasks (`T`, scope/all); modals: project/task tree (`P`), task tree (`w`)
- task tree modal (`w`, from any item): the lineage of that item only
  - rows: the project, then each ancestor down to the item's task, then that task's own subtasks
  - siblings at every ancestor level are hidden; a hidden count on the ancestor row (`+19`) expands them on `l`, `h` folds again
  - never the whole project; the tasks page is for that

```js
Project    = { id, name, theme: Theme, status, created, dir_ids: [id], default_dir?: id,
               settings: { harness?, preset?, worktree: { [dir_id]: worktree_id } } }   // default worktree per directory
Place      = { host, dir_id, worktree_id?, branch? }   // where work happens; task place > parent place > project defaults
Active     = { task_id, place: Place }                 // one row; project is ProjectOf(task); place is the resolved one
Settings   = { repo_roots: [{ host, dir }], stale_after, pr_poll, … }   // scan roots for the first run and the palette scan
Task       = { id, parent_id, project_id, title, theme: Theme, status, easy?, snoozed_until?, place?: Place, created, updated }
Assignment = { [window]: { host, session, task_id, project_id } }
Theme      = { color: ansiName, glyph }
```

- `Project has_many :tasks (top-level only)`
- `Task belongs_to :project (root only); Task belongs_to :parent (Task); Task has_many :subtasks`
- `Assignment belongs_to :pane (by host + window); belongs_to :task or :project`
- `Project has_one :theme; Task has_one :theme`
- `Project has_and_belongs_to_many :dirs (code); Project has_one :default_dir (Dir); Project has_one :default_worktree per dir`
- `Task has_one :place (optional; subtasks inherit)`
- `Active belongs_to :task; Active has_one :project (through task); Active has_one :place`

### 6.4 prompts — presets, queue, stash, dispatch, agent start

- tables: `prompt_presets`, `queued_prompts`, `prompt_stashes`
- rules: apply preset (prefix once, cwd), queue target, `Start(spec)` (start agent, record submission, assign), `Dispatch(q)`, new terminal (create session if missing), status text (incl. `BlockedBy`, `PromptNote`)
- commands: `prompts.start-agent`, `prompts.new-terminal`, `prompts.queue`, `prompts.dispatch`, `prompts.add-preset`, `prompts.stash`
- emits: `queue.changed`, `presets.changed`
- modals: prompt modal (`p`), presets list, queue list
- composer: one binding submits now, another queues for the end of the turn; the queue list shows a prompt the moment it is queued (today it is empty while the prompt still sends)
- composer completion: `@` paths, `/` skills and commands, attachments; an option that names a task or pane previews its recent scrollback beside the list
- a preset is a prefix prepended once plus an optional cwd; the composer offers the presets and `+ new preset…`
- depends on: daemon, work (`Target`), panes

```js
Preset        = { id, name, prefix, cwd, created }
QueuedPrompt  = { id, text, preset, task_id, project_id, cwd, session, agent, window, created }
StashedPrompt = { draft_id?, text, saved }
StartSpec     = { host, session, agent, name, cwd, prompt, preset?, task?, project?, place?: Place, attach?: [path] }
                // place: the resolved host/dir/worktree/branch the agent is expected to work in; recorded on the turn
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
- page: context (`C`); two scopes: the pane the deck is on, and all
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
- history is a timeline of everything the deck manages: prompt submitted, response completed, command run, session start, subagent start/stop, assignment, task status change, capture written, reminder fired, worktree dirty/clean, head moved (commit, merge, rewrite, checkout), PR opened/merged/closed, CI changed
- a turn records the place it ran in (`HarnessTurn.place`) so a commit or dirty change can be traced back to the turn, and the turn to its task
- review queue: a turn is listed only after it finishes, in finishing order, oldest at the top, newest at the bottom; it lives in the top section of the deck rail (§7.1), not only on its own page
  - highlighting an entry previews it in the detail area and does not mark it reviewed
  - giving the detail area focus (`l` or `right`) on an entry marks it reviewed; `r` toggles the mark by hand either way
  - a reviewable document (an md or html the agent wrote) is an entry too, once it exists

```js
HistoryEntry   = { id, kind, at, observed, source, source_id, session?, window?, summary, detail, turn?: HarnessTurn }
HarnessTurn    = { id, harness, conversation_id, host, session, window, prompt, response?,
                   started_at, completed_at?, transcript_path?, response_message?, place?: Place }
Review         = { id: promptHistoryId, turn_id?, session, window, pane, harness, prompt, response,
                   responses: [ReviewResponse], output?, started_at, completed_at, reviewed_at }
ReviewResponse = { id, at, text }
ReviewMark     = { [historyId]: reviewedAtMs }
```

- `Review belongs_to :pane (window); has_many :responses (HistoryEntry); has_one :mark; has_one :output (Capture, -turn)`
- `HistoryEntry belongs_to :pane (window)`

### 6.7 captures — files + autocapture

- folder: `~/.local/share/tuios-deck/captures`
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
VisibleNote = { note: Note, via: "own"|"parent"|"project", owner: name }
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

- `~/.config/tuios-deck/config`, key action table (51 actions / 4 modes), `Binding(mode, action)`
- registry reads `Action` from here

```js
Config = { keys: { [mode]: { [action]: key } }, … }
Action = { name, mode, default, does }
```

### 6.11 setup, complete, focus (unchanged leaves)

- setup: `Items()` table and CLI `deck setup` (list), `deck setup status`, `deck setup install`, `deck setup uninstall`
  - every required external setup asset (hooks, extensions, scripts, helpers, configuration templates) must be stored in this repo and embedded in the distributed binary; setup must work without a source checkout or a separate inbox installation
  - install materializes and configures the packaged files; no manual hook copying or shell edits are required for harness turn capture
  - installation is idempotent; status identifies missing, modified, conflicting, and migration-required files; uninstall removes owned files only, preserving unrelated configuration and rejecting unowned files/symlinks
  - the OMP integration captures delivered requests through final answers; setup records the installing executable and selected `-data` database, and replaces the older managed deck activity reporter so completions are not duplicated
  - reload/restart OMP after installation; rerun setup if the deck executable or database location changes; other harness adapters must follow the same terminal-turn and packaging contract
- complete: slash commands, `@` paths; shared by shells
- focus: idle/activity clock

### 6.12 vim — neovim sessions as deck items

- a vim session is the deck's own editor: a tuios pane running `nvim` that the deck started, for editing the files of a project or task; it is the third kind of pane beside terminal and agent
  - same rail section, same row format, same assignment, same `No Task` rule; `enter` goes live on it like any pane
  - opened in the worktree it was made for, with a session file per vim session so closing and reopening restores it (`nvim -S`)
  - a pane running nvim that the deck did not start is still a terminal
- opening neovim starts it in the active task's resolved place; a form may pick another worktree
- commands: `vim.open`, `vim.list`, `vim.forget`
- [ ] where sessions are discovered: a sessions dir the deck owns, or nvim's own

```js
VimSession = { id, name, session_file: path, window?, project_id, task_id, place: Place, cwd, created }   // window: the pane while it is open
```

- `VimSession belongs_to :project; VimSession belongs_to :task (optional); belongs_to :worktree (through place); has_one :pane (window, while open)`

### 6.13 code — directories, worktrees, branches, commits, PRs, CI

- the source-control side of a project: where its code lives and what state that code is in; work (§6.3) owns the work, this unit owns the places the work happens and what happened to them
- tables: `dirs`, `worktrees`, `branches`, `commits`, `head_moves`, `prs`, `claims`, `place_messages`
- a directory is a path on a tuios host (`host` + `path`); `local` is the deck's own host; the same path on two hosts is two directories
  - `kind: "repo"` when the path is inside a git repository, `"dir"` otherwise; a plain dir has one implicit worktree, itself, and no branch
  - a directory may belong to more than one project (a shared library); a project lists its directories and picks a default
  - new directories come from a native picker, the repo scan (`code.scan-repos`: first run and palette) or the CLI; the scan lists repos, the person attaches them to projects
  - git and `gh` run on the directory's host, through that host's tuios daemon; a host the deck cannot reach leaves its rows `unknown`, never `clean`
- worktrees: `git worktree list` per repo, refreshed by `code.refresh`, on a timer (`worktree_poll`, default 30s) and after every turn or command in a pane inside the repo; the deck records what git reports and does not create worktrees (see §10)
  - each worktree knows its branch, `head`, and whether it is dirty; `observed` says how old that knowledge is
  - who is on it: every pane whose `cwd` is inside the worktree, with its task and whether it is working (`WorktreeUse`), derived from the panes unit, never stored
- dirty attribution: when a refresh sees the status change, the change is blamed on what ran in that worktree since the previous observation
  - an agent turn (`HarnessTurn`) in a pane inside the worktree → `{ kind: "turn", turn_id }`
  - a shell command in a terminal pane inside the worktree (history command entry) → `{ kind: "command", history_id }`
  - nothing the deck saw → `{ kind: "unknown" }`, never a guess; every cause in the window is kept, newest first
  - the blame list clears when the worktree is clean again; history keeps both the dirty and the clean entry
- branches and commits: each worktree's branch, its upstream, ahead/behind, and the commits made since the deck first saw the branch
  - a commit is blamed like a dirty change: the turn or command that moved `HEAD`
  - a branch can be bound to a task (`code.bind-branch`); every commit, PR and dirty change on it then links to that task and its project; a turn's commit also links to the turn's task through its pane assignment, and the two must agree or the row shows both
- head moves: every change of a worktree's `HEAD` is a row with `from`, `to` and `kind`; `kind` comes from the graph: `to` descends from `from` → `commit`, or `merge` when `to` has two parents; `from` no longer reachable → `rewrite` (rebase, amend, reset); a branch switch → `checkout`
  - after a rewrite the deck matches the old commits to the new ones by patch id and sets `Commit.superseded_by`, so turn → commit links survive rebases and squashes; the old sha stays in history
- PRs and CI: for every branch with an upstream, `gh pr view --json` and `gh pr checks`, polled on `pr_poll` (default 2m) and refreshed when a turn ends; the PR links to its branch, so to its task
  - CI is one state per PR with the per-check list under it; `unknown` with a reason when `gh` is missing, offline or rate-limited
  - a context item of kind `pr` links to the same row (`code.link-pr`)
- starting an agent in the right place: `NewSpec` (§7.1) resolves host, directory, worktree and branch from the task's place, else the parent's, else the project's defaults; the start form shows the resolved place and warns, without blocking, when
  - the worktree is dirty (with the blame), or another agent is already working in it
  - the worktree's branch is not the task's bound branch, or that branch is behind its base
  - the task's PR is merged or closed, or its CI is failing
  - the quick bindings (`n a`, `n t`, `n v`) still spawn at once; the warning shows in the status line and on the row instead
- shared places: two panes are in the same place when they are in the same worktree, or on the same branch in different worktrees; the deck knows this from `WorktreeUse` and `Branch`, and it is the one standard way agents in a shared place talk to each other
  - the deck owns the record (`PlaceMessage`, `Claim`) and the routing (who is in the place); tuios mail is only the transport, addressed by host + session + pane; the deck never types into a pane to talk to it
  - with the deck server (§10) the server delivers directly to the pane's client and writes the row in the same step; the mail transport remains for panes the server does not reach
  - every message is a `PlaceMessage`: one kind, the place it is about, the paths it names, free text, and the turn it came from; the deck sends it to every other pane in the place and records it in history under the sender's task
  - kinds: `claim` (I am editing these paths), `release` (done with them), `heads-up` (I am about to commit, rebase, switch branch, run a migration), `handoff` (take this over, with what is done and what is left), `question`, `answer`
  - a claim is also a row (`Claim`) on the worktree, so the code page, the start form and a later agent see it without reading mail; a claim ends on `release`, when the turn ends, or when the pane closes
  - starting an agent into a shared place prepends a standard preamble to its prompt: who else is there (pane, task, working or idle), their open claims, the paths touched by uncommitted changes with their blame, and the exact mail commands to claim, release, hand off and ask; the agent is told to claim before editing and to send `heads-up` before any head move
  - a human in the shared place gets the same information on the pane's rail row and detail; the `n a` quick start shows the preamble's summary in the status line
  - conflicts are warnings, never locks: a claim on a path another pane claims, a head move during another pane's open turn, or a commit touching paths another pane claims shows on both rows with the two turns named; the person decides
  - CLI: `deck code message --json '{ kind, worktree_id|branch_id, paths?, text }'` and `deck code claim|release --json` so any harness can take part; `deck code place --window W` prints the preamble for a running pane
- polling never touches view state: no selection, scroll, filter or modal changes; stale rows say so (§0 state inventory)
- commands: `code.attach-dir`, `code.detach-dir`, `code.scan-repos`, `code.refresh`, `code.bind-branch`, `code.unbind-branch`, `code.link-pr`, `code.claim`, `code.release`, `code.message`, `code.place`
- emits: `dirs.changed`, `worktrees.changed`, `branches.changed`, `prs.changed`, `claims.changed`, `place_messages.changed`
- listens: `window-created`, `window-closed`, `history.changed` (turn and command ends drive refresh and blame)
- page: code (`D`, scoped): one section per directory, a row per worktree: branch, short head, dirty + blame, agents on it, PR state, CI state; detail lists head moves and commits with their turns and tasks; `enter` on a PR opens it
- depends on: panes (cwd, working), history (turns, commands), work (assignments, tasks, places)

```js
Dir         = { id, host, path, kind: "repo"|"dir", remote?: url, default_branch?, created, observed }
Worktree    = { id, dir_id, path, branch_id?, head: sha, main: bool, dirty: Dirty | "clean" | "unknown", observed }
Dirty       = { since, files: n, blame: [Blame] }
Blame       = { kind: "turn"|"command"|"unknown", turn_id?, history_id?, host?, window?, task_id?, at }
WorktreeUse = { worktree_id, host, window, task_id?, working: bool }        // derived from panes, not stored
Branch      = { id, dir_id, name, upstream?, ahead, behind, head: sha, task_id?, observed }
Commit      = { dir_id, sha, branch_id, subject, author, at, blame?: Blame, task_id?, superseded_by?: sha }
HeadMove    = { id, worktree_id, from: sha, to: sha, kind: "commit"|"merge"|"rewrite"|"checkout", at, blame?: Blame }
PR          = { id, dir_id, branch_id, number, url, title, base, state: "draft"|"open"|"merged"|"closed", head: sha,
                ci: CI, task_id?, observed }
CI          = { state: "pending"|"passing"|"failing"|"unknown", reason?, checks: [{ name, state, url }], observed }
Claim       = { id, worktree_id, host, window, task_id?, turn_id?, paths: [path], text?, since, until? }   // until: released, turn ended or pane closed
PlaceMessage = { id, kind: "claim"|"release"|"heads-up"|"handoff"|"question"|"answer", from: { host, session, window, task_id?, turn_id? },
                 place: { worktree_id?, branch_id? }, to: [{ host, session, window }], paths?: [path], text, reply_to?: id, at, delivered: [{ window, at, error? }] }
Preamble    = { place: Place, others: [{ window, task_id?, working, claims: [Claim] }], dirty: Dirty?, head: sha, branch, pr?: PR,
                commands: { claim, release, handoff, ask } }   // rendered as text at the top of a new agent's prompt
```

- `Dir has_many :worktrees; Dir has_many :branches; Dir has_many :prs; Dir has_and_belongs_to_many :projects`
- `Worktree belongs_to :dir; Worktree has_one :branch; Worktree has_many :head_moves; Worktree has_many :uses (panes, by cwd)`
- `Branch belongs_to :dir; Branch has_many :commits; Branch has_one :pr; Branch belongs_to :task (optional)`
- `Commit belongs_to :branch; Commit belongs_to :turn (optional, through blame); Commit has_one :task (through branch or turn)`
- `HeadMove belongs_to :worktree; HeadMove belongs_to :turn or :history_entry (through blame)`
- `PR belongs_to :branch; PR has_one :ci; PR has_one :task (through branch)`
- `Blame belongs_to :turn or :history_entry; Blame has_one :task (through the pane's assignment)`
- `Claim belongs_to :worktree; Claim belongs_to :pane (host + window); Claim belongs_to :turn (optional); Claim has_one :task (through the pane's assignment)`
- `PlaceMessage belongs_to :sender (pane); PlaceMessage belongs_to :worktree or :branch; PlaceMessage has_many :recipients (panes); PlaceMessage belongs_to :reply_to (PlaceMessage, optional); PlaceMessage has_one :history_entry`

## 7. Shells

### 7.1 tui — `internal/ui`

- keeps: `Model` as view state only (selection, scroll, modal slot, page, live)
- loses: domain logic (→ units), page enum (→ registry `Page`), closures over Model in forms (→ `Field.source`)
- one modal slot; `replace` or close; mass-add is the one parked modal
- shared list navigation applies to every list: rail, pages, modals, trees, palette, help, pickers, and auto-complete suggestions
  - in normal mode, `j` / `k` move down / up one item; `h` / `l` move left / right between areas or fold / expand tree nodes
  - `d` / `u` move down / up half a page; `ctrl+f` / `ctrl+b` move down / up a full page
  - `g` / `G` jump to the top / bottom of the list
  - `{` / `}` jump to the previous / next section or group, rather than a single item
  - `ctrl+n` / `ctrl+p` move down / up lists, especially auto-complete suggestions, including while typing in the associated input
- text inputs use readline bindings for line-wise navigation and editing: `ctrl+a` / `ctrl+e` go to the start / end of the line; `ctrl+f` / `ctrl+b` move forward / back one character; `ctrl+h` is backspace
  - input mode keeps printable characters as text and gives readline bindings priority over list or form actions; `ctrl+n` / `ctrl+p` still navigate suggestions
  - live mode keeps its own leader and key forwarding rules below
- forms: a box in the top ~8 lines of the window; the content below is pushed down and shrinks by that much
  - a field is a button with one highlighted char; that char focuses the field and enters input mode
  - a form opens in normal mode (keys pick fields, `esc` closes, `/` filters); `esc` in input mode returns to normal; `tab` / `shift+tab` cycle fields
  - every option list is fuzzy; `ctrl+n` / `ctrl+p` move in it; moving through options previews the option's object: the rail selects it, the detail shows it
  - a task, project or parent field with no exact match creates one on submit: the typed text is the name; a new task goes under the form's parent (the pinned task, or the field's chosen parent), a new project is a new project; the hint reads `new: <text>` so it is never a surprise
  - `+ add new…` opens the mass-add outline (parked form) for more than one at a time; in it `tab` / `shift+tab` change the nesting level
  - delete confirmation defaults to `y`; `esc` closes the palette so `ctrl+p` can move up in it
- modal input library: every modal and form runs on one engine; a config of modes, bindings (key → action) and actions (action → method on the object); fed keys one at a time, it tracks the mode and the object
  - [ ] plain text input through neovim (embedded or headless) is the ideal; the engine is the fallback
- new pane bindings: two per kind, six in all, on every page
  - quick: `n t` terminal, `n a` agent, `n v` vim session; spawns at once from `NewSpec`, no form, no question, the pane is live-ready when the key returns
  - with form: `N t`, `N a`, `N v`; opens the form with the same `NewSpec` prefilled, the person edits, submit spawns; the form shows the resolved place and the code unit's warnings (§6.13)
  - `NewSpec` comes from the highlighted rail row when it is a pane or a vim session: its host, tuios session, task, project, place/cwd, and for an agent its harness and preset; otherwise from the pin: the current tuios session, the pinned task, its resolved place, `settings.harness`, `settings.preset`
  - the new pane is assigned to that task before the key returns, so it never lands in `No Task`
  - binding names in config: `new_terminal`, `new_agent`, `new_vim`, `new_terminal_form`, `new_agent_form`, `new_vim_form`
- the title line always shows the pin: project glyph + name, task title, hidden pane count; `P` opens the switch modal from any page
- deck rail layout (see `docs/images/deck-rail-annotated.png`): two sections, one list for `j`/`k`
  - top: the review queue, finished turns and documents under the pin, oldest first; focus on the right (`l`/`right`) marks the entry reviewed, preview does not
  - bottom: the active panes, agents and terminals still working or waiting, grouped as `o`/`O` says; in `all` mode, `No Task` comes last; in `scope` mode, unassigned items and their group are absent
  - a pane moves from the bottom to the top when its turn ends, and back when a prompt is sent
- selecting any terminal, agent or running vim row on the pane/deck page shows a read-only terminal preview anchored at the bottom of the detail area, above the help line
  - show the actual recent scrollback and terminal screen, not an activity log or agent transcript substituted for it; vim and other alternate-screen applications show their current screen
  - metadata and transcript may remain above it, but cannot push the preview out of view; reduce metadata first on short terminals
  - previewing never focuses, sends input to, resizes, or acquires a size lease on the target pane; it never marks a turn reviewed
  - bound capture requests, ignore results for old selections, and preserve selection, filters, modals and scroll during refresh; no disruptive heartbeat
  - label loading, empty, closed, unavailable and cached previews explicitly, with target identity and capture time; render terminal styling safely without executing control sequences
  - the [preview acceptance scenarios](ui-state-visibility.md#terminal-preview) cover terminal, agent and vim screens, stale responses and non-interference
- rows expose simultaneous status flags and counts, including locally saved prompts as well as daemon-owned queue entries; details expand every indicator and its reason
  - use one [status legend and inventory](ui-state-visibility.md#indicator-contract) across pane, agent and vim rows; color supplements text, never replaces it
  - a new backend state is incomplete until its visible cue, transition, failure behavior and verification are documented
- help line (last row): the bindings that apply to the current mode and the highlighted row, not a fixed list; `F1` / `?` open the full help modal
- keybinding help follows the [approved visual reference](images/help-good.png): a centered, thin-bordered panel titled `Keys`, with the deck still visible behind it
  - use two balanced columns on wide terminals; group shortcuts under readable uppercase headings: Pages, Move, Shell, Live, Selection, List & Palette, Form
  - separate groups with a blank line and leave a clear gutter between columns; keep each group together where it fits
  - each group has an aligned key column and a description column; size key columns for the longest chord so descriptions never collide with keys
  - use an accent for keys, normal foreground for descriptions and a secondary foreground for headings and border; headings remain legible, not nearly invisible
  - write short, concrete action descriptions; wrap longer descriptions beneath their description column rather than clipping the meaning with ellipses
  - derive the displayed keys and descriptions from effective registry/config bindings, including remaps and mode-specific actions; the screenshot sets appearance, not binding semantics
  - distinguish the current mode and selection-specific actions; group shortcuts by context so identical keys in different modes are not ambiguous
  - collapse to one column when two columns cannot fit readable descriptions; scroll when height is insufficient, with a visible position/overflow cue and a fixed `esc close` footer
  - retain keyboard navigation and section jumps in help; closing restores the previous selection, filter, scroll and modal state without sending keys to a pane
  - acceptance: compare wide-terminal rendering with the reference, then check narrow/short terminals, long descriptions, multi-key chords and remapped bindings; no clipped keys, overlapping columns or inaccessible entries
- deck page keys: `h` / `l` move between rail and detail; `{` / `}` jump by group (`No Task` is one); `o` / `O` cycle the grouping; `w` the task tree modal (lineage only, see §6.3); `e` edit
- stale panes: no activity past `stale_after` marks the row stale and groups them; a palette command closes them
- pages dispatch through registry: `keys`, `rail`, `detail`, `helpLine`
- live mode: `enter` on a pane goes live; the live screen draws in the detail area under a live bar, the rail stays; never full-screen on the deck side
  - `ctrl+a` is the leader; the key after it is a command; every other key goes to the pane untouched, including `esc`
  - `ctrl+a d` detach (back to the deck) · `ctrl+a j` / `ctrl+a k` next / prev pane · `ctrl+a Z` / `ctrl+a f` zoom / fullscreen the pane inside tuios (its own session, not the deck) · `ctrl+a ctrl+a` types a literal ctrl+a · `ctrl+a ?` keys · `esc` after the leader cancels it
  - bindings live in config under mode `live`: leader, detach, next_pane, prev_pane, zoom_pane, fullscreen_pane, help
  - never a bare key as the exit: no held `esc`, no `ctrl+z`; the pane's program owns those
  - one input goroutine in order; `stream-pane` for the size lease and frames; `capture-pane` is the screen
- presence held by shell; transcript reader takes nonce as arg

```js
ViewState = { pin: Scope, all: { [pageId]: bool }, page: pageId, sel: { pane?: window, task?: id, ctx?: id }, scroll: { [pageId]: n },
              modal?: { def: Modal, state }, parked?: modal, confirm?, live?, status, filter?: query }
NewSpec   = { kind: "terminal"|"agent"|"vim", host, session, task_id, project_id, place: Place, cwd, harness?, preset?, name?,
              warnings: [{ kind: "dirty"|"busy"|"branch"|"behind"|"pr"|"ci", text }] }
            // from the highlighted pane or vim row, else from the pin; cwd is place's worktree path
InputLib  = { modes: [name], mode: name, bindings: [{ mode, key, action }],
              actions: { [action]: (object, key) => void }, object }     // feed(key) → runs the bound action, may switch mode
```

### 7.1a Lessons from tuios's Bubble Tea use

Read against tuios (`charm.land/bubbletea/v2` v2.0.8, the version the deck pins) on 2026-10-18. herdr is Rust on ratatui and is not a reference for any of this.

- same skeleton: one pointer-receiver model, `Init`/`Update`/`View`, a type switch over messages, a re-armed `tea.Cmd` per channel (their `ListenForPTYData`, our `waitLive` and the events tap); nothing structural to copy
- modes: tuios's `Mode` enum holds two values; every other state is a `ShowX` boolean or pointer, routed by a fixed priority chain of ~20 `if`s plus eight prefix flags; their own comments record overlay kinds left out of that chain and clicks landing on the panel behind
  - keep: one `mode` enum (eight values today) with the mutually exclusive modals exclusive by construction; never add a `ShowX` boolean beside it; the registry's `Modal` table is the one list of kinds
  - keep: pointer gates (`help`, `focus`, `live`) checked before the mode, in a fixed order, and only those three
- modal stacking: both codebases built a stack piecemeal; deck has `formStack` (one slot), `confirm.Back`, the deferred `reshowTree` and `resumeProto`; tuios has `sidebarReturnMode` and `scratchReturnMode` for its modes, and for overlays the real thing: `OverlayZOrder`, reconciled every frame from a gate table, raised on click, topmost dismissed by a click outside every panel, with a test that every kind has a place in the table
  - §7.1's one modal slot plus one parked modal is the right size; if a third layer ever appears, replace the four return paths with one explicit stack, not a fifth path
  - a check that every registered modal kind is drawable and routable, the way tuios tests its gate table
- paste goes through the same router as keys: tuios overlays answer `pasteTakenByOverlay`; the deck's `Update` has a second mode switch for `tea.PasteMsg` mirroring `handleKey`, so a new modal needs both edited; the input library's `feed` takes a key or a paste
- `esc` dismisses notifications without being consumed: tuios clears its dock message on any `esc` and lets the key go on to whatever owns it; the deck's status line should do the same
- one settle point after every handler: tuios computes its sync commands (files, git, dock, motion, next tick) once in `update` after `handleMsg`, not in each of fifty handlers; the deck's three `defer`s in `Update` are the same move; keep one such point, never per-handler hooks
- ticks: tuios arms one deadline timer for the earliest due job (`nextWake`) and has no standing tick; the deck runs a fixed one-second `tea.Tick` for the detail re-read even on pages that never read it; with `worktree_poll`, `pr_poll`, reminders and the detail re-read all wanting a timer, one `nextWake` over them is the shape
- per-message panic recovery: tuios recovers inside its message handler, puts up a crash overlay and returns the model unchanged, so one bad event does not end the program; a panic in the deck's loop exits the deck (the emptied-detail-with-kept-scroll case was one); worth a `recover` in `Update` that sets the status line and keeps the model
- not needed: a shared `ProgramOptions()` enforced by a test (tuios has five `tea.NewProgram` sites, the deck has one), the frame cache and `renderSkipped` (nothing in the deck composes an emulator frame), the mouse-motion whitelist until something hovers
- mouse: the deck has none; tuios's shape if it is added
  - mouse reporting in Bubble Tea v2 is a field on the view, not a program option: `view.MouseMode = tea.MouseModeAllMotion` in `View`
  - View records hit rectangles, Update consumes them: every panel appends one `Hit` per frame, reset at the start of the frame, so click handlers never re-derive layout; the deck's rail rows, tree rows and palette rows are already lists with a y range each
  - click dispatch order mirrors z-order: context menu, overlays (highest z containing the cell, raised on click), rail, dock, panes; a click on no panel dismisses the topmost
  - a `tea.WithFilter` whitelist drops motion before `Update` unless a named feature is waiting for it; clicks, releases and wheel always pass, one handler file each; drag state lives on the model
  - first build: clicks and wheel only (select a rail row, click a tab, scroll the detail, click a palette row); no motion filter until something hovers; in live mode a click inside the pane is forwarded through `send-keys` like a key

```js
Hit     = { kind: modalId | "rail" | "detail" | "palette", x, y, z, w, h,
            rows: [{ y, h, idx, dec?: Rect, inc?: Rect }] }   // appended by View, cleared per frame
Hits    = [Hit]                                                // Update: highest z containing (x, y) wins
Wake    = { at, job: "detail" | "worktree_poll" | "pr_poll" | "reminder" }   // one timer, earliest job
```

### 7.2 web — removed for now

- not used; delete `internal/web`, `scripts/e2e-web.sh`, `scripts/wscheck`
- reinstate later as a shell over the bus and registry

### 7.3 cli (new)

- `deck <unit> <command> --json '{…}'` generated from bus `list()`
- reads: `deck <unit> list` per table
- one subcommand per concept (project, task, context, prompt, reminder, note, capture, vim), each mirroring its unit's commands, so an agent can drive the deck; AGENTS.md says so
- `deck list-actions`, `deck config init`, `deck docs` from the registry

## 8. Flows (who touches what)

- start agent from TUI
  - key → resolve `Place` (task → parent → project) → code unit warnings → `Form form.start-agent` → submit `prompts.start-agent` → bus → prompts unit → daemon `start-agent` on the place's host → `work.assign` (tx: assignments) → emit `assignments.changed` → shells re-read
- turn ends in a worktree
  - history records the turn with its place → `history.changed` → code unit refreshes that worktree → status changed: `Dirty.blame` gets the turn; `HEAD` moved: `HeadMove` + `Commit` with the turn, task through the pane's assignment → PR/CI refresh for the branch → `worktrees.changed`, `prs.changed` → code page and the rail row re-read
- human command in a terminal pane
  - command end → history command entry → same refresh; the blame is `{ kind: "command", history_id }`
- rebase or squash
  - refresh sees `HEAD` not descending from the last `head` → `HeadMove{ kind: "rewrite" }` → old commits matched by patch id → `superseded_by` set → turn → commit links still resolve
- second agent into a worktree another agent is working in
  - `n a` → resolve `Place` → `WorktreeUse` shows the other pane → `Preamble` built from its claims, the dirty blame and the branch → prepended to the prompt → `prompts.start-agent` → the new agent sends `claim` through `deck code message` → `code.message` → tuios mail to the first pane + `place_messages` row + history entry under the sender's task → `claims.changed` → both rail rows show the two claims; overlapping paths show a warning on both
- agent about to rebase in a shared worktree
  - `heads-up` message → delivered to every other pane in the place → the deck records it; the following `HeadMove{ kind: "rewrite" }` is blamed on that turn and carries the heads-up id, so the other agent's next turn sees why its base moved
- pane closes
  - daemon `window-closed` → runner → panes unit → `panes.changed` → work unit miss counter (2 misses → prune, tx: assignments) → `assignments.changed`
- turn ends
  - daemon `agent-activity` → runner → history (batch insert) + autocapture (file) → `history.changed` → reviews page re-reads `Turns`
- switch pin
  - `P` → project/task tree (real rows only) → `Enter` on a clean task or project → `work.pin` → tx: active → `active.changed` → every page in scope mode, including Tasks, re-reads with the new `Scope`; pages in all mode keep showing all rows
- cli patch task
  - `deck work patch-task --json` → bus → tx: tasks → `tasks.changed` → TUI re-reads

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
9. wiring to cmd/deck, reminders as unit → e2e-all

## 10. Open decisions

- [ ] command naming: `unit.verb` vs `unit/verb`
- [ ] deck server: one long-lived process owns the store and the daemon subscription, like the tuios daemon; the TUI and the CLI are clients over a unix socket and never open the database. Removes cross-process locking entirely (today both processes open the same SQLite file; `View` only removes the read side of the contention), gives agent mail one router, and makes `deck <concept> <command>` a request to the server instead of a second writer. An earlier version of the deck ran this way; recommended as the next structural step
- [ ] does `panes` unit cache or re-list on every `panes.changed`
- [ ] where `Theme` pool lives: work or registry
- [ ] multiple hosts: one daemon connection per host, or the local daemon relaying to registered hosts
- [ ] remote git: run through the host's tuios daemon, or over ssh directly
- [ ] PR provider: `gh` only for the first build, or an interface with GitHub first
- [ ] deck events: typed Go structs or `map[string]any` like daemon events
- [ ] neovim as the text input engine: embedded, headless server, or not at all
- [ ] the pin: one per deck process or one per tuios session
- [ ] vim session discovery: deck-owned dir or nvim's
- [ ] does the deck create worktrees (`git worktree add`) and branches for a task, or only list and record them
- [ ] dirty attribution window: blame everything since the last observation, or only panes that were active in it
- [ ] shared-place messages when a recipient is not an agent (a human terminal): tuios mail to the pane, a deck notification, or both
- [ ] should a claim on the same paths by two agents stay a warning, or should the start form refuse the quick `n a` and require the form
- [ ] mouse support in the tui: clicks and wheel over recorded hit rectangles (§7.1a), or keyboard only
- [ ] one deadline timer over every poll (§7.1a) or a tick per unit
