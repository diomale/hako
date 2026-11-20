# Milestone 1 — Compatibility Audit (HAKO), revised for text-first priority

Date: 2026-11-20
Revision: 2 — priorities updated by explicit user decision.

## 0. Priority revision (authoritative for this milestone)

The user has explicitly decided that **audio is not a priority**. The immediate
objective is a **working terminal-based AI assistant using OpenRouter**.

Therefore:

| Item | Status |
|---|---|
| Terminal text chat via OpenRouter | **PRIMARY OBJECTIVE** |
| Python 3.13.5 / ARMv7 / `armhf` HTTP + TLS compatibility | **IN SCOPE** |
| OpenRouter public endpoint reachability without an API key | **IN SCOPE** |
| Free-model validation and selection strategy | **IN SCOPE** |
| Credential secrecy (no keys in source, logs, reports, output) | **IN SCOPE** |
| Raspberry Pi 3B hardware/OS audit results | **KEPT — see section 1** |
| Microphone detection | **DEFERRED** |
| Speaker playback / 3.5 mm jack testing | **DEFERRED** |
| Vosk installation and import test | **DEFERRED** |
| Speech recognition / live transcription test | **DEFERRED** |
| TTS installation and playback test | **DEFERRED** |
| Audio feedback / mic gating design | **DEFERRED** |

None of the deferred audio items are required to start the text-chat
foundation. `pi-audit-commands.sh` and `pi-live-tests-manual.md` remain in the
repository as reference material, but their audio sections are not gates for
Milestone 2.

This revision performed **no package installation, no system configuration
changes, no model downloads for the Pi, and no application-code
implementation**. All checks were read-only metadata inspection, public HTTP
requests without credentials, and documentation updates.

## 1. Hardware and operating system audit (retained)

### 1.1 Pi reachability history

Initial audit (revision 1):

| Check | Result |
|---|---|
| `getent hosts hakoniwa` | `192.168.123.47` (`hakoniwa.bbrouter`) |
| `ping 192.168.123.47` | 100% packet loss |
| ARP neighbour `.47` | `FAILED` |
| TCP port 22 on `.47` | unreachable (`No route to host`) |
| ARP sweep `192.168.123.0/24` | router `.1`, `.35`, desktop `.45` only |

Current re-check for this revision:

| Check | Result |
|---|---|
| Port 22 on `192.168.123.47` | **OPEN** |
| `ssh -o BatchMode=yes n01ce@hakoniwa` | `Permission denied (publickey,password)` |
| SSH agent identities | none |
| `~/.ssh/config` | absent |

Conclusion: the Pi is now online, but non-interactive key-based SSH is not
authorized for this desktop. **No new on-device measurements were obtained.**
If you want me to run read-only checks directly, authorize a public key or
paste the output of the commands in section 8. No password or API key should be
shared in this chat.

### 1.2 Expected Pi profile (still pending on-device confirmation)

| Item | Expected | Verified on device? |
|---|---|---|
| Board | Raspberry Pi 3 Model B Rev 1.2 | No |
| CPU | BCM2837, 4× ARM Cortex-A53 | No |
| Architecture | `armv7l` / `armhf` (32-bit) | No |
| RAM | 1 GB (shared with GPU) | No |
| OS | Raspberry Pi OS 13 Trixie, 32-bit | No |
| Kernel | Linux ARMv7 | No |
| Python | 3.13.5 | No |
| Hostname / user / target path | `hakoniwa` / `n01ce` / `/home/n01ce/hako` | No |
| USB mic / 3.5 mm jack | present | **DEFERRED — not required** |

## 2. Python 3.13.5 ARMv7 / armhf compatibility for HTTP + TLS

This is now the critical compatibility path. Evidence from Debian Trixie
`armhf` package metadata:

| Component | Debian Trixie armhf version | Relevance |
|---|---|---|
| `python3-minimal` | `3.13.5-1` | Base interpreter |
| `python3.13` | `3.13.5-2+deb13u5` | Full interpreter |
| `libpython3.13-minimal` | `3.13.5-2+deb13u5` | Contains `_ssl.cpython-313-arm-linux-gnueabihf.so`, `ssl.py`, `urllib/request.py` |
| `libssl3t64` | `3.5.7-1~deb13u3` | OpenSSL runtime used by `_ssl` (dependency confirmed) |
| `ca-certificates` | `20250419+deb13u1` | Default CA trust store for certificate validation |
| `python3-requests` | `2.32.3+dfsg-5+deb13u1` | Optional high-level HTTP client |
| `python3-urllib3` | `2.3.0-3+deb13u2` | `requests` dependency |
| `python3-certifi` | `2025.1.31+ds-1` | Optional CA bundle for `requests` |
| `python3-httpx` | `0.28.1-1` | Available but unnecessary (more dependencies) |

