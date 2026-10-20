# Forms redesign (B-31)

Every form and picker already runs on one engine, `internal/ui/forms.Editor`, fed by `internal/input.Engine`
and built from `registry.Form` definitions. What was wrong was the layout (one row of buttons, one value
visible), the ranking (a subsequence test), and the linkage (hard-coded to field names). The redesign keeps
the engine, the async sources with their revision guard, previews and `NewTarget`, and splits it into
separate pieces:

| piece        | file                         | changes when                              |
|--------------|------------------------------|-------------------------------------------|
| data         | `registry.Field` in each unit | a form gains or loses a field             |
| kinds        | `forms/kinds.go`             | a new kind of value (record, path, enum)  |
| linkage      | `forms/linkage.go`           | the hierarchy rules                       |
| ranking      | `forms/rank.go`              | completion order                          |
| validation   | `forms/validate.go`          | a new rule                                |
| keys         | `forms/input.go` + config    | bindings (remappable, in `list-actions`)  |
| presentation | `forms/layout*.go`, `view_list.go` (parts), `view.go` (box), `theme.go` | how it looks |

## Data: field definitions declare their relationships

```js
FieldDef = { name: "parent_id", label: "Assignment", key: "a", kind: "assignment",
             source?: "work.tasks", add?: "task" | "project" | "session",
             parent?: "project_id", exclude?: "id",
             required?: true, options?: ["one", "two"], unscoped?: true,
             validate?: "number" | "json" | "required", type?, multi?, hint }

Kind = { name: "task", source: "work.tasks", record: true, create: "task" }
// task      work.tasks                    records, create on no match
// parent    work.tasks + work.projects    records (a project means a root task), create on no match
// project   work.projects                 records, create on no match
// assignment  work.tasks + work.projects  combined project/task selection, staged optional descendants
// destination prompts.destinations        combined session/window selection; add: session permits creation
// directory | file | files                fs completion + ctrl+o native picker
// bool | number | json | multiline | text

Relationship = { child: "task", parent: "project", by: "ancestry" }  // derived from FieldDef.parent; never per form code
```

The start-agent form declares `{ name: "task", kind: "assignment", parent: "project" }`; add-task declares
`{ name: "parent_id", kind: "assignment", parent: "project_id" }`; edit and move keep `exclude: "id"`.
The paired parent definition supplies payload metadata but is not a second visible field. A picked task
fills both payload identifiers. A project selection opens an optional Task field instead. Destination
uses the same interaction for session/window, with Host displayed separately before it.

## Behaviour: one record graph, three rules

All record choices loaded by a form go into one graph `{ id → { parent, kind, label } }`; a root task's parent
is its project. Every rule is a walk of that graph:

- child sets parent: picking a child sets each `parent` field to the child's nearest ancestor of that field's
  kind (a task's project is its root project; a task's parent task is its direct parent), then cascades
- parent scopes child: a child's choices are the records under the parent's value, direct children first,
  with their path; an explicitly chosen parent filters strictly, a default (pin) parent only sorts first,
  so ownership pickers can still retarget across projects (outline §10)
- re-check: when the user changes a parent, a child no longer under it is cleared with
  `cleared: <child> not under <parent>` in the hint line

Completion ranks exact > prefix > word prefix > substring > subsequence over label, path and id. Tree mode
keeps ancestor context; `alt+f` flattens choices with paths inline. Unmatched composite-root text becomes a
new parent name on blur or Escape, then focuses an optional child. Newly named tasks repeat this until a
child is blank. Existing tasks do not add another child. All new work records save atomically through
`work.apply-tree-draft`, using unique `draft:` references rather than titles; intermediate records never
become command arguments. Session/window creation remains owned by the prompts unit.

Field labels and option labels show weighted shortest-unique suffix hints, recalculated after each query edit.
A repeated key costs 0.5; another key costs 1. Each repeat still consumes a distinct text character.
A space requires the preceding query character to be word-final, including a trailing space. Hints show
spaces as `␠` and show `‹enter›` when the query is unique. Unresolved hints show `‹…›`: search stops after
12 ordinary-keystroke units or 2,000,000 scanned query/text bytes. Every eligible competitor remains in
the uniqueness check; the limit never turns an ambiguous query into a unique hint.

## State

