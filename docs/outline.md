# Modular deck: outline

Working outline of the redesign in [the modular report](../reports/2026-10-18-modular-redesign.md). Nested lists, shapes, relationships. Fill in details under each node.

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
           units: [work, prompts, context, history, reviews, captures, notes, reminders, panes],
           shells: [tui | cli] }
```

## 2. Store — `internal/store`

- one database, per-table repos, one transaction API
- backends: json-per-table (step 6), sqlite (current, becomes "a backend")
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
                   scoped: bool }   // true: the page shows only rows under the pin; tasks page is false
PaletteCommand = { id, group, label, hint, key?, run: Command }
Grouping       = { id, levels: ["harness","project","top-task"] }
Modal          = { id, kind: "list"|"form"|"tree", source: sourceId, onPick: { replace: id } | { command } }
Form           = { id, submit: commandName, fields: [Field], box: "top" }   // drawn in the top ~8 lines, content pushed down
Field          = { name, key: char, source: sourceId, preview?: sourceId, add?: "task"|"project", multi?: bool, hint? }
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
  - new project: pick an existing repo (the common case) or a folder, which the deck turns into one with `git init`
  - on pick the deck lists the repo's worktrees (`git worktree list`) into `trees`; the person picks the default
  - every new agent or terminal starts in the active project's chosen tree unless the form says otherwise; `Start(spec).cwd` defaults to it
  - `settings` per project: default tree, default harness, default preset
- the pin: the deck is always pinned to one task; its project is the task's root project
  - `active` is one row and never empty once a task exists; `Scope` is derived from it
  - set only through the switch modal (`P`): projects, then their tasks and subtasks, as one fuzzy tree
    - every level ends with `+ new…`; typing a name that matches nothing offers to create it there, under the highlighted node, without leaving the modal
    - `enter` on a task pins it; `enter` on a project pins its first open task, or creates one if it has none
  - almost everything the UI shows is under the pin: panes in the rail, context, captures, history, reviews, queue, vim sessions, notes
  - not scoped, ever: the tasks/projects page (`T`), the help, the palette, the settings
  - a pane assigned to another task is not in the rail; a count in the title line says how many are hidden
  - a pane with no assignment is always in the rail, under every pin, in a `No Task` group at the bottom; its rows draw in the red/white theme; it leaves the group the moment it is assigned
- first run, no projects: the deck asks for a list of dirs (`repo_roots`), scans them for git repos, and offers each repo as a project to create; the scan is repeatable from the switch modal
- inheritance: anything created with a parent takes the parent's task and project (a context item from an assigned pane, a note on a task, a queued prompt on a task, a subtask); the child stores no project of its own
- themes
  - a project or task gets a random theme from the unassigned pool at creation
  - a theme counts as assigned while its owner is in a non-final state; final states: `done`, `skipped`
  - a pane with no assignment draws in the obnoxious red/white theme, inside the rail's `No Task` group
- rail row for a pane: first 4 chars of the project name in the project's theme, then the task title in the task's theme
- task edit (`e`): title, parent (fuzzy), status; `ctrl+h` / `ctrl+l` walk the parent up and down so a task can be added under any node from anywhere
- rules owned here (today split ui/web)
  - `Resolve(window)` → task/project
  - `Target(task, project)` by id or name
  - assign new window
  - two-miss pruning, fed by `panes.changed`
  - themes: 16 colours, free-colour pool, glyph sections
  - snoozes, `easy`, status, `MoveTask`
  - `ProjectOf(task)` walks parents to root (subtasks store no project_id)
- commands: `work.add-project`, `work.patch-project`, `work.set-tree`, `work.pin`, `work.scan-repos`, `work.add-task`, `work.patch-task`, `work.move-task`, `work.assign`, `work.unassign`, `work.snooze`, `work.mass-add`
- emits: `projects.changed`, `tasks.changed`, `assignments.changed`
- pages: tasks (`T`, unscoped), tree modal (`w`); modal: switch (`P`)

```js
Project    = { id, name, theme: Theme, status, created, repo: path, trees: [Tree], default_tree: path,
               settings: { harness?, preset? } }
Tree       = { kind: "worktree"|"clone"|"dir", path, repo?, branch? }
Active     = { task_id, tree: path }                   // one row; project is ProjectOf(task)
Settings   = { repo_roots: [dir], stale_after, … }          // scan roots for the first run and the switch modal
Task       = { id, parent_id, project_id, title, theme: Theme, status, easy?, snoozed_until?, created, updated }
Assignment = { [window]: { session, task_id, project_id } }
Theme      = { color: ansiName, glyph }
```

- `Project has_many :tasks (top-level only)`
- `Task belongs_to :project (root only); Task belongs_to :parent (Task); Task has_many :subtasks`
- `Assignment belongs_to :pane (by window); belongs_to :task or :project`
- `Project has_one :theme; Task has_one :theme`
- `Project has_many :trees; Project has_one :default_tree (Tree)`
- `Active belongs_to :task; Active has_one :project (through task); Active has_one :tree`

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
StartSpec     = { session, agent, name, cwd, prompt, preset?, task?, project?, attach?: [path] }
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
- reviews: a view over history; only the mark is stored
  - turn = prompt-submitted + every response-completed until next prompt
  - `<task-notification>` prompt keeps turn open
  - listed when not awaiting and window subagent count == 0
- `Turns(window)`, `Mark(id)`
- commands: `reviews.mark`, `reviews.unmark`
- emits: `history.changed`, `reviews.changed`
- pages: history, reviews, Turns tab
- history is a timeline of everything the deck manages: prompt submitted, response completed, command run, session start, subagent start/stop, assignment, task status change, capture written, reminder fired
- review queue: a turn is listed only after it finishes, in finishing order; opening an entry marks it reviewed; opening the page or highlighting an entry never does

```js
HistoryEntry   = { id, kind, at, observed, source, source_id, session?, window?, summary, detail }
Review         = { id: promptHistoryId, session, window, pane, harness, prompt, response,
                   responses: [ReviewResponse], output?, started_at, completed_at, reviewed_at }
