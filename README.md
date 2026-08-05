# VoiceLens

[![CI](https://github.com/588h6fnmnv-hub/voicelens/actions/workflows/ci.yml/badge.svg)](https://github.com/588h6fnmnv-hub/voicelens/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)

A production-ready, open-source Python CLI for audio and voice analysis. VoiceLens uses Typer for modern CLI command parsing and Rich for beautifully formatted terminal outputs.

---

## Features

- **Modern CLI Design**: Built on top of [Typer](https://typer.tiangolo.com/) for clean and powerful command-line argument parsing.
- **Rich Output**: Generates beautifully colored terminal outputs, tables, and status report panels with [Rich](https://github.com/Textualize/rich).
- **Environment Diagnostics**: Includes an in-built `doctor` command to diagnose system, platform, and audio tool readiness.
- **Production-Ready**: Configured with Ruff for linting/formatting, Pytest for testing, and GitHub Actions for continuous integration.

---

## Installation

VoiceLens requires **Python 3.12 or newer**.

### Using `uv` (Recommended)

```bash
# Clone the repository
git clone https://github.com/your-username/voicelens.git
cd voicelens

# Install editable mode
uv pip install -e .
```

### Using `pip`

```bash
# Clone the repository
git clone https://github.com/your-username/voicelens.git
cd voicelens

# Install editable mode
pip install -e .
```

---

## Usage

Once installed, the `voicelens` executable will be added to your PATH.

### 1. Show Help & Options

To view all available commands and options, run:

```bash
voicelens --help
```

Or run via module execution:

```bash
python -m voicelens --help
```

### 2. View Version

Check the currently installed version:

```bash
voicelens --version
# or
voicelens -v
```

### 3. Run System Diagnosis

Diagnose and verify your system configuration using the `doctor` command:

```bash
voicelens doctor
```

---

## Development & Testing

### Code Quality

We use [Ruff](https://github.com/astral-sh/ruff) for linting and formatting.

**Run Linting & Formatting checks:**

```bash
ruff check .
ruff format --check .
```

### Running Tests

We use [Pytest](https://docs.pytest.org/) for running tests.

**Run tests with coverage reports:**

```bash
pytest
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
