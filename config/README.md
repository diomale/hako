# Configuration

`hako.ini` contains non-secret runtime settings for HAKO.

| Section | Key | Purpose |
|---|---|---|
| `app` | `name` | Display name |
| `app` | `version` | Must match `hako.__version__` |
| `app` | `description` | Short banner text |
| `app` | `default_mode` | `chat` or `talk` at startup |
| `runtime` | `log_level` | `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL` |
| `runtime` | `log_file` | Log path; relative paths resolve from the project root |
| `runtime` | `history_limit` | Reserved bound for future conversation history |

The config path can be overridden with `HAKO_CONFIG` or `--config`. No API key
or other credential belongs in this file. Credential handling is reserved for
Milestone 9.
