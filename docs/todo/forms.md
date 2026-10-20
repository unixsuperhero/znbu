# Forms and UI work

[Current behavior and target design](../outline/forms.md). This file holds only unfinished acceptance. B-04 help alignment, B-21 settings, and B-25 palette search behavior are recorded in the outline, not repeated as active work. Historical tests are evidence reported by their authors, not tests run during consolidation.

<a id="b-31"></a>
## B-31 forms acceptance gaps

Status: partial, verification gap. Priority: p1. The committed `5f1bd56`/`fff163c` [baseline](../outline/forms.md#b-31) is implemented, and `fff163c` was already verified in the preceding work. Keep the [detailed plan](../plans/forms-redesign.md) linked until the remaining acceptance is resolved.

- Render `form.start-agent` in a real PTY at both 80 and 200 columns and assert one field/value row per field. The original log used 150 columns and explicitly did not cover these widths. Existing per-layout cases are not evidence that these two widths passed.
- Keep catalog-backed agent, skill, and command completion open where it depends on [B-34](agents.md#b-34). Do not replace that requirement with recognized harness names or the partial local skill list.

The richer [composer B-62](../outline/agents.md#b-62) and inferred [launch defaults B-61](../outline/agents.md#b-61) now have separate owner-reported verification in `e4cf07a`. They are no longer pending work here and do not supply the missing original 80/200-column evidence.

Original fulfilled checks remain in the outline and [preserved B-31](../sources/znbu/docs/todo.md#b-31-forms-redesign-precise-modal-hierarchy-aware-replaces-the-top-8-lines-box): field accelerator shows INPUT, `3` selects row three, task selection derives project, parent P limits descendants, `zzq-new` creates on submit, and selecting `box` restores the compact renderer. The former top-only form model is replaced by the layout interface; historical source text remains immutable.

<a id="b-23"></a>
## B-23 optional embedded Neovim field engine

Status: open. Priority: p2. Size: L. [Current input engine](../outline/forms.md#navigation) stays the default. A managed Neovim pane is not this feature. The old open choice of embedded/headless/no Neovim was resolved for current Matomeru behavior in favor of shared text input, but this optional future proposal remains preserved, not falsely implemented or silently discarded.

Run one app-owned `nvim --embed --headless` with a controlled profile, no user configuration, swap, or network. Vendor vim-rsi at `45540637` with its license. Neovim owns text, cursor, mode, and undo; the app holds acknowledged snapshots and draws Msgpack-RPC remote-UI content within the field layout. Keep one scratch buffer per live field, including undo in hidden buffers. Picker queries and filters deliberately stay on the shared engine.

```js
EditorSnapshot = { owner: "form-instance-42", field: "description", activation: 7, changedtick: 19,
                   lines: ["Prepare release", "Check migrations"],
                   cursor: { row: 1, byteColumn: 6 }, mode: "insert",
                   presentation: { cells: [], cursorCell: { row: 1, column: 6 } } }
```

Activation changes on focus; changedtick changes on text. Closed-form and stale-activation events are dropped. `editor.engine` offers `shared` and `neovim`, defaulting to `shared`. With shared selected, existing editing stays untouched and no Neovim process starts. The original environment notes Neovim 0.11 on vps2; the spike and behavior checks belong there through `scripts/verify-vps.sh`, not the user's live daemon.

Retain the seven-step plan:

1. Spike buffer attach, remote redraw, completion, Visual block, key encoding, and input-drain-before-read on vps2. Record version, cold-start latency, and input-to-render latency.
2. Add `internal/editor/` with the pinned licensed vim-rsi runtime, embedded app initialization, and a minimum-version check.
3. Use an ordered RPC worker with finite deadlines, stable field identities, lifecycle recovery, bounded shutdown, and separate field undo.
4. Render cells, highlights, cursor, mode, command line, messages, and completion in the field box.
5. Migrate form text editing, paste, reads, and acceptance. Reject newlines in single-line fields.
6. Provide a configurable host action to leave editing for form navigation. Escape enters Neovim Normal mode and never discards the form. Route mass-add through the same adapter while retaining shared picker/filter callers.
7. Add end-to-end cases to the existing suites. Update implementation documentation only after behavior is proven.

Acceptance:

- Counts, operators, text objects, and dot-repeat produce literal expected text after compound edits.
- Returning to a field retains its undo history; switching fields does not merge undo stacks.
- Rapid input followed immediately by save persists every completed edit before acceptance.
- Stale events cannot overwrite another form. Engine failure leaves the last acknowledged draft recoverable.
- Save, cancel, field switching, and native file/directory pickers remain reachable while editing.

Source: [original B-23](../sources/znbu/docs/todo.md#b-23-neovim-as-the-input-engine-behind-form-fields-behind-a-settings-toggle), which references the older `redeck-astra2/docs/plans/neovim-input-engine.md`. That external plan was not supplied as an implementation artifact. [Managed editor sessions](../outline/knowledge.md#editorvim) remain a different concept.

<a id="b-33"></a>
## B-33 nested command palette

Status: open. Priority: p1. Size: M. Depends on the implemented [B-25 search semantics](../outline/forms.md#b-25); the skills branch also depends on [B-34](agents.md#b-34).

Replace the flat palette with a registry-backed stack of single-column lists. The root contains commands and one `›` row per sub-palette. A record opens its verbs. The help-style presentation is a centered thin-bordered panel with group headings, muted pink key column, aligned descriptions, and a footer showing position and close hint. Key width comes from the widest key and stays consistent. Every width retains one column.

```js
PaletteStack = [ { id: "root", filter: "" }, { id: "panes", filter: "dec" },
                 { id: "verbs", of: { kind: "pane", id: "w-123" } } ]
SubPalette = { id: "panes", kind: "pane", source: "panes.windows", key: "w" }
Verb = { kind: "pane", name: "show", key: "s", label: "Show in detail", command: "ui.show" }
```

The title includes breadcrumbs such as `Palette › Panes › deck-review`. Units register their own `verb` and `sub-palette` definitions; generated `mtm docs` lists them. Preserve every proposed branch and action:

| Branch | Leader | Verbs |
| --- | --- | --- |
| Pages | `;g` | Enter opens the page directly, no verb level |
| Panes | `;w` | Show, live, capture, star, rename, close |
| Projects | `;j` | Show, pin, edit, new task, tree |
| Tasks | `;t` | Show, pin, edit, done, assign pane, note |
| Documents | `;d` | Open, star, copy path |
| Skills | `;k` | Show, open file, copy name |

Add pending-prefix support to `internal/input.Engine`, as used for live leaders. `;` is the proposed normal-mode leader and `;;` reopens the last sub-palette. Enter descends from record to verbs and executes a verb. `h` or Left pops one level while retaining that level's filter and highlight. Escape follows B-25: leave typed search, then close the entire stack; preserve the empty-filter close exception. Each branch honors `palette.open_in_search`. Register descend/pop actions in effective config/help rather than hard-coding a second key system.

Acceptance:

- `mtm list-actions` exposes `palette-pages` through `palette-skills` in normal mode with `;g` through `;k`.
- A real PTY `;w` shows `Palette › Panes` with only pane rows. Enter shows that pane's verbs. `h` restores the pane list and filter.
- `;g`, then Enter on Tasks, opens the Tasks page.
- At 80, 120, and 200 columns, every row retains both borders with no leaked border glyph or offset.

User addition during consolidation. Preserve common verbs across units, pages, actions, and palette labels: create/new, edit, and delete. Add a verb-first route alongside the existing object-first record routes, both executing the same registered commands.

- `new…` opens `new terminal`, `new agent`, `new vim`, `new prompt`, `new project`, `new task`, and `new note` with consistent labels.
- Terminal and Vim choices then offer ranked repository/project base directories through the existing [ranked-path contract](../outline/work.md#rankedpaths), preserving host separation, manual entry, and the platform picker.
- Agent creation offers harness, model, and directory, but their ordering remains an explicit open decision. Do not silently copy terminal/Vim ordering or assume the current form order settles it.
- Prompt variants can include question, reference document, researcher, and designer. Keep them illustrative, not a closed taxonomy, and reconcile them with [agent prompt designs](../outline/agents.md) before implementation.
- Create/new, edit, and delete have consistent palette naming and action meaning across [work](../outline/work.md), [panes](../outline/panes.md), [agents](../outline/agents.md), and other units. Resolve final create/new wording rather than creating duplicate commands solely for labels.
- Exercise the complete verb-first nested flow, directory choice, back navigation/filter preservation, cancellation, and exactly one resulting command. Preserve the original per-kind sub-palette and width acceptance above.

[Canonical shared-verb design](../outline/forms.md#commonverbs).

Source: [original B-33](../sources/znbu/docs/todo.md#b-33-nested-command-palette-styled-like-the-help-modal-sub-palettes-per-kind).

<a id="b-36"></a>
## B-36 interchangeable palette styles

Status: open. Priority: p2. Size: M. Build after [B-33](#b-33), not as a separate palette implementation. [Form layouts](../outline/forms.md#b-31) are precedent, not completed palette scope.

Use one engine for sources, filtering, stack navigation, and row verbs. Expose four to five presentation-only styles through `palette.style` on the settings page, switchable without restart. Preserve the candidate set until the final style choice is explicit:

- `list`: the single-column help-modal look.
- `popup`: small fuzzy popup at the cursor.
- `bar`: bottom command input with completions above it.
- `side`: a panel replacing detail.
- `full`: fullscreen list with preview.

A style is one file behind a registry interface. The same palette end-to-end cases run under every selected style and prove identical nested navigation, filter preservation, verbs, search preference, and close behavior. Source: [original B-36](../sources/znbu/docs/todo.md#b-36-command-palette-styles-several-interchangeable-looks-chosen-in-settings).

<a id="b-29"></a>
## B-29 whole-app UI/UX design pass

Status: open. Priority: p2. Size: M. The implemented help correction and completed research do not complete this pass. [Research recommendations and unresolved alternatives](../outline/forms.md#research) remain its design input. [Research-adoption tracking](delivery.md#b-72) links any additional cross-domain recommendations.

The original request specifies Claude Fable 5.1 with `frontend-design`. That is a requirement of the future design assignment, not a model used for this consolidation. Review dashboard rail/detail, page tabs, help, forms, palette, tree editor, review accordion, documents, downloads, action items, settings, and every other page/modal.

Produce one `docs/design/<page>.md` note per page with before/after ASCII mockups and exact tokens for color roles, borders, row density, and selected-row style. Implement the agreed changes only after the notes. Changes to existing appearance follow the settings-toggle rule. Include the implemented B-04 fix rather than reopening its old diagnosis.

Acceptance:

- Every page has its design note, including forms, help, and palette.
- Preserve the approved help alignment and effective binding semantics.
- Attach before/after screenshots at 120 and 200 columns under `docs/attachments`.
- Resolve research alternatives explicitly. Keep one-line-first rail requirements, random-unused-pool project themes, configured live leader, and read-only preview safety unless a later approved decision replaces them.
- Track unproven form research additions such as ghost text and matched-rune highlighting rather than describing all recommendations as shipped.

Source: [original B-29](../sources/znbu/docs/todo.md#b-29-uiux-pass-on-every-page-with-fable-51-and-the-frontend-design-skill); [design-sample brief](../sources/matomeru/docs/research/tui-design-samples.md); [form research and adoption decisions](../research/tui-forms.md).

<a id="b-60"></a>
## B-60 complete the UI-state visibility matrix

Status: open, cross-domain acceptance audit. This newly assigned identifier preserves previously unnumbered [UI visibility requirements](../ui-state-visibility.md). The [canonical matrix](../outline/forms.md#visibility) states required behavior, not a runtime pass. Existing domain implementations remain valid baselines. Do not rebuild a feature solely because an old source observation predates it.

For each state, record its authoritative source, read-model field, row/global cue, detail explanation, entry transition, clearing transition, and reproducible rendered end-to-end scenario. Add missing read-model outcomes when errors currently disappear into logs. Keep unknown distinct from zero/success and preserve unfamiliar daemon values in details. Cues compose; width truncation retains attention and `+N statuses` with complete detail.

Acceptance must cover the complete matrix:

- Pane working/awaiting/ready flags, needs-you plus blocked, closed versus unknown, stale activity with age/threshold, and active subagents.
- Local and daemon queue counts, untargeted queues, accepted/waiting/blocked/failed/unknown delivery, partial target creation, and draft/stash owner/time. [B-63](agents.md#b-63) owns the queue outcome/read-model implementation. Stashes do not count as queued.
- Unread plus finished-unread, distinct acknowledgement rules, transcript/tool failures, pagination/more/reset/untrusted state, and terminal preview independent of transcript success.
- Ownership/No Task, scope/ALL and hidden count, task status/easy/snooze, ordering, tree draft applying/conflict/commit, and assignment proposed versus approved.
- Current/historical and reviewed/unreviewed turns/documents, changed-document invalidation, running/completed history, and failed/unknown tool outcomes.
- Enabled/disabled reminders, next due, last attempt, and inspectable delivery/notification errors after a transient notice clears. Schedule advancement does not establish delivery.
- Context kind/star/pin and gather omissions/warnings before submit; inherited note source owner; capture kind/owner/age/truncation and unreadable-source errors.
- Connection connecting/disconnected/resyncing/current states, last success, stale retained data, and command/form pending, validation failure, command failure, and success. Failed submission retains unsaved input; errors clear only on correction, successful retry, or explicit dismissal.

Terminal preview acceptance remains substantive and links the [pane baseline](../outline/panes.md):

1. A unique terminal line appears at the detail bottom without live mode. An agent's terminal remains visible when transcript reading fails. A running Neovim pane shows its alternate screen rather than old shell output.
2. Delay A's capture, select B, then finish A. B never displays A. Closing B mid-capture produces closed/unavailable, not successful empty output.
3. Compare target focus, input, and dimensions before/after selection and refresh. Nothing changes. Output arriving behind an open form preserves its text, selection, and keyboard focus.
4. Exercise empty output, narrow/short layout, Unicode, truncation, disconnect/reconnect, and malicious terminal controls. Capture is bounded and selection-scoped, takes no size lease, cannot acknowledge review, retains the help line, and labels cached output with age/error. Fresh capture clears only its preview error.
5. A persisted Vim session without a live window is explicitly non-live and is not launched for preview. Never fabricate buffer-modified state absent from the backend.

Run these application checks only on uniquely named throwaway VPS daemons with finite timeouts. This consolidation ran no application checks. The original inventory's source observations and historical logs cannot stand in for these scenarios.

Every tool invocation and shell command used for the application scenarios has an enforced finite timeout. A timeout longer than 15 minutes requires a reason and explicit permission.
