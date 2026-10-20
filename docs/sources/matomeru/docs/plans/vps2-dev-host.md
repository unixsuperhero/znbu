# Plan: vps2 as a second development host

Written 2026-10-19. Goal: at least one agent thread does its day-to-day mtm work on
vps2 (a Linux host reached by SSH alias), while the Mac keeps the
macOS-only paths and the final word on anything macOS-specific. Linux results do not
prove macOS behavior; both platforms are supported.

## Current state

```js
vps2 = {
  tooling:   ["claude 2.1.303 (logged in)", "gh (logged in)", "omp 18.10.0", "go 1.27.1", "bun 1.4.2", "nvim 0.11"],
  repo:      { hub: "/root/proj/redeck-astra.git", checkout: "/root/proj/redeck-astra (origin = hub)" },
  mac:       { remote: "vps2 -> ssh://vps2/root/proj/redeck-astra.git" },
  runner:    "scripts/verify-vps.sh rsyncs the Mac tree into runs/run.* and runs there",
  daemons:   "host tuios daemon for dev work; uniquely named throwaway daemons only inside the e2e suites",
}
```

Background on the shared auth-proxy idea is in the user's private notes on the Mac.

## Steps

Each step names its verification. Do them in order unless marked independent.

### 1. Linux fallbacks for the two remaining macOS-only context actions

`internal/context/context.go` hardcodes `pbcopy` for `copy` and `open` for `open` /
`open-with`. Notifications (`internal/reminders/reminders.go`) and the picker
(`internal/picker/picker.go`) already branch on the OS.

```js
copy = { darwin: "pbcopy", linux: ["wl-copy", "xclip -selection clipboard", "xsel --clipboard --input"] }  // first found on PATH
open = { darwin: "open [-a App] -- target", linux: "xdg-open -- target" }                                // open-with on linux: run the named application directly
```

- Keep the error text pattern ("clipboard copy requires ... on PATH") so the e2e
  fixtures that shim `pbcopy` and `open` keep passing on both hosts.
- Verify: `scripts/verify-vps.sh go test ./internal/context/...` and
  `scripts/verify-vps.sh bash scripts/e2e.sh` green; on the Mac, the existing
  `e2e_scenarios.py` clipboard and open-args checks unchanged.

### 2. Branch and sync protocol between the two checkouts

- One branch per host per task. Never edit the same branch on both hosts at once.
- Mac: `git push vps2 <branch>`; vps2: `git fetch origin && git checkout <branch>`.
  Reverse direction is `git push origin <branch>` on vps2 and `git fetch vps2` on the
  Mac. `main` is fast-forward only.
- The runner (`scripts/verify-vps.sh`) stays the way the Mac verifies; the vps2 agent
  runs `scripts/e2e-all.sh` directly in its checkout with `MTM_E2E_TMP=/root/vtmp`.
- Verify: a round trip (branch pushed from the Mac, one commit added on vps2, pulled
  back) lands cleanly with `git log --oneline -3` showing both commits.

### 3. Launch the first agent thread on vps2

- Start it in a new tuios session on the host daemon (`tuios new -s mtm-dev`), in
  `/root/proj/redeck-astra`, on its own branch from step 2.
- It reads the same `AGENTS.md`; coordinate with the Mac agent by tuios mail across
  hosts (`tuios hosts test vps2` already works). The earlier one-at-a-time PTY suite
  protocol is withdrawn by the VPS-first rule: run concurrently, report contention
  with evidence.
- Verify: the thread completes one small task end to end (edit, `go test`, e2e
  suite, commit, push to hub) with the user attached to the session at least once.

### 4. Measure concurrency on vps2 (independent of 3, needs 2)

Known evidence: two overlapping full suites once drove the load well past the core
count and PTY render waits failed. Memory was never the limit.

- Run two full suites at once, one from the runner and one from the vps2 checkout.
  Record `uptime` load and which, if any, PTY checks time out.
- If only PTY suites fail, narrow that workload (for example longer render waits or a
  PTY-only lock), not a host-wide lock.
- Verify: a written result in this file's log section with load numbers and the
  decision.

### 5. Orphan sweep after a timeout kill (independent)

`scripts/e2e-run.sh` kills its own named daemon in an EXIT trap. A run killed by
`timeout --kill-after=15s` in `scripts/verify-vps.sh` gets SIGKILL, skips the trap,
and leaves a `de<random>` daemon and its temp directory behind.

- Add a sweep at the start of `verify-vps.sh`'s remote block and `e2e-all.sh`: list
  tuios servers whose name starts with `de` and whose socket directory is under a
  dead `mtm-e2e.*` temp dir, and `kill-server` only those. Never touch the unnamed
  host daemon.
- Verify: start a suite, SIGKILL it, run the sweep, `ps` shows no leftover `tuios
  --server de*` process.

### 6. Known flakes to burn down (independent, any order)

- `e2e-daemon.sh`: "transcript lost structured authorization failure", 2 of 4 runs
  on vps2.
- `e2e-setup.sh` turn-capture: after `l` the loop reads the screen once, sees no text
  on a slow render, pages past the answer. Fix shape: expect `DETAIL / FOCUSED` and
  the answer text before paging, and wait for a screen change after each PageDown.
- outline `shared_navigation`: "previous section selects previous group start"
  times out under full-suite load, passes targeted.
- Verify each: 5 consecutive green runs on vps2 of the affected suite.

### 7. Decision: shared auth proxy or per-machine logins

Per-machine login works today (vps2 is logged in). A shared auth proxy on the Mac
would remove logins for future boxes, at the cost of
the terms-of-service grey area described in the notes. Default: keep per-machine
logins; revisit only if a third machine appears.

## Log

- 2026-10-19: tooling, hub repo and login done; plan written.
