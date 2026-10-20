# TUI design samples

Research deliverable [B-03](../outline/delivery.md#b-03) is complete; adopting a pattern is separate work in [B-29](../todo/forms.md#b-29) and [B-72](../todo/delivery.md#b-72). No links were refetched and no UI was exercised for this consolidation. The [preserved original](../sources/matomeru/docs/research/tui-design-samples.md) retains the original wording. Use the [topic index](tui-design-samples.outline.md) to compare alternatives.

Reference material for restyling mtm's Bubble Tea v2 UI. Each area below maps
to a screen or widget mtm already has (see `internal/ui/view.go`,
`render_*.go`, `help_view.go`, `catalog_view.go`, `tree_edit.go`, `forms/`,
`live/`). The original researcher recorded each URL as fetched or returned by a search;
image URLs served through GitHub's `camo` proxy or signed `private-user-images`
links are omitted because they expire, and the README that embeds them is linked
instead.

Dated research observation from the original `view.go`, not a current-runtime claim: one amber accent (`214`) for titles,
tabs, group headings and the selected row; dim grey (`245`) for secondary text;
red (`203`) for errors; `›` prefix on the selected rail row; ` ─ Group ─ `
headings; a full-width `─` rule under the title line; a `┌─┐ │ │ └─┘` box for
the help overlay; status line then hints line at the bottom.

<a id="dashboard"></a>
## Dashboard (rail + detail, title line, help line)
- lazygit. Stacked list panels on the left (Status, Files, Branches,
Commits, Stash), one large main view on the right, a one-line keybinding hint
strip along the bottom, and the focused panel's title drawn bold inside its
border. Source: https://github.com/jesseduffield/lazygit (main screenshot:
https://user-images.githubusercontent.com/8456633/174470852-339b5011-5800-4bb9-a628-ff230aa8cd4e.png).
Borrow: a highlighted panel title to show which pane (rail vs detail) has focus,
instead of relying on the `›` row prefix alone.
- gh-dash. Tabs for user-defined sections across the top, a dense table of
PRs/issues in the middle, a right-side preview of the selected item, and a
bottom help line; whole UI themed by a `colors` block with `primary`/`secondary`
text colors. Source: https://github.com/dlvhdr/gh-dash (overview GIF:
https://github.com/dlvhdr/gh-dash/raw/main/docs/src/assets/overview.gif; themes
and help screenshots on https://gh-dash.dev/). Borrow: mtm's page tabs already
sit on the title line; gh-dash shows that a theme can be reduced to a handful of
named colors (`text.primary`, `text.secondary`, border, selection) and still
look distinct.
- k9s. Header block (cluster info + a column of key hints) above a
full-width resource table, breadcrumbs at the bottom, `:` command prompt and `/`
filter overlaid on the table; all colors come from a YAML skin that names body,
info, help, frame (border, menu, crumbs, status, title) and view (table, yaml,
logs) roles. Source: https://github.com/derailed/k9s (pods:
https://github.com/derailed/k9s/raw/master/assets/screen_po.png; logs:
https://github.com/derailed/k9s/raw/master/assets/screen_logs.png; dracula skin:
https://github.com/derailed/k9s/raw/master/assets/skins/dracula.png). Borrow: a
skin schema that names UI roles (frame.border, frame.status, table.cursor)
rather than hard-coding ANSI 214/245/203 in `view.go`.
- fzf `--style full`. Four separately bordered regions (input, list,
preview, header) with rounded corners and per-region `--color` keys
(`list-border`, `input-border`, `preview-border`, `label`). Source:
https://github.com/junegunn/fzf (presets:
https://raw.githubusercontent.com/junegunn/i/master/fzf-style-full.png,
https://raw.githubusercontent.com/junegunn/i/master/fzf-style-minimal.png,
borders: https://raw.githubusercontent.com/junegunn/i/master/fzf-4-borders.png).
Borrow: the `default` / `full` / `minimal` preset idea. mtm could ship a
"minimal" (current rule-only) and a "full" (bordered rail and detail) chrome
preset.

```
 MATOMERU  ◆ proj · task        1 Panes  2 Tasks  3 History ...
──────────────────────────────────────────────────────────────
 PANES / 07 · scope           │ Status   running
 ─ Review Queue ─             │ Session  work / 3
 › fix rail linger            │ Pane     9332…
   dim secondary line         │
 ─ No Task ─                  │ PROMPT
   shell                      │ ...
──────────────────────────────────────────────────────────────
 Ready
 j/k move  l detail  / filter  : command  ? keys
```

<a id="rows"></a>
## Rail list rows (two-line rows, group headings, selection, counts)
- Charm bubbles `list`. The reference two-line row: bold title plus a dim
description line, a title bar with a status "N items", a `/` filter prompt that
replaces the title, and pagination dots under the list. Source:
https://github.com/charmbracelet/bubbles (List section; GIF served from
stuff.charm.sh/bubbles-examples/list.gif). Borrow: the selected item is marked
with a colored left bar (`┃`) plus a tinted title, not a full-row background;
mtm's `›` could become a colored bar that also tints the secondary line.
- fzf. Pointer character (`--pointer`, default `▌`/`>`), a marker column
for multi-selected rows, a match counter (`12/3400`) on the info line,
`--header-lines` for sticky group headers, and the selected row drawn with a
different `fg+`/`bg+` pair. Source: https://github.com/junegunn/fzf (color
example: https://raw.githubusercontent.com/junegunn/i/master/fzf-color.png).
Borrow: the `matched/total` counter in the rail header when a filter is active
(mtm currently shows only `/ query`), and reverse-video only on the current row
with matched characters highlighted.
- gh-dash. Table rows pack state glyph, number, title, author, time and
check status into one line, with section counts in the tab labels and the
selected row inverted. Source: https://github.com/dlvhdr/gh-dash. Borrow: put
the row count into the tab or group heading (`─ Review Queue 3 ─`) so counts are
visible per group, not only per page.
- atuin. History rows show relative time, duration and exit status as
fixed-width muted columns before the command, with the active filter mode
(session / directory / global) named in the header. Source:
https://github.com/atuinsh/atuin (demo:
https://github.com/atuinsh/atuin/raw/main/demo.gif). Borrow: mtm's `· scope` /
`· all` indicator becomes a named mode badge in the rail header, and the dim
secondary line uses fixed-width columns (age, state) instead of free text.

