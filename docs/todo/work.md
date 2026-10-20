# Work, projects, and places: remaining work

[Current behavior and target model](../outline/work.md) · [Pane work](panes.md)

Only unfinished acceptance is active here. Implemented [B-37 bulk creation](../outline/work.md#b-37) and [B-47 Git inventories](../outline/work.md#b-47) live in the outline. [B-07](../outline/work.md#b-07) is superseded, not an active request to rebuild the legacy mass-add outline. Historical evidence is not a test performed during this consolidation.

Implemented canonical backlog import [B-13](../outline/work.md#b-13) lives in the outline.

<a id="b-43"></a>
## B-43: Give projects their own knowledge and deliverables page

Status: open · priority: p2 · size: not estimated

The existing project record and task tree do not implement this workflow. [Target concept](../outline/work.md#projects-as-knowledge-and-deliverables).

Acceptance:

- Open a dedicated Projects page and select a project without using Tasks as its only entry point.
- Record and view four project-associated categories: things to know, things to do, things to make, and things to share. Support the organizing question for one particular project and as a reusable way to approach any project.
- Request agent research for a knowledge item at the chosen depth: a small concise answer, a medium answer of a few paragraphs, or a large full report. Agents obtain what they can rather than merely recording the question.
- Keep each project-specific question and its answer or report associated with that project.

Sources: [original B-43](../sources/znbu/docs/todo.md#b-43-give-projects-their-own-page-organized-around-what-needs-to-be-known-done-made-and-shared) and [captured user request](../sources/hub/prompts/mtm-todo.md). Related reusable knowledge/research ideas remain in the [ecosystem outline](../outline/ecosystem.md) and [ecosystem backlog](ecosystem.md).

Implemented continuous bulk editing and existing-record renames [B-44](../outline/work.md#b-44) live in the outline.

<a id="rankedpaths"></a>
<a id="b-46"></a>
## B-46: Resolve the remaining directory-ranking acceptance

Status: partial · priority: p2 · size: not estimated

The ranked directory catalog is implemented in commit `e4cf07a`. Its owner reports VPS acceptance of directory/default/composer behavior. The [implemented ranking](../outline/work.md#rankedpaths) and [directory plan](../plans/ranked-dir-suggestions.md) retain local canonical deduplication, tracked directories, contextual ordering, unrelated-project candidates, manual paths, and remote isolation. Those are not still-pending construction tasks.

Remaining acceptance:

- Resolve the original plan's request to collect current agent/terminal cwds and rank from most common to least common. The implemented catalog uses successful-launch frequency within contextual ranks; ordinary pane activity supplies candidates but does not add launch-frequency samples. Either retain current-cwd frequency as a separate ranking signal or record an explicit accepted replacement. Do not describe these two counts as equivalent.
- Preserve the distinction in the plan and user-facing ranking explanation. One successful launch must not be inflated by later ordinary activity or a queue/stash entry.
- Keep the native-picker verification boundary explicit. The owner reports VPS Linux verification, not a new macOS native-picker run. If closing this item's original path-choice acceptance relies on that picker, attach the platform-specific evidence rather than treating Linux as proof.

Owner evidence received during consolidation names commit `e4cf07a` and VPS runs `run.8tnoOG3b` and `run.uag5oacy`. These are reported historical runs, not checks performed here. The original [directory suggestion note](../sources/matomeru/docs/plans/ranked-dir-suggestions.md) remains preserved verbatim. Launch-setting precedence is a separate [defaults contract](../outline/agents.md#launchdefaults), not B-42's sparse preset layers.

<a id="b-48"></a>
## B-48: Implement the full Place and observed Git model

Status: open · priority: p2 · size: not estimated

The current project repository/tree settings, explicit provenance records, and [implemented read-only Git inventories](../outline/work.md#b-47) are distinct baselines. None completes the [multi-directory Place target](../outline/work.md#places) or [automatic Git attribution target](../outline/work.md#gitattribution).

Acceptance retains the original model and edge cases:

- Make projects named work independent of repository identity. Support zero or many host-qualified directories, shared by several projects, including plain directories. Naming a project does not infer a path. Native selection, repo scan, and CLI attachment remain separate actions. First-run scan offers repositories as attachable directories, with one project per repo as the default proposal.
- Identify each directory by host and canonical path. A plain directory has one implicit worktree and no branch. Preserve per-project default directory and default worktree per directory. Task Place overrides parent Place, which overrides project defaults. Blank fields inherit. Agent, terminal, and Vim starts resolve both host and cwd from that Place unless explicitly overridden.
- Run Git/`gh` on the directory's host. An unreachable host means unknown, not clean. Record observation time and stale state. Resolve daemon routing versus direct SSH explicitly before implementation.
- Observe worktrees on explicit refresh, on the planned thirty-second `worktree_poll` default, and after a turn or command in the repository. This automatic observation target is not already implemented by lazy/manual catalog reads. Derive panes and working state from cwd as `WorktreeUse`, not a second persistent ownership truth.
- Record dirty changes with every observed cause since the prior observation, newest first: turn, terminal command, or unknown. Never guess an actor. Clear active blame when clean but keep dirty and clean transitions in history. Settle whether all observed causes or only active panes qualify, without silently deleting either original alternative.
- Track branch upstream, ahead/behind, and commits observed since first sighting. Bind branches to tasks. Link dirty changes, commits, and PRs through the branch and through recorded turn ownership. If those disagree, show both.
- Record every HEAD move from the graph as commit, merge, rewrite, or checkout. Rebase, amend, reset, and squash retain old SHAs and use patch IDs to populate `Commit.superseded_by`, preserving turn-to-commit links.
- Refresh upstream PR and check state on completed turns and at the planned two-minute `pr_poll` default. Preserve aggregate CI plus individual checks. Missing `gh`, network failure, and rate limits yield unknown with a reason. PR context items resolve to the same PR row. Decide GitHub-only `gh` versus a provider interface explicitly.
- Show a scoped directory/worktree view with branch, short HEAD, dirty state and blame, agents present, PR state, and CI. Detail shows head moves and commits with their tasks/turns. Enter opens a PR. Resolve the old Code `D` proposal against Panes `D`, Git `W`, and GitHub `V` without losing data acceptance.
- Display nonblocking launch warnings for dirty/blamed changes, another working agent, wrong bound branch, behind-base branch, merged/closed PR, and failing CI. Quick `n a`, `n t`, and `n v` still launch immediately, with warnings in status and on the row.
- Preserve selection, scroll, filter, and modal state across observation. Stale rows state their age. Retain the target schemas, relationships, commands, events, and turn/command/rewrite flows consolidated in the outline, not just their record names.
- Decide task-created branches/worktrees versus record-only behavior. Current Matomeru does not create Git worktrees. Do not imply that decision changed because a catalog lists them.

[Shared claims/messages](#b-02) remain a separate deliverable over this Place model. Cross-record tracing remains [B-28](architecture.md#b-28). Sources: [complete original code-unit design](../sources/znbu/docs/outline.md#613-code--directories-worktrees-branches-commits-prs-ci), [original work model](../sources/znbu/docs/outline.md#63-work--projects-tasks-assignments), and [original flows](../sources/znbu/docs/outline.md#8-flows-who-touches-what).

<a id="b-02"></a>
## B-02: Build application-owned shared-place messaging

Status: open · priority: p2 · size: L

The [shared-place design](../outline/work.md#sharedplaces) is retained in full. Existing tuios mail and task/project notes do not implement application-owned claims, records, or routing.

Acceptance:

- Discover other panes in the same worktree, or on the same branch in different worktrees, using host-qualified identity and derived worktree uses. Persist `PlaceMessage` and `Claim`, not only transient transport mail.
- Support all six message kinds: claim, release, heads-up, handoff, question, and answer. Preserve sender pane/task/turn, Place, paths, text, reply links, recipients, and per-recipient delivery outcome. Each message reaches every other pane in the place and appends history under the sender's event-time task.
- Use tuios mail addressed by host/session/pane. Never inject message text as terminal keystrokes. Resolve direct application-server delivery through [the server decision](architecture.md#b-70), retaining mail for clients the server cannot reach.
- End claims on release, turn completion, or pane closure. Show persistent open claims on code rows and launch forms so later agents do not need to reconstruct them from mail.
- Prepend the standard shared-place prompt preamble with other panes/tasks, working/idle state, open claims, dirty paths and blame, HEAD/branch/PR state, and exact claim, release, handoff, and ask commands. Tell agents to claim before editing and send heads-up before head moves. Show equivalent information to humans in row/detail and the quick-start status summary.
- Show overlapping-path claims, a head move during another pane's open turn, and commits touching another pane's claimed paths as warnings on both rows naming both turns. Claims do not silently become locks. Preserve the alternative of refusing quick start on overlap as an explicit unresolved decision, not implemented behavior.
- Retain the CLI message/claim/release/place contracts, claim/message change events, and full schemas/relationships in the outline. A heads-up preceding a rewrite remains associated with the resulting head move.
- Decide how human-terminal recipients receive the information: tuios mail, an application notification, or both. This and the server choice gate parts of the design; neither can disappear from acceptance merely because basic transport exists.

Sources: [original B-02](../sources/znbu/docs/todo.md#b-02-deck-owned-agent-messaging-shared-places) and [complete original shared-place section](../sources/znbu/docs/outline.md#613-code--directories-worktrees-branches-commits-prs-ci). Related cross-agent coordination ideas remain in the [ecosystem outline](../outline/ecosystem.md) and [ecosystem backlog](ecosystem.md).
