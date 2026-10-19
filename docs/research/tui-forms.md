# TUI forms: research for deck's forms redesign

Input to B-31 (forms redesign). Deck is Go on Bubble Tea v2 (`charm.land/bubbletea/v2`) and Lip Gloss v2.
Each source lists what it does well, where to look, and what deck should take. The recommendation is
at the end.

What deck needs from a form, from the outline (§7.1 forms) and B-31:

```js
Need = { modal: "normal | input",          // keys pick fields in normal mode, type in input mode
         jump: "one key per field",         // not tab-cycling
         fields: "visible list, every value shown",
         completion: "fuzzy over real records, current value first, preview into rail/detail",
         hierarchy: "child sets parent; parent scopes child",
         create: "no exact match → new record on submit, hint `new: <text>`",
         engine: "the one shared modal input engine (internal/input), registry-driven bindings + help" }
```

## 1. deck today — `internal/ui/forms/*.go` (redeck-astra2)

Files: `/Users/unixsuperhero/proj/redeck-astra2/internal/ui/forms/{editor,input,choices,view}.go`
(about 1500 lines), `/Users/unixsuperhero/proj/redeck-astra2/internal/input/` (`Engine`, `EditText`,
`ListIndex`), outline lines 115 and 463-473.

```js
Field  = { name, key, source: "work.tasks", preview, add, hint, type: "text|bool|number|json|path|textarea", multi }
Form   = { id, submit: commandName, fields: [Field], box: "top" }
Editor = { fields: [fieldState], focus, engine: input.Engine, revision, lineage, completions }
fieldState = { text, cursor, selected, choices, previews, query, index, touched, loading, derivedProject }
```

Does well:
- already modal: `Form` and `FormInput` modes in `internal/config/keys.go`, fed through `input.Engine`,
  so remaps and the help modal see every form key
- `assignKeys` gives every field one highlighted letter, skipping keys the list actions use
- sources are registry queries (`Field.Source`), loaded async with a `revision` guard against stale
  replies; previews on `ctrl+n`/`ctrl+p` select the object in the rail and detail
- create-on-no-match exists: `submission()` returns `NewTarget{Field, Kind, Text, ParentID, ProjectID}`
- one linkage rule exists: `inheritProject` sets the project field from a picked task's
  `root_project_id`; `parent-up`/`parent-down` walk the lineage

Falls short:
- `Height()` is a constant 8: the box shows one row of field buttons and only the focused field's value,
  so the user cannot see the whole form
- linkage is one-way and hard-coded to field names (`task`, `task_id`, `parent_id`); a parent does not
  scope the child's choices, and changing a parent never re-checks the child
- fuzzy is a subsequence test (`choices.go fuzzy`), no ranking, no current-value-first
- per-type behaviour is a switch in `inputKey` rather than a field kind with its own source and
  completion

Take: keep the engine, the registry-driven fields, `NewTarget`, the revision guard and previews. Replace
the layout, the ranking, and the linkage.

## 2. tuios — `internal/app/*_prompt.go`, `internal/overlay`

Files: `~/proj/tuios/internal/app/worktree_prompt.go`, `render_worktree_prompt.go`,
`render_file_prompt.go`, `render_dialog_text.go`, `internal/input/worktree_prompt_input.go`,
`internal/app/command_palette.go`, `pkg/fuzzy`. tuios does not use huh or bubbles at all; every dialog
is hand-built on Lip Gloss v2.

Does well:
- one dialog shape for every prompt: `overlay.Dialog{Title, Width, Body, Hints: [{Key, Label}]}`,
  centred, width from `overlay.DialogFitWidth(preferred, screenWidth)`
- a field row is `sigil + label column (fixed width) + value`; the inactive marker is padded to the sigil
  width so labels stay in one column
- an empty field shows the value the verb will derive (the session name from repo + branch) in the
  muted ink, so the default is visible rather than imagined
- text windows to its tail so the cursor stays visible; paths are cut from the front
- the refusal replaces the hint line under the fields, so a second try looks in the same place
- input is a tiny per-dialog handler (`esc`, `enter`, `tab`, then shared `promptTextKeys`)
- the palette ranks with its own `pkg/fuzzy` and groups rows by category

Take: the row shape (sigil, aligned label column, value, muted derived default), the error-in-hint-line
rule, the hint footer, and a ranked fuzzy package. Do not take tab-only focus or per-dialog key code.

## 3. charmbracelet/huh — the Bubble Tea form library