<a id="detail"></a>
## Detail pane (key/value header, sections, scroll, h/l focus)
- k9s describe / logs. Describe views are plain key-value blocks with keys
in one color and values in another; log views add a top bar naming the resource
with toggles (timestamps, wrap, fullscreen) shown as key hints. Source:
https://github.com/derailed/k9s (logs:
https://github.com/derailed/k9s/raw/master/assets/screen_logs.png). Borrow: a
one-line section bar for OUTPUT that shows the `f` fullscreen and wrap toggles,
mirroring mtm's expanded mode.
- lazygit main view. The right pane renders diffs/commit detail with a
scroll indicator in the panel title (`1 of 12`) and remembers scroll per panel;
focus is shown by the border colour. Source:
https://github.com/jesseduffield/lazygit. Borrow: a `line/total` or percentage
marker in the detail heading so the user knows how much of RESPONSE/OUTPUT is
below the fold.
- gh-dash preview. The sidebar preview shows a bold title, a muted metadata
block (author, branch, checks) and then the body rendered as markdown, separated
by blank lines rather than rules. Source: https://github.com/dlvhdr/gh-dash.
Borrow: render PROMPT/RESPONSE as glamour markdown in the detail pane and
separate sections with spacing plus a dim heading instead of full-width rules.
- Charm bubbles `viewport`. Scrollable region with a footer showing `NN%`;
the canonical Bubble Tea pager pattern. Source:
https://github.com/charmbracelet/bubbles (Viewport section). Borrow: a
right-aligned `NN%` on the detail header line.

