# Milestone 2 Report — Core CLI Foundation

Date: 2026-11-20
Milestone: 2 — Core CLI Foundation only
Status: Complete on the development workspace; awaiting user review.

## 1. Scope and compliance

Implemented only the CLI/application foundation described in the master
specification:

- application entry point
- CLI interface and command routing
- configuration
- logging
- error types
- application lifecycle and graceful shutdown
- basic status reporting
- modular package structure with reserved placeholders

Explicitly **not** implemented:

- OpenRouter client, HTTP requests, free-model selection, retries/cooldown
- Text chat engine or conversation storage
- Persistent memory / SQLite
- Credential storage, hidden prompts, environment key precedence
- Voice, microphone, audio playback, Vosk, eSpeak/Piper, VAD
- Schedule integration or Google Calendar
- Any audio live test

Restrictions observed:

- No packages installed on the Pi or desktop.
- No Raspberry Pi system configuration changed.
- No live API requests made.
- No API key requested, read, displayed, logged, or stored.
- No old TARS/HAKONIWA code used or modified.
- No additional milestone behaviour implemented.

## 2. Files created

### Source and launcher

| File | Purpose |
|---|---|
| `scripts/hako` | Executable launcher; adds `src/` to `PYTHONPATH` and runs `python3 -m hako.main` |
| `src/hako/__init__.py` | Package version `0.2.0` |
| `src/hako/main.py` | argparse entry point, config/logging setup, top-level error handling |
| `src/hako/app.py` | Application lifecycle, input loop, mode state, resource-release hooks, shutdown |
| `src/hako/cli/output.py` | Prompt, message, error, and banner output helpers |
| `src/hako/cli/commands.py` | Command handlers and command registry; later-milestone placeholders |
| `src/hako/cli/router.py` | Slash-command parsing and dispatch; plain-text classification |
| `src/hako/core/config.py` | INI config loading/validation; `HAKO_CONFIG` support |
| `src/hako/core/errors.py` | `HakoError`, `ConfigError` |
| `src/hako/core/lifecycle.py` | SIGINT/SIGTERM handling |
| `src/hako/core/logging.py` | Rotating file logger with credential redaction |
| `src/hako/core/models.py` | `Mode` enum (`chat`, `talk`) |
| `src/hako/core/resources.py` | `Releaseable` protocol for future resources |
| `src/hako/core/status.py` | Status snapshot and terminal formatting |
| `src/hako/utils/paths.py` | Project-root and path helpers |
| `src/hako/utils/__init__.py` | Utils package marker |

Reserved packages (docstring only, no behaviour):

- `src/hako/ai/__init__.py`
- `src/hako/voice/__init__.py`
- `src/hako/memory/__init__.py`
- `src/hako/credentials/__init__.py`

### Configuration and data placeholders

| File | Purpose |
|---|---|
| `config/hako.ini` | Non-secret default settings |
| `config/README.md` | Configuration key reference |
| `requirements.txt` | Comment-only; no runtime dependencies in M2 |
| `data/.gitkeep` | Reserved for future local data |
| `logs/.gitkeep` | Reserved for runtime logs |
| `models/.gitkeep` | Reserved for deferred speech models |

### Tests

| File | Coverage |
|---|---|
| `tests/helpers.py` | Shared config factory |
| `tests/test_config.py` | Valid config, env override, invalid values, version match |
| `tests/test_logging.py` | Redaction filter, file logging |
| `tests/test_cli.py` | Help/status routing, placeholders, no-prompt API key checks, unknown commands |
| `tests/test_app.py` | Run loop, EOF/exit/stop, signal handling, resource release, idempotent close |
| `tests/test_architecture.py` | Imports, reserved-package emptiness, no network helpers, launcher/requirements checks |

### Documentation

| File | Purpose |
|---|---|
| `documentation/architecture.md` | Module layout, dependency direction, lifecycle, extension points |
| `documentation/cli-reference.md` | Command and config reference |
| `documentation/milestone-02-core-cli-foundation.md` | This report |

## 3. Files changed

- `README.md` — updated from Milestone 1 audit status to Milestone 2 CLI
  foundation status, with current scope, run/test commands, and documentation
  links.

