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

### B-08 Rail height budget: sections capped by percent, one-line rows, panes get most of it

status: ready · priority: p1 · size: M · owner: · branch: · verified:

Learned from tuios's own rail: `appearance.sidebar.sections = sessions:25,terminals,files:25,agents:34`
gives every section a percent share of the height, a section scrolls inside its share, and
`agent_rest_fold` folds a resting agent row to one line after a duration. Deck's rail today lets the
review queue grow without limit and spends two lines on every row, so half the value takes all the
space.

- each rail section gets a percent cap of the rail height from config, with a default that hands the
  majority to the panes section (for example `review:25,panes:60,working:15`); a section scrolls
  within its share and shows `+N more` or a scroll mark, never pushes the next section down
- rows are one line unless the second line carries something the first does not; the rule for when a
  row earns a second line is written in the outline (for example: selected row, agent with a message,
  row that is stale) and applies to every page
- the panes section keeps the grouping headings from §7.1; headings count against the section's share

Acceptance:

- with 40 finished turns and 3 panes on a 40-row terminal, the review section takes at most its share
  and the panes are all visible; `j` inside the review section scrolls it
- a resting pane row is one line; a selected or messaging row is two; `deck config init` writes the
  default shares and the e2e layout case asserts both

notes:
- 2026-10-19 from the comparison with tuios's sidebar.

### B-09 Pane lifecycle in the rail: working at the bottom and locked, review at the top, rest in the middle

status: ready · priority: p1 · size: L · owner: · branch: · verified:

The rail becomes three sections that a pane moves through. Replaces the two-section rule in §7.1.

```js
RailSection = "review" | "panes" | "working"
Lifecycle   = submit prompt → "working" (bottom, locked, oldest first, newest at the very bottom)
            → turn ends → "review" (top; jumps to the bottom of that section; pronounced style:
              background colour and a glyph)
            → every accordion opened (= reviewed) → "panes" (middle), but only once the rail focus
              moves to a different pane
```

- working section: a pane goes there the moment its state turns working or any active state after a
  prompt (agents for sure; terminals after a command are undecided, see below). Rows are locked:
  moving the cursor over a locked row shows no preview, the detail says `press u to unlock`; `u`
  unlocks that row until focus leaves it, then it locks again on its own
- review section: one row per pane that produced review records, never one per turn. Focusing the row
  shows the review accordion (B-10) as the default detail, not the Screen tab; the pane's screen is
  still reachable through the tab bar (B-06)
- panes section: everything else, grouped as `o`/`O` say
- a pane with nothing left to review returns to the middle only after the user moves rail focus off
  it, so the row does not jump from under the cursor

Acceptance:

- submitting a prompt through `p` moves the row to the bottom section within one refresh, locked, and
  `j` onto it shows the unlock hint and no screen; `u` shows the screen; `k` away then `j` back shows
  the hint again
- `turn_end` moves the row to the top section with the review style; opening every accordion then
  moving to another row returns it to the middle; it does not move while focused
- order in the working section is submission time, oldest first; in the review section, finishing
  time, oldest first
- §7.1 rewritten for three sections; `history_review` and `shared_navigation` cases updated

Open before claiming: do terminals enter the working section after a command, or agents only; the key
`u` is free today but check `deck list-actions`.

notes:
- 2026-10-19 the human called this the important one.

### B-10 Review accordion: the detail for a pane with unreviewed turns

status: ready · priority: p1 · size: L · owner: · branch: · verified:

Modelled on tuios-deck's Turns tab (`~/proj/tuios-deck` README "The Turns tab", `internal/ui/turns.go`):
an accordion, one row per thing to review, oldest at the top, everything collapsed on open.

```js
Accordion     = { pane, rows: [TurnRow], context: [ContextItem], auto_reviewable_count }
TurnRow       = { turn_id, prompts: [Prompt], response, started_at, completed_at,
                  reviewed_at?, auto_reviewable: bool, starred: bool, project_id, task_id }
// several review records on one turn_id (steering prompts, one response) collapse into one TurnRow
```

