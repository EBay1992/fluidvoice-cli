# Publishing fluidvoice-cli to PyPI

## Prerequisites

```bash
pip install build twine
```

Create accounts at [pypi.org](https://pypi.org) and optionally [test.pypi.org](https://test.pypi.org).

## Build

```bash
cd fluidvoice-cli
python -m build
```

Artifacts land in `dist/fluidvoice_cli-<version>-py3-none-any.whl` and `.tar.gz`.

## Test Upload (recommended first)

```bash
twine upload --repository testpypi dist/*
pip install --index-url https://test.pypi.org/simple/ fluidvoice-cli
```

## Production Upload

```bash
twine upload dist/*
```

## Upstream PR to FluidVoice

Upstream adoption is tracked in [FluidVoice #529](https://github.com/altic-dev/FluidVoice/issues/529). When opening follow-up issues on [altic-dev/FluidVoice](https://github.com/altic-dev/FluidVoice/issues), use:

**Title:** Official companion CLI for Local API — adoption discussion

**Body:** (see ADOPT.md)

Optionally submit a README patch PR linking to PyPI and GitHub repo.

## GitHub Issue Template

Save as `.github/ISSUE_TEMPLATE/api_mismatch.md` when repo is standalone.
