# Upstream adoption issue draft

Copy the body below when opening an issue on https://github.com/altic-dev/FluidVoice/issues

---

**Title:** Companion CLI for Local API — adoption discussion

## Summary

We've built **fluidvoice-cli**, a MIT-licensed companion CLI for the FluidVoice Local API. It targets batch transcription, history export, dictionary management, and CI-friendly `--json` output.

**Install (latest v0.1.2):**

```bash
pip install https://github.com/EBay1992/fluidvoice-cli/releases/download/v0.1.2/fluidvoice_cli-0.1.2-py3-none-any.whl
```

## Why this helps FluidVoice users

- **Batch workflows** — transcribe folders of course videos, podcasts, or meetings
- **Scripting** — exit codes and JSON output for automation
- **API documentation by example** — typed Python client with tests against `/v1/*` endpoints
- **Long media** — ffmpeg chunking for files beyond direct API limits

## Commands

```bash
fluidvoice doctor
fluidvoice batch ~/Videos --pattern "*.mp4" --use-history-cache
fluidvoice history export ./exports
```

## Proposed integration

1. Link from FluidVoice README under "Developer Tools"
2. Or vendor at `tools/fluidvoice-cli/` with shared maintainers

Full proposal: [ADOPT.md](https://github.com/EBay1992/fluidvoice-cli/blob/main/ADOPT.md)

Repo: https://github.com/EBay1992/fluidvoice-cli

## API endpoints used

- `GET /v1/health`
- `POST /v1/transcribe` (path and base64)
- `GET /v1/history`
- `POST /v1/postprocess`
- `GET/POST /v1/dictionary/*`

Happy to adjust to API changes and co-maintain. Feedback welcome.
