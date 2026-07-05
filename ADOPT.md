# Adoption Proposal for FluidVoice Maintainers

## Summary

**fluidvoice-cli** is a MIT-licensed companion CLI for the FluidVoice Local API. It provides batch transcription, history export, dictionary management, and CI-friendly JSON output — use cases that complement the macOS app's interactive dictation workflow.

## Why Adopt?

1. **Documented API surface** — The CLI encodes the Local API contract as typed Python client code with tests, making API changes visible in CI.
2. **Power-user workflows** — Course creators, podcasters, and developers need folder batch jobs, not one-file-at-a-time UI flows.
3. **No app coupling** — Separate package; communicates only via `http://127.0.0.1:47733/v1/`.
4. **Community onboarding** — `pip install fluidvoice-cli` lowers the barrier for developers evaluating FluidVoice.

## Proposed Integration Options

### Option A: Link from FluidVoice README (lowest friction)

Add to FluidVoice README under "Developer Tools":

```markdown
### Companion CLI
[fluidvoice-cli](https://pypi.org/project/fluidvoice-cli/) — batch transcription and scripting via the Local API.
```

### Option B: Vendor into FluidVoice repo

```
FluidVoice/
  tools/
    fluidvoice-cli/   # this package, co-maintained
```

Release tags can track FluidVoice versions (e.g. `cli-v0.1.0+fluid-1.6.0`).

### Option C: Official org repo

Create `altic-dev/fluidvoice-cli` as a sibling repo with shared maintainers.

## Maintenance Model

| Area | Owner |
|------|-------|
| Local API contract | FluidVoice team |
| CLI features & releases | CLI maintainers (community + Fluid) |
| Breaking API changes | FluidVoice announces; CLI updates within one release cycle |

## What We Need from Fluid

1. Stability commitment for documented Local API endpoints (`/health`, `/transcribe`, `/history`, `/postprocess`, `/dictionary/*`)
2. Changelog notice when endpoints change
3. Optional: review of this client against `_autodocs/api-reference`

## Demo Commands

```bash
fluidvoice doctor
fluidvoice batch ~/Videos --pattern "*.mp4" --use-history-cache
fluidvoice history export ./exports
fluidvoice batch ./media --json --dry-run   # CI integration
```

## Contact

Open an issue in this repo or reach out via FluidVoice GitHub discussions to discuss adoption.
