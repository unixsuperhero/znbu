# Todo files: parsable format and agent dispatch

Canonical plan, integrated from matomeru3 commits `da244e4` and `b7c4a07`.
This document proposes the extension to [implemented B-13](../outline/work.md#b-13);
[remaining acceptance](../todo/work.md#todo-dispatch) is not an implementation claim.

Matomeru indexes the backlog; agents do the work. The canonical items live in
`~/proj/znbu/docs/todo/*.md` under `## B-nn` headings. Matomeru needs only the
index fields from each item (id, title, status, priority, size) and hands the
rest of the item to an agent as text. The format therefore needs very little:
a parsable heading, one parsable field line, and nothing else.

Current status after rebasing onto `4219e44`: canonical index/directory import is
already implemented in B-13. `todomd.Parse` follows the canonical `docs/todo.md`
index and its concept sections, parses status, priority, and size, and preserves
body text. Import upserts by B identifier and retains notes and ownership.
Do not replace this working parser or restrict import to the historical 39 open
items. The source `Item` has no per-item file/line fields; stored todos have no
size or source-location fields. `todo_dir`, structured export, marked dispatch,
and the orchestrator preset remain proposed. The 39-item survey below is historical.
Canonical acceptance lives in `~/proj/znbu/docs/todo/work.md#todo-dispatch`.

## Proposed structured export

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
unknown-key retention would also need implementation.

## Pieces

| piece | where | changes when |
|---|---|---|
| format | this plan, `docs/todo/*.md` | a new index field is needed |
| parser | `internal/todomd` (extended) | the format changes |
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
2. **Extend the existing parser only where needed (mtm).** Keep canonical index
   traversal, closed dispositions, mixed field separators, and size parsing. Add
   per-item source file/line and define exact-body preservation and missing-field
   warnings for the structured export. A topical-directory entry point may scan
   `*.md`, but must not replace canonical-index import or drop completed items.
   Verify against the current canonical inventory, not the historical 39-item count.
3. **Extend directory configuration and export (mtm).** Add the proposed
   `todo_dir` setting, default `~/proj/znbu/docs/todo`, and native directory picker.
   Keep existing `todos.import` upserts, status/body import, and note/owner
   preservation. Extend stored metadata with size and source file/line.
   `mtm todo export --json` prints the proposed `Item` list above.
   Verify import against the current canonical inventory; a second import adds
   zero rows. Do not change completed dispositions or use the historical count.
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
reuses the start-agent flow, so the open B-63 durable queue (`~/proj/znbu/docs/todo/agents.md`)
is not a prerequisite.
