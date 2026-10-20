# Ima / Now unfinished work

Updated 2026-10-17. This is the known unfinished-work inventory, not a priority system. Capture ideas here without treating every idea as an approved feature.

## Goal and constraints

Authoritative goals: [iwants.md](iwants.md). Current implementation: [README](../../proj/now/README.md), [design](../../proj/now/docs/design.md), [user stories](../../proj/now/docs/user-stories.md).

- Funnel tasks, subtasks, and actionable noise into one system. Make finishing one small task the central mode.
- Keep abstraction levels separate except the deliberate generic selector. Preserve keyboard-driven, modal operation.
- Attribute actions to tasks rather than restricting when or why a person may work. Do not add priority gates.
- Preserve the three-minute idle reset, fifteen-minute no-break split, event history, task theme, and intentionally deferred learning motivations.
- Keep the app responsive. Background activity must not reset input, focus, selection, or the current screen.
- Every option list supports Ctrl+n / Ctrl+p, including focused filters. Enter acts on the selected option.

## Completed locally: Neovim task-entry plugin

Requested in session `01a148d2-bab7-755a-8445-4305bd35b618`; persistence clarified by the owner on 2026-10-17.

- [x] Implement a Lazy-installable plugin in `unixsuperhero/ima`, exposed as `require('now')`, `:Now`, and `:NowApply`.
- [x] Open/reuse a dedicated split without replacing unsaved buffers. Enter turns text into task rows; Tab and Shift-Tab adjust nested task/subtask depth. Retain normal Vim editing and undo.
- [x] Make plugin bindings configurable or disableable; do not claim unrelated global keys.
- [x] Store pending text in the app-owned durable `draft.json`. Temporary describes its lifecycle, not an OS cache. Recover across Neovim restarts.
- [x] Explicitly apply the whole draft into real Now tasks with hierarchy and original cwd. Validate before publication, retain failed drafts, and use the batch receipt to prevent duplicate retries.
- [x] Verify empty/mid-line Enter, subtree edits, root boundaries, undo/redo, split/window reuse, restart, failed apply/save, configurable bindings, concurrent recovery ownership, and lost-response retries against real Neovim and Now storage.
- [x] Document installation, draft location, apply behavior, recovery, and verification commands in the repository README.
- [x] Publish the project and enable/install the GitHub-backed Lazy plugin. Both `:Now` and `:NowApply` are registered; the configured CLI uses `uv run --project ~/proj/now now` because no standalone `now` is on PATH.

Resolved: this is neither session-only scratch text nor a live task-database editor. It is durable pending text that becomes tasks when applied. General rename/reparent/delete APIs for already-created tasks are not required by this workflow.

Implemented in `3924a01` and `4e48eeb`; recovery/editor refinements in `e678a8e`. Documentation commits: `e3612fc`, `2efe02c`, and `e678a8e`. Published to `origin/main` on 2026-10-17. The live Neovim spec and its tracked dotfiles counterpart now enable both commands; the installed GitHub plugin and Lazy lock entry use `572a596`. Unrelated personal config edits were preserved.

Verification: 47 Python tests passed in the backend worker. Both `nvim --headless -u NONE -l tests/neovim_draft.lua` and `tests/neovim_persistence.lua` passed after the final plugin change. A real terminal session typed a parent/subtask, exited Neovim, reopened from another cwd, applied the recovered outline, and confirmed original cwd and parent links. The actual Now TUI then offered only the child; completing it exposed the parent.

Installed-plugin verification on 2026-10-17 used normal Neovim startup with the actual user config and isolated `NOW_HOME`: `:Now` preserved the original buffer, and `:NowApply` persisted the expected parent/child tasks through the configured CLI. Restart existing editor instances to load the changed Lazy spec.

Durability boundaries: acknowledged draft saves survive restart; saves are asynchronous and cannot preserve a just-typed edit if the process is killed before a save finishes. Lifecycle flushes and failed-save recovery files cover ordinary exit and save errors while storage is writable. Filesystem failure points were injected; physical power-loss testing and other OS/Neovim versions were not exercised. Installed Neovim was 0.12.3.

## Completed locally: persistent agents from the TUI

- [x] `a` opens a task-scoped launcher with inherited cwd, configurable interactive command, multiline prompt, and keyboard/button submission.
- [x] Native tuios panes continue when Now switches tasks or exits. Durable run records reconnect to the same pane after restart; no worktree or custom agent supervisor.
- [x] `g` lists task agents from Now or all agents from Picker normal mode. Details show original prompt, status, cwd, and bounded pane output; `o` focuses the native pane and `x` confirms stopping only that pane.
- [x] Ctrl+n / Ctrl+p navigation, selection, reading position, and modal focus survive background refresh. Refresh is not activity.
- [x] App-launched done/needs-input/error transitions create task-linked attention, deduplicated across watcher and polling. Find and Noise open agent details.

