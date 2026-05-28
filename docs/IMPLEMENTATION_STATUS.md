# Implementation Status

This document maps the current project implementation against `docs/PRD.md` after the improvement batches.

## Implemented

| PRD Area | Status | Notes |
|---|---:|---|
| Modular project structure | Implemented | `core/`, `data/`, `models/`, `ui/`, `docs/`, and `tests/` are present. |
| Chemistry engine | Implemented | Buffer formulation, speciation, ionic strength, activity coefficients, and buffer capacity are implemented. |
| Davies activity correction | Implemented | Used by chemistry and Ksp calculations. |
| Ksp precipitation predictor | Implemented | Multi-salt prediction with saturation index and risk labels. |
| Ksp database | Implemented for MVP | Expanded from 17 to 39 salts. Not intended to be exhaustive. |
| Expert system | Implemented | YAML knowledge base, rule engine, and conflict resolver are implemented. |
| Fuzzy risk classifier | Implemented | Combines saturation index and expert hazard score. |
| Media-template recommender | Implemented | Similarity-based heuristic recommender. |
| Constraint optimizer | Implemented for MVP | Deterministic heuristic ranking and concentration search. |
| CLI wizard | Implemented | Interactive flow in `ui/wizard_cli.py`. |
| Web dashboard/API | Implemented | FastAPI app in `ui/dashboard.py`. |
| HTML report generation | Implemented | `ui/reporter.py` writes a self-contained HTML report. |
| Pydantic schemas | Implemented | Input/result/session models in `models/session.py`. |
| Test foundation | Implemented | Pytest suite covers data, imports, buffer engine, Ksp, expert rules, optimizer, reporter, dashboard, and CLI import safety. |
| Dependency declaration | Implemented | `requirements.txt` added. |
| README | Implemented | Install, run, test, and limitation notes added. |

## Partially Implemented

| PRD Area | Status | Notes |
|---|---:|---|
| AI/ML layer | Partial | Fuzzy logic and heuristic recommendations exist. No trained supervised model pipeline. |
| Constraint solver | Partial | Uses deterministic heuristic and bisection search. Not a full multi-objective scientific optimizer. |
| Visualization | Partial | HTML report includes a chart. Full risk heatmap is not implemented. |
| Data layer | Partial | JSON/YAML data files exist. SQLite persistence is not implemented. |
| Session model | Partial | `SessionHistory` model exists. Persistent history storage does not. |
| Report export | Partial | HTML export exists. PDF export does not. |

## Deferred

These PRD items are intentionally deferred from the current MVP improvement pass:

1. 200+ Ksp database.
2. SQLite/SQLAlchemy session history.
3. PDF export with ReportLab or another renderer.
4. Real supervised ML training pipeline.
5. Streamlit rewrite.
6. Full thermodynamic database integration.
7. Advanced heatmap visualization.
8. Laboratory-grade validation dataset and calibration.

## Current Verification Commands

Run these commands from the project root:

```bash
python -m compileall core ui models
pytest -q
```

Expected result after the improvement batches:

```text
compileall passes
pytest passes
```

## Scientific Use Note

The application is an advisory calculation and screening tool. It does not replace laboratory validation, calibrated instruments, or safety review for hazardous reagents.
