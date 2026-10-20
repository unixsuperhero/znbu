# Todo files: parsable format and agent dispatch

Matomeru indexes the backlog; agents do the work. The canonical items live in
[`docs/todo/*.md`](../todo/) under `## B-nn` headings. Matomeru needs only the
index fields from each item (id, title, status, priority, size) and hands the
rest of the item to an agent as text. The format therefore needs very little:
a parsable heading, one parsable field line, and nothing else.

Implemented baseline: the [B-13 todo unit](../outline/work.md#b-13) with its
page on `B`, the `mtm todo …` commands, and the `todos.import` command that
reads the old single-file `### B-nn` layout through `internal/todomd`. That
parser no longer matches the directory layout, so step 2 replaces it.

## What Matomeru parses

```js
Item = {
  id: "B-32", title: "rich prompt presets and recorded questions",
  status: "partial",            // open | partial | verification-pending | implemented | superseded
  priority: "p1", size: "M",    // size: S | M | L | XL | none ("not estimated" reads as none)
  file: "docs/todo/agents.md", line: 31,
  body: "…every line from the heading to the next heading, verbatim…",
}
```

Survey of the 39 remaining items on 2026-10-20:

| Field | Source line | State |
|---|---|---|
| id, title | `## B-nn Title` after `<a id="b-nn"></a>` | 39 of 39 parse; the colon after the id is optional |
| status, priority, size | first `Status:` line after the heading | 34 of 39 have one, in two separator styles (`. ` and ` · `) |
| body | heading to next `## ` or end of file | always works |

## Format rules

Only these two lines are machine-read. Everything else is free Markdown for the agent.

1. Heading: `<a id="b-nn"></a>` then `## B-nn Title`. No colon after the id.
2. Field line, the first non-blank line after the heading:
   `Status: open · priority: p2 · size: M.` Keys are case-insensitive;
   the parser accepts both `. ` and ` · ` separators and ignores trailing prose,
   so an item with extra text on that line still imports.

No linter, no acceptance checkboxes, no execution-state field in the file.
If agents later need to see claims in the files, add `owner: …` to the field line;
the parser already keeps unknown keys.

## Pieces

| piece | where | changes when |
|---|---|---|
| format | this plan, `docs/todo/*.md` | a new index field is needed |
| parser | `internal/todomd` (rewritten) | the format changes |
| import | `internal/work/todos.go` `todos.import` | a parsed field maps to a new todo column |
| setting | `todo_dir` in `internal/settings` | the backlog moves |
| page | todo page in `internal/ui` | selection or filtering changes |
| dispatch | `todos.dispatch` in `internal/work` | how a hand-off prompt is built |
| preset | a `prompt_presets` row | how the orchestrator is instructed |

## Steps

1. **Normalize the field lines (znbu).** Add a `Status:` line to the 5 items
   without one and use the ` · ` separator everywhere. No wording changes.
   Verify: `grep -c '^## B-'` equals `grep -c '^Status:'` per file; the diff
   touches only `Status:` lines.
2. **Rewrite the parser (mtm).** `todomd.ParseDir(dir)` scans `*.md`, splits
   on `## B-nn` headings, reads the field line as `key: value` pairs with either
   separator, and keeps the body verbatim with file and line. Items with no field
   line import with blank fields and a `warning` in the result; nothing fails.
   Verify: `go test ./internal/todomd` on a fixture copied from `docs/todo/`,
   asserting 39 items, every id, and the status/priority/size of B-32 and B-31.
3. **Import from the directory (mtm).** `todo_dir` setting, default
   `~/proj/znbu/docs/todo`, with the native directory picker. `todos.import`
   upserts by id so re-import updates status, priority, size and body without
   duplicating rows or losing notes. `mtm todo export --json` prints the
   `Item` list above for agents that want structure.
   Verify: `mtm todo import` then `mtm todo list` shows 39 rows; a second import
   adds 0 rows.
4. **Select and filter on the page (mtm).** Space toggles a mark, `/` filters,
   and a status/priority filter cycles with one key chosen through
   `mtm list-actions` conflict review. Marked rows show a glyph in the rail.
   Verify: PTY e2e marks two rows and the rail shows both glyphs.
5. **Dispatch (mtm).** `todos.dispatch` takes the marked ids, builds one prompt
   (for each item: id, title, file path, body), prepends the orchestrator preset,
   and opens the existing start-agent composer with that prompt and the cwd
   prefilled from the focused project or `todo_dir`. Nothing is written back to
   the files. `mtm todo dispatch --json '{"ids":["B-32","B-42"]}'` does the
   same from the CLI.
   Verify: PTY e2e dispatches two items and the new pane's first turn contains
   both ids and both file paths; CLI dispatch returns the window id.
6. **Orchestrator preset (text only).** A `prompt_presets` row, kind agent,
   position prepend: split the items into independent scopes, claim worktrees
   with `scripts/agent_worktrees.py`, fan out one agent per scope, never use
   Fable for subagents, verify through `scripts/verify-vps.sh`, and report
   through the mtm MCP. Can be written at any point.

Steps 1 and 6 need no code. Steps 2 to 5 are one matomeru branch; step 5
reuses the start-agent flow, so the open [B-63 durable queue](../todo/agents.md#b-63)
is not a prerequisite.
