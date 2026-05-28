# Intelligent Buffer Wizard

Intelligent Buffer Wizard is a Python MVP for designing and checking chemical buffer formulations. It combines buffer speciation, ionic strength correction, Ksp precipitation prediction, expert-rule diagnostics, heuristic recommendations, and HTML reporting.

## Features

- Buffer formulation calculations with activity-coefficient correction.
- Ionic strength and species distribution estimates.
- Ksp-based precipitation risk prediction.
- YAML-backed expert rules for compatibility, precipitation, and toxicity warnings.
- Fuzzy risk classification from precipitation and expert-system severity.
- Heuristic buffer and media-template recommendations.
- CLI wizard for interactive formulation workflows.
- FastAPI dashboard for browser/API workflows.
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

The CLI supports:

1. formulating a buffer,
2. searching media templates,
3. ranking buffer options,
4. exporting an HTML protocol report.

## Run the Dashboard

```bash
uvicorn ui.dashboard:app --host 127.0.0.1 --port 8000
```

Then open:

```text
http://127.0.0.1:8000
```

Main API endpoints:

```text
GET  /api/buffers
GET  /api/templates
POST /api/formulate
POST /api/optimize
```

Example formulation request:

```bash
curl -X POST http://127.0.0.1:8000/api/formulate \
  -H 'Content-Type: application/json' \
  -d '{
    "buffer_name": "Phosphate",
    "target_ph": 7.4,
    "concentration": 0.02,
    "temperature_c": 25.0,
    "added_salts": [{"name": "NaCl", "concentration": 0.15}],
    "environment": "closed",
    "application": "biochemistry",
    "exposure": "dark"
  }'
```

## Generate Reports

HTML report generation is available through the CLI export flow and through `ui.reporter.HTMLReporter`:

```python
from ui.reporter import HTMLReporter

HTMLReporter().generate_report(result, "reports/buffer_report.html")
```

PDF export is not implemented in this MVP.

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
core/chemistry/   Buffer, ionic strength, speciation, ion-pool, and Ksp logic
core/expert/      YAML knowledge base, rule engine, and conflict resolver
core/ai/          Fuzzy classifier, recommender, and optimizer
models/           Pydantic schemas
data/             Buffer catalog, Ksp data, media templates, expert rules
ui/               CLI, FastAPI dashboard, and HTML reporter
docs/             PRD and project documentation
tests/            Pytest test suite
```

## Data Coverage

- Buffer catalog: common lab buffers such as Phosphate, Tris, HEPES, MES, MOPS, Bicarbonate, Citrate, and related systems.
- Ksp database: expanded MVP database covering common carbonate, phosphate, sulfate, halide, fluoride, hydroxide, and metal precipitates.
- Media templates: reference formulations for similarity comparison.
- Expert rules: compatibility, precipitation, and toxicity YAML rules.

## Current Limitations

This project is an MVP-oriented prototype.

- Ksp database is expanded but not exhaustive; it is not a 200+ salt thermodynamic database.
- Recommender and optimizer are heuristic, not trained supervised ML models.
- SQLite session history is not implemented yet.
- PDF export is not implemented yet; HTML reporting is available.
- PRD mentions Streamlit, but the current web UI uses FastAPI.
- Calculations are advisory and do not replace laboratory validation.

## Verification Status

Current expected verification commands:

```bash
python -m compileall core ui models
pytest -q
```
