# Todo

The one place to write down what deck should do next. Humans add items; agents on vps2 pick them up.
Finished items roll into the outline, so this file only ever holds open work.
[The outline](outline.md) stays the target design; an item here is work toward it and moves into the
outline's done list when it ships.

## How to use this file

- One item per `### B-nn` heading. Give it an ID, a status, a size and acceptance you could check from
  a terminal. Empty fields are fine; a title alone is a valid item.
- Status is one of `idea`, `ready`, `claimed`, `review`, `done`, `parked`. Only `ready` items may be
  claimed.
- An agent claims an item by setting `status: claimed` and `owner: <tuios agent id or name>` on a branch
  pushed to the vps2 hub, so two agents never take the same item. It flips to `review` with the branch
  name and the verification log path, and the human or the orchestrator moves it to `done`.
- Keep notes under the item, dated, newest last. Decisions go there, not in chat.
- Work the list top to bottom inside a priority. `p1` is tonight, `p2` is this week, `p3` is someday.

```js
Item = { id: "B-01", status: "ready", priority: "p1", size: "M",   // S < half a day, M a day, L more
         owner: "", branch: "", verified: "",                          // filled by the claiming agent
         acceptance: ["checkable statement", ...], notes: ["2026-10-19 …"] }
```

## p1 · tonight

### B-03 Gather TUI design samples for every deck screen and widget

status: review · priority: p1 · size: S · owner: Claude Fable subagent (session_01Cg7zBUciGaMHsqweicyuGP) · branch: main (redeck-astra) · verified: file reviewed by the parent session; 55 samples, 73 unique links

Research only, no code. For each screen type and widget deck uses (dashboard rail + detail, two-line
rows and group headings, detail key/value blocks, fuzzy filter and palette, forms and pickers, prompt
composer, tree editor, help overlay, catalog browser, live mode, the history/reviews/captures/context/
tasks pages, status line and notices), collect 2 to 4 samples from popular TUI tools and the web with
links and a note on what deck could borrow. Output is `redeck-astra/docs/research/tui-design-samples.md`. It feeds a
later restyle item.

Acceptance:

- the file exists with a section per area, every link was actually fetched or returned by a search
- a closing "Patterns worth adopting" list and a "Not found" list

notes:
- 2026-10-19 started in the background by a subagent while the rest of the backlog is written.
- 2026-10-19 done, committed in redeck-astra. Not found: a public assign-flow sample with snapshot + approval, a composer showing the target pane's scrollback, stable images for Telescope/Textual/lazygit dialogs, an authoritative TUI design article. Waiting on the human to read it and move it to done.

### B-01 Orchestrator agent that catches agents spinning their wheels

status: ready · priority: p1 · size: M · owner: · branch: · verified:

An always-on agent in its own tuios pane on vps2. It watches every worker agent in its fleet, decides
whether each one is still making progress, and talks to the ones that are not. It never edits code.

What "spinning wheels" means, any one of these:

- same reported state for longer than 20 minutes while `working`, with no new commit on its branch
- the same file edited or the same command run three times with the same failure in the tail of the pane
- a `needs_input` prompt that has waited more than 10 minutes
- more than 90 minutes on one backlog item of size S, or three hours on M

What it does about it, in order:

1. reads the pane tail and the item's notes before saying anything
2. mails the worker one question through tuios mail: what it is trying, what blocked it, what it will try
   next. One message, then wait for the reply, no reply chains.
3. if the answer is a plan, let it run and check again at the next deadline; if the answer is the same
   plan as before, tell it to stop, commit what it has to its branch, write a dated note under the item,
   and release the item back to `ready`
4. answers `needs_input` prompts itself only when the question is one the backlog item already answers;
   otherwise leaves it and includes it in the morning report
5. writes a morning report to `znbu/docs/reports/<date>.md`: per item, status, branch, what shipped, what is
   stuck and why, and what needs the human

Acceptance:

- a worker agent stuck in a loop on a throwaway task gets one mail within 25 minutes and is released
  within 60, with the item back at `ready` and a note explaining why
- a worker that is slow but progressing is not interrupted
- the orchestrator never sends keys into a pane that is `needs_input` without reading the prompt first
- the morning report exists and names every item touched overnight
- it runs on vps2 with finite timeouts on every call and survives its own tuios daemon restart

Start from `tuios --skill fleet` and `tuios --skill recipes` (the conductor recipe), `tuios list-agents
--json`, `tuios subscribe` for state changes, and `tuios read-agent-messages` / `send-agent-message`.
Checkpoints (`tuios --skill checkpoints`) give it a per-turn diff to judge progress without reading the
whole pane.

notes:
- 2026-10-19 asked for so a batch of features can run on vps2 overnight without the human watching.

