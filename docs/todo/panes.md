# Panes and reviews: remaining work

[Current behavior and target design](../outline/panes.md) · [Work and places](work.md)

The outline owns implemented [B-06 tabs](../outline/panes.md#b-06), [B-09 lifecycle](../outline/panes.md#b-09), [B-10 accordion](../outline/panes.md#b-10), [B-30 stale grouping](../outline/panes.md#b-30), and [B-38 nested rail](../outline/panes.md#b-38). They are not active construction items here. Recorded verification is historical evidence, not a check performed during this consolidation.

Implemented rail budgets [B-08](../outline/panes.md#b-08), page-level explicit tab memory [B-41](../outline/panes.md#b-41), and close-time completion [B-45](../outline/panes.md#b-45) now live in the outline.

<a id="panes-page-and-rail"></a>
## Panes page and left rail redesign

Status: open · source: [Panes page and rail target](../outline/panes.md#panes-page-and-rail)

- Make the Panes page the full global inventory of agents, terminals, and live Vim panes; retain pane search, grouping, review/working lifecycle, detail tabs, and live entry. Offer an explicit project filter on that page without carrying a project-page selection into it. Keep unassigned and stale rows discoverable.
- Prototype a slim persistent rail for page navigation, current-page state, and attention counts; move the full pane tree and its section budgets into Panes. Compare reachable review and working-agent actions at narrow and normal terminal widths before removing the current rail list. An attention indicator must take the person directly to the matching row.
- Migrate existing rail selection, keyboard shortcuts, live next/previous pane, and create-jump behavior to the Panes page or an explicit global shortcut. Do not silently drop B-06, B-08, B-09, B-10, B-38, or B-41 behavior during the cutover.

<a id="b-49"></a>
## B-49: Complete the noninterfering preview contract

Status: verification-pending · priority: p1 · size: not estimated

[B-06](../outline/panes.md#b-06) supplies actual Screen captures, output refresh, a periodic fallback, and scroll/follow controls. The [richer retained preview contract](../outline/panes.md#preview) needs evidence beyond that baseline. Do not replace a screen with transcript text when capture fails.

Remaining acceptance:

- Reserve the detail area's bottom, above help, for the selected terminal, agent, or running Vim screen. Shrink metadata first. Show an explicit too-small state rather than silently dropping the preview.
- For a normal terminal show bounded recent scrollback and the current screen, preserving spacing and supported colors. Identify truncation. For Neovim or another alternate-screen program show its current layout rather than earlier shell output, cropping without changing target dimensions. Identify cropping.
- Name session, window, and capture time. Distinguish loading, current, cached, empty, closed, unavailable, and too-small. A saved Vim session without a live window must not be opened just to obtain a preview.
- Acquire no size lease for a read-only subscription. Bound capture duration and retained bytes. Cancel obsolete requests and reject late results when target identity changes.
- Refresh only the selected target, preferably from events. Selection, filters, modals, scroll, keyboard focus, target focus, and target input remain unchanged. Preview causes no resize, review acknowledgement, or work-completion mutation.
- Render supported terminal styling without executing clipboard, title, hyperlink, or other terminal-control sequences. On a failure retain only the same target's prior screen, label it cached with age and error, and never present it as fresh/live.

Preserve all six source scenarios when recording acceptance on a uniquely named throwaway tuios daemon:

1. Print a unique terminal line, select the row, and observe it in the bottom preview without entering live mode.
2. Select an agent and observe actual terminal output even when transcript retrieval fails.
3. Open Neovim in an isolated pane and observe its alternate screen, not shell output from before launch.
4. Delay capture A, select B, and then finish A. B never shows A's output. Close B during capture and show closed/unavailable rather than a successful blank screen.
5. Compare target focus, input, and dimensions before and after selection/refresh. They do not change. Keep a form open while output arrives and retain its input and selection.
6. Exercise empty output, narrow/short layout, Unicode, truncation, disconnect/reconnect, and malicious escape sequences. Cached output has an age. A fresh capture clears only the preview error.

Source: [terminal preview requirements](../ui-state-visibility.md#terminal-preview), also retained in the [original shell design](../sources/znbu/docs/outline.md#71-tui--internalui). The general simultaneous-indicator work is separate in [Forms and shared UI](forms.md), not silently claimed by this preview item.

<a id="b-50"></a>
## B-50: Establish the complete host-qualified pane inventory

Status: verification-pending · priority: p2 · size: not estimated

The [current relay and shared snapshot](../outline/panes.md#daemon) are implemented. The original pane registry promises panes across registered hosts and host/session/window identity wherever a pane is stored. The audited remote path reads host sessions and host agents. Complete remote-terminal enumeration and every persisted identity boundary were not established by that evidence.

Remaining acceptance:

- List panes for the local daemon and registered hosts through the shared inventory, including remote terminals as well as agents. Identical session/window names on different hosts remain distinct.
- Preserve host-qualified identity through selection, assignment, queue receipts, presence/transcript access, capture, and live stream routing. A remote target must never accidentally use a local pane with the same raw name.
- Record unavailable/stale host state without calling a failed observation an empty successful inventory or pruning assignments from it. Prove recovery against the two-successful-snapshot pruning rule.
- Retain the implemented local-daemon relay and its same-connection `open-host-connection` behavior unless a separate architectural decision changes it. This item does not invent a direct per-host connection architecture.

The feature owner reports SSH remote-launch verification for commit `e4cf07a`. That proves a remote launch path, not enumeration of every remote terminal or every persistence boundary. These are reported owner results, not a new run by this consolidation. Sources: [original panes design](../sources/znbu/docs/outline.md#62-panes--live-pane-registry), `internal/daemon/{hosts,client,stream}.go`, and `internal/panes/hosts.go`. Host-aware Git and shared-place delivery remain [B-48](work.md#b-48) and [B-02](work.md#b-02).