Links: https://github.com/charmbracelet/huh; v2 is `charm.land/huh/v2` v2.0.3 (2026-03-10, on
`charm.land/bubbletea/v2` v2.0.2, `charm.land/bubbles/v2` v2.0.0, `charm.land/lipgloss/v2` v2.0.1).
Local v1 source: `~/go/pkg/mod/github.com/charmbracelet/huh@v0.8.0`.

```js
Form  = { groups: [Group], theme, keymap, accessible, layout, showHelp, showErrors }
Group = { title, description, fields: [Field], hideFunc }         // a group is a page
Field = Input | Text | Select[T] | MultiSelect[T] | Confirm | Note | FilePicker
Input = { title | TitleFunc(fn, bindings), suggestions | SuggestionsFunc(fn, bindings), validate, value: &string }
Select[T] = { options | OptionsFunc(fn, bindings), filtering, inline, height, value: &T }
```

Does well:
- dependent fields: `TitleFunc`, `DescriptionFunc`, `OptionsFunc`, `SuggestionsFunc` take a function and
  a `bindings` pointer; huh hashes the bindings and re-runs the function only when the hash changes
  (`eval.go`, cached per hash), running `OptionsFunc` inside a `tea.Cmd` (`updateOptionsMsg`). This is the
  cleanest model of "a child's options depend on its parent" in any Go form library
- `Validate(func(T) error)` per field; errors drawn under the field and blocking advance
- `Theme` (v2: a function of dark/light returning `*Styles`) with `Focused` and `Blurred`
  `FieldStyles` (title, description, selector, option, selected option, error) and five bundled themes
- accessible mode: the same form runs as plain line-by-line prompts with no TUI
- `Group.WithHideFunc` skips whole pages conditionally; `Layout` stacks or columns groups
- `Select` filters with `/`

Falls short for deck:
- focus is sequential only: `NextField`, `PrevField`, `NextGroup`, `PrevGroup`; there is no "jump to
  field by key" and no normal/input split; every printable key goes to the focused field
- each field kind owns its own `KeyMap` (`InputKeyMap`, `SelectKeyMap`, …) built on `bubbles/key`, outside
  deck's `input.Engine`, so remaps and the help modal would need a second binding source
- `Select` cannot hold free text, so create-on-no-match needs an `Input` plus suggestions, which only
  prefix-match
- the form owns the screen region it draws; deck wants previews to drive the rail and detail

