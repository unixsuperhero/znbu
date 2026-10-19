# Prompts

Every prompt given to an agent building the deck from the outline, in the order sent. One file per prompt, frontmatter holds the metadata; `index.json` is the same list for programs.

## Types

- `00-init`: the first prompt a fresh agent gets with the outline
- `01-restart`: a fresh agent replacing a killed one, with the lesson added
- `02-steer`: a message sent while the agent's turn is active (mail; it reads it at its next turn start)
- `03-round`: a new task given to an agent that reported done

## Metadata

```js
Prompt = { seq, type, agent, harness_model, target: 'session / window', cwd, sent_at,
           delivery,                 // how it reached the pane
           agent_state_at_send,      // idle | working | done | needs_input
           steering_active_turn,     // true when sent into a turn already running
           notes }
```

## Index

| seq | type | agent | sent | state at send | steering | file |
|---|---|---|---|---|---|---|
| 1 | `00-init` | modular | 19:36 | idle (fresh pane) | no | [01-modular.md](00-init/01-modular.md) |
| 2 | `00-init` | redeck | 19:37 | needs_input (trust prompt) | no | [02-redeck.md](00-init/02-redeck.md) |
| 3 | `00-init` | astra | 19:37 | idle (fresh pane) | no | [03-astra.md](00-init/03-astra.md) |
| 4 | `01-restart` | redeck | 20:12 | idle (fresh pane) | no | [04-redeck.md](01-restart/04-redeck.md) |
| 5 | `02-steer` | modular | 20:26 | working (final suite run; it mailed done minutes later) | yes | [05-modular.md](02-steer/05-modular.md) |
| 6 | `02-steer` | redeck | 20:26 | working | yes | [06-redeck.md](02-steer/06-redeck.md) |
| 7 | `03-round` | astra | 20:31 | done (idle after round 1) | no | [07-astra.md](03-round/07-astra.md) |
