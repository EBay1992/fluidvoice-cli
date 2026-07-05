# fluidvoice-cli

Professional command-line companion for the [FluidVoice](https://github.com/altic-dev/FluidVoice) Local API on macOS.

Batch-transcribe media, export history, manage dictionaries, and integrate FluidVoice into scripts and CI — with structured JSON output, ffmpeg chunking for long files, and clear error messages.

## Prerequisites

1. **macOS** with [FluidVoice](https://altic.dev/fluid) installed
2. **Local API enabled**: FluidVoice → Settings → Advanced → Local API → Enable
3. **ffmpeg** (for files longer than ~4.5 minutes): `brew install ffmpeg`
4. **Python 3.11+**

## Install

```bash
pip install fluidvoice-cli
```

Development install:

```bash
cd fluidvoice-cli
pip install -e ".[dev]"
```

## Quick Start

```bash
# Preflight checks
fluidvoice doctor

# Check API health (exit 0 = healthy)
fluidvoice health

# Transcribe one file
fluidvoice transcribe lecture.mp4 -o lecture.txt

# Batch-transcribe a folder (skip existing outputs)
fluidvoice batch ./videos --pattern "*.mp4" --skip-existing

# Use FluidVoice history cache when available
fluidvoice batch ./course --use-history-cache --pattern "*.mp4"

# Machine-readable output for CI
fluidvoice batch ./videos --dry-run --json
```

## Commands

| Command | Description |
|---------|-------------|
| `fluidvoice health` | Check Local API status |
| `fluidvoice doctor` | Platform, ffmpeg, and API preflight |
| `fluidvoice transcribe FILE` | Transcribe a single file |
| `fluidvoice batch DIR` | Batch-transcribe media in a directory |
| `fluidvoice history list` | List transcription history |
| `fluidvoice history export DIR` | Export history to `.txt` files |
| `fluidvoice postprocess TEXT` | AI-enhance text via FluidVoice |
| `fluidvoice dict add-word WORD` | Add custom dictionary word |
| `fluidvoice dict list-words` | List custom words |
| `fluidvoice dict add-replacement A B` | Add replacement rule |
| `fluidvoice dict list-replacements` | List replacement rules |
| `fluidvoice config show` | Show resolved configuration |

### Global flags

- `--json` — JSON output for scripting/CI
- `--no-color` / `NO_COLOR` — disable colors
- `-v, --verbose` — verbose logs
- `--host`, `--port` — override API endpoint
- `--config PATH` — TOML config file
- `--chunk-seconds`, `--max-direct-seconds` — media chunking thresholds

## Configuration

Precedence: **CLI flags → environment variables → `~/.config/fluidvoice/config.toml` → defaults**

Example `~/.config/fluidvoice/config.toml`:

```toml
host = "127.0.0.1"
port = 47733
chunk_seconds = 240
max_direct_seconds = 280
timeout_seconds = 3600
```

Environment variables use the `FLUIDVOICE_` prefix (e.g. `FLUIDVOICE_PORT=47733`).

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User error |
| 2 | FluidVoice Local API not reachable |
| 3 | ffmpeg/ffprobe missing |
| 4 | Partial batch failure |

## API Compatibility

Tested against FluidVoice Local API v1:

| Endpoint | Used by |
|----------|---------|
| `GET /v1/health` | `health`, `doctor` |
| `POST /v1/transcribe` | `transcribe`, `batch` |
| `GET /v1/history` | `history` |
| `POST /v1/postprocess` | `postprocess` |
| `GET/POST /v1/dictionary/*` | `dict` |

See FluidVoice API docs: [api-reference](https://github.com/altic-dev/FluidVoice/tree/main/_autodocs/api-reference)

## Development

```bash
pip install -e ".[dev]"
ruff check src tests
pytest
fluidvoice --install-completion  # shell completion
```

## Collaboration with FluidVoice

This CLI is designed as a **standalone companion** that the FluidVoice team can adopt upstream. See [ADOPT.md](ADOPT.md) and [CONTRIBUTING.md](CONTRIBUTING.md).

## License

MIT — see [LICENSE](LICENSE). FluidVoice is GPLv3; this CLI is a separate tool that communicates via the documented Local API.
