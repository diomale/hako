# HAKO Architecture (Milestone 2)

## Layout

```text
hako/
├── config/hako.ini                 Non-secret runtime settings
├── requirements.txt                No third-party dependencies (M2)
├── scripts/hako                    Launcher: PYTHONPATH + python3 -m hako.main
├── src/hako/
│   ├── __init__.py                 Package version
│   ├── main.py                     argparse entry point, top-level error handling
│   ├── app.py                      Application lifecycle and main input loop
│   ├── cli/
│   │   ├── output.py               Terminal prompt/emit helpers
│   │   ├── commands.py             Command handlers and registry
│   │   └── router.py               Input parsing and dispatch
│   ├── core/
│   │   ├── config.py               INI loading/validation
│   │   ├── errors.py               HakoError / ConfigError
│   │   ├── lifecycle.py            SIGINT/SIGTERM handling
│   │   ├── logging.py              Redacting file logger setup
│   │   ├── models.py               Mode enum
│   │   ├── resources.py            Releaseable protocol for future resources
│   │   └── status.py               Status snapshot and formatting
│   ├── utils/paths.py              Dependency-free path helpers
│   ├── ai/                         Reserved: OpenRouter (M3), docstring only
│   ├── voice/                      Reserved: audio (deferred), docstring only
│   ├── memory/                     Reserved: SQLite memory (M8), docstring only
│   └── credentials/                Reserved: API key handling (M9), docstring only
└── tests/                          Mocked unit + architecture checks
```

## Dependency direction

```text
main -> app -> cli.router -> cli.commands -> core.status
                     |              |
                     |              -> core.models
                     -> cli.output -> core.models
                     -> core.errors

main -> core.config -> core.errors, core.models, utils.paths
main -> core.logging -> utils.paths
main -> core.lifecycle -> app (TYPE_CHECKING only)
```

Rules enforced by `tests/test_architecture.py`:

- Source imports are limited to the Python standard library and `hako`.
- No implemented module imports `hako.ai`, `hako.voice`, `hako.memory`, or
  `hako.credentials`.
- Reserved packages contain only a docstring.
- No network/credential helpers (`urlopen`, `getpass`, `HTTPConnection`, etc.)
  are present in `src/`.
- `requirements.txt` has no active dependency lines.
- The launcher contains no install/download commands.

## Lifecycle

1. `scripts/hako` sets `PYTHONPATH` to `src/` and runs `python3 -m hako.main`.
2. `main()` parses `--config` / `--version`, loads and validates configuration,
   configures logging, creates `Application`, and installs signal handlers.
3. `Application.run()` prints the banner and enters a prompt loop.
4. `CommandRouter.dispatch()` classifies each line:
   - slash input → registered command handler;
   - plain text → "chat not implemented" message (no backend call);
   - empty input → no output.
5. SIGINT/SIGTERM call `Application.stop()` and raise `KeyboardInterrupt`, which
   the loop catches for a clean exit. EOF and `/exit` also stop the loop.
6. `Application.close()` releases any registered resources and is idempotent.

## Extension points for later milestones

- **OpenRouter (M3):** add a client under `src/hako/ai/`; keep HTTP/TLS and
  free-model validation there. The CLI/status layer only displays results.
- **Text chat (M4):** attach a conversation engine to `Application`; use
  `config.history_limit` for bounding. Router stays unchanged.
- **Memory (M8):** add SQLite store under `src/hako/memory/`; register any
  long-lived handles via `Application.register_resource()`.
- **Credentials (M9):** add secure storage under `src/hako/credentials/`;
  never pass keys through argv or logs. The redaction filter already masks
  credential-shaped log text.
- **Voice (deferred):** add ASR/TTS adapters under `src/hako/voice/`; register
  audio resources so mode switches and shutdown release them safely.

No extension point is implemented as behaviour in Milestone 2; reserved
packages are intentionally empty.

## Security notes

- No API key is read, requested, stored, logged, or displayed.
- Logging uses `ssl`-independent stdlib file handling only; no network code.
- The redaction filter masks `sk-...`, `Bearer ...`, and `api_key: ...` shapes
  before messages reach the log handler.
- Tests use only synthetic strings for redaction checks; no real credential is
  involved.
