"""Tests for VoiceLens CLI commands and integration."""

import runpy
from unittest.mock import patch

from typer.testing import CliRunner

from voicelens import __version__
from voicelens.cli import app
from voicelens.commands.doctor import perform_system_checks

runner = CliRunner()


def test_cli_help():
    """Verify that --help shows the usage description and list of commands."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.output
    assert "doctor" in result.output
    assert "Show the version and exit." in result.output


def test_cli_version():
    """Verify that --version shows correct version and exits."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "VoiceLens" in result.output
    assert __version__ in result.output

    # Test short version option -v
    result_short = runner.invoke(app, ["-v"])
    assert result_short.exit_code == 0
    assert __version__ in result_short.output


def test_cli_doctor():
    """Verify that doctor command executes and outputs system checks correctly."""
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "VoiceLens System Diagnosis" in result.output
    assert "Python Runtime" in result.output
    assert "Disk Space" in result.output
    assert "Diagnosis Summary" in result.output


def test_perform_system_checks_direct():
    """Directly test perform_system_checks function."""
    assert perform_system_checks() is True


def test_perform_system_checks_disk_failure():
    """Test perform_system_checks handling of shutil.disk_usage exception."""
    with patch("shutil.disk_usage", side_effect=Exception("Disk error")):
        assert perform_system_checks() is True


def test_perform_system_checks_ffmpeg_found():
    """Test perform_system_checks with simulated ffmpeg found in PATH."""
    with patch("shutil.which", return_value="/usr/bin/ffmpeg"):
        assert perform_system_checks() is True


def test_main_module_execution():
    """Test executing the CLI via the __main__.py module path."""
    with patch("voicelens.cli.app") as mock_app:
        runpy.run_module("voicelens.__main__", run_name="__main__")
        assert mock_app.call_count == 1


def test_cli_module_execution_as_main():
    """Test executing cli.py as __main__."""
    with patch("typer.Typer.__call__") as mock_call:
        runpy.run_module("voicelens.cli", run_name="__main__")
        assert mock_call.call_count == 1
