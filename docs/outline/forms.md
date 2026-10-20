# Forms, navigation, settings, and UI state

This document separates implemented behavior from target decisions. [Remaining work](../todo/forms.md) uses the same topics. Source paths in code font are relative to Matomeru. Historical verification below is recorded evidence, not a check performed during this consolidation.

<a id="navigation"></a>
## Navigation and input

The shared input engine owns modes, effective bindings, and actions. Forms, modal lists, help, palette, trees, page lists, and completion lists use the same navigation vocabulary. Normal mode uses `j` and `k` for one item, `h` and `l` for area changes or tree folds, `d` and `u` for half a visible page, `ctrl+f` and `ctrl+b` for a full visible page, and `g` and `G` for the ends. `{` and `}` select the start of the previous or next contiguous section. Lists without sections use their first and last items. Arrows, Home, End, PageUp, and PageDown remain available. Page distances account for headings and multiline entries.

Text input preserves printable characters, including motion letters and braces. Readline editing takes priority: `ctrl+a` and `ctrl+e` reach current-line edges, `ctrl+b` and `ctrl+f` move one character, and `ctrl+h` erases text. `ctrl+n` and `ctrl+p` navigate suggestions while typing. Raw BS and DEL remain distinct in configuration. Form input uses `alt+h` for parent-up so `ctrl+h` remains Backspace; normal form mode retains `ctrl+h` for parent-up. Delete uses the Delete key. Mass-add uses `alt+m`, not the full-page-backward chord.

