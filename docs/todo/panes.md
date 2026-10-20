# Panes and reviews: remaining work

[Current behavior and target design](../outline/panes.md) · [Work and places](work.md)

The outline owns implemented [B-06 tabs](../outline/panes.md#b-06), [B-09 lifecycle](../outline/panes.md#b-09), [B-10 accordion](../outline/panes.md#b-10), [B-30 stale grouping](../outline/panes.md#b-30), and [B-38 nested rail](../outline/panes.md#b-38). They are not active construction items here. Recorded verification is historical evidence, not a check performed during this consolidation.

<a id="b-08"></a>
## B-08: Budget rail height by section and compact resting rows

Status: open · priority: p1 · size: M

The three [lifecycle sections](../outline/panes.md#b-09) exist, but a single growing list is not independent height allocation. Keep the original intent that panes receive most rail space rather than allowing reviews to displace all useful panes.

Acceptance:

- Give each section a configurable percentage cap of usable rail height. A candidate default is `review:25,panes:60,working:15`; the exact default must retain a majority for panes. Section headings count against that section's share.
- Scroll each section within its allocation and show `+N more` or a visible scroll marker. Overflow cannot push the next section offscreen. Existing grouping/tree headings remain visible within the middle section's budget.
- Make resting rows one line. Selected or messaging rows use two. Write the rule for any other second-line case, such as stale rows, in the outline and apply it across pages. A second line must carry information absent from the first.
- With forty finished turns and three panes in a forty-row terminal, reviews occupy no more than their configured share and all three panes remain visible. Moving `j` within Review scrolls that section rather than expanding it.
- `mtm config init` emits the default section shares. Rendered layout acceptance checks both the percentage budget and one-line/two-line policy.

The original comparison also records tuios's duration-based resting-row fold and per-subagent group cap as relevant alternatives. They inform the policy; they do not establish Matomeru's implementation. Sources: [original B-08](../sources/znbu/docs/todo.md#b-08-rail-height-budget-sections-capped-by-percent-one-line-rows-panes-get-most-of-it) and [implementation-side copy](../sources/matomeru/docs/todo.md#b-08-rail-height-budget-sections-capped-by-percent-one-line-rows-panes-get-most-of-it). The code audit found lifecycle ordering, not percentage caps or independent scroll allocations.

<a id="b-41"></a>
## B-41: Keep the page's last explicitly chosen detail tab

Status: open · priority: p2 · size: not estimated

This changes [B-06's current per-pane memory](../outline/panes.md#b-06). It is not satisfied by restoring each row's previous tab. The last tab explicitly selected on the page remains active while navigating that page's rows.

Acceptance:

- Explicitly select a detail tab, move through several rows in the left list, and retain that tab. Do not reset to a default or restore a different per-row tab.
- Explicitly choose another tab, then keep that new choice on subsequent row navigation.
- Apply the same rule to every tabbed page, including Panes. Automatic row-specific choices must not override an explicit page-level choice.

Source: [original B-41](../sources/znbu/docs/todo.md#b-41-keep-the-last-explicitly-chosen-detail-tab-while-navigating-a-page) and [user request](../sources/hub/prompts/mtm-todo.md). The audited `paneTabs` map is keyed by selection identity and automatically remembers Turns for panes with unreviewed records; it does not implement this acceptance.

<a id="b-45"></a>
## B-45: Offer task or project completion when closing a pane

Status: open · priority: p2 · size: not estimated

[Current pane closure](../outline/panes.md#pane-closure-and-work-completion) observes lifecycle and prunes assignments. It does not mean the associated work is finished.

Acceptance:

- Closing an associated pane offers an explicit choice to mark its task or project done.
- Accepting updates the chosen task or project. Declining closes the pane without changing that owner's completion state.
- Closing a pane alone never silently implies completion.

Source: [original B-45](../sources/znbu/docs/todo.md#b-45-offer-task-or-project-completion-when-closing-its-pane) and [user request](../sources/hub/prompts/mtm-todo.md). Task/project mutations and pane-close observation exist separately; no completion-choice workflow was found in the audit.

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
