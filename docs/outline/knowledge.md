# Knowledge, files, and editor sessions

This document groups saved context, notes, documents, downloads, captures, the history archive, and Matomeru-owned Neovim sessions. [Remaining work](../todo/knowledge.md) uses the same boundaries. [Panes and reviews](panes.md) owns review interaction and rail placement, [work](work.md) owns task/project scope and places, and [architecture](architecture.md#b-28) owns cross-record provenance.

Current behavior below comes from the implementation audit and named source files. Historical verification is recorded evidence, not a check performed during this consolidation. Target decisions are marked explicitly and linked to unfinished acceptance. The concurrent feature owner later reported completion and verification of commits `ec0d83a` and `e4cf07a`; matching archive/inventory behavior is recorded below without promoting the broader place/provenance targets.

<a id="context"></a>
## Context items

The context unit owns `context_items`. Items retain the task or project of their source pane at extraction. Task-owned rows store `task_id` without duplicating the inherited project. Items survive pane closure and daemon restart; a `window-closed` event does not prune them.

The original item format remains the domain contract, with implementation fields shown separately:

```text
ContextItem = {
  id, kind: "link"|"file"|"dir"|"pr"|"prompt"|"command", text,
  session, window, pane, project_id, task_id, starred, pinned, created,
  sources: [Source], group?, provenance
}
Source = { kind, session, window, pane, at, entry_kind?, cwd? }
Counts = { scrollback, activity, transcript, history, total }
GatherSpec = { session, window, pane, cwd, human_nonce, text }
Gathered = { items: [ContextItem], counts: Counts, warnings?: [text] }
```

`ContextItem` belongs to its source pane by stable window ID and to a task or project. Its own type is not a store-row alias. `Source.kind` records the extraction stream; `entry_kind` distinguishes prompt or command content within that stream. `cwd` resolves relative paths. Starred documents also create context items with kind `document`; the original six-kind extraction list is not an exhaustive list of items other units may add.

The scoped `C` page has a separate pane/all-panes filter. All panes still obey the work pin; it is not the page's independent work-scope/all toggle. A pane filter requires an explicit session and window. Rows support text filtering, sorting by `created`, `created-asc`, `kind`, `text`, `starred`, or `pinned`, and grouping by kind, project, task, pane, or session. The default is newest first. Empty task/project groups are labeled `No Task` and `No Project`; missing-owner groups sort last. Equal timestamps have a deterministic store-order tie break.

Commands are `context.extract`, `context.add`, `context.patch`, `context.delete`, `context.insert`, `context.copy`, `context.open`, `context.open-with`, and `context.terminal`. Writes emit `context.changed`. `context.add` lets another unit save an item it already knows, including document stars. Saved extraction deduplicates by kind, text, task, and project, merges distinct source streams, and retains an existing item's star/pin state. Adding an existing known item updates its saved star/pin flags rather than creating another row.

Evidence: Matomeru `internal/context/context.go`, `extract.go`, `gather.go`, and `list.go`. Source design: [original context section, lines 260-280](../sources/znbu/docs/outline.md#65-context--items-extraction-actions) and [implementation-era context section, lines 307-327](../sources/matomeru/docs/outline.md#65-context--items-extraction-actions).

<a id="extraction"></a>
### Extraction and actions

`Extract`, `Unwrap`, and `Gather` cover scrollback, agent activity, transcript, and command history. `Gather` requires a session and window, resolves ownership before saving, and returns separate source counts plus a deduplicated saved total. Explicit `text` is treated as supplied scrollback and avoids daemon reads. Otherwise, recent `capture-pane` content is required. Failed optional activity, transcript, or command-history reads appear in `warnings`, not as invented empty-success results.

Extraction preserves these formats and edge cases:

- `Unwrap` removes ANSI controls, normalizes CRLF, and repairs a URL split by a hard terminal wrap. It keeps ordinary newlines so separate prompts or commands do not become one string.
- Prompt and command entries save their complete text as typed items, then also extract links and paths from that text.
- HTTP and HTTPS URLs lose trailing prose punctuation and unmatched closing parentheses. GitHub `/pull/` links and GitLab-style `/-/merge_requests/` links become `pr` items.
- Paths inside URLs do not become duplicate file items. A file's `:line` or `:line:column` suffix is removed. `~/` expands to the current home directory; relative paths use the recorded source cwd. Bare dotted words count only when they name an existing file. A trailing slash or an existing directory produces kind `dir`.
- Activity and transcript entries contribute text, tool targets, files, diff filenames, and plan text. User text entries become prompts; shell or Bash targets become commands. Command history uses each command's recorded cwd.
- Transcript access requires a live `human_nonce`, supplied explicitly or by the calling shell's presence. Without it, extraction skips the transcript and reports that fact. The transcript request is bounded to 1,000 entries. Nanosecond activity timestamps are normalized to milliseconds.

Actions keep their side effects explicit:

| Action | Contract |
| --- | --- |
| Copy | `context.copy` accepts a saved item ID or nonempty raw text. It runs `pbcopy`; missing `pbcopy` and subprocess failures are visible errors. |
| Insert | Requires an explicit destination session and window. It calls `send-text` with paste enabled and submit disabled. |
| Open | Applies to links, PRs, files, and directories. The current context implementation uses macOS `open`; this is not the cross-platform downloads opener. |
| Open with | Uses `open -a` and requires an explicit application. Prompt and command items are not openable. |
| Terminal | Applies to a file or directory. A file uses its containing directory; the directory must exist. An explicit session is required, and `prompts.new-terminal` creates the terminal. |

Evidence: Matomeru `internal/context/extract.go:55-150`, `gather.go:51-171`, and `context.go:290-383`. The original extraction/action contract is preserved in the [context section](../sources/znbu/docs/outline.md#65-context--items-extraction-actions). Broader stream-driven metadata matching remains the adjacent [context-matcher idea](ecosystem.md#ext-024), with [its own unresolved work](../todo/ecosystem.md#ext-024), not an implemented extraction mode.

<a id="b-05"></a>
## B-05: Notes and ownership

Status: partial. Task/project notes work; arbitrary-owner notes do not. The implementation audit found only `task_id` and `project_id` ownership in `internal/notes/notes.go`. Task detail loads `notes.visible`; this does not establish a `NOTES` section on every other page.

The current model is:

```text
Note = { id, text, task_id, project_id, created, updated, provenance }
VisibleNote = { note: Note, via: "own"|"parent"|"child"|"project", owner: name }
```

Exactly one owner ID is stored. `Note` belongs to a task or project. A task sees its own notes, ancestor notes, descendant notes, and its project's notes. Parent and child visibility is mutual. The implementation-era `child` label makes descendant notes distinct from parent inheritance. `notes.add`, `notes.patch`, and `notes.delete` exist, as does note transfer during todo promotion.

The target replaces the two owner columns with a polymorphic owner without losing that inheritance:

```text
Note = { id, text, owner: Owner, created, updated }
Owner = {
  kind: "task"|"project"|"pane"|"context"|"capture"|"review"|
        "vim"|"reminder"|"prompt"|"download"|"document"|"action",
  id
}
Visible = { note: Note, via: "own"|"parent"|"child"|"project"|"owner", owner: name }
```

The first nine kinds come from B-05's original schema. Downloads, documents, and action items were explicitly added in its later note. Pane identity is `session/window`, not its mutable display name. Pane notes remain readable after closure. Exact owner-kind spellings for the later additions belong to the unfinished contract; they are not accepted by the current commands.

Every page's selected-row detail is intended to end with a `NOTES` section, newest last, inherited rows labeled, wrapped to detail width, and scrolled with the rest of the detail. Empty notes show one dim line. Adding uses the existing notes textarea with the selected owner prefilled and shown in its title. Editing and deletion preserve selection and scroll. The add-note binding, whether review notes belong to a turn or a history entry, and where closed-pane notes are surfaced remain open.

[Remaining B-05 acceptance](../todo/knowledge.md#b-05) owns the migration, per-owner validation, detail editing, and rail markers. The later dedicated Notes page is [B-91](../todo/knowledge.md#b-91), not a prerequisite for the detail work.

Evidence: Matomeru `internal/notes/notes.go:19,181,202`, `internal/ui/model.go:486`, and missing download notes in `internal/ui/render_downloads.go`. Sources: [original notes unit, lines 335-346](../sources/znbu/docs/outline.md#68-notes), [implementation-era notes unit, lines 383-394](../sources/matomeru/docs/outline.md#68-notes), and [B-05, lines 1518-1561](../sources/znbu/docs/todo.md#b-05-notes-on-almost-anything-shown-in-the-detail-pane-of-every-page).

<a id="b-11"></a>
## B-11: Documents

Status: implemented core. The `M` Documents page lists agent-written Markdown and HTML documents under the pin, starred first and then newest. The document unit reads the review unit's document listing. It owns `documents_state`, not the document bodies. Saved state includes the star, `read_at`, the context item made by a star, and the reusable glow pane.

```text
Document = {
  id: "document:<sha256>", path, name, kind: "md"|"html",
  session, window, pane, harness, task_id, project_id,
  starred, read_at, created
}
```

The original target also specified `written_by: { session, window, turn_id }`. The current listing exposes session/window but does not consistently carry the originating turn ID. This provenance gap remains in [B-28](../todo/architecture.md#b-28); completion of the Documents page does not close it.

Current behavior includes:

- `documents.list` and `documents.preview` supply the page. `mtm document list --task ID` returns rows with `starred` and `read_at`. `documents.star` toggles a star or accepts an explicit `starred` value; `documents.read` and `documents.open` update reading state.
- `*` stars a document. The star creates a kind `document` context item through `context.add`; unstarring deletes that item. It appears on the Context page and in the owning task's, ancestor tasks', and project's `STARRED CONTEXT` detail. It does not appear on sibling tasks. This implements the requested direct task/project visibility and the context-scope inheritance rule.
- Highlighting Markdown renders read-only detail with `glow -w <detail width>`. HTML shows source or a text rendering; the implementation-era outline records source when glow is absent. A preview alone does not set `read_at`.
- `Enter` opens `glow -tl <path>` in the document's tuios session, or the `mtm` session if that session is gone. Keys then go to glow. `Ctrl+a d` returns to Documents, not another page. A living glow pane is reused on the next open.
- Unopened rows use unread styling and `new ·`; opening live sets `read_at` and quiets the row. `y` copies the path.

The documented glow version was 3.0.0. `-t` selects TUI, `-l` adds line numbers in TUI, `-p` selects pager, `-w` sets width, and `-n` preserves newlines. There is no local-only flag. `glow -tln` is valid, but the chosen live command is `glow -tl`. Glow must be present on the host for actual Markdown rendering/live viewing.

Evidence: Matomeru `internal/documents/documents.go`, especially star/context and reusable open handling at lines 254-326, and `internal/ui/render_documents.go`; audit commit `6b72b72`. The historical `documents` acceptance case reports the two `history_review` documents as unread, a live/detach round trip that clears unread, and a star visible in task, project, and context. Its recorded log is `/root/proj/redeck-astra-verification/runs/run.j6e4SZd4/verification.log`. VPS verification used a glow stand-in because glow was unavailable there. Real glow 3.0.0 flags were checked on the Mac in the original report. Neither check was rerun here.

Sources: [B-11 design, acceptance, and dated caveats, lines 876-911](../sources/znbu/docs/todo.md#b-11-documents-page-starred-docs-glow-preview-live-mode-unread-theme) and [implementation-era documents contract, lines 459-470](../sources/matomeru/docs/outline.md#614-documents--internaldocuments). [B-05](../todo/knowledge.md#b-05) still owns document notes. Review-document placement and accordion behavior belong to [panes and reviews](panes.md#b-10).

<a id="b-27"></a>
## B-27: Downloads

Status: partial. The `L` Downloads page watches and rescans a downloads directory, lists newest modification first, and copies absolute paths. Directory entries are one row each, never recursively walked. Dotfiles are hidden; a missing directory is an empty list.

```text
Download = { id: path, path, name, size, modified, dir?, seen }
DownloadPageState = { marked: [path] }
```

`modified` is represented by the timestamp returned in the listing. The original example used an RFC 3339 string such as `2026-10-19T21:04:11Z`. Seen state persists in `downloads_seen` by path plus modification time, so replacement at the same path is unread again. Marks are page state and clear on leaving the page.

The unit uses `fsnotify` and emits `downloads.changed`. Every list read rescans, and page opening reloads, so missed watcher events do not leave stale contents. New entries appear at the top without moving the selected row. Rows show name, size, age, an unread `new ·` prefix, and a check mark when marked. Selecting a row once marks that modification seen. Detail currently shows absolute path, size, modification time, and state.

`y` copies the selected absolute path through `context.copy`. With marks present, it copies all marked absolute paths in list order, one per line, then clears the marks. Missing `pbcopy` is reported rather than silently succeeding. `Space` toggles a mark. `Enter` calls `downloads.open`, using `open` on macOS or `xdg-open` elsewhere; the path must be an entry of the configured directory. `mtm download list` returns JSON rows newest first, including modified, size, seen, and path.

The directory currently comes from `MTM_DOWNLOADS_DIR` at construction and defaults to `~/Downloads`. The historical `DECK_DOWNLOADS_DIR` spelling predates the rename. A `downloads.dir` setting is still absent from `settings.Definitions`. The intended `NOTES` block for owner kind `download`, ID equal to the absolute path, is also absent. These are [remaining B-27 acceptance](../todo/knowledge.md#b-27), with notes supplied by [B-05](../todo/knowledge.md#b-05).

Evidence: Matomeru `internal/downloads/downloads.go`, `internal/ui/render_downloads.go`, audit commit `4ea5142`, and the `settings.Definitions` gap. The recorded historical log is `/root/proj/redeck-astra-verification/runs/run.85RFtc62/verification.log`. Its downloads case covers watch-within-one-second, newest first, dotfiles, unread until selected, single and marked copies, open, and CLI output. It explicitly excludes the missing notes acceptance. Historical environment and local unread-style deviations do not close the directory setting or shared-theme requirements. No runtime check was performed here.

Sources: [B-27, lines 1474-1516](../sources/znbu/docs/todo.md#b-27-downloads-page-watch-downloads-newest-first-copy-absolute-paths) and [implementation-era downloads unit, lines 442-456](../sources/matomeru/docs/outline.md#613-downloads--internaldownloads).

<a id="history"></a>
## History and complete agent turns

History owns an append-only `history` table. Live events are batched for one insert per second. The `H` page is the scoped timeline; read-only history listing does not change ownership. Review marks live separately in `review_marks`; reviews are a view over history, not another copy of the conversation.

The archive and review relationship formats are:

```text
HistoryEntry = {
  id, kind, at, observed, source, source_id, sequence?, session?, window?,
  task_id?, project_id?, pane?, harness?, agent_id?, cwd?, tool?, target?, files?, ok?,
  summary, detail, turn?: HarnessTurn, provenance
}
HarnessTurn = {
  id, harness, conversation_id, session, window, pane?, prompt, response?,
  started_at, completed_at?, transcript_path?, response_message?
}
Review = {
  id: promptHistoryId, turn_id?, session, window, pane, harness, prompt, response,
  responses: [ReviewResponse], output?, started_at, completed_at, reviewed_at
}
ReviewResponse = { id, at, text }
ReviewMark = { [historyId]: reviewedAtMs }
```

`HistoryEntry` belongs to a pane by window ID. `Review` belongs to a pane, has response history entries, one optional mark, and one optional `Capture` of kind `turn`. The original richer target also gives `HarnessTurn` a `host` and `place: Place`; that is still tied to [place and Git attribution work](work.md#gitattribution), not established by the current turn schema or catalog page.

A turn means one delivered user request through the final agent answer. It does not mean one model response or one tool cycle. The archive contract preserves:

- The full prompt and final response, stable turn and conversation IDs, harness, pane/session, start/completion timestamps, transcript reference, and final-message metadata. A clipped activity summary is not the archive.
- Automatic continuations and retries keep the turn open. OMP completes on `agent_end` only when `willContinue !== true`, never on its lower-level `turn_end`.
- Queued input is not a delivered request. Steering delivered while a turn is open belongs to that turn. A `<task-notification>` prompt does not complete the turn. Aborted/error stops do not enter the completed review queue.
- `history.capture-turn --json -` records the start first and appends a separate immutable completion. Identical repeated delivery is idempotent. Conflicting reuse of the compound session/window/harness/conversation/turn identity is rejected. Completion retains the start's task, project, cwd, and pane even if assignment changes meanwhile.
- Required IDs must be nonempty. Timestamps are Unix milliseconds; completion cannot precede start. Response data requires `completed_at`. A completion without its start is rejected.
- Packaged harness captures correlate by stable turn ID. Uncorrelated native activity groups responses until the next prompt. Completed turns remain reviewable when a later prompt starts; only unfinished turns and turns awaiting subagent completion stay out.

`Turns(window)`, `Mark(id)`, `reviews.mark`, and `reviews.unmark` support the review view. The units emit `history.changed` and `reviews.changed`. History, Reviews, and the Turns tab share that archive. Exact review focus/marking, the rail queue, and the later accordion design are owned by [panes and reviews](panes.md#b-10), not a separate knowledge backlog.

The original timeline covers prompt submission, response completion, commands, session creation, subagent start/stop, assignment, task status change, capture writes, and fired reminders. Its target also includes worktree dirty/clean changes, HEAD moves for commit/merge/rewrite/checkout, PR open/merge/close, and CI changes. These Git-aware events and turn-to-place-to-commit chains remain the [Git attribution target](work.md#gitattribution) and [B-28 provenance remainder](../todo/architecture.md#b-28). Manual code records or an inventory page do not establish automatic detection.

Evidence: Matomeru `internal/history/history.go:28-120` and `internal/history/turns.go:18-119`; the latter implements immutable start/completion, conflict rejection, and start-time ownership. Source contract: [original history section, lines 282-317](../sources/znbu/docs/outline.md#66-history--reviews) and [implementation-era history section, lines 329-365](../sources/matomeru/docs/outline.md#66-history--reviews). The [concise change-walker idea](ecosystem.md#ext-025) and [its open decisions](../todo/ecosystem.md#ext-025) remain adjacent ideas, not a claim that the timeline explains every change.

<a id="observedconversations"></a>
### Observed conversation inventory

The implemented AI Sessions subsection reads the scoped history archive and groups recorded turns by host, harness, conversation ID, and event-time task/project ownership. Reassignment creates a separate ownership segment rather than rewriting an earlier conversation record. Rows retain unique terminal sessions, windows, pane names, cwds, transcript paths, turn IDs, and history entry IDs, plus the first start, latest event, turn count, and latest recorded prompt/response. Host identities derived from session and window must agree; an unqualified identity is local.

This is an inventory of observed harness conversations, not every session on disk or a tuios terminal-session inventory. It does not add `host`/`Place` to the underlying turn schema or close B-28. The AI/Git/GitHub subsection implementation in `e4cf07a` is reported complete and verified by its owner. Relevant recorded runs are `run.0FUXkwfs` for AI provenance and `run.uag5oacy` for the TUI. No run was repeated here. Evidence: Matomeru `internal/ai/sessions.go:18-108`, `internal/ai/ai.go`, and [implementation-era inventory section, lines 473-481](../sources/matomeru/docs/outline.md#615-ai-and-git-inventories--internalai-internalgitcatalog). Full AI and Git UI contracts stay in [agents](agents.md) and [work](work.md#gitcatalog).

<a id="captures"></a>
## Captures and autocapture

The captures unit owns files, not a store-backed table. The current default folder is `~/.local/share/matomeru/captures`; the source's `~/.local/share/tuios-deck/captures` is historical naming. `List`, `Read`, and `Dir` remain the unit's read contract. Commands are `captures.capture` and `captures.delete`, with a Captures page and `captures.changed` events.

```text
Capture = {
  name, path, size, modified, session, pane, window?, turn_id?,
  kind: "turn"|"cmd"|"", task_id?, project_id?, provenance
}
CaptureArgs = { session, window, pane?, kind?, turn_id? }
CapturePreview = { Capture, content, truncated }
```

An empty kind is a manual capture. Automatic captures use `-turn` or `-cmd` filename suffixes. Command captures read `last-command-output`; manual and turn captures read recent terminal content. Session and stable window ID are required; a pane label is recorded when available and otherwise defaults to the window ID. The legacy file relationship uses session plus pane name, but packaged turn snapshots link to their review by session, window ID, and turn ID. Exact timestamps and mutable names are not sufficient correlation.

The files contain terminal snapshots, not a substitute for structured full prompt/final-answer records. Autocapture consumes command completion and packaged turn-end activity when enabled. The packaged `mtm-turn:` target supplies a stable turn ID. A missed completion cannot be reconstructed from the current screen; `Resync` does not pretend to recover it.

Files use timestamp, escaped session, escaped pane, and a generated ID, ending in `.txt`. Reads and deletes accept saved capture filenames only and reject traversal, directories, and symbolic links. Private metadata beside each capture retains write-time scope, window, turn, and provenance. Task-owned metadata does not duplicate the project. Legacy files without metadata remain readable in all mode without guessing ownership from a pane's current assignment. Historical captures keep their recorded ownership rather than following later assignment.

Saving writes a private temporary file, syncs and closes it, writes ownership metadata, then renames the capture into place. Cancellation or rename failure removes the unfinished metadata. A missing `capture-pane` content field is an error; an actual empty content string is not the same failure. Preview reads at most 256 KiB and reports truncation.

Evidence: Matomeru `internal/captures/captures.go`, `ownership.go`, and `preview.go`. Sources: [original captures section, lines 319-333](../sources/znbu/docs/outline.md#67-captures--files--autocapture), [implementation-era captures section, lines 367-381](../sources/matomeru/docs/outline.md#67-captures--files--autocapture), and [implementation-era ownership decision, lines 608-610](../sources/matomeru/docs/outline.md#10-open-decisions). Notes on captures remain [B-05](../todo/knowledge.md#b-05). Automatic clipboard/pane intake in Ima remains [separate ecosystem work](../todo/ecosystem.md#ext-020); it is not implied by Matomeru autocapture.

<a id="editorvim"></a>
## Matomeru-owned Neovim sessions

A saved Vim session is Matomeru's editor for project/task files. It is a tuios pane running the real `nvim` binary, not embedded text input in a form. A pane running Neovim that Matomeru did not start remains an ordinary terminal. Saved sessions use the same pane row, assignment, `No Task` rule, and live entry as terminal and agent panes.

The implementation stores this session metadata:

```text
VimSession = {
  id, name, path, project_id, task_id, cwd, created, updated,
  session, window_id, state: "running"|"closed"
}
OpenSpec = { id?, name?, task_id?, project_id?, tree?, session?, cols?, rows? }
```

`path` is the session file. Metadata and session files are Matomeru-owned beside the selected database; Neovim's global session directories are never scanned. Closing the pane retains the session for reopening after Matomeru restarts. `panes.changed` reconciles stored window identities with the live snapshot and emits `vim.changed` when session state changes. Task ownership inherits the project rather than duplicating it in storage.

`vim.open` starts in the active project/task's existing tree unless the form chooses another directory. Existing saved sessions keep their saved cwd unless overridden. A running session is focused rather than duplicated. Missing `nvim` reports `missing_binary`; no shell or fake editor substitutes for it. A missing target tree, non-directory tree, or absent cwd is an error. Matomeru does not create a worktree.

The process is launched directly as a tuios terminal window. An existing session file is passed with `nvim -S`; the launch sets cwd, writes a session, and installs a `VimLeavePre` save for later restoration. Escaped Vim literals and `fnameescape` keep paths out of Ex command syntax. A missing tuios session is created before retrying the window creation. A returned pane is assigned to its task/project. A created pane whose metadata or assignment write fails is reported as an existing pane plus a failure, not as a successful saved session.

`vim.list` and the registered `vim.sessions`/`vim_sessions` sources list sessions. The palette offers Open Neovim and Neovim sessions; the resume modal focuses a running session or restores a closed one. The current registry does not provide the dedicated phase-2 Vim page or `vim.forget`.

The richer original target is retained, not described as current storage:

```text
VimSessionTarget = {
  id, name, session_file: path, window?, project_id, task_id,
  place: Place, cwd, created
}
```

That session belongs to a project, optionally a task, a worktree through its place, and a pane only while open. Opening uses the task's resolved place and may choose another worktree. The original discovery alternatives were an app-owned session directory or Neovim's own directory. The implementation chose app-owned files; that decision is settled. A host/worktree-aware `Place` record and `vim.forget` remain [B-92](../todo/knowledge.md#b-92); the [work place design](work.md#places) owns the shared model. The dedicated page is [B-91](../todo/knowledge.md#b-91).

Optional Neovim-backed form fields are the separate, unresolved [B-23](../todo/forms.md#b-23). The implementation-era decision not to embed Neovim does not silently discard that request. Ima's durable task-entry plugin is [source-reported ecosystem behavior](ecosystem.md#ext-026), not evidence that this session manager or Matomeru's tree editing satisfies it.

Evidence: Matomeru `internal/vim/vim.go`, `register.go`, and `assign.go`. Sources: [original editor/session design, lines 381-395](../sources/znbu/docs/outline.md#612-vim--neovim-sessions-as-deck-items), [implementation-era Vim unit, lines 429-440](../sources/matomeru/docs/outline.md#612-vim--neovim-sessions-as-mtm-items), and [phase 2 page and input-engine proposals](../outline-phase2.md).

<a id="agentinstructions"></a>
## Generated reference and agent instruction context

Registry definitions generate runtime documentation for structs, pages, concepts, actions, command discovery, and configuration defaults. Generated command reference is context for agents that drive Matomeru through its concept-oriented CLI. It does not replace source documentation for private symbols, field comments, implementations, or relationships. Missing comments remain visibly undocumented rather than becoming invented behavior descriptions. [Source-documentation adoption](../todo/delivery.md#b-71) remains a separate gate.

The phase-2 unit workflow uses generated structure plus human notes as agent instructions. Its prompt body contains the unit's outline/shape text, selected notes as a numbered list, and current build rules. It opens in the regular composer so presets, attachments, and edits still apply. The default cwd is Matomeru's own repository tree, not the active pin. The original question of embedding the outline text or linking its path remains open. This is target context construction, not a claim that a meta workflow currently dispatches agents.

Agent-written Markdown/HTML stays reviewable as [documents](#b-11); a star also makes that document persistent [context](#context). That saved material retains its source and ownership. Agent-generated answers are not evidence that their requested implementation or verification occurred. Historical implementation prompts and their model instructions remain in the [prompt archive](../prompts/README.md); they are provenance, not current worker-policy overrides.

Packaged harness reporting hooks/extensions/scripts and configuration templates are the setup unit's responsibility. The original contract embeds the required assets in the distributed binary, installs them idempotently without a source checkout or manual copying, records the executable/database, replaces the older managed reporter, and requires reload after installation. The [full setup contract](delivery.md#setup) records the packaged OMP baseline; [B-76](../todo/delivery.md#b-76) owns remaining setup acceptance and other harness adapters. Configuring a harness for MCP does not prove it captures the complete delivered request through final answer. A terminal snapshot or generated instruction file does not substitute for the [full structured turn archive](#history).

Sources: [registry generation, lines 104-137](../sources/znbu/docs/outline.md#5-registry--internalregistry), [concept CLI, lines 591-596](../sources/znbu/docs/outline.md#73-cli-new), [packaged setup assets, lines 370-379](../sources/znbu/docs/outline.md#611-setup-complete-focus-unchanged-leaves), [Go source documentation decision](../go-code-review.md), and [phase 2, unit modal and notes-to-prompt sections](../outline-phase2.md).

<a id="unitnotes"></a>
## Phase-2 unit notes and generated prompts

Status: target, not implemented by the current notes unit. The [phase-2 plan](../outline-phase2.md) remains unfinished and is referenced by [B-90](../todo/knowledge.md#b-90), [B-91](../todo/knowledge.md#b-91), and [B-64 prompt management](../todo/agents.md#b-64). Current prompt/queue behavior and its remaining work are in [agents](agents.md#unitprompts).

Every unit is intended to register its own page. Notes has rows by owner with inherited notes marked, `e` edit, `d` delete, and `a` add under the pin. Vim has session rows, `Enter` open, and `d` forget. Each page is scoped, supports `S`, and is read-only in all mode except assignment. `Page.unit` identifies the owner; the shell orders pages by unit ID without another unit-specific switch.

One binding on every page, proposed as `I`, opens that page's unit modal. `unit: <id>` in the palette opens any unit. The modal has three folds read from the registry/store, never hand-written copies:

```text
UnitModal = {
  unit: id,
  shape: {
    structs: [Struct], relationships: [Relation], commands: [name],
    emits: [type], listens: [type], pages: [id]
  },
  notes: [UnitNote], prompts: [UnitPrompt]
}
Struct = { name, fields: [{ name, type, json?, doc? }] }
Relation = {
  from: struct, kind: "belongs_to"|"has_many"|"has_one"|"through",
  to: struct, via?
}
UnitNote = {
  id, unit, text, status: "open"|"prompted"|"done",
  prompt_id?, created, done_at?
}
UnitPrompt = {
  id, unit, note_ids: [id], text, preset?, window?, submitted?, turn_id?, created
}
```

The shape fold contains Go-source-derived structs/fields through the docs generator, relationships as written in the outline, commands, events, and pages. Each struct starts collapsed to its name. The notes fold holds free text about a unit and a change the person wants. `a`, `e`, and `d` add/edit/delete; `Space` selects notes for a prompt.

`UnitNote` belongs to a unit and optionally a prompt. `UnitPrompt` belongs to a unit, has many notes, belongs to a pane through window ID, and has one history turn. A new `meta` unit owns `unit_notes` and `unit_prompts`; no domain unit stores notes about itself. Commands are `meta.add-note`, `meta.patch-note`, `meta.delete-note`, `meta.prompt`, and `meta.reopen-note`. It emits `unit_notes.changed` and `unit_prompts.changed`, and listens through history for the turn-end activity.

The complete target lifecycle is:

1. Select notes in the notes fold and press `p`. Build the prompt from the unit's generated shape/outline node, the numbered selected notes, and current build rules.
2. Open the composer with the prompt. Presets, attachments, and edits apply. Default cwd is the app's own repository, not the pin's tree.
3. Submit with `prompts.start-agent` or `prompts.queue`. Save `UnitPrompt`, including its window/submission, and move the selected notes to `prompted` with their prompt ID.
4. Correlate that prompt's `prompt-submitted` with its window's eventual completed response. Save `turn_id`, set those notes to `done`, and set `done_at`. Automatic continuation and task notifications do not complete the turn.
5. List the finished turn in the normal review queue. Opening the turn also shows the unit notes it closed.
6. Press `o` to reopen a note. Clear `prompt_id` and `done_at` and return it to `open`.

The source's window/time correlation must respect the stronger current [stable-turn archive contract](#history), rather than treating the first intermediate response as completion. The open decisions remain `I` versus `Ctrl+i`, embedded outline text versus a path link, one or multiple in-flight prompts per unit, and whether settings or an app-named project records the app's repository tree. These alternatives have not been resolved by the consolidation.

Source: [phase 2, lines 5-61 and 70-75](../outline-phase2.md). Deferred focus mode, optional Neovim text input, web shell, and suite timing/trimming remain with their owning domains; unit notes do not turn those deferrals into shipped work.

<a id="knowledgepagedesign"></a>
## Page design inputs and adjacent ideas

The [TUI design research, pages section, lines 384-424](../sources/matomeru/docs/research/tui-design-samples.md#11-pages-history-timeline-reviews-captures-context-tasks) proposes compact/full history rows with relative time, duration, exit state, named filter mode, and selected-turn preview. It also proposes reviewed/unreviewed glyphs and a tested light theme, review/stale badges on timeline rows, configurable split direction/percentage, a command-log view, and capture size/position alongside list-plus-preview. These are research proposals, not current UI claims. The whole-app pass and [remaining sample adoption](../todo/delivery.md#b-72) decide their use. The research's deterministic task-color proposal conflicts with the later random unused-theme decision; the [work theme contract](work.md) owns that choice.

Related ecosystem requirements stay in one place:

- [Context matchers](ecosystem.md#ext-024) and [their unfinished specification](../todo/ecosystem.md#ext-024) cover metadata attached from streams/events.
- [Change walker](ecosystem.md#ext-025) and [its unresolved format](../todo/ecosystem.md#ext-025) cover concise explanations of task/action/change and why.
- [Deferred learning](ecosystem.md#ext-016) and [its lock-policy decisions](../todo/ecosystem.md#ext-016) cover learn-for-later runs. Existing Ima Later behavior is source-reported, not Matomeru evidence.
- [Noise capture and extraction](ecosystem.md#ext-015), [dedicated to-know questions](ecosystem.md#ext-019), and [their remaining decisions](../todo/ecosystem.md#ext-019) are adjacent to this saved-knowledge model. The separate [Projects-page research-depth request](../todo/work.md#b-43) keeps its short, medium, and full-report answer sizes.