Take: the `OptionsFunc(fn, bindings)` dependency model (re-evaluate on the parent's value, cache by
value, async with a guard), per-field `Validate`, the `Focused`/`Blurred` theme struct, and an accessible
fallback (deck's is the CLI: `deck <concept> <command> --json`).

## 4. bubbles v2 — textinput suggestions, list filtering

Links: https://github.com/charmbracelet/bubbles (`charm.land/bubbles/v2` v2.1.1), `textinput/`,
`list/`. Local v1: `~/go/pkg/mod/github.com/charmbracelet/bubbles@v0.21.1-…/textinput/textinput.go`.

Does well:
- `textinput`: `SetSuggestions`, `ShowSuggestions`, `AcceptSuggestion` (`tab`), `NextSuggestion` /
  `PrevSuggestion` (`ctrl+n` / `ctrl+p`), the rest of the suggestion drawn as ghost text after the cursor
- `list`: fuzzy filter (`sahilm/fuzzy`) with matched-rune highlighting, status bar with counts,
  pagination, `FilterValue()` per item

Falls short: suggestions are prefix-only and single-line; the list is a whole page component with its
own keymap.

Take: ghost text for the best completion in a text field, and matched-rune highlighting in option rows.

## 5. lazygit — menus and prompts with suggestions

Links: https://github.com/jesseduffield/lazygit, `pkg/gui/types/common.go` (`PromptOpts{Title,
InitialContent, FindSuggestionsFunc, HandleConfirm}`, `MenuItem{Label, Key, OnPress, Tooltip}`),
`pkg/gui/controllers/helpers/suggestions_helper.go`.

Does well:
- a prompt is a single text field with a suggestions panel under it fed by `FindSuggestionsFunc(text)`;
  new-branch and checkout prompts suggest existing branches, and typing a name that matches nothing
  simply creates it: create-on-no-match with no extra step
- menus show each option's key in a muted column; one key picks, or move and `enter`
- confirmations are a small box with the question and `enter`/`esc` hints

Take: suggestions recomputed from the typed text on each keystroke, and "no match means create" as the
plain default; the key column for option rows.

## 6. k9s — tview forms in dialogs

Links: https://github.com/derailed/k9s, `internal/view/pf_dialog.go` (port-forward form),
`internal/ui/dialog/{prompt,confirm,plugin_inputs}.go`.

Does well: a centred dialog with labelled rows (label column, input), defaults prefilled from the
selected resource (container, ports), OK/Cancel buttons, validation on submit that leaves the dialog
open.

Falls short: tab-only focus, no completion.

Take: prefill every field from the current selection (deck: the pin and the highlighted row).

## 7. gh-dash — search bar with autocomplete

Links: https://github.com/dlvhdr/gh-dash, `internal/tui/components/search/search.go`,
`internal/tui/components/inputbox/inputbox.go` (`SetAutocomplete`), `internal/tui/components/fuzzyselect/`.

Does well: the search and comment inputs are bubbles text inputs with a `fuzzyselect` autocomplete
whose items come from data already loaded (labels, users, repos), fuzzy-filtered as you type, shown in
a dropdown under the field, toggled by one key, excluding values already present.

Take: completion sources are deck's own loaded records, not a separate fetch, so it is instant.

## 8. posting — jump mode and autocomplete (Textual)

Links: https://github.com/darrenburns/posting, `docs/guide/navigation.md` (jump mode),
`src/posting/widgets/input.py`, `jump_overlay.py`.

Does well:
- jump mode: one key overlays a letter on every focusable widget; the next letter focuses it. Fields
  never fight list keys because labels exist only while the overlay is up
- URL and header inputs autocomplete from history and variables (`$var`), with a dropdown

Take: the fallback when a form has more fields than free letters: a jump key that labels every field.

## 9. Textual — Input, Select, validation

Links: https://textual.textualize.io/widgets/input/ (`suggester=SuggestFromList`, `validators=[…]`,
`valid_empty`), https://textual.textualize.io/widgets/select/, https://textual.textualize.io/widgets/selection_list/.

Does well: an `Input` takes a `Suggester` object (async, cached, case-insensitive) and a list of
validators whose failures style the input and post a `Changed` event; `Select` and `SelectionList` are
separate widgets for one and many.

Take: a completion source is an object per field kind (`Suggester`), separate from the field; validation
is declarative per field.

## Synthesis for deck

```js
FieldKind  = { name: "task", source: "work.tasks", rank: "fuzzy(title, path)", currentFirst: true,
               createKind: "task", parentField: "parent", projectField: "project", validate }
DependsOn  = { field: "task", on: ["project", "parent"] }   // huh's bindings, made explicit in the registry
FormRow    = { key: "t", label: "task", value: "Fix login ▸ deck", state: "set | default | new | error" }
```

- layout: tuios's row shape, every field visible with its value; the focused field opens its option
  list under it
- keys: deck's own modal engine; one letter per field in normal mode, posting-style jump labels as the
  fallback
- completion: per field kind, ranked fuzzy, current value first, ghost text (bubbles) and matched-rune
  highlights
- dependencies: huh's `OptionsFunc(fn, bindings)` idea, declared in the registry as `dependsOn`
- create: lazygit's "no match creates", with deck's `new: <text>` hint

## Recommendation: rebuild deck's engine (do not adopt or wrap huh)

Rebuild `internal/ui/forms` on deck's existing `internal/input` engine and registry, borrowing huh's
ideas rather than its code.

Reasons:
1. Modal field jumps are the core of the design, and huh has no normal mode and no jump-to-field API;
   its focus is `NextField`/`PrevField` only. Adding them means forking `Form` and `Group`.
2. Deck has one shared modal input engine and one binding source (`internal/config/keys.go`, the
   registry, `deck list-actions`, the help modal). huh brings a second key system per field kind
   (`bubbles/key` keymaps), which breaks remapping and the effective-bindings help.
3. Create-on-no-match and fuzzy ranking over records need a select that holds free text; huh's `Select`
   cannot, and its `Input` suggestions only prefix-match.
4. Hierarchy linkage (child sets parent, parent scopes child, re-check on change) is deck-specific; huh's
   `OptionsFunc` covers the scoping half, and the cost of wrapping is higher than writing the 50-line
   dependency evaluator deck needs.
5. Deck already owns most of the parts (async sources with a revision guard, previews, `NewTarget`,
   readline editing); what is wrong is the layout and the linkage, both of which a rewrite fixes.

Wrapping huh would only pay off for throwaway yes/no and single-text prompts; those already run on
deck's modal slot, so one engine stays simpler. huh v2 being on Bubble Tea v2 removes the compatibility
objection, not the design ones.
