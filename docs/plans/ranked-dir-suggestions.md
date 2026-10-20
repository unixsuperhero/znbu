# Ranked directory suggestions

Status: implemented baseline with remaining acceptance in [B-46](../todo/work.md#b-46). This plan is not another backlog. [Current behavior](../outline/work.md#rankedpaths) owns the implemented result.

## Original request and current decision

The [preserved original note](../sources/matomeru/docs/plans/ranked-dir-suggestions.md) proposes collecting agent and terminal working directories and sorting them from most common to least common. It is a directory-selection idea, not a request to limit choices to the active project.

Commit `e4cf07a` implements a richer catalog in `internal/work/directories.go`. It combines current input, focused evidence, successful-launch history, project repositories/worktrees, and other tracked paths. Context determines ranking without excluding unrelated projects. The feature owner reports verification on VPS Linux during this consolidation. No build, daemon, or application check ran as part of writing this plan.

The two frequency concepts are not interchangeable. A directory repeated among currently open panes is current-cwd frequency. A directory repeatedly used by successful launches is successful-launch frequency. The implemented catalog counts successful launches within contextual ranks. Pane activity, queue entries, stashes, and ordinary history contribute candidate paths but do not count as successful launches. [B-46](../todo/work.md#b-46) retains the decision whether current-cwd frequency also remains a ranking signal or the newer rule explicitly replaces it.

## Candidate set

Candidates are valid canonical local directories, deduplicated by canonical path. Existing input retains priority. Candidate sources include:

- Focused pane evidence and successful terminal/agent launches.
- Every project's repository, selected default tree, and recorded trees, including projects outside the pin.
- Pane and saved Vim cwd values.
- Context directories, parent directories of context files, and cwd values on context sources.
- Preset cwd, queued/stashed prompt cwd, and local recorded history.
- Repositories and worktrees discovered beneath configured repository roots.
- The Matomeru process cwd and the user's home directory as lower-priority choices.

The selected task/project scope changes relevance, not the existence of other candidates. Unrelated projects remain selectable. The currently selected preset can also supply scoped relevance. New suggestions must not silently create a project, initialize Git, assign a pane, or change the active pin.

The implementation bounds repository discovery to five seconds and caches the root set's result for one minute. A failed optional source does not justify inventing a directory. Cancellation remains authoritative. Canonicalization rejects paths that do not resolve to a usable directory.

## Ranking

The implemented precedence is:

1. The current explicit cwd.
2. Evidence for the focused target.
3. Successful launches within the chosen task/project context.
4. Scoped project or selected-preset evidence.
5. Other tracked application directories.
6. Repositories and worktrees found beneath configured roots.
7. The process cwd.
8. Home.

Within one rank, successful-launch count sorts descending, then last-observed time descending, then canonical path for stable ties. Deduplication keeps the strongest relevance rank. An ordinary activity event cannot increase successful-launch count. A queue entry is not proof of a launch. Duplicate observations of one local path must not create several chooser rows.

Defaulting the launch fields is a separate [agent launch-default contract](../outline/agents.md#launchdefaults). Explicit/restored values take precedence there. Ranking a path does not select an existing destination pane or overwrite a field the user edited.

## Host and picker boundaries

Remote host evidence is never resolved against the local filesystem. Host-qualified session/window identities are checked as well as explicit `host`, including nested draft/source records. Selecting a remote destination returns no local directory suggestions. Remote history stays separate from local history, and local native-picker results are not sent to a remote host.

Manual paths and the native directory picker remain available for local selection. The feature owner's Linux verification did not exercise the macOS native picker. Keep that platform boundary in the evidence rather than describing Linux as complete picker verification.

Repository identity and live Git reads belong to [Git inventories](../outline/work.md#b-47). Multi-host directory ownership and inherited Place are a broader [B-48 target](../todo/work.md#b-48), not features automatically supplied by ranked suggestions.

## Recorded evidence and unresolved acceptance

The owner reports commit `e4cf07a`, pushed to the implementation repository's main branch, with launch-default, composer, directory, remote-launch, and full TUI/live checks. Reported runs include `run.8tnoOG3b` for the composer and `run.uag5oacy` for the TUI. [The preserved implementation outline](../sources/matomeru/docs/outline.md) describes `work.directories` and its local/remote boundary. These are owner-reported results, not runs performed by this documentation change.

The still-applicable acceptance is concentrated in [B-46](../todo/work.md#b-46): resolve current-cwd versus successful-launch frequency explicitly, preserve that explanation and launch-count integrity, and attach native-picker evidence if that platform behavior is used to close the item. The original note stays preserved even after the decision is resolved.