## p2 · this week

### B-05 Notes on almost anything, shown in the detail pane of every page

status: ready · priority: p2 · size: L · owner: · branch: · verified:

Today a note belongs to exactly one task or project (outline §6.8). Open it up so a note can hang
off nearly any row deck shows, and so the page that lists those rows shows their notes in the
main-content area on the right, not in a modal.

```js
Note    = { id, text, owner: Owner, created, updated }
Owner   = { kind: "task"|"project"|"pane"|"context"|"capture"|"review"|"vim"|"reminder"|"prompt", id }
// pane notes key on session + window id, like captures, and stay readable after the pane closes
Visible = { note: Note, via: "own"|"parent"|"project"|"owner", owner: name }   // inherited marking stays
```

Pieces, in build order:

1. store + commands: polymorphic owner on `notes`, migration of the two existing columns into it,
   `notes.add|patch|delete` accept `owner`, `deck note list --owner kind:id`, visibility rules keep
   today's task/project inheritance and add "a row sees its own notes"
2. detail pane: every page's detail ends with a `NOTES` section for the selected row, newest last,
   inherited notes marked with `via`, wrapped to the detail width, scrolling with the rest of the
   detail; empty shows one dim line, never a blank gap
3. keys: add a note under the selected row from any page, edit and delete a note when detail focus is
   on it; the form is the existing notes textarea with the owner prefilled and shown in the title.
   `a` is taken by Assign and `n` by "create on this page", so pick the key in the outline first
4. the notes page from phase 2 §1 (by owner, inherited marked) can come after; it is not needed for
   the detail view

Acceptance:

- `deck note add --json '{"owner":{"kind":"pane","id":"<session/window>"},"text":"…"}'` works for every
  kind in `Owner`, and `deck note list --owner` returns it; unknown kinds are rejected with `invalid_args`
- on each of Panes, Tasks, Context, Captures, History, Reviews, the detail of a row with notes shows the
  `NOTES` section with the text, and the rail row carries a note count or glyph
- adding, editing and deleting from the detail keeps the selection and scroll (same rule as refresh)
- the `descendant_notes` outline case still passes and gains one assertion per new owner kind

Open before claiming: the key for "add note here"; whether a review note belongs to the turn or to the
history entry; whether a closed pane's notes surface anywhere besides history.

notes:
- 2026-10-19 asked for notes on "almost anything", displayed in the right pane on that item's page.

### B-04 Help modal: two rows shift left and leak border glyphs

status: ready · priority: p2 · size: S · owner: · branch: · verified:

Screenshot: [attachments/B-04-help-modal-alignment.png](attachments/B-04-help-modal-alignment.png),
deck on a wide terminal, `?` on the Panes page, filter `all`.

What is wrong, visible in the screenshot:

- two rows are one cell left of every other row, in both columns at once: the row holding `}` / `h`
  ("Fold tree or return to parent (also Left)") and the row holding `d` / `l` ("Expand tree or
  inspect option (also Right)"). The same rows show a stray `│` at the left edge of the modal and
  another just inside the right edge, so the row is being rendered one cell wider than the panel.
  Probable cause, unverified: those two right-column descriptions are the widest in their group and
  overflow the column by one cell, so the joined row breaks the border. Check the width measurement
  on a row whose description is exactly the column width.
- the description column starts at a different x in every group (PAGES at the key + 1 cell, MOVE
  padded to `shift+tab`, SHELL to `ctrl+r`, SELECTION to `delete`, FORM narrower again), so the two
  columns read as a ragged stack of tables rather than one. Decide whether descriptions align per
  column (one key width per column) or per group, and apply it everywhere; the approved reference is
  `images/help-good.png`.

Acceptance:

- no row in the help modal is offset from its neighbours and no border glyph appears inside a row, at
  80, 120 and 200 columns, for every tab filter
- descriptions line up according to the chosen rule, and the e2e help case asserts the rule on at
  least one wide and one narrow capture

notes:
- 2026-10-19 reported from a screenshot; not to be worked on yet.

## p3 · someday

### B-02 Deck-owned agent messaging (shared places)

status: idea · priority: p2 · size: L

Already designed in [the outline](outline.md) under the code unit, "shared places": the deck owns the
record (`PlaceMessage`, `Claim`) and the routing, tuios mail is only the transport, and every message
lands in history under the sender's task. Open decisions 598 (deck server) and 610 (messages to a human
terminal) gate parts of it. Split into claimable items when it comes up.

notes:
- 2026-10-19 the design was settled earlier today in the outline; this entry only tracks building it.

## Done

Move finished items here with their branch and the verification log path, then add the behavior to the
outline's done list.