Implemented in `91a6480` and `572a596`. `uv run python -m unittest discover -s tests` passed all 62 tests. Actual isolated Now/tuios smoke launched authenticated OMP agents, delivered prompts, switched tasks, quit/reopened Now during an agent turn, recovered output/context, navigated with Ctrl+n/Ctrl+p, focused the native pane, cancelled a stop, and confirmed stops without closing other panes. Find and Noise links were exercised.

Boundaries: requires tuios plus an installed/authenticated interactive agent CLI. Provider login/trust/approval remains in its native pane. Outside tuios, attach to the dedicated `now-agents` session; focusing does not open a terminal application. Output is the latest bounded snapshot, not a continuous archive while Now is closed. The existing `:ask` one-shot is not restart-safe; use `a` for persistent work. Broader external attribution and automatic follow-up child tasks remain proposals below.

## Standalone distribution

A macOS arm64 PyInstaller executable was built and exercised in session `01a148d2-bab7-755a-8445-4305bd35b618`. Its recorded path is `/tmp/now-standalone.qQ6Alw/dist/now`; it existed at this inventory's initial creation. It predates the new plugin backend and later navigation changes.

- [ ] Preserve or rebuild the executable outside `/tmp` before sharing it.
- [ ] Put the proven build procedure into a repeatable repository build/release workflow; package and publish release artifacts when requested.
- [ ] Decide the project license and include required dependency notices before public redistribution.
- [ ] Address macOS signing/notarization for downloaded releases.
- [ ] Build and exercise each additional supported OS/architecture separately. Linux needs attention to current macOS `open` calls; do not claim cross-platform support from one Mac build.
- [ ] Document external optional dependencies and credentials: `gh`, `h-mcp`, configured agent CLI, and their authentication are not bundled.
- [x] Publish the local Now project commits to `github.com/unixsuperhero/ima` on `origin/main` (2026-10-17). Release artifacts remain separate work.

## Remaining product goals and decisions

These are not all approved implementation tasks. Keep proposals distinct from commitments.

- [ ] Define and implement dedicated behavior for to-know tasks. They currently have a kind/label but no question/answer workflow of their own.
- [ ] If a web UI is pursued, mirror TUI behavior exactly while improving visual presentation. No independent web-only workflow is requested.
- [ ] Decide whether first-class projects add value. Current grouping is task `cwd` and parent tasks; do not introduce a project type merely because it was mentioned.
- [ ] Define a concrete way to encourage writing/documentation within task work. The goal exists; a specific workflow has not been agreed.
- [ ] Reconcile the broad goal of attributing every action with current coverage. App shell runs, prompts, and app-launched persistent agents carry tasks, but a general typed action model for external ask/run/write events is not implemented.
- [ ] Decide whether any new multiplexer functionality is needed beyond tuios/herdr integration. A separate multiplexer is an option, not a commitment.
- [ ] Automate clipboard/pane capture only if desired. They are currently manual `capture -s` source labels.

## Recorded ideas not yet adopted

Sources: [context matchers](ideas/context-matchers.md), [change walker](ideas/change-walker.md), and the [original design conversation](ideas/fml-2026-10-15-180521-goal.txt), especially its final multiplexer discussion. These are proposals, not claims about current behavior.

- [ ] Context matchers over prompts, agent replies, shell input/output, and source events that attach typed metadata.
- [ ] A concise model-guided walkthrough of tasks/actions/changes so the owner understands what happened and why without reading every tool call.
- [ ] Task context pointers to session/window/pane, potentially focusing or opening the task's workspace and updating window titles on selection.
- [ ] Capture tuios mail and pane output as noise with source references.
- [ ] Attribute externally launched agent prompts and replies to their originating tasks; optionally create small linked "read reply" / "answer agent" child tasks. App-launched persistent agents now retain task links and task-linked attention, but automatic child-task extraction and attribution for arbitrary external panes are not built.
- [ ] Decide the no-active-task behavior for externally observed actions. The original proposal suggested creating a task from the action instead of blocking it.

## Already implemented; do not reopen as unfinished

The TUI/CLI core loop; task/subtask storage; idle and overrun behavior; CLI activity touches; out-of-pane notifications; Noise screen and capture/extract/drop; GitHub and Slack MCP pollers; attributed app command/prompt runs; tuios activity and agent-state noise; Later and locked learn motivations; Review; generic Find; task theming; Ctrl+n / Ctrl+p option-list navigation.

Historical rough edges in the original conversation predate these features. This inventory excludes them from pending work. Verification and live integration coverage are separate from feature existence.
