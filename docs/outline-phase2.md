# Modular deck: phase 2

Follow-ups to [the outline](outline.md). Nothing here is needed for the initial build; each item assumes the outline is built and extends it. Same conventions.

## 1. A page per unit

- today only work, context, captures, history and reviews have pages; notes, reminders, prompts, vim and panes live in modals or other units' pages
- every unit registers one page of its own, listed under its id in the registry, with keys and palette commands for managing that unit's rows and nothing else
  - notes page: by owner, inherited marked, `e` edit, `d` delete, `a` add under the pin
  - reminders page: next-due order, `t` toggle, `s` snooze, `e` edit
  - prompts page: presets and the queue side by side, `enter` dispatch, `e` edit, `d` drop, `m` move to a task
  - vim page: sessions, `enter` open, `d` forget
  - panes page: every pane of every session with harness, state, assignment, stale; `a` assign, `x` close
- all scoped, all with the `S` toggle, all read-only in `all` mode except assign
- `Page.unit` already names the owner; the shell orders the page list by unit id, so a new unit's page appears without edits elsewhere

## 2. The unit modal

- one binding on every page (`I`) opens the modal for that page's unit; from the palette, `unit: <id>` opens any unit's
- three sections, each a fold, all read from the registry and the store, never hand-written

```js
UnitModal = { unit: id,
              shape:    { structs: [Struct], relationships: [Relation], commands: [name], emits: [type], listens: [type], pages: [id] },
              notes:    [UnitNote],
              prompts:  [UnitPrompt] }
Struct    = { name, fields: [{ name, type, json?, doc? }] }            // from the Go source through `deck docs`
Relation  = { from: struct, kind: "belongs_to"|"has_many"|"has_one"|"through", to: struct, via? }
```

- shape fold: the unit's structs and their fields, the relationships as the outline writes them, each struct collapsed to its name until opened; this is the outline's §6 node for that unit, generated
- notes fold: free text on the unit, a change the person wants; `a` adds, `e` edits, `d` deletes, `space` selects for a prompt

```js
UnitNote   = { id, unit, text, status: "open"|"prompted"|"done", prompt_id?, created, done_at? }
UnitPrompt = { id, unit, note_ids: [id], text, preset?, window?, submitted?, turn_id?, created }
```

- `UnitNote belongs_to :unit; UnitNote belongs_to :prompt (optional)`
- `UnitPrompt belongs_to :unit; UnitPrompt has_many :notes; UnitPrompt belongs_to :pane (window); UnitPrompt has_one :turn (history)`

## 3. Notes to prompt to turn

- `p` in the notes fold builds a prompt from the selected notes
  - body: the unit's outline node (the shape fold as text), then the notes as a numbered list, then the build rules from outline §0b
  - the composer opens with it, so presets, attachments and edits apply; cwd defaults to the deck's own repo tree, not the pin's
- submit goes through `prompts.start-agent` or `prompts.queue` like any prompt; the notes flip to `prompted` with the prompt id, the prompt records the window
- the turn ends → history's `response-completed` for that window after the prompt's `prompt-submitted` → the prompt gets its `turn_id`, its notes flip to `done` with `done_at`
  - a `<task-notification>` prompt does not end it (same rule as reviews)
  - the review queue lists that turn like any other; opening it shows the notes it closed
- a note can be reopened (`o`), which clears `prompt_id` and `done_at`

```js
// flow
notes[space] → p → composer(prefilled) → prompts.start-agent → UnitPrompt{ window, submitted }
  → history: prompt-submitted … response-completed → UnitPrompt.turn_id, UnitNote.status = done
```

- tables: `unit_notes`, `unit_prompts`; owner: a new `meta` unit, so no domain unit stores notes about itself
- commands: `meta.add-note`, `meta.patch-note`, `meta.delete-note`, `meta.prompt`, `meta.reopen-note`
- emits: `unit_notes.changed`, `unit_prompts.changed`; listens: `agent-activity` (through history, for the turn end)

## 4. Also deferred

- focus mode (left out of the outline on purpose; its rules are in the old deck's TODO)
- neovim as the text input engine, if §10 of the outline settles on it
- a web shell over the bus and registry
- timing and trimming the e2e suites (wait for instructions)

## 5. Open decisions

- [ ] `I` or `ctrl+i` for the unit modal
- [ ] does the prompt body embed the outline node or link to it by path
- [ ] one prompt per unit at a time, or many in flight
- [ ] where the deck's own repo tree is recorded: settings, or a project named after the deck