The Milestone 1 audit report and its helper scripts were left unchanged.

## 4. Tests performed and results

All commands were run in `/home/diomale/hako` on the Parrot development
desktop with Python 3.13.5. No Pi commands were run.

### 4.1 Automated unit and architecture tests

Command:

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

Final result:

```text
Ran 34 tests in 0.035s
OK
```

Breakdown:

| Test module | Tests | Result |
|---|---:|---|
| `test_app.py` | 8 | OK |
| `test_architecture.py` | 7 | OK |
| `test_cli.py` | 9 | OK |
| `test_config.py` | 8 | OK |
| `test_logging.py` | 2 | OK |

Notable assertions:

- `/apikey set` and `/apikey remove` do not call `getpass.getpass`.
- `/status` does not print credential-like strings and states that key status
  was not queried.
- Plain text is not forwarded to any backend.
- Reserved packages contain docstrings only.
- `src/` contains no network or credential helper calls.
- Mode switches and shutdown release registered resources exactly once.
- SIGINT/SIGTERM handlers request shutdown and interrupt the input loop.

An initial test run exposed two defects: `logging.handlers` was not imported
explicitly, and a pre-stopped application reset its stop flag and consumed
input. Both were fixed and the final run above is clean.

### 4.2 Syntax checks

Commands:

```sh
python3 -m compileall -q src tests
sh -n scripts/hako
```

Result: both passed.

### 4.3 Import checks

Command:

```sh
PYTHONPATH=src python3 -c "import hako.main, hako.app; print('imports OK')"
```

Result: `imports OK`.

A broader import check of all core/CLI modules also passed.

### 4.4 Offline launcher smoke test

A temporary config file in `/tmp/opencode` was used so no project log file was
created. The launcher was fed `/help`, `/status`, and `/exit` via stdin.

Result:

- banner printed
- help listed all 14 documented command forms
- `/status` reported `CLI foundation: READY`, `OpenRouter client: PLANNED`,
  and `key status not queried`
- `/exit` terminated cleanly
- log file was created at the configured temporary path

No network access occurred.

## 5. Architecture checks

`tests/test_architecture.py` enforces the Milestone 2 boundary:

- Allowed imports: standard library modules used by the code plus `hako`.
- Forbidden local imports: `hako.ai`, `hako.voice`, `hako.memory`,
  `hako.credentials`.
- Forbidden network/credential attributes: `urlopen`, `urlretrieve`,
  `HTTPConnection`, `HTTPSConnection`, `create_connection`, `getpass`.
- Reserved packages must contain only a docstring.
- Launcher must not contain `pip`, `apt`, `curl`, `wget`, or `install`.
- `requirements.txt` must have no active dependency lines.

All checks passed.

## 6. Known limitations

1. The Pi was not accessed in this milestone. SSH key auth remained denied in
   the last check, so the design is desktop-verified only, not Pi-verified.
2. `/status` reports the host platform (`Linux / x86_64` on the desktop). On
   the Pi it will report the Pi's `platform.machine()` value, expected
   `armv7l`.
3. SIGTERM handling raises `KeyboardInterrupt` to interrupt the input loop;
   this is adequate for the terminal foundation but more sophisticated
   signal-driven resource cleanup can be added with real services later.
4. No conversation history exists despite `history_limit` being present in
   config; it is a reserved setting for Milestone 4.
5. Resource-release hooks are registered by nothing in Milestone 2; the
   protocol is an extension point, not active audio behaviour.
6. Configuration errors are printed to stdout via `emit_error`; this is
   acceptable for the CLI foundation but could be moved to stderr later.
7. The Milestone 1 public-endpoint/Pi TLS check is still pending on-device
   confirmation.

## 7. Next steps (not performed)

After approval:

1. Milestone 3 — OpenRouter client with stdlib HTTPS, dynamic free-model
   validation, timeouts, retry/cooldown, and redacted error handling.
2. Execute the Milestone 1 section 8A Pi TLS check, or authorize SSH key
   access, so the Pi path can be verified before live API testing.
3. Later, after text chat is working: reconsider audio milestones separately;
   audio remains DEFERRED.

Do not treat any later-milestone placeholder output as functioning behaviour.
