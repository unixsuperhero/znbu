# Plan: vps2 as a second development host

Status: unfinished, tracked by [B-73](../todo/delivery.md#b-73). [Delivery context](../outline/delivery.md#vpsplan). Written 2026-10-19; the [preserved original](../sources/matomeru/docs/plans/vps2-dev-host.md) keeps all original wording and verification proposals.

Goal: at least one agent thread does day-to-day Matomeru development on vps2, a Linux host reached by SSH alias. The Mac retains macOS-specific work and final platform acceptance. Linux results never prove macOS behavior. This consolidation ran no plan acceptance.

## Recorded baseline

The original plan records Claude 2.1.303 and gh logged in, OMP 18.10.0, Go 1.27.1, Bun 1.4.2 and Neovim 0.11. Recorded checkout/hub paths are `/root/proj/redeck-astra` and `/root/proj/redeck-astra.git`; the Mac remote is vps2, the Linux checkout's origin is the hub. These historical names do not rename the Matomeru module. The snapshot runner creates isolated run.* trees rather than using the development checkout.

The host daemon supports development sessions; verification uses only unique throwaway daemons, never that host daemon. The private Mac notes hold background on the shared-auth idea. Existing remote suite logs and the protocol in implementation AGENTS.md establish a baseline, not every acceptance below.

## Steps and dependencies

Keep the seven original steps. Run them in order unless a step is explicitly independent. Each step remains open until its own evidence is recorded, even when related infrastructure already exists.

<a id="linuxfallbacks"></a>
### 1. Linux fallbacks for context copy, open and open-with

Current source `internal/context/context.go` still looks up pbcopy and uses macOS open arguments. Notifications in reminders and the native picker already have OS-specific behavior; those do not fix context actions.

```js
copy = { darwin:"pbcopy", linux:["wl-copy", "xclip -selection clipboard", "xsel --clipboard --input"] }
// Linux chooses the first installed tool on PATH.
open = { darwin:"open [-a App] -- target", linux:"xdg-open -- target" }
// Linux open-with executes the explicit application directly.
```

Retain literal argument passing, not shell interpolation. Preserve the error shape `clipboard copy requires ... on PATH` and existing fixtures that shim pbcopy/open. Acceptance requires Linux copy/open/open-with behavior plus unchanged Mac clipboard/open-argument checks. The original verification proposal was `scripts/verify-vps.sh go test ./internal/context/...`, `scripts/verify-vps.sh bash scripts/e2e.sh` and Mac `e2e_scenarios.py` clipboard/open checks. Those are preserved historical proposals, not commands run here or authorization for local checks/new unit tests. Current project policy governs the eventual checks.

<a id="branchsync"></a>
### 2. Branch and sync protocol

One branch per host per task; never edit one branch on both hosts simultaneously. The documented protocol is Mac `git push vps2 <branch>`, Linux fetch from origin and check out that branch. Reverse direction is Linux push origin and Mac fetch vps2. Main is fast-forward only. Commands here describe the planned workflow, not operations performed during consolidation.

The Mac continues to verify through scripts/verify-vps.sh. The Linux agent runs scripts/e2e-all.sh directly in its checkout with MTM_E2E_TMP=/root/vtmp. Acceptance is one recorded round trip: push a branch from Mac, add one Linux commit, pull it back, and show both commits in `git log --oneline -3`. Existing documentation alone does not prove that round trip.

<a id="firstthread"></a>
### 3. First real agent thread on vps2

After step 2, start a new development session on the host daemon, originally `tuios new -s mtm-dev`, in the recorded checkout on its own branch. Read the same AGENTS.md. Coordinate with the Mac thread through cross-host tuios mail; the original record says tuios hosts test vps2 already works. The current permitted model/login rules override the old plan's available-tool list.

The former one-at-a-time PTY protocol is withdrawn. Independent snapshot runs may overlap; report contention with evidence. Acceptance is one small task completed through edit, verification, commit and hub push, with the user attached at least once. The original gate included go test plus end-to-end verification; retain that provenance without introducing new unit tests or claiming it ran here. Historical overnight worker logs do not by themselves establish user attachment or this complete gate.

<a id="concurrency"></a>
### 4. Measure concurrency

Independent of step 3; depends on step 2. Historical observation: two overlapping full suites drove load beyond the core count and PTY render waits failed; memory was not the limit. This is a reported observation, not a fresh measurement.

Run two full suites concurrently, one snapshot runner and one Linux checkout. Record uptime load and exactly which PTY checks time out. If only PTY work fails, adjust that workload, such as bounded longer render waits or a PTY-only lock, not a host-wide lock. Acceptance is a written result in this plan's evidence log with load numbers and the decision. [B-39](../todo/delivery.md#b-39) separately owns the approximately four-worker runner and timing target.

<a id="orphansweep"></a>
### 5. Orphan sweep after timeout force-kill

Independent. scripts/e2e-run.sh has an EXIT trap for its named daemon, but `timeout --kill-after=15s` may SIGKILL the parent before cleanup. The original observation is an orphan `de<random>` daemon and temporary directory.

Add a sweep at the beginning of the remote verify block and e2e-all. It may kill only a tuios server whose name starts de and whose socket directory belongs to a dead mtm-e2e.* temporary directory. A prefix alone is insufficient ownership evidence. Never touch the unnamed host daemon or live test processes. Acceptance: force-kill a throwaway suite, run the sweep and establish with process inspection that no owned `tuios --server de*` orphan remains. No force-kill or sweep was performed here.

<a id="flakes"></a>
### 6. Known flakes

Independent; any order. Retain each original failure and separate acceptance:

- e2e-daemon.sh: `transcript lost structured authorization failure`, reported in two of four vps2 runs.
- e2e-setup.sh turn capture: after l, a single read can see no text on a slow render and page past the answer. Wait for DETAIL / FOCUSED and answer text before paging; after each PageDown wait for the screen to change.
- Outline shared_navigation: `previous section selects previous group start` times out under full-suite load but passes targeted.

Acceptance is five consecutive green vps2 runs of each affected suite, with logs. A later unrelated green suite or owner's feature check is not evidence for this repetition gate. [B-40](../todo/delivery.md#b-40) governs targeted iteration versus the one final full run; do not conflate deliberate flake measurement with a general full-suite-per-item policy.

<a id="authchoice"></a>
### 7. Shared auth proxy versus per-machine logins

Per-machine login worked at the recorded baseline. Keep it as the default. A shared proxy on the Mac could avoid new logins for future machines but carries the policy/terms concern from the private notes. Revisit only if a third machine appears; do not build or configure a proxy as part of this plan consolidation. Broader auth/routing ideas remain in [ecosystem](../outline/ecosystem.md) and [ecosystem todo](../todo/ecosystem.md).

## Evidence log

- 2026-10-19 original plan records tooling, hub and login complete, with no step-specific completion log.
- Consolidation inspected context source and runner declarations only. Context Linux fallbacks remain absent; no seven-step runtime acceptance, branch round trip, load measurement, orphan sweep, flake repetition or auth change was performed.
