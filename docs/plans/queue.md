# Queue page: rapid-fire items that agents take in batches (B-39)

Canonical integration note, 2026-10-20. The original plan below calls this B-39,
but canonical [B-39](../todo/delivery.md#b-39) remains the isolated runner.
The batch queue maps to [B-63](../todo/agents.md#b-63) as a separate implementation
scope, not proof of prompt delivery outcomes. Branch implementation is awaiting
the parent's final VPS proof.

Current session precedence supersedes the historical default below. An explicit
`queue.dispatch` session wins, then a nonblank configured `queue.session`. With
neither set, the blank default delegates to ordinary project-named launch
session resolution. New panes must not default to a hard-coded `queue` session.
The historical source text is retained below for the remaining design details.

A queue item is lighter than a todo: free multi-line text, typed as fast as the
person can think, and optionally pointed at a repository (a directory) and a
harness. Agents come to the queue, take a small batch of ready items that share
a repository, do them, and finish them through the mtm MCP server (or the CLI).
Batches are small on purpose: iterate quickly, come back often.

Conventions are the outline's: js-style shapes, `?` optional.

## Unit — `internal/queue` (package `queue`)

Tables `queue_items`, `queue_batches`, owner `queue`.

```js
QueueItem  = { id, text, title, status: "ready"|"claimed"|"done"|"failed",
               project_id?, repo?: path, harness?, batch_id?, owner?, session?, window?,
               result?, notes: [string], position, created, updated, claimed_at?, finished_at?,
               provenance }                                 // title = first non-empty line, ≤ 80 chars
QueueBatch = { id, item_ids: [id], status: "claimed"|"done"|"failed"|"released",
               owner, session?, window?, agent?, cwd?, project_id?, repo?, name?, error?,
               created, updated, finished_at? }
ClaimResult = { batch: QueueBatch, items: [QueueItem], prompt }
DispatchResult = { started: [{ batch: QueueBatch, session, window, name, status }],
                   released: [QueueBatch], active, reason? }   // reason: "queue_empty" | "max_agents"
```

Rules

- group key of an item: `repo`, else the default tree of `project_id`, else `""` (no repository; the agent
  works wherever it is started)
- a batch is up to `limit` ready items that share one group key, taken in `position` order starting at
  the first ready item (or exactly the `ids` given, which must all be ready)
- `queue.finish` on a batch marks every unfinished item of it; a batch is `done` when every item is finished and
  none failed, `failed` otherwise; finishing writes `result` on each item and a dated note
- `queue.release` puts items back to `ready` (clearing batch, owner, session, window) and marks the batch `released`
- reconcile (inside `dispatch`, and on the daemon event `window-closed`): a `claimed` batch whose window is gone
  is released with the note `pane closed`
- `queue.dispatch`: reconcile; count `active` claimed batches; while `active < max_agents`, claim the next group
  and start an agent with `prompts.start-agent` `{ session, agent, cwd, name, prompt, project }`; a start failure
  releases that batch with the error and stops; explicit `ids` always start one batch, ignoring `max_agents`
  - agent: args `agent` > the batch's item harness (first item that names one) > `queue.harness` setting > empty
    (prompts resolves the project's default harness and launch defaults)
  - cwd: the group key; empty cwd lets prompts pick the project tree or the launch default
  - session: args `session` > `queue.session` setting (`queue`)
  - name: `queue: <first title>` (first five words, ≤ 32 chars)
  - prompt: `queue.Prompt(batch, items, instructions)`, see below

Commands (all `--json`)

- `queue.add { text, project_id?, repo?, harness? }` → QueueItem; `text` required
- `queue.patch { id? | ids?, text?, project_id?, repo?, harness?, status?, note? }` → [QueueItem]
  (one row or many; `status` only among the four; `note` appends one dated line)
- `queue.delete { id? | ids? }` → `{ deleted: [id] }`
- `queue.claim { limit?, ids?, repo?, project_id?, owner?, session?, window?, agent? }` → ClaimResult;
  `limit` defaults to the `queue.batch_size` setting; nothing ready → error `queue_empty`;
  an id that is not ready → `not_ready`
- `queue.finish { id? | ids? | batch_id?, status?: "done"|"failed", result? }` → [QueueItem] (`done` default)
- `queue.release { id? | ids? | batch_id?, note? }` → [QueueItem]
- `queue.dispatch { limit?, max_agents?, ids?, session?, agent?, project_id? }` → DispatchResult
- read `queue.prompt { batch_id }` → `{ prompt }`

Sources (registry): `queue.list` and `queue.items` (ready first by position, then claimed, then done and
failed newest-finished last; every row carries `_section`: `READY` / `CLAIMED` / `DONE`), `queue.batches`,
`queue.detail` (`[{ id, text }]`, the detail text: title line, status · repo · harness · batch, the full text,
the result, notes, provenance), `queue.statuses`, `queue.help`.

Emits `queue.changed`. Listens `window-closed`. CLI concept `queue`:
`mtm queue add|patch|delete|claim|finish|release|dispatch --json '{…}'`, `mtm queue list`, `mtm queue batches list`.

Settings section `queue`: `batch_size` number 3 · `max_agents` number 2 · `session` text `queue` ·
`harness` text `` · `instructions` text `` (appended to every batch prompt).

Prompt (`queue.Prompt`):

```
You are working through a batch from the mtm work queue (batch <id>).
Working directory: <cwd or "the directory you were started in">.

Items:
1. [<item id>] <text, indented on continuation lines>
2. …

Rules: do the items in order; commit after each one; run only targeted checks while you work.
When the batch is done call the mtm MCP tool queue_finish with batch_id "<id>" and a short result,
or run: mtm queue finish --json '{"batch_id":"<id>","status":"done","result":"…"}'.
An item you cannot do: finish it with status "failed" and say why in result.
Keep the turn short and stop when the batch is finished.
<instructions setting, if any>
```

## Page `queue` (TUI)

`Page{ ID: "queue", Title: "Queue", Unit: "queue", Rail: "queue.list", Detail: "queue.detail", Keys: "queue",
Help: "queue.help" }`, not scoped, no tick.

Rail row: `<title>` then a second line `<status> · <repo basename or project name or "no repo"> · <harness>`,
`✓` prefix on a marked row; sections READY / CLAIMED / DONE (`{` / `}` jump).

Keys on the page (mode `queue`, registered by the unit as actions without commands; the shell handles them):

- `n` add: opens `form.queue.add` (fields `text` multiline required, `project_id`, `repo` directory, `harness`)
  straight into input mode on `text`
  - `ctrl+enter` (new form-input action `submit-again`, every form) submits and reopens the same form with the
    same values except its text fields, so the next item keeps the repository and harness; the status line says
    `added: <title>`; `ctrl+s` submits and closes; `esc` closes
- `space` marks / unmarks the row (multi-select, like downloads)
- `t` target: opens `form.queue.assign` (`ids` hidden, `project_id`, `repo`, `harness`) for the marked rows,
  else the selected row; submit is `queue.patch`
- `c` finish done, `f` finish failed, `R` release: `queue.finish` / `queue.release` with the marked ids, else the
  selected id; marks clear afterwards
- `enter` dispatch the marked rows (else the selected row) as one batch: `queue.dispatch { ids }`; the shell
  jumps to the new pane like any pane-creating command
- `D` dispatch next batches: `queue.dispatch {}`
- `e` edit (`form.queue.patch`: `id`, `text`, `project_id`, `repo`, `harness`, `status`), `delete` removes with
  confirmation

Palette (group Queue): `Add queue item`, `Target queue items`, `Dispatch queue` (`queue.dispatch`),
`Watch the queue` (adds a `schedules.add` of kind `command` running `queue.dispatch` every 60 s).

## MCP tools (`internal/mcp`)

`queue_list { status? }`, `queue_add { text, repo?, project_id?, harness? }`,
`queue_claim { limit?, ids? }` (pane-bound: owner, session and window are the pane's; the pane's project is
never used as a filter), `queue_finish { batch_id?, ids?, status?, result? }` (pane-bound),
`queue_release { batch_id?, ids?, note? }` (pane-bound). Listed only while `queue.add` is on the bus.
Every call records `mcp.<tool>` in history like the other tools; after `queue_finish` the server pokes the pane row.

## Verification

Outline case `queue` (`scripts/e2e_queue.py`, joined to the matrix; `scripts/e2e-queue.sh`; a line in
`scripts/e2e-all.sh`):

1. CLI: add four items (two with repo A, one with repo B, one without), list order and `_section`, title from
   the first line, `patch` with `ids` sets repo and harness on two rows, `claim` with `limit` 2 returns the two
   repo-A items and a prompt naming both ids and the cwd, a second `claim` returns repo B, `claim` on an empty
   queue → `queue_empty`, `finish` by `batch_id` with a result closes both items and the batch, `release` returns
   an item to ready and the batch to released
2. dispatch: with the fake agent (`/bin/sh scripts/e2e-agent.sh`) as `agent`, `dispatch {limit: 2, max_agents: 1}`
   starts one pane in session `queue`, the prompt reaches the pane (`accepted:` in its capture), a second
   `dispatch` reports `max_agents`, closing the pane and dispatching again releases the first batch (`pane closed`
   note) and starts the next
3. MCP: `mcp serve` bound to a fixture pane: `queue_claim` returns a batch owned by that window,
   `queue_finish` closes it, the history shows `mcp.queue_finish` with the pane's window
4. TUI: the Queue page through the switcher; `n`, type a two-line item, `ctrl+enter`, type a second item,
   `ctrl+enter`, `esc`: both rows listed, ready first; `space` on two rows, `t`, choose repo, `ctrl+s`: both rows
   show the repo; `c` on a marked row: the row moves to DONE
