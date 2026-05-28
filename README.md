# Intelligent Buffer Wizard

Intelligent Buffer Wizard is a Python prototype for designing and checking chemical buffer formulations. It combines buffer speciation, ionic strength correction, Ksp precipitation prediction, expert-rule diagnostics, heuristic recommendations, and HTML reporting.

## Features

- Buffer formulation calculations with activity-coefficient correction.
- Ionic strength and species distribution estimates.
- Ksp-based precipitation risk prediction.
- YAML-backed expert rules for compatibility, precipitation, and toxicity warnings.
- Heuristic fuzzy risk classification and formulation recommendation.
- CLI wizard and FastAPI dashboard.
- HTML report generation.

## Install

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run the CLI

```bash
python ui/wizard_cli.py
```

## Run the Dashboard

```bash
uvicorn ui.dashboard:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

## Run Tests

```bash
pytest -q
```

Compile-check the Python modules:

```bash
python -m compileall core ui models
```

## Project Layout

```text
core/chemistry/   Buffer, ionic strength, speciation, and Ksp logic
core/expert/      YAML knowledge base and rule engine
core/ai/          Fuzzy classifier, recommender, and optimizer
models/           Pydantic schemas
data/             Buffer catalog, Ksp data, media templates, expert rules
ui/               CLI, FastAPI dashboard, and HTML reporter
docs/             PRD and project documentation
tests/            Pytest test suite
```

## Current Limitations

This project is still an MVP-oriented prototype.

- Ksp database is useful but not exhaustive.
- Recommender and optimizer are heuristic, not trained supervised ML models.
- SQLite session history is not implemented yet.
- PDF export is not implemented yet; HTML reporting is available.
- PRD mentions Streamlit, but the current web UI uses FastAPI.
- Calculations are advisory and do not replace laboratory validation.
