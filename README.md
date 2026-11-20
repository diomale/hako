# HAKO

Lightweight, locally operated AI assistant foundation for Raspberry Pi 3 Model B
(ARMv7 / `armhf`, Raspberry Pi OS 13 Trixie, Python 3.13.5).

**Status:** Milestone 2 — Core CLI Foundation complete. Application code now
exists, but only for lifecycle, configuration, logging, command routing, and
status reporting.

**Immediate objective:** terminal-based AI text chat via OpenRouter. Audio work
(microphone, speaker, Vosk, speech recognition, TTS) is **DEFERRED** and is not
a gate for the text-chat foundation.

## Current scope

Implemented:

- `scripts/hako` launcher and `python3 -m hako.main` entry point
- INI configuration loading with validation and `HAKO_CONFIG` / `--config` overrides
- File logging with defensive credential redaction
- Graceful lifecycle: input loop, SIGINT/SIGTERM handling, EOF handling,
  resource-release hooks, idempotent shutdown
- CLI command routing for all documented commands
- Basic `/status` reporting

Not implemented yet (deliberate):

- OpenRouter client / HTTP requests / free-model selection (Milestone 3)
- Text chat engine and conversation history (Milestone 4)
- Persistent memory or SQLite (Milestone 8)
- Credential storage or API key prompts (Milestone 9)
- Voice, microphone, playback, speech recognition, TTS (deferred)
- Schedule / Google Calendar integration (not in current roadmap)

Later-milestone commands are routed but return explicit "not implemented"
messages; they perform no future work.

## Run

```sh
./scripts/hako
```

Inside the CLI, type `/help` for commands and `/exit` to quit. Plain text is
classified as chat input but is not sent anywhere in this milestone.

Alternative config path:

```sh
./scripts/hako --config /path/to/hako.ini
```

or:

```sh
HAKO_CONFIG=/path/to/hako.ini ./scripts/hako
```

No API key is needed, requested, read, or displayed in Milestone 2.

## Tests

```sh
PYTHONPATH=src python3 -m unittest discover -s tests -v
python3 -m compileall -q src tests
sh -n scripts/hako
```

HAKO has no third-party runtime dependencies in this milestone
(`requirements.txt` is comment-only).

## Documentation

- `documentation/milestone-01-compatibility-audit.md` — hardware/dependency audit
- `documentation/architecture.md` — module layout and boundaries
- `documentation/cli-reference.md` — command reference
- `documentation/milestone-02-core-cli-foundation.md` — Milestone 2 report

## Independence and deployment notes

HAKO is an independent project. It does not use, modify, or depend on TARS or
HAKONIWA. Target deployment path on the Pi is `/home/n01ce/hako`; the desktop
development mirror is `/home/diomale/hako`.

The Milestone 1 Pi-side HTTP/TLS reachability check remains pending. This
milestone was implemented and tested on the desktop with Python 3.13.5; no Pi
packages were installed and no Pi configuration was changed.
