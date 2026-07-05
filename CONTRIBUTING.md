# Contributing to fluidvoice-cli

Thank you for contributing. This project is designed for collaboration with the [FluidVoice](https://github.com/altic-dev/FluidVoice) team and the wider community.

## Development Setup

```bash
git clone <your-fork>
cd fluidvoice-cli
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
ruff check src tests
pytest -v
pytest --cov=fluidvoice_cli
```

Media tests require `ffmpeg` on macOS. Linux CI runs client/CLI tests with mocked HTTP.

## Code Style

- Python 3.11+ with type hints
- Format and lint with **ruff**
- Keep commands thin; business logic in `client.py`, `media.py`, `history.py`
- All user-facing errors use `FluidVoiceError` subclasses with `exit_code`

## Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: add history export --format srt`
- `fix: handle empty history API response`
- `docs: update API compatibility table`
- `test: mock transcribe path fallback`

## Pull Request Checklist

- [ ] Tests added or updated
- [ ] `ruff check` passes
- [ ] README updated if CLI surface changed
- [ ] API compatibility table updated if endpoints changed

## Reporting API Mismatches

If FluidVoice changes the Local API, open an issue with:

1. FluidVoice app version
2. Endpoint and request/response payload
3. Expected vs actual behavior
4. `fluidvoice doctor --json` output

## Release Process

1. Bump version in `src/fluidvoice_cli/__init__.py` and `pyproject.toml`
2. Update CHANGELOG.md
3. Tag `v0.x.x`
4. `python -m build && twine upload dist/*`

See [PUBLISHING.md](PUBLISHING.md) for PyPI details.