- opening a row marks it reviewed; a row stays open until the accordion closes. All opened → the pane
  is reviewed and B-09 lets it leave the review section
- auto-reviewable: a turn that has later prompts after it was most likely read outside deck. Those
  rows get a different background, a line above the list names the key that marks all of them
  reviewed at once; the most recent turn is never auto-marked
- several review records with the same turn id are one row with all its prompts listed and the one
  response
- `*` (or the key the outline picks) stars a row for finding later; starred rows are listed first on
  the reviews page
- every row carries the project and task of the pane that produced it
- under the turn rows, the context items extracted from those responses, sorted and uniq'd, most
  recent first, auto-associated with the pane's project and task; starrable in place. A starred
  context item shows in the detail of the task it is directly on and of that task's direct parents
  (the parent task chain and the project), not of siblings or cousins

Acceptance:

- a pane with three finished turns opens an accordion with three collapsed rows, oldest first;
  `enter` on one marks only it reviewed (`deck review list` shows `reviewed_at`)
- two review records with one turn id render as one row; opening it marks both
- turns 1 and 2 of 3 are flagged auto-reviewable, the mass key marks exactly those two
- a context item extracted from turn 3 appears under the rows, starring it makes it appear in the
  detail of the pane's task and project, and in no sibling task
- the review page lists starred rows first

notes:
- 2026-10-19 defined together with B-09; B-09 owns the rail movement, this owns the detail.

### B-11 Documents page: starred docs, glow preview, live mode, unread theme

status: ready · priority: p2 · size: M · owner: · branch: · verified:

Reviewable documents already exist as review entries (§6.6: an md or html the agent wrote). Give them
a page and a star.

```js
Document = { id, path, kind: "md"|"html", written_by: { session, window, turn_id }, project_id,
             task_id, starred, read_at?, created }
```

- a documents page, key to be chosen (`A` captures, `C` context, `H` history, `D` panes, `R` reviews,
  `T` tasks are taken), listing every agent-written document under the pin; starred first
- a starred document is also a context item on its direct parents, so it shows in the task's and
  project's detail (same parent rule as B-10) and in the context page
- highlighting an md row previews it in the detail with `glow -tln` style rendering (the exact glow
  flags to be confirmed against the installed glow); html rows show the source or a text rendering
- `enter` goes live on the preview the same way as a pane: keys go to glow, `ctrl+a d` comes back
- until a document has been opened live once, its row uses an "unread" theme that stands out;
  opening live sets `read_at` and the row goes quiet

Acceptance:

- the page lists the two documents the `history_review` case writes, unread-styled; `enter` then
  `ctrl+a d` round-trips and the row is no longer unread
- starring one shows it in the owning task's detail and the project's detail, and on the context page
- `deck document list --task ID` returns the rows with `starred` and `read_at`

notes:
- 2026-10-19 asked for with the review lifecycle; glow must be present on the host for the preview.

### B-06 Pane detail: tab bar with a live Screen tab first, learned from tuios-deck

status: ready · priority: p1 · size: L · owner: · branch: · verified:

Today a pane row's detail opens on the transcript (`TRANSCRIPT · ] Turns`), so moving `j`/`k` down
the rail shows text that looks the same for every agent. Telling panes apart means `enter` into live
mode and `ctrl+a d` back out, for every pane. tuios-deck solved this: the main area is a tab bar and
the first tab is the pane's screen.

What to take from `~/proj/tuios-deck` (README "The deck page", "Live: typing into a pane";
`internal/ui/model.go` tabs, `view.go` detailLines, `live.go`):

- tabs `1 Screen · 2 Activity · 3 Transcript · 4 Turns`, drawn as a bar at the top of the detail with
  the pane's `session › name`, its assignment glyph and path, stale age and last message beside it.
  `1`–`4`, `[` `]`, `tab` / `shift+tab` switch from the rail or the detail; the bar brightens and
  underlines the shown tab when the detail has focus