```js
FormState = { layout: "list" | "box", mode: "form-list" | "form" | "form-input" | "mass-add",
              cursor: 2, jumping: false, choosing: false, choosePrefix: "",
              finding: false, findQuery: "", findCursor: 0, findIndex: 0,
              fields: [{ id, owner?, def: FieldDef, text, query, index, origin: "default" | "user" | "derived",
                         choices: [Choice], flat: false, draftKind?, sourceRevision, err }],
              hint: "new: Fix login" }
Choice = { id, label, kind: "task", parent, path: "mtm › Login", preview }
Row    = { key: "t", label: "Assignment", recall: "‹n›", value: "Fix login", path: "mtm", state: "set | default | new | error",
           focused: true, input: true, required: true, missing: false }
```

## Keys (list layout, mode `form-list`)

Normal: `j`/`k` field cursor (also arrows), `g`/`G` first/last field, a field's letter focuses it and enters
input, `1`-`9` focus the Nth field, `'` shows jump labels and the next key jumps, `enter`/`i`/`/` input at the
cursor, `c` clear then input, `ctrl+n`/`ctrl+p` move the cursor field's options, `ctrl+h`/`ctrl+l` walk the
lineage, `tab`/`shift+tab` next/previous field, `ctrl+s` submit, `esc` close. Field letters skip
`j k g G u d h l i c ' / ?`.

`alt+/` opens the optional field finder from either mode in every layout. Type a fuzzy field query,
use `ctrl+n` / `ctrl+p` to move, and press Enter to edit that field. Escape cancels the finder.
Existing shortcuts still enter focused value search directly.

Input (`form-input`, shared with the box): `tab`/`shift+tab` next/previous field, `ctrl+n`/`ctrl+p` options,
`enter` picks (or ends a one-line text), `esc` normal, readline as before, `ctrl+o` native picker,
`ctrl+space` path completion. List layouts return to normal on the next field after picking; BOX keeps
its historical same-field input mode until Escape.

Both modes expose remappable `alt+c` cycle, `alt+o` choose, and `alt+f` tree/flat. Boolean choices include
true/false and an unset default when optional. Choice labels extend past `z`; Enter disambiguates a shorter
label, navigation scrolls the choices, and Escape cancels the chooser. Cycle and letter choice commit the
value in NORMAL; selecting a parent or typing a new name can instead focus a newly inserted child in INPUT.

Every asynchronous reply addresses a stable field identity and source generation. Inserting or removing
children cannot redirect an older result to another field. `DraftValues()` retains staged rows for prompt
stash; `Values()` contains only the original command payload. `registry.WithFormValues` gives sources a
snapshot of selected host/harness/model; only changed dependencies reload, without replacing typed values.

## Presentation

`forms.layout` (settings section `forms`, default `list`; the layouts are below). Every layout but `box`
draws the same parts: title and mode, then the status line (`<field>: <value> · <hint>`, `new: …`, `cleared: …`, `! error`),
then one row per field `› t  task      Fix login   mtm`, the focused choice field's options under it, and a
key line. A `Theme` holds focused and blurred styles; the box keeps its own renderer.

## Layouts: one interface, one file each

The setting `forms.layout` names a layout; the settings page lists the choices with a line each
(`settings.Definition.Choices`) and refuses any other value. The next form opened uses the new value, so it
switches without a restart.

```js
Layout = { name: "split", placement: "full" | "detail" | "overlay" | "top",
           keys: "form-list" | "form",                  // normal-mode table; every layout but box shares form-list
           size(width, height) => [w, h],               // inside the area the shell offers
           render(editor, width, height) => string }    // composes the shared parts below

Parts  = { head: [title · mode, status, rule], fieldBlock(width, rows, expand), expansion: options | editor,
           focusPanel, asideLines: prompt-target preview, foot: key line }
```

| layout   | placement | draws                                                                      |
|----------|-----------|----------------------------------------------------------------------------|
| `list`   | full      | head, every field row with the focused field's options under it, keys     |
| `split`  | full      | field rows left; the focused field's label, hint, editor and options right |
| `modal`  | overlay   | the list in a centred bordered panel over the dashboard                    |
| `inline` | detail    | the list beside the rail (full width under 100 columns)                    |
| `box`    | top       | the pre-B-31 box in the top eight lines, its own keys (tab cycling)        |

Linkage, ranking, create-on-no-match and validation live in the engine, so they behave the same under every
layout; the e2e cases `form_jump`, `form_child_parent`, `form_parent_scope`, `form_create` and
`form_layout_toggle` (`scripts/e2e_forms.py`) loop over every layout. `E2E_FORMS_LAYOUT=<name>` runs any other
outline case under one layout. Adding a layout is a file with an `init()` that calls `registerLayout`, plus its
line in the setting's choices.
