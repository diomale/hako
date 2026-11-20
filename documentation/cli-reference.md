# HAKO CLI Reference (Milestone 2)

Start with:

```sh
./scripts/hako
```

The prompt shows the active mode, e.g. `hako[chat]>`.

## Commands

| Command | Milestone 2 behaviour |
|---|---|
| `/help` | Lists all commands and their intended purpose. |
| `/status` | Shows version, active mode, Python/platform/architecture, config/log paths, and subsystem states. |
| `/chat` | Selects `chat` mode; no chat engine is attached yet. |
| `/talk` | Selects `talk` mode; no microphone or speaker is opened. |
| `/clear` | Reports that no conversation history exists yet. |
| `/memory` | Placeholder: memory status is reserved for Milestone 8. |
| `/memories` | Placeholder: memory listing is reserved for Milestone 8. |
| `/remember <info>` | Placeholder: saving memories is reserved for Milestone 8. |
| `/forget <ID>` | Placeholder: deleting memories is reserved for Milestone 8. |
| `/clear-memory` | Placeholder: clearing memories is reserved for Milestone 8. |
| `/apikey` | Reports that credential status is reserved for Milestone 9; no key status is checked. |
| `/apikey set` | Placeholder: no hidden prompt is shown and no key is read. |
| `/apikey remove` | Placeholder: no credentials are touched. |
| `/exit` | Requests a clean shutdown. |

Input without a leading `/` is classified as chat text and receives a
"chat is not implemented in Milestone 2" message. Nothing is sent to any
network service.

Empty input produces no output.

## Status fields

`/status` reports:

- app name, version, description
- active mode (`chat` or `talk`)
- Python version
- platform and machine architecture
- active configuration path
- active log file path
- subsystem states: `READY`, `PLANNED`, `DEFERRED`, or `NOT IN SCOPE`

Credential status is deliberately not queried; the status output states
"key status not queried".

## Exit behaviour

- `/exit`, EOF (Ctrl-D), SIGINT (Ctrl-C), and SIGTERM all stop the loop cleanly.
- Registered resources (none in Milestone 2) are released on mode switches and
  on shutdown.
- The launcher exits with code `0` on a normal session and `2` on a
  configuration error.

## Configuration options

```sh
./scripts/hako --config /path/to/hako.ini
HAKO_CONFIG=/path/to/hako.ini ./scripts/hako
```

`--config` takes precedence over `HAKO_CONFIG`; if neither is set,
`config/hako.ini` in the project root is used. See `config/README.md`.