- Screen is the default and is read-only: the pane's rendered screen from `capture-pane`, redrawn when
  the stream says the pane printed, with a one-second safety re-read; keeps the scroll unless
  following the bottom; `G` follows newest output again; `j`/`k` scroll a line with the detail
  focused, `J`/`K` half a page
- `enter` on a pane goes live, which is the same Screen tab with the keyboard routed to the pane:
  the only visual change is the live bar and the cursor. `ctrl+a d` drops the keyboard and the Screen
  stays. `ctrl+a j`/`k` go live on the next or previous rail pane without leaving
- the rail never changes shape between browsing and live; the detail is never full-screen except
  `ctrl+a z`
- the detail re-reads once a second and the list refreshes on daemon events; selection, tab and
  scroll survive both

Keep from the current deck: the review-queue rows in the rail, the transcript and turns content, the
leader semantics in §7.1, and the stream lease rules already in the outline.

```js
PaneDetail = { tab: "screen"|"activity"|"transcript"|"turns", follow: bool, scroll: int,
               live: { keyboard: bool, view: "normal"|"zoomed"|"fullscreen" } }
```

Acceptance:

- selecting any pane row shows its actual screen within one second, without going live; two agents
  with the same name are distinguishable from the rail alone
- `1`–`4`, `[` `]` switch tabs from both the rail and the detail; the chosen tab persists per pane
  across refreshes and across re-selection
- `enter` then `ctrl+a d` leaves the detail on the Screen tab with the same scroll; the rail did not
  move or resize at any point
- outline §7.1 updated with the tab bar; the `shared_navigation` and live e2e cases assert the Screen
  tab and the detach round trip

notes:
- 2026-10-19 asked for after comparing with tuios-deck; this is the one the human called out as most
  important.

### B-07 Mass-add outline: prefill the existing tree and reuse names, learned from tuios-deck

status: ready · priority: p2 · size: M · owner: · branch: · verified:

The current mass-add (`alt+m` / `+ add new…`, outline §6.3 and §7.1) is a parked form where
`tab` / `shift+tab` nest new lines. tuios-deck's "Adding many at once" (README) is still a
plain outline but gets more right. Adopt:

- opens prefilled with every existing project (by name) and its tasks and subtasks nested beneath,
  drawn dim with their mark and status (`deck  ✓ done`), cursor on an empty line after them. The
  user sees where a new line lands and never retypes a parent
- existing names are reused, never duplicated: a line equal to an existing title under the same parent
  is the existing item, so new lines under it become its children. A top-level line may also name a
  task by path, `deck / command palette`, to add under it
- blank lines and `#` comments are skipped; the hint shows an example outline when the store is empty
- `ctrl+s` validates the whole outline first and refuses with the line number: indent under nothing,
  indent that jumps more than one level, odd spaces. Nothing is created on refusal; on success the
  status says `added N projects, M tasks` and the tasks page keeps its selection
- mass-add only adds: deleting a prefilled line deletes nothing, editing one renames nothing (the
  edited text is a new item). The hint says so
- line editing: `enter` splits and keeps the indent, `backspace` at line start joins, `ctrl+u` clears
  the line, `tab`/`shift+tab` indent and outdent without leaving the field, 14 lines visible with the
  cursor kept in view

Keep deck's rule that every root task needs a project (a bare top-level task line is a project, as in
tuios-deck, or is rejected; decide in the outline) and the one-parked-modal rule.

Acceptance:

- opening mass-add on a store with two projects and nested tasks shows them dim in the outline, and
  typing one indented line under an existing task creates exactly one task under it
- an invalid indent is refused with its line number and no row is written
- `deck task list` after a save shows the new rows in outline order with the right parents
- the `mass_add` outline case covers prefill, reuse, path lines, refusal and the status message

notes:
- 2026-10-19 "not great, but better than ours".

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