The shell has one modal slot and one parked form for bulk creation. A modal replaces or closes the active slot. The model holds selection, scroll, page, filter, modal, confirmation, live state, and status rather than domain rules. Help, focus, and live gates have a fixed priority before ordinary modes. A third independent overlay would require an explicit stack, not another unrelated return path. These last architectural constraints, unified paste routing, status dismissal without consuming Escape, one post-handler settle point, panic recovery, timers, and possible mouse hit rectangles remain [event-loop decisions](architecture.md#eventloop), not claims that every recommendation is implemented.

Source: [original shell and Bubble Tea notes](../sources/znbu/docs/outline.md), sections 7.1 and 7.1a; [implementation outline](../sources/matomeru/docs/outline.md), sections 7.1 and 10. The configured live leader belongs to [panes](panes.md), not text-input navigation.

<a id="b-31"></a>
<a id="forms"></a>
## B-31 implemented form engine

Status: partial acceptance, with a verified committed baseline. Commits `5f1bd56` and `fff163c` implement the shared engine and its later combined selectors. The assignment records `fff163c` as verified in the preceding work. The older B-31 log is `vps2:/root/proj/redeck-astra-verification/runs/run.VRG1P8eF/verification.log`; that run used 150 columns and explicitly did not cover the original 80/200-column requirement. [B-31 remaining acceptance](../todo/forms.md#b-31) keeps that gap without calling the committed engine unverified.

One `internal/ui/forms.Editor`, fed by `internal/input.Engine`, reads registry form definitions. Kinds, linkage, ranking, validation, keys, and rendering are separate concerns. `editor.go`, `kinds.go`, `linkage.go`, `choices.go`, `rank.go`, `validate.go`, `input.go`, and `layout*.go` are the implementation evidence identified by the audit. The [detailed canonical plan](../plans/forms-redesign.md) preserves the schemas, algorithms, limits, and layout interface.

```js
Form = { id, submit: commandName, fields: [Field] }
Field = { name, label?, key?, kind?, source?, preview?, add?, parent?, exclude?,
          required?, options?, unscoped?, validate?, type?, multi?, hint? }
Row = { key, label, recall?, value, path?, state: "set | default | new | error",
        focused, input, required, missing }
```

`kind` selects completion, source, filesystem picker, and validation. An omitted kind falls back to the older type/source metadata. Relationships use the actual `parent` and `exclude` schema. The research proposal called this `dependsOn`; it is not a second mandatory field API. `exclude` removes the edited record and its descendants from its own parent choices.

### Layouts and keys

`forms.layout` is an enumerated setting. Changing it affects the next opened form without a restart. Layouts change presentation, not ranking, linkage, creation, or validation.

Single-select fields share one options control across forms and layouts. Definitions supply the options and whether custom text is accepted. Finite settings, including `forms.layout`, use the same cycle and labeled-choice behavior as other finite fields. Suggested paths use the editable variant, with the native picker still available. A selected path must remain editable without retyping it; nearby suggestions must not overwrite a manually edited path.

For a suggested path, use `alt+o` and its displayed label to select it, then edit the field with `i`, Enter, or its field shortcut. The editor starts with the full selected path. Enter commits the edited text even when similar suggestions remain. Escape, Tab, and submit also preserve the edit. `ctrl+n` or `ctrl+p` explicitly returns to selecting a suggestion.

| Value | Placement and behavior |
| --- | --- |
| `list` | Default, full-width field/value rows, focused editor or choices below its row |
| `split` | Field rows left, focused label, hint, editor, and choices right |
| `modal` | Centered bordered panel over the dashboard |
| `inline` | Detail area beside the rail, full width below 100 columns |
| `box` | Retained compact top-eight-line presentation with historical tab cycling |

The title names the form and mode. A status line shows the focused full value, hint, creation intent, cleared-child explanation, or validation error. Each field has a value row, followed by its active editor or choices and a binding footer. Required fields carry `*`; empty required values say `missing required` in a bold error style in every layout. Filled required values remain emphasized. Validation uses the effective edited value and still checks numeric and JSON rules.

Normal mode supports field letters, `1` through `9`, and a `'` jump-label overlay. Field accelerators skip configured motions and reserved `j k g G u d h l i c ' / ?`. `enter`, `i`, or `/` edits the current field; `c` clears then edits; `ctrl+s` submits; Escape closes. In input mode, Tab and Shift+Tab switch fields, `ctrl+n` and `ctrl+p` move options, and Escape returns to normal. Enter commits a choice or a single-line edit and advances in list layouts. `box` retains same-field input after a pick until Escape. A selected parent can instead focus a newly inserted child.

`alt+/` opens a fuzzy field finder in every layout and mode. Escape cancels it. `alt+c` cycles booleans and options with wraparound; optional booleans include the unset default. `alt+o` opens labeled choice mode. Labels extend beyond `z`, Enter disambiguates a shorter ambiguous label, navigation scrolls, and Escape cancels. These actions are remappable. `alt+f` switches between a hierarchical tree and flat paths.

### Completion, hierarchy, and creation

Completion ranks exact, prefix, word-prefix, substring, and subsequence matches over label, path, and identifier, with the current value first. Moving an option previews its object in the rail and detail. Tree filtering retains matching descendants and their ancestors. Flat choices retain ancestry inline.

Recall hints use the same matcher as filtering and recompute after each query edit. Repeating the preceding key costs 0.5; another key costs 1. Every repeat consumes a distinct character. A space, including a trailing space, requires the preceding character to end a word. `␠` displays a required space and `‹enter›` means the query is unique. Search stops after 12 ordinary-keystroke units or 2,000,000 scanned query/text bytes. `‹…›` means unresolved, not unique. Every eligible competitor, including offscreen choices, participates.

All record choices form an ancestry graph. Picking a child fills its nearest parent of the declared kind and cascades. A task supplies its root project. An explicitly chosen parent strictly filters descendants, direct children first. A default parent from the pin only sorts its children first, so ownership can move across projects. Changing an explicit parent clears an incompatible child with `cleared: <child> not under <parent>`.

An `assignment` field combines project and task instead of showing the paired project payload field. Selecting a task fills both identifiers without adding another child. Selecting a project opens an optional Task row. Unmatched root text commits as a new project name on blur or Escape and focuses its optional Task. Each newly named task can open a Subtask until a child is blank; an existing task does not add another child.

A `destination` combines session and window. Host precedes it. A picked window supplies host and session. With `add: "session"`, a selected or new session opens an optional Window/name row. A blank child creates a window, an existing name chooses that window, and unmatched text names a new one. Assignment-only destinations omit `add` and accept existing windows, including those outside the current task pin. Session/window creation stays in prompts, not work.

No case-insensitive exact match adds a final `+ new <kind>: <text>` choice, selected when no record matches. The hint states `new: <text> under <parent>`. Typing and cancellation create nothing. Work creation uses unique `draft:` references, never names, and one `work.apply-tree-draft` transaction, parents first. Duplicate names remain separate identities. Only resolved command fields reach submission. `DraftValues()` retains staged rows for stashes; `Values()` contains the original command payload.

Async sources, completions, and native picks address stable field identities and source generations. Inserted or removed rows cannot redirect an older reply to another field. `registry.WithFormValues` supplies a snapshot of host, harness, and model. Only changed dependencies reload; unrelated typed values stay intact.

Kinds cover task, parent, project, assignment, destination, window, preset, status enum, filesystem paths, booleans, numeric values, JSON, text history, and multiline text. The full disk-catalog-backed agent/skill completer remains dependent on [B-34](../todo/agents.md#b-34). The separately implemented [Prompt/Settings composer](agents.md#composer) has newer owner-reported verification in commit `e4cf07a`; it is not inferred from this earlier baseline.

Sources: [B-31 original acceptance and historical note](../sources/znbu/docs/todo.md#b-31-forms-redesign-precise-modal-hierarchy-aware-replaces-the-top-8-lines-box); [preserved detailed plan](../sources/matomeru/docs/plans/forms-redesign.md); [implementation shell contract](../sources/matomeru/docs/outline.md), section 7.1.

<a id="nativepickers"></a>
## Native filesystem pickers

Directory, file, and multi-file fields keep the native OS picker through the configured picker binding, normally `ctrl+o`. `ctrl+space` requests path completion. Native dialogs retain platform navigation rather than adopting list motions. Local native-picker acceptance is macOS-specific; a Linux exclusion is not a successful native-dialog check.

Commit `e4cf07a` adds host-dependent launch safety: remote hosts do not receive local directory suggestions or local picker results, local cwd validation, or local MCP setup. The owner reports VPS SSH remote-launch acceptance for this extension. Native macOS picker interaction was not exercised on Linux. [Launch defaults](agents.md#launchdefaults) and [ranked directories](work.md#rankedpaths) record their current scope.

<a id="b-04"></a>
<a id="help"></a>
## B-04 help and effective binding reference

Status: implemented. `internal/ui/help_view.go` measures one key width per column, wraps descriptions beneath that column, and pads the border. `internal/ui/view.go` strips U+FE0E and U+FE0F in `clean()`. Terminals disagreed about those variation selectors behind the overlay, shifting rows and leaking a border glyph. The original hypothesis of a description-width bug was not the confirmed cause.

The approved [help image](../images/help-good.png) defines appearance, not keys. The centered thin-bordered `Keys` panel leaves the dashboard visible. Wide terminals have two balanced columns with clear gutters and groups kept together; narrow terminals have one column. Groups include Pages, Move, Shell, Live, Selection, List & Palette, and Form. Keys use the accent, descriptions the normal foreground, and headings and borders a readable secondary foreground. Long descriptions wrap, not silently clip. Short terminals scroll with a position/overflow cue and a fixed close hint.

Help derives keys and descriptions from effective registry/config bindings, including remaps, multi-key chords, current mode, selection-specific actions, and the configured live leader. Unbound actions remain searchable. Tab and Shift+Tab select overview/mode filters, `/` filters, list navigation and section jumps select shortcuts, and Enter inspects the effective action. Closing restores selection, filter, scroll, and modal state without sending a key to a pane.

Commit `852246b` and `scripts/e2e-help.py` are the audit evidence. The [historical B-04 note](../sources/znbu/docs/todo.md#b-04-help-modal-two-rows-shift-left-and-leak-border-glyphs) records every filter at 80, 120, and 200 columns, aligned descriptions, no internal border glyph, and no variation selectors. Recorded run: `/root/proj/redeck-astra-verification/runs/run.e0LEqHJM/verification.log`. The [original defect screenshot](../attachments/B-04-help-modal-alignment.png) remains source evidence, not the current rendering.

<a id="b-21"></a>
<a id="settings"></a>
## B-21 settings

Status: implemented in `internal/settings/settings.go`, `internal/ui/actions.go`, and commit `19c2b35`. The audit covers typed persistent values, defaults, changed-value saves, required-needs metadata, service section forms, palette commands, and CLI filter/init operations. Recorded verification: `/root/proj/night/logs/lane-2-B-21.log`.

```js
Setting = { id: "section.key", section, key, value, updated }
Definition = { section, key, type: "text | bool | number | list", default, hint?, required?: label }
View = { ...Setting, type, default, stored, required, needs?, hint?, title, status, text }
Need = { section, key, needs }
```

The `settings` table stores one JSON row per section/key. Config provides defaults and is never rewritten by the app. Unknown keys remain storable with a stable shape. Whole numbers normalize to integers and lists to string lists. Secrets stay outside this table: `gh`, MCP server credentials, environment variables, and harness configuration retain credential ownership.

`settings.set` coerces declared booleans, integers, and newline/comma-separated lists. `settings.save` writes only changed rows and advances only their `updated` values. `settings.unset` restores the default. `settings.init` writes missing defaults without changing existing values or timestamps. Reads overlay stored values on defaults. Sources include `settings.list`, `settings.detail`, `settings.sections`, `settings.needs`, and `settings.definitions`; changes emit `settings.changed`.

`E` opens the unscoped settings page. Enter or `e` edits a row; Delete restores its default after confirmation. `,` opens its section form. On a service page whose id or unit names a section, `,` opens that service's prefilled shared form; elsewhere it opens settings. List settings use multiline fields. `Settings…` in the palette opens the page; `<section> settings…` opens the section. Required empty settings produce `needs: <label>` and the dependent lookup skips rather than errors. Service-specific feature claims remain in their owning [automation items](../todo/automation.md).

CLI includes `mtm settings list --section identity`, `set --json`, `save --json`, `unset --json`, and `init`. The identity, Slack, GitHub, Linear, schedules, notify, palette, and forms sections preserve their original preferences: GitHub and Slack identities, oncall dates/channels/groups and mention/DM watches, review queries and poll intervals, Linear enablement, schedule timeout, optional OS notifications, indicator character, and palette search behavior. Original acceptance covers a disappearing GitHub needs line on refresh, prefilled Slack section edits, settings navigation from another page, section-only reads, and repeated init without timestamp changes.

The original shared setting definitions include these concrete keys and defaults. Service-specific acceptance remains with the owning service when its integration differs from the shared settings mechanism.

| Section | Keys and stated defaults |
| --- | --- |
| `identity` | `github_user`, `slack_user`, `slack_user_id`, `name` |
| `slack` | `oncall_weeks` as Monday dates, `oncall_channels`, `oncall_group`, `watch_dms`, `watch_mentions` |
| `github` | `review_query`, `oncall_review_query`, `watch_interval_seconds` default 300, `my_prs_poll_seconds` default 300 |
| `linear` | `enabled` |
| `schedules` | `default_timeout_seconds` |
| `notify` | `os_enabled` default false, `indicator_char` |
| `palette` | `open_in_search` default true |
| `forms` | `layout` default `list`, with the five choices documented above |

Required examples are `identity.github_user` for GitHub review/watch lookups and `identity.slack_user_id` plus Slack `oncall_weeks` for oncall. Empty required values remain highlighted on settings and produce the service needs line without attempting the dependent lookup.

Sources: [original B-21](../sources/znbu/docs/todo.md#b-21-settings-a-page-plus-per-service-config-areas-reachable-by-one-key-or-one-command); [implementation reference](../sources/matomeru/docs/outline.md#13-b-21-settings-a-page-plus-per-service-config-areas).

<a id="b-25"></a>
<a id="palette"></a>
## B-25 searchable palette

Status: implemented. `:` focuses the empty filter when `palette.open_in_search` is true, its default. The first character filters without `/`; `ctrl+n` and `ctrl+p` move the highlight, and Enter runs the highlighted command. Escape with typed text leaves search but preserves the query and highlight for navigation; a second Escape closes. Escape with an empty filter closes immediately. `/` in navigation re-enters search at the query end; `/` typed into the empty initial palette filter is ignored. Disabling the setting restores navigation-first behavior. Other modals keep their own Escape semantics.

Evidence: `internal/ui/actions.go` (`openPalette`, `paletteOpensSearching`, `modalKeyAction`), `internal/settings/settings.go`, and commits `b1a68da` and `1fab230`. Recorded verification: `/root/proj/night/logs/lane-2-B-25.log`; [historical acceptance](../sources/znbu/docs/todo.md#b-25-command-palette-opens-in-search-mode).

The current palette is flat. [B-33](../todo/forms.md#b-33) adds a registry-backed stack and per-record verbs. [B-36](../todo/forms.md#b-36) adds presentation-only palette styles after that stack. Five form layouts do not satisfy either palette item.

<a id="commonverbs"></a>
## Shared verbs and verb-first creation

Status: target added by the user during consolidation. [B-33](../todo/forms.md#b-33) owns implementation acceptance. Units, pages, actions, and command-palette labels should share common verbs for create/new, edit, and delete instead of naming the same operation differently in each place.

The palette also needs nested verb-first choices. A top-level `new…` opens `new terminal`, `new agent`, `new vim`, `new prompt`, `new project`, `new task`, and `new note`. Preserve the existing object-first record/verb branches as another route to the same registered commands, not a second implementation of each action. Decide the final create-versus-new wording consistently; the user named both, not two different domain operations.

After terminal or Vim, offer ranked repository/project base directories before creation, reusing [ranked paths](work.md#rankedpaths) and [managed panes](panes.md). Agent creation needs harness, model, and directory choices, but their order is explicitly undecided. Do not infer an approved sequence from the terminal/Vim flow or current form order. Keep [launch defaults](agents.md#launchdefaults), host safety, editable forms, and work assignment consistent whichever order is chosen.

Prompt creation may offer variants such as question, reference document, researcher, and designer. These are examples to explore, not a closed taxonomy or a decision that prompts must have those four kinds. Relate them to [question presets](agents.md#questionpresets), [field presets](agents.md#fieldpresets), and [per-unit prompts](agents.md#unitprompts) without declaring those concepts equivalent. This is documentation of unfinished product design, not shipped palette behavior.

<a id="styles"></a>
<a id="research"></a>
## Style decisions and research recommendations

The [forms research](../research/tui-forms.md) recommends keeping `internal/input`, registry bindings, guarded async sources, previews, and create-on-submit rather than adopting or wrapping huh. Huh's sequential focus, separate per-field keymaps, and select fields that cannot hold free text conflict with modal field jumps and create-on-no-match. Bubble Tea v2 compatibility removes a version objection, not those design objections.

Adopted form principles are aligned sigil/label/value rows with visible derived defaults, an error in the hint line, declared dependency refresh with guards, per-field validation, focused/blurred styles, record-backed ranked completion, and temporary jump labels. The research also recommends ghost text, matched-rune highlights, history/variable completion, and the CLI as an accessible fallback. Those recommendations are not all established by the form baseline and remain part of [B-29's design pass](../todo/forms.md#b-29).

The [design-sample research](../sources/matomeru/docs/research/tui-design-samples.md) supplies alternatives rather than approved or shipped UI. Keep these ideas in the design pass:

- Role-based accent, muted, error/warning, selected background, border, and group-heading styles. Project colors override the accent only. Focused and unfocused rows/panel titles differ. Named palettes, dark/light markdown styles, minimal/full chrome, and configurable split direction/percentage remain alternatives.
- Filter `matched/total`, per-group counts, matched-character highlights, explicit scope badges, fixed-column age/state metadata, and detail line/total or percentage. Default two-line research rows do not override the one-line-first rail requirement in [panes](panes.md).
- Help-style palette rows with hints and shortcut columns, discovery entries for an empty query, argument grammar hints, centered dropdown, bottom bar, cursor popup, side panel, and fullscreen preview alternatives. The [palette backlog](../todo/forms.md#b-33) preserves the selected single-column stack before style variants.
- Dim rather than hide the dashboard behind a modal; show pending operations before atomic approval. Keep direct field labels, separate notices from key hints, and modified draft markers. Tree guides and right-aligned counts/status should agree with [work](work.md).
- Composer completion may open upward to protect its target preview; attachments can be chips; an external-editor escape, line-number gutter, end marker, elapsed-time/token status, and markdown prompt/response rendering remain proposals. No exact public example of the requested target-scrollback-above-composer layout was found.
- Optional severity toasts, spinner/busy feedback, stale-age gradients, capture position/size, timeline outcome columns, reviewed badges, collapsible catalog definitions, and in-app docs linked to full docs remain design choices, not accepted runtime claims.
- A visible pending live leader, optional popup live view, and explicit live toggles are proposals. Research mockups use `ctrl+x`; Matomeru's configured leader, initially `ctrl+a`, remains authoritative. Deterministic project colors in research do not replace the chosen random-unused-pool rule.

The research author reported fetched/search-returned URLs, with unstable private/camo images omitted. This consolidation did not refetch them. Missing exact Assign examples, composer examples, stable Telescope/Textual/lazygit images, and an authoritative general TUI-design article are limitations of the research, not evidence for an implementation. Whole-app design notes, code changes, and screenshots remain [B-29](../todo/forms.md#b-29).

<a id="visibility"></a>
## UI state visibility contract

Status: target acceptance matrix, not a claim that every state is visible. [B-60](../todo/forms.md#b-60) owns the cross-domain coverage. [Queue outcomes](agents.md#queueoutcomes) need a read-model change as well as rendering. The original [UI state inventory](../ui-state-visibility.md) records source observations without a runtime audit; newer [pane work](panes.md) may implement portions, but does not close this entire matrix.

Every user-relevant state needs its source, read-model field, row or global cue, detail explanation, entry transition, clearing transition, and reproducible scenario. Internal locks and counters do not need badges. Their user-visible consequences do. States compose: needs-input does not hide blocked, unread does not hide completion, and working does not hide queue entries. Error/attention precedes blocked/unknown, then queue/unread, then activity. A narrow row retains attention and `+N statuses`; detail still explains all states. Unknown never means zero, ready, or success.

Use stable text/counts with supplemental color. A shared legend covers `W/A/R` working/awaiting/ready, `!/B` attention/blocked, `Qn` unique pending prompts, `Un/F` unread/finished unread, `Sn/~` subagents/stale, `?/E` unknown/failure, and `Z/*/P` snoozed/starred/pinned. These are display labels, not replacement daemon enum values. Preserve unfamiliar values in detail. Highlighting alone cannot acknowledge, deliver, or clear work.

| Area | Required visible result and limits |
| --- | --- |
| Pane lifecycle and attention | Authoritative primary state plus simultaneous flags; needs-you and blocker coexist, closed differs from unknown |
| Queue, dispatch, and drafts | Local and daemon pending identity/counts without duplication; untargeted task/project queue; accepted/waiting/evidenced-delivered/blocked/failed outcomes; partial target identity; stashes show owner/time and never count as queued |
| Unread and subagents | Unread count independent of finished unread; explicit acknowledgement; active subagent count even when parent awaits children |
| Freshness and transcript | Activity age/threshold differs from source disconnection; tool failure, unavailable transcript, older/more/reset/untrusted pagination visible; incomplete history never labeled complete |
| Terminal and vim | Read-only actual screen/tail at detail bottom; loading/current/cached/empty/closed/unavailable states with identity and capture time; saved vim without a live window says so; never invent modified-buffer state |
| Ownership and work | Owner, No Task, scope/ALL and hidden count; filtered absence is not deletion; task status, easy marker, snooze/wake and ordering remain visible |
| Tree and assignment | Unsaved, applying, failed/conflicted, and committed differ; proposed ownership never appears assigned before approval |
| Review and history | Reviewed/unreviewed and current/historical distinguish turns/documents; document changes invalidate review; running/completed and failed/unknown tool outcomes are explicit |
| Reminders | Enabled state, next due, last attempt, and inspectable delivery/notification errors; schedule advancement is not proof of delivery |
| Context, notes, captures | Kind/star/pin; omitted or unavailable gather sources before submission; inherited note owner; capture age, owner, kind, truncation; unreadable source is not empty |
| Connection and commands | Connecting/disconnected/resyncing/current plus reason and last success; retained data marked stale; pending, validation failure, command failure, and success at the affected object; failed submit retains draft |

Terminal preview must use the daemon capture boundary without a size lease, input, focus, resize, or review mutation. Normal terminals show bounded recent tail plus screen; alternate-screen programs show their current screen, cropped without resizing the target. Render supported styling without executing terminal controls, including title, clipboard, or hyperlink commands. Refresh only the selected target, reject stale selection replies, bound duration and bytes, shrink metadata first, retain help, and show an explicit too-small state. A failed refresh labels retained output cached with age/error, never live and never another pane's screen. These requirements also apply when transcript retrieval fails.

Coverage includes saved-to-daemon queue handoff, blocked plus needs-you, unread plus finished, subagents, partial dispatch failure, closed/missing receipts, reconciliation failure, stale versus disconnected, snooze/wake, draft conflict, changed document review, reminder failure, context warnings, and truncated captures. Application checks use uniquely named throwaway tuios daemons on VPS with finite timeouts. No such application check was run during this documentation change.