Findings:

- Python's `ssl`, `http.client`, and `urllib.request` are part of the
  interpreter standard library on `armhf`; no architecture-specific wheel is
  needed. The `_ssl` extension is built for `cpython-313-arm-linux-gnueabihf`.
- `ssl.create_default_context()` provides `CERT_REQUIRED` and hostname
  verification by default; on the development Python 3.13.5 it reports
  `verify_mode=2`, `check_hostname=True`, with TLS 1.2 and TLS 1.3 available.
- `requests` is pure Python and available as a native Debian armhf package
  with `urllib3` and `certifi`. It introduces no unknown ARM binary.
- Recommendation: use **stdlib `urllib.request` + `ssl.create_default_context()`**
  as the first HTTP client. If friendlier error handling is needed later,
  `python3-requests` is an acceptable armhf-native alternative. Avoid adding
  `httpx` unless a concrete need appears.
- Certificate validation must remain enabled. Do not set
  `CERT_NONE` or `check_hostname=False` as a workaround.

## 3. OpenRouter public endpoint reachability (no API key)

Verified from the Parrot desktop (Python 3.13.5, OpenSSL 3.5.9), with **no
credential of any kind supplied**:

| Check | Result |
|---|---|
| `GET https://openrouter.ai/api/v1/models` | HTTP **200**, `Content-Type: application/json`, server Cloudflare |
| TLS negotiated | TLSv1.3, cipher `TLS_AES_256_GCM_SHA384` |
| Certificate | CN `openrouter.ai`; issuer Google Trust Services `WE1`; valid `2026-11-18` → `2027-02-16` |
| Default CA validation | succeeded with hostname checking enabled |
| Cache headers | `Cache-Control: public, max-age=120, ...` |
| Rate-limit headers on `/models` | none observed |

This proves the **public model catalog endpoint requires no API key** and can
be used for pre-flight connectivity and free-model validation.

Not performed, by design:

- No request to `/api/v1/chat/completions` (would require a key).
- No API key was requested, read, logged, displayed, or stored.
- No attempt was made to inspect the user's credentials.

The Pi's reachability to this endpoint is **still unverified** because SSH is
not authorized. Section 8 gives an exact no-key command for you to run on the
Pi.

## 4. Reliable free-model selection strategy

The catalog is dynamic: the first check returned 477 models, a later check
returned 478, and 15 had numerically zero `prompt` and `completion` pricing.
A model must never be assumed free permanently.

Observed zero-pricing models at check time (not a permanent allowlist):

- `liquid/lfm-3-1.7b:free` — `text->text`, 262,144 context
- `nvidia/nemotron-3.5-lightning:free` — `text->text`, 1,000,000 context
- `recursive/flint-v1.0:free` — `text->text`, 262,144 context
- `inclusionai/ling-3.2-flash:free` — `text+image->text`
- `google/gemma-4-31b-it:free` — `text+image+video->text`
- `openrouter/free` — router, `text+image->text`
- plus other preview/multimodal entries

All observed free entries had empty extra pricing maps (no hidden nonzero
`web_search`, `image`, `audio`, or reasoning charges).

Mandatory strategy for the later implementation:

1. Fetch `GET /api/v1/models` at startup (or with a short TTL cache, e.g. 6 h)
   using verified TLS and **no API key**.
2. A candidate is eligible only if:
   - `pricing.prompt` and `pricing.completion` parse as numbers and equal `0`;
   - **all** numeric `pricing` values are zero (reject hidden extras);
   - `architecture.input_modalities` includes `text` and
     `architecture.output_modalities` includes `text`;
   - id does not indicate `:batch`;
   - the model is currently present in the freshly fetched catalog.
3. Treat the `:free` suffix as a useful hint, **not** as proof by itself.
4. Prefer small text-only candidates first for the Pi (e.g. the currently
   observed `liquid/lfm-3-1.7b:free`), then other verified text-capable free
   models, then the `openrouter/free` router.
