"""CLI integration tests."""

from __future__ import annotations

from typer.testing import CliRunner

from fluidvoice_cli.main import app

runner = CliRunner()


def test_version() -> None:
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "fluidvoice" in result.stdout


def test_help() -> None:
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "transcribe" in result.stdout
    assert "batch" in result.stdout


def test_config_show() -> None:
    result = runner.invoke(app, ["config", "show"])
    assert result.exit_code == 0


def test_config_show_json() -> None:
    result = runner.invoke(app, ["--json", "config", "show"])
    assert result.exit_code == 0
    assert '"port": 47733' in result.stdout


def test_batch_dry_run(tmp_path) -> None:
    (tmp_path / "demo.mp4").write_bytes(b"x")
    result = runner.invoke(app, ["--json", "batch", str(tmp_path), "--dry-run"])
    assert result.exit_code == 0
    assert "demo.mp4" in result.stdout