<a id="filter"></a>
## Fuzzy filter bar (`/`) and command palette (`:`)
- fzf. Prompt line with a `>` prefix, a `matched/total` info line
(`--info=inline` collapses it onto the prompt), matched characters highlighted
in the accent color on every row, optional sticky `--header`, and preset styles
(`default`, `full`, `minimal`) that decide how much chrome surrounds the list.
Source: https://github.com/junegunn/fzf
(https://raw.githubusercontent.com/junegunn/i/master/fzf-style-minimal.png,
https://raw.githubusercontent.com/junegunn/i/master/fzf-preview.png). Borrow:
highlight the matched characters inside rail rows while `/` is active and show
`7/42` beside the query.
- Telescope (Neovim). Prompt on top or bottom with a results list and a
preview window; `dropdown` theme is a small centered palette without preview,
`ivy` is a bottom-anchored panel, `cursor` is a tiny list at the cursor;
`prompt_prefix`, `selection_caret` and `entry_prefix` are configurable glyphs.
Source: https://github.com/nvim-telescope/telescope.nvim (preview GIF:
https://i.imgur.com/TTTja6t.gif; dropdown theme:
https://i.imgur.com/SorAcXv.png). Borrow: the `dropdown` shape for mtm's `:`
palette. a short centered box with the prompt on top, 8–10 options, and no
preview. while `/` stays inline in the rail header.
- Textual command palette. Ctrl+P opens a single input (`🔎` prefix,
placeholder "Search for commands…") above a list where each hit is a bold title
plus a dim one-line help text, fuzzy-matched letters highlighted; with an empty
query it shows "discovery" hits. Source:
https://textual.textualize.io/guide/command_palette/. Borrow: two-line palette
entries (command + hint) and a default set of discovery entries when the `:`
prompt is empty, instead of a blank list.
- k9s `:` / `/` prompts. The command prompt sits at the top of the table,
accepts `resource ns /filter @ctx` grammar with inline autocompletion, and `/`
filter supports `!` inverse, `-l` label and `-f` fuzzy prefixes; both are drawn
as one line in the frame, not a modal. Source: https://github.com/derailed/k9s.
Borrow: let the `:` palette accept arguments after the command (`:assign
task-id`) with a dim hint showing the grammar.

```
 ╭─ : ─────────────────────────────────╮
 │ > asg                               │
 │ › Assign pane to task     a         │
 │     pick a task, snapshot, approve  │
 │   Switch pin               s        │
 │     change project / task scope     │
 ╰────────────────────────── 2/14 ─────╯
```

<a id="forms"></a>
## Modals and forms (pickers, previews, confirm, assign flow)
- Charm huh. Field groups act as pages; Select shows a `>` cursor on the
current option, MultiSelect uses `[•]`/`[ ]` boxes, Confirm renders two buttons
with the active one filled, every field has a title line and a dim description
line, and five bundled themes (Charm, Dracula, Catppuccin, Base16, Default)
prove the same form can be re-skinned by swapping a theme struct. Source:
https://github.com/charmbracelet/huh (Select, MultiSelect, Confirm and theme
images are embedded in the README). Borrow: huh's theme struct (focused/blurred
field styles, title, description, option, selected option, button) as the shape
of mtm's form styles.
- lazygit menus and confirmations. Actions open a centered bordered menu
listing options with their key in a muted column; confirmations are a small
centered box with the question and `enter confirm / esc cancel` hints; the menu
for e.g. reset/nuke shows a one-line description per option. Source:
https://github.com/jesseduffield/lazygit (demo clips `nuke_working_tree.mp4`,
`interactive_rebase.mp4` in the README). Borrow: a key column in option pickers
so a modal option can be chosen by one key or by moving the cursor.
- Textual toast/modal docs. `ModalScreen` dims the underlying screen and
places a bordered dialog in the center; toasts are bordered boxes with title and
body. Source: https://textual.textualize.io/widgets/toast/. Borrow: dim (not
hide) the dashboard behind the confirm dialog so context stays visible.
- oil.nvim confirmation preview. Before applying filesystem edits, a
floating confirmation window lists the pending operations and asks y/n;
`skip_confirm_for_simple_edits` removes it for trivial cases. Source:
https://github.com/stevearc/oil.nvim. Borrow: mtm's assign flow already has a
snapshot plus approval step; render that snapshot like oil's pending-operations
list (one line per change, verb first) rather than a free-text summary.
- posting jump mode. Pressing the jump key overlays single-letter labels on
every focusable region so the user types the letter to move focus. Source:
https://github.com/darrenburns/posting
(https://github.com/darrenburns/posting/raw/main/docs/assets/features/jump-mode.gif).
Borrow: for multi-field forms, letter labels on fields are a cheaper alternative
to tabbing.

<a id="composer"></a>
## Text composer: prompt, completion, attachments and scrollback preview
- opencode TUI. Bottom-anchored composer; typing `@` runs a fuzzy file
search in the cwd and shows a completion list above the input, `/` opens a
slash-command list, `!` prefixes a shell command, and a `ctrl+x` leader key with
a 2000 ms timeout drives everything else. Source: https://opencode.ai/docs/tui/
(screenshot in README:
https://github.com/anomalyco/opencode/raw/dev/packages/web/src/assets/lander/screenshot.png).
Borrow: the completion popup opens upward from the composer so the pane preview
above it is never covered; a single visible leader-key hint in the footer.
- Claude Code interactive mode. A single-line prompt that grows into
multi-line input (backslash+Enter, Option+Enter or Shift+Enter in supported
terminals), `/` slash commands with an inline completion list, `@` to attach
files, and Ctrl+G to open the prompt in an external editor. Source:
https://code.claude.com/docs/en/interactive-mode.md (search result; third-party
summaries at https://claudefa.st/blog/guide/mechanics/interactive-mode and
https://pilot-shell.com/blog/interactive-mode). Borrow: the "open in $EDITOR"
escape hatch for long prompts, and attachments listed as chips under the input.
- Charm bubbles `textarea`. Multi-line editor with line numbers in a dim
gutter, a `┃` cursor-line marker, soft wrapping and placeholder text; the
reference Bubble Tea composer widget. Source:
https://github.com/charmbracelet/bubbles (Text Area section). Borrow: the dim
line-number gutter plus end-of-buffer marker to make the composer visibly a
multi-line editor rather than a text field.
- Codex CLI. Composer with `@` file search and slash commands, approval
prompts (yes / no / always) inline in the transcript, and a working indicator
with elapsed time and token count under the input. Source:
https://github.com/openai/codex (splash:
https://github.com/openai/codex/raw/main/.github/codex-cli-splash.png; docs at
https://developers.openai.com/codex). Borrow: a one-line "working · 12s · 3.2k
tokens" status under the composer while a turn runs.

```
 ┌ pane scrollback (last 8 lines) ──────────────────┐
 │ $ go test ./...                                   │
 │ ok   internal/ui   0.42s                          │
 └───────────────────────────────────────────────────┘
  1 │ Fix the rail linger so reviewed rows drop after
  2 │ 3s. See @internal/ui/review_linger.go
    ╰ @ path  / command  ctrl+s send  esc cancel     📎 1
```

<a id="tree"></a>
## Tree editor: projects, tasks, insertion, rename and atomic save
- oil.nvim. The directory is a plain buffer: add, rename or delete lines
with normal Vim motions, then `:w` applies the edits atomically after a floating
confirmation window lists the pending operations; `:Oil --float` opens the same
editor in a bordered float with configurable padding and border. Source:
https://github.com/stevearc/oil.nvim. Borrow: this is the closest match to
mtm's tree editor (edit freely, Ctrl+s commits, Escape discards); adopt the
pending-operations confirmation list before an atomic save, and show a `[+]`
modified marker in the editor title while unsaved edits exist.
- neo-tree.nvim. Tree with `│` and `└` indent guides (`indent_size = 2`,
`padding = 1`), expander glyphs before folders, a trailing right-aligned
git-status/detail column, and a clickable "source selector" tab bar above the
tree; `a` add (with brace expansion `x{a,b,c}`), `r` rename, `d` delete open
small bordered prompts. Source: https://github.com/nvim-neo-tree/neo-tree.nvim
(right-aligned symbols:
https://github.com/nvim-neo-tree/resources/raw/main/images/Neo-tree-with-right-aligned-symbols.png;
source selector:
https://github.com/nvim-neo-tree/resources/raw/main/images/Neo-tree-source-selector.png).
Borrow: dim `│`/`└` guides instead of space indentation, and a right-aligned
status column (open pane count, stale) on each task row.
- lipgloss `tree` package. `tree.Root().Child(...)` with
`DefaultEnumerator` (`├──`, `└──`) or `RoundedEnumerator` (`╰──`), separately
styled root, enumerator and items. Source:
https://github.com/charmbracelet/lipgloss (Rendering Trees section). Borrow:
mtm already depends on lipgloss v2; use the rounded enumerator for the tasks
page and the tree editor so both pages share one tree look.
- Textual DirectoryTree / Tree. Indented tree with folder icons, branch
lines and a highlighted cursor line spanning the full width. Source:
https://textual.textualize.io/widget_gallery/. Borrow: the full-width cursor bar
for the current tree node, which reads better than a prefix glyph when nodes are
indented at different depths.

```
 TASKS · editing (unsaved)                 ctrl+s save  esc discard
 ◆ matomeru
 ├── rail linger                         2 panes
 │   ╰── drop reviewed rows after 3s     1 pane
 ├── _new task_                          ← o inserted here
 ╰── docs: tui design samples            stale
```

<a id="help"></a>
## Help overlay: columns, groups, fuzzy search and footer
- which-key.nvim. Popup of `key ➜ description` pairs laid out in columns
(`layout.width`, `layout.spacing = 3`), groups prefixed with `+`, a centered
title, three presets (`classic`, `modern`, `helix`) that differ mainly in border
and position, and a help message in the command line (`<esc> close, <bs> up a
level, <c-d>/<c-u> scroll`). Source: https://github.com/folke/which-key.nvim.
Borrow: the `key ➜ description` separator and `+group` prefix for mtm's grouped
headings; a bottom-anchored "helix" style variant for narrow terminals where a
centered box is too tall.
- lazygit `?` menu. Keybinding menu lists action descriptions with the key
right-aligned in a muted color, is filterable by typing, and the bottom line
shows `optionsTextColor` key hints; panel titles carry jump keys when
`showPanelJumps` is on. Source:
https://github.com/jesseduffield/lazygit/blob/master/docs/Config.md. Borrow:
typing in the help panel filters rows immediately (mtm has fuzzy search; show
the query in the panel title like `Keys / asg`).
- btop help menu. Full-screen centered box with two columns of key /
description, section headers in the accent color, and the box title embedded in
the top border. Source: https://github.com/aristocratos/btop
(https://github.com/aristocratos/btop/raw/main/Img/help-menu.png). Borrow: the
embedded title in the top border (`┌ Keys ──┐`) that mtm already uses, plus
accent-colored section headers rather than bold white.
- Charm bubbles `help`. Short help: one line of `key desc` pairs separated
by ` • `; full help: several columns of key/desc with keys dim and descriptions
normal, truncating gracefully at narrow widths. Source:
https://github.com/charmbracelet/bubbles (Help section). Borrow: the ` • `
separator and automatic column truncation for mtm's bottom hints line.
- yazi `[help]` / `[which]` theme sections. Help has `chord`, `action` and
`hovered` styles; the which-key popup has `cols` (1–3), `cand` (candidate keys),
`rest`, `desc` and a configurable `separator`. Source:
https://yazi-rs.github.io/docs/configuration/theme. Borrow: name the help styles
the same way (chord, action, hovered, cols) in mtm's config so a theme file can
restyle the overlay.

<a id="catalog"></a>
## Catalog / docs browser (registry definitions with detail)
- Textual MarkdownViewer. A table-of-contents tree in a left sidebar beside
the rendered document; headings in the TOC are nested, tables render as
DataTables, links navigate with back/forward history. Source:
https://textual.textualize.io/widgets/markdown_viewer/. Borrow: mtm's catalog
list on the left can act as a TOC with nested groups (concept → command), and
the detail pane renders the definition's doc as markdown.
- glow. File browser ("stash") listing markdown documents with name and
modified date, then a pager with `less`-style keys and `?` for hotkeys;
dark/light auto-detection with JSON stylesheets for the markdown renderer.
Source: https://github.com/charmbracelet/glow. Borrow: glamour stylesheets for
rendering catalog docs; auto-pick dark/light by terminal background.
- Textual widget gallery. Each entry is a short description followed by a
rendered example; `OptionList` draws options separated by thin dividers,
`Collapsible` uses `▶`/`▼` arrows for expandable sections. Source:
https://textual.textualize.io/widget_gallery/. Borrow: `Collapsible` sections in
the catalog detail (Fields, Examples, Bindings) so long definitions stay
scannable.
- harlequin. Data catalog tree on the left, editor and results on the
right, and `F1` opens a subset of the docs inside the app with a link back to
the website. Source: https://github.com/tconbeer/harlequin. Borrow: an in-app
"docs subset + link to full docs" pattern for mtm's `mtm docs` output.

<a id="live"></a>
## Live mode (embedded terminal pane under a live bar, leader key)
- zellij floating panes. Floating panes sit over the tiled layout, toggle
with `Alt f`, keep running while hidden, can be pinned on top, and a bottom
status bar shows the current mode and the keys available in it. Source:
https://zellij.dev/features/
(https://zellij.dev/img/floating-panes-feature-demo.gif; stacked panes:
https://zellij.dev/img/stacked-panes-feature-demo.gif). Borrow: a mode indicator
in the live bar (`LIVE · leader ctrl+x`) that changes color while the leader
chord is pending, exactly like zellij's mode-colored status bar.
- tmux display-popup. Centered floating window with a border, opened by a
binding such as `bind C-g display-popup -E "cmd"`, closed when the command
exits; commonly used for scratch shells. Source:
https://waylonwalker.com/tmux-floating-popups/ and
https://willhbr.net/2023/02/07/dismissable-popup-shell-in-tmux/. Borrow: the
"dismissable scratch pane" feel. mtm's live area could offer a `popup` variant
that floats over the dashboard instead of replacing the detail pane.
- lazydocker. Left panels (Project, Containers, Images, Volumes) with the
right main panel tabbed into Logs, Stats, Config, Top, Env; the Stats tab draws
ASCII CPU/memory graphs and logs stream live in the right pane. Source:
https://github.com/jesseduffield/lazydocker
(https://github.com/jesseduffield/lazydocker/raw/master/docs/resources/demo3.gif).
Borrow: tab the detail pane (`Detail | Output | Live`) so live mode is a tab of
the detail area rather than a separate layout.
- k9s logs view. A streaming pane with a top bar that names the source and
exposes toggles (`t` timestamps, `w` wrap, `f` fullscreen) as key hints. Source:
https://github.com/derailed/k9s
(https://github.com/derailed/k9s/raw/master/assets/screen_logs.png). Borrow: the
live bar lists its toggles as `key label` pairs in the same style as the bottom
hints line.
- opencode leader key. `ctrl+x` leader with a `leader_timeout` of 2000 ms
and every command listed with its chord in the docs. Source:
https://opencode.ai/docs/tui/. Borrow: show the pending leader chord in the
status line (`ctrl+x …`) and cancel it visibly on timeout.

```
 ┌ LIVE  work / 3 · ctrl+x leader · ctrl+x q leave ───┐
 │ $ go test ./internal/ui/...                        │
 │ ok   internal/ui  0.61s                            │
 │ $ █                                                │
 └────────────────────────────────────────────────────┘
 Live input goes to work / 3        All other keys pass through
```

<a id="pages"></a>
## Pages: history timeline, reviews, captures, context, tasks
- atuin. History rows with fixed-width muted columns (relative time,
duration, exit status) before the command, filter mode named in the header,
`style = compact | full`, `inline_height`, and a `show_preview` pane for the
selected entry. Source: https://github.com/atuinsh/atuin
(https://github.com/atuinsh/atuin/raw/main/demo.gif). Borrow: history timeline
rows as `12m  3.2s  ✓  prompt summary`, with a compact/full style switch and a
preview of the selected turn.
- gitui. Tabs across the top (Status, Log, Files, Stashing, Stashes), a
commit log with graph/author/date columns, a bottom key bar, bordered popups,
and a light theme variant. Source: https://github.com/gitui-org/gitui
(https://github.com/gitui-org/gitui/raw/master/demo.gif; light theme:
https://github.com/gitui-org/gitui/raw/master/assets/light-theme.png). Borrow: a
reviewed/unreviewed glyph column on the reviews page, like gitui's
staged/unstaged markers, and a tested light theme.
- serie. Commit list with hash, author, date and ref badges, a detail view
for the selected commit, and `?` for keys; the graph is drawn in the left
column. Source: https://github.com/lusingander/serie
(https://github.com/lusingander/serie/raw/master/img/list.png; detail:
https://github.com/lusingander/serie/raw/master/img/detail.png). Borrow: colored
ref-style badges (`[reviewed]`, `[stale]`) at the end of timeline rows.
- lazyjj. Log on the left and change details on the right, split
`horizontal` or `vertical` by `lazyjj.layout` with `layout-percent`, tabs for
Log/Files/Bookmarks/Command log, `?` help and `:` command popup, highlight color
`#323264`. Source: https://github.com/Cretezy/lazyjj. Borrow: a
user-configurable split direction and percentage for rail vs detail, and a
"command log" page that shows every CLI call mtm made.
- yazi. Three-column file manager (parent, current, preview) with a header
path line and a status bar whose separators, mode badge and progress are
themeable (`[status]`, `[mode]`, `[tabs]`). Source:
https://github.com/sxyazi/yazi and
https://yazi-rs.github.io/docs/configuration/theme. Borrow: the captures page as
list + preview with the status bar showing size/position (`3/12`) of the
selected capture.
- taskwarrior-tui / kanban (awesome-ratatui). Task table with live filter
updates, colors derived from Taskwarrior urgency/project, and kanban-style
boards with sprint grouping. Source:
https://github.com/kdheepak/taskwarrior-tui, https://github.com/kanban-rs/kanban
(via https://github.com/ratatui/awesome-ratatui). Borrow: per-project color
derived from a deterministic hash (mtm already themes pane labels per project)
applied to task rows on the tasks page.

<a id="status"></a>
## Status line, notices/toasts, progress, stale indicators, themes
- Textual Toast / ToastRack. Notifications are bordered boxes with an
optional title and body, three severities (`information`, `warning`, `error`)
each with its own CSS class, a per-toast timeout, stacked in a `ToastRack`
aligned to a corner (`align: right top`). Source:
https://textual.textualize.io/widgets/toast/. Borrow: reminder notices as
stacked corner toasts with severity color on the border, auto-dismissing,
instead of replacing the status line.
- Charm bubbles `spinner` / `progress`. Several spinner glyph sets (dots,
line, mini-dot, jump, pulse, points, globe, moon, monkey) and a gradient
progress bar with optional percentage; `huh` shows a spinner with a label while
a long action runs. Source: https://github.com/charmbracelet/bubbles (Spinner,
Progress sections) and https://github.com/charmbracelet/huh (Spinner GIF).
Borrow: a braille-dot spinner in the rail row of any working agent, and in the
title line while `Syncing sources`.
- k9s skins. YAML skin naming `body`, `info`, `help`, `frame` (border,
menu, crumbs, status, title) and `views` (table, yaml, logs) roles; Dracula and
other community skins ship in the repo. Source: https://github.com/derailed/k9s
(https://github.com/derailed/k9s/raw/master/assets/skins/dracula.png). Borrow: a
role-based theme file for mtm (accent, muted, error, selected, border, group
heading) so per-project colors override only `accent`.
- lazygit theme block. `activeBorderColor [green, bold]`,
`inactiveBorderColor [default]`, `searchingActiveBorderColor [cyan, bold]`,
`optionsTextColor [blue]`, `selectedLineBgColor` (blue on dark, computed on
light), `inactiveViewSelectedLineBgColor` (grey), `border: rounded | single |
double | hidden | bold`. Source:
https://github.com/jesseduffield/lazygit/blob/master/docs/Config.md. Borrow: a
different selected-row background when the rail is not focused (inactive view)
and a distinct border color while `/` search is active.
- btop. Theme files drive a gradient across graphs and the process list
(`proc_gradient`), and `followed_bg`/`followed_fg` highlight the tracked
process; main/options/help menus are centered boxes. Source:
https://github.com/aristocratos/btop
(https://github.com/aristocratos/btop/raw/main/Img/normal.png). Borrow: a muted
gradient (bright → dim) by age for stale rows instead of a binary `stale` label.
- gh-dash themes. The same dashboard rendered in Catppuccin, Gruvbox and
Tokyo Night from a `colors.text.primary/secondary` theme block. Source:
https://gh-dash.dev/. Borrow: ship two or three named palettes and document how
a palette maps to mtm's roles.

<a id="patterns"></a>
## Patterns worth adopting
- One accent color for selection, titles and active tab; everything else is
default foreground or dim. Tools that look polished (lazygit, gh-dash, fzf
minimal) use three to four roles: accent, muted, error/warn, selected
background.
- Selected row: full-width tinted background with bold text on the focused
panel, a grey background when the panel is unfocused (lazygit
`inactiveViewSelectedLineBgColor`), never a bare prefix glyph alone.
- Two-line rows (title + dim description) are the norm for Bubble Tea lists;
keep the second line fixed-width columns (age, state, count) rather than prose.
- Show `matched/total` next to the filter query and highlight matched characters
in rows (fzf, Textual palette).
- Palette and picker entries carry a short dim hint on a second line and a
right-aligned key column, so each option is reachable by cursor or by one key
(lazygit menus, which-key, Textual palette).
- Help: `key ➜ description` or `key  description` pairs in auto-fitted columns,
`+group` headings in the accent color, filterable by typing, title embedded in
the top border, and a bottom-anchored variant for short terminals.
- Bottom hints line: ` • `-separated `key desc` pairs, truncated gracefully;
keep the status/notice line separate from the hints line (mtm already does
this).
- Borders: pick one family (rounded is the current favorite in lazygit, btop,
fzf full, superfile); use full borders only for modals, the live pane and the
help overlay, and thin rules or a left bar for the rail and detail.
- Focus is shown by border color or title color of the panel (lazygit, zellij),
not only by the row cursor.
- Modals dim the screen behind them rather than replacing it (Textual
ModalScreen, tmux/zellij popups), and confirmations list the pending operations
(oil.nvim) before an atomic apply.
- Working/busy state is a spinner glyph in the row plus a short status under the
composer (`working · 12s · 3.2k tokens`); notices are corner toasts with a
severity-colored border and an auto timeout.
- Themes are role-based files (k9s skins, lazygit theme, yazi theme.toml,
gh-dash colors): name the roles once in config, then per-project colors override
only the accent.

<a id="notfound"></a>
## Not found
- No public screenshot or write-up of an "assign flow with a candidate snapshot
and approval step" exactly like mtm's; the closest analogues are oil.nvim's
pending-operations confirmation and Codex/Claude Code approval prompts.
- No sample of a composer that shows the target pane's recent scrollback *above*
the editor; opencode, Claude Code and Codex show the transcript above the input,
which is the nearest pattern.
- No fetched image for Telescope's `ivy`/`cursor` themes, Textual's command
palette or toasts (docs are text-rendered only), or lazygit's confirm dialogs
(README demos are `.mp4` files without stable URLs).
- No authoritative terminal-UI design article surfaced; the search returned only
community "skill" pages, so the pattern list above is derived from the tools
themselves.