5. Prefer stable ids over `:preview` when both are verified.
6. On timeout, HTTP 429, or persistent model failure: apply per-model cooldown
   and rotate to the next **verified** free candidate. Never fall back to a
   paid model, never silently switch pricing classes.
7. If no verified free model exists, fail closed with a clear terminal
   message and send no chat request.
8. Show the active model via `/status`.
9. Re-validate on every process start; do not persist a model as permanently
   free.

## 5. Security and credential handling

- API keys are **not** used in this audit and appear nowhere in these files.
- No key in source code, logs, reports, tests, `argv`, or terminal output.
- Future design (Milestone 2/3): environment variable takes precedence over
  `~/.config/hako/credentials`; credential directory `0700`, file `0600`;
  hidden prompt for setting; explicit confirmation for removal; env vars must
  never be overwritten or removed; no fake/placeholder key.
- HTTP client must redact `Authorization` headers in all error paths and logs.
- Do not ask the user to paste a key into this chat.

## 6. Resource estimates, revised for text-only

Text-first HAKO has a much smaller footprint than the original audio plan:

| Component | Estimate |
|---|---|
| Python 3.13 + stdlib HTTP/SQLite on Pi | ~25–60 MB RSS |
| Catalog cache + bounded conversation state | <5 MB |
| **Text-chat foundation total** | **~30–70 MB RSS** |
| Deferred: Vosk small model | ~80–180 MB (not required now) |
| Deferred: Piper/eSpeak | ~5–350 MB (not required now) |

This comfortably fits the Pi 3B's 1 GB for the text objective. No speech model
will be loaded.

## 7. Revised risks and limitations

1. **No on-device confirmation yet** — SSH is open but key auth is denied; Pi
   TLS reachability and exact package versions remain unverified on hardware.
2. OpenRouter's free catalog changes; strategy in section 4 must be dynamic.
3. Preview and router models may be less stable than named stable models.
4. Chat endpoint behaviour (401/429 handling, timeouts) is untested because
   no key was used, as required.
5. Audio compatibility findings from revision 1 remain valid as background
   information, but all audio work is DEFERRED and is not a Milestone 2 gate.
6. No application code or automated tests exist yet.

## 8. Exact commands for the user

### 8A. Required Pi check for text-first Milestone 2 (read-only, no key)

Run this on the Pi and paste the output. It verifies Python, TLS, CA trust, and
OpenRouter's public endpoint without credentials:

```sh
python3 --version
python3 - <<'PY'
import json, ssl, urllib.request
ctx = ssl.create_default_context()
print('OpenSSL:', ssl.OPENSSL_VERSION)
print('verify_mode:', ctx.verify_mode, 'check_hostname:', ctx.check_hostname)
url = 'https://openrouter.ai/api/v1/models'
with urllib.request.urlopen(url, timeout=20, context=ctx) as r:
    print('HTTP status:', r.status)
    data = json.load(r)
def is_zero(v):
    try:
        return float(v) == 0.0
    except (TypeError, ValueError):
        return False
free = [m for m in data.get('data', [])
        if is_zero(m.get('pricing', {}).get('prompt'))
        and is_zero(m.get('pricing', {}).get('completion'))]
print('models:', len(data.get('data', [])), 'zero-priced:', len(free))
for m in free[:8]:
    print(' ', m['id'])
PY
```

Alternative one-line certificate check (`ssl_verify_result: 0` means OK):

```sh
curl -sS -o /dev/null -w 'http=%{http_code} ssl_verify=%{ssl_verify_result}\n' \
  https://openrouter.ai/api/v1/models
```

If you prefer direct read-only inspection over SSH, authorize an SSH public
key for `n01ce@hakoniwa`; do not share a password or API key in chat.

### 8B. Deferred audio checks

The commands in `pi-audit-commands.sh` and `pi-live-tests-manual.md` remain
available for a later audio milestone. They are **not required now** and must
not block progress on text chat.

## 9. Recommendation

**Proceed to Milestone 2 (Core Architecture / text-chat foundation) after the
section 8A Pi check passes.** The design is feasible: Python 3.13 on Trixie
`armhf` has working standard-library TLS with certificate validation, the
OpenRouter public catalog is reachable without a key from the development
machine, and free-model eligibility can be verified dynamically.

I will not claim the Pi works until the on-device TLS check is confirmed.
No packages will be installed, no configuration changed, and no application
code implemented until you approve the next milestone.