ReviewResponse = { id, at, text }
ReviewMark     = { [historyId]: reviewedAtMs }
```

- `Review belongs_to :pane (window); has_many :responses (HistoryEntry); has_one :mark; has_one :output (Capture, -turn)`
- `HistoryEntry belongs_to :pane (window)`

### 6.7 captures — files + autocapture

- folder: `~/.local/share/tuios-deck/captures`
- autocapture: `events.Handler`, writes `-turn` / `-cmd` on turn or command end
- `List`, `Read`, `Dir` (no store import)
- commands: `captures.capture`, `captures.delete`
- page: captures

```js
Capture = { name, path, size, modified, session, pane, kind: "turn"|"cmd"|"" }
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

- setup: embedded omp extension, `Items()` table, install/status/uninstall
- complete: slash commands, `@` paths; shared by shells
- focus: idle/activity clock

### 6.12 vim — neovim sessions as deck items

- a vim session is listed on the deck pages beside panes, with the same rail row format
- opening neovim starts it in the active project/task's tree; a form may pick another tree
- commands: `vim.open`, `vim.list`
- [ ] where sessions are discovered: a sessions dir the deck owns, or nvim's own

```js
VimSession = { id, name, path, project_id, task_id, cwd, created }
```

- `VimSession belongs_to :project; VimSession belongs_to :task (optional); belongs_to :tree`

## 7. Shells

### 7.1 tui — `internal/ui`

- keeps: `Model` as view state only (selection, scroll, modal slot, page, live)
- loses: domain logic (→ units), page enum (→ registry `Page`), closures over Model in forms (→ `Field.source`)
- one modal slot; `replace` or close; mass-add is the one parked modal
- forms: a box in the top ~8 lines of the window; the content below is pushed down and shrinks by that much
  - a field is a button with one highlighted char; that char focuses the field and enters input mode
  - a form opens in normal mode (keys pick fields, `esc` closes, `/` filters); `esc` in input mode returns to normal; `tab` / `shift+tab` cycle fields
  - every option list is fuzzy; `ctrl+n` / `ctrl+p` move in it; moving through options previews the option's object: the rail selects it, the detail shows it
  - `+ add new…` opens the mass-add outline (parked form); in it `tab` / `shift+tab` change the nesting level
  - delete confirmation defaults to `y`; `esc` closes the palette so `ctrl+p` can move up in it
- modal input library: every modal and form runs on one engine; a config of modes, bindings (key → action) and actions (action → method on the object); fed keys one at a time, it tracks the mode and the object
  - [ ] plain text input through neovim (embedded or headless) is the ideal; the engine is the fallback
- the title line always shows the pin: project glyph + name, task title, hidden pane count; `P` opens the switch modal from any page
- deck page keys: `h` / `l` move between rail and detail; `{` / `}` jump by group (`No Task` is one); `o` / `O` cycle the grouping; `w` the task tree modal from any item; `e` edit
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
ViewState = { pin: Scope, page: pageId, sel: { pane?: window, task?: id, ctx?: id }, scroll: { [pageId]: n },
              modal?: { def: Modal, state }, parked?: modal, confirm?, live?, status, filter?: query }
InputLib  = { modes: [name], mode: name, bindings: [{ mode, key, action }],
              actions: { [action]: (object, key) => void }, object }     // feed(key) → runs the bound action, may switch mode
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
  - key → `Form form.start-agent` → submit `prompts.start-agent` → bus → prompts unit → daemon `start-agent` → `work.assign` (tx: assignments) → emit `assignments.changed` → shells re-read
- pane closes
  - daemon `window-closed` → runner → panes unit → `panes.changed` → work unit miss counter (2 misses → prune, tx: assignments) → `assignments.changed`
- turn ends
  - daemon `agent-activity` → runner → history (batch insert) + autocapture (file) → `history.changed` → reviews page re-reads `Turns`
- switch pin
  - `P` → switch modal (tree of projects → tasks, `+ new…` at every level) → `work.pin` → tx: active → `active.changed` → every scoped page re-reads with the new `Scope`; tasks page unchanged
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

- [ ] json-per-table vs keep sqlite as the only backend
- [ ] command naming: `unit.verb` vs `unit/verb`
- [ ] does `panes` unit cache or re-list on every `panes.changed`
- [ ] where `Theme` pool lives: work or registry
- [ ] `Tree.kind`: does the deck manage worktrees itself or only record a path
- [ ] deck events: typed Go structs or `map[string]any` like daemon events
- [ ] neovim as the text input engine: embedded, headless server, or not at all
- [ ] the pin: one per deck process or one per tuios session
- [ ] vim session discovery: deck-owned dir or nvim's
- [ ] does the deck create worktrees (`git worktree add`) or only list and record them
