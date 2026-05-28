# Intelligent Buffer Wizard Improvement Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` or `superpowers:executing-plans` to execute this plan batch-by-batch. Each batch must end with verification and a commit.

**Goal:** Move the project from prototype to a verifiable, runnable, documented MVP aligned with `docs/PRD.md`.

**Architecture:** Keep the existing modular layout: `core/chemistry`, `core/expert`, `core/ai`, `data`, `models`, and `ui`. Improve missing foundations first, then fill feature gaps, then add tests and documentation.

**Tech Stack:** Python, Pydantic, YAML/JSON data files, FastAPI web dashboard, Rich CLI, pytest test suite. Optional scientific libraries can be added only when directly used.

---

## Current Gap Summary

The project already has a usable prototype structure, but it is not complete against `docs/PRD.md`.

Main gaps:

1. No dependency file: no `requirements.txt` or `pyproject.toml`.
2. No test suite: `tests/` has 0 test files.
3. Web dashboard imports fail without dependencies: `fastapi` missing.
4. Ksp database exists but is small: 17 salts. User approved adding more, but not requiring 200+.
5. Placeholder code remains:
   - `core/ai/optimizer.py`
   - `core/chemistry/ksp_predictor.py`
   - `ui/reporter.py`
6. AI/ML layer is mostly heuristic, not real supervised ML.
7. Constraint optimization is simplified and contains dummy logic.
8. SQLite/session history is not implemented and is not required for this immediate pass unless time allows.
9. PDF export is not implemented. HTML export exists.
10. PRD mentions Streamlit, but project uses FastAPI. This plan standardizes on FastAPI to avoid unnecessary rewrite.

---

## Definition of Done

The improvement pass is complete when:

1. Project can be installed from a declared dependency file.
2. Core modules import successfully in a fresh environment.
3. Chemistry, Ksp, expert rules, recommender, optimizer, CLI-safe functions, and reporter have tests.
4. Placeholder `pass` statements are removed or justified as harmless constructors only.
5. Ksp database is expanded beyond the current 17 salts with meaningful common salts.
6. FastAPI dashboard can start with declared dependencies.
7. README explains install, run, test, and known limitations.
8. `pytest` passes.
9. `python -m compileall core ui models` passes.

---

# Execution Batches

## Batch 1 — Project Foundation and Dependencies

**Purpose:** Make the project installable and testable.

**Files:**
- Create: `requirements.txt`
- Create: `README.md`
- Create: `tests/conftest.py`
- Create: `tests/__init__.py`
- Modify: `.gitignore` if needed

**Steps:**

1. Create `requirements.txt` with runtime and test dependencies:
   ```txt
   pydantic>=2.0
   PyYAML>=6.0
   fastapi>=0.110
   uvicorn[standard]>=0.27
   rich>=13.0
   pytest>=8.0
   httpx>=0.27
   ```

2. Create initial `README.md` covering:
   - project purpose
   - install command
   - CLI run command
   - dashboard run command
   - test command
   - current limitations

3. Create `tests/conftest.py` with reusable fixtures for loading:
   - `data/buffer_catalog.json`
   - `data/ksp_database.json`
   - `data/media_templates.json`
   - `data/rules/`

4. Run:
   ```bash
   python -m compileall core ui models
   pytest -q
   ```

5. Expected result:
   - compile passes
   - pytest may report no tests or only fixture import success until next batch

6. Commit:
   ```bash
   git add requirements.txt README.md tests .gitignore
   git commit -m "chore: add project setup and test foundation"
   ```

---

## Batch 2 — Core Smoke Tests

**Purpose:** Lock current behavior before changing internals.

**Files:**
- Create: `tests/test_data_loading.py`
- Create: `tests/test_core_imports.py`
- Create: `tests/test_buffer_engine.py`

**Steps:**

1. Add data loading tests:
   - buffer catalog has at least 10 buffers
   - Ksp database has at least 17 salts before expansion
   - media templates has at least 5 templates
   - each rule YAML file has a top-level `rules` list

2. Add import tests for:
   - `BufferEngine`
   - `PrecipitationPredictor`
   - `KnowledgeBase`
   - `RuleEngine`
   - `FuzzyRiskClassifier`
   - `FormulationRecommender`
   - `ConstraintOptimizer`
   - `HTMLReporter`

3. Add buffer engine test:
   - solve Phosphate pH 7.4, 20 mM, with NaCl
   - assert ionic strength > 0
   - assert species concentrations are returned
   - assert buffer capacity > 0

4. Run:
   ```bash
   pytest tests/test_data_loading.py tests/test_core_imports.py tests/test_buffer_engine.py -q
   ```

5. Commit:
   ```bash
   git add tests
   git commit -m "test: add core smoke coverage"
   ```

---

## Batch 3 — Expand Ksp Database

**Purpose:** Improve precipitation prediction coverage without targeting 200 salts.

**Files:**
- Modify: `data/ksp_database.json`
- Create: `tests/test_ksp_database.py`

**Target database size:** 35–60 salts.

**Add common salts covering:**
- calcium phosphates
- magnesium phosphates
- calcium carbonate
- magnesium carbonate
- barium sulfate
- strontium sulfate
- calcium sulfate
- silver chloride/bromide/iodide
- lead chloride/sulfate/carbonate
- iron hydroxides
- aluminum hydroxide
- copper hydroxide
- zinc hydroxide
- calcium fluoride
- magnesium fluoride

**Steps:**

1. Preserve the current JSON schema.

2. Add validation tests:
   - every salt has `name`, `formula`, `ksp`, `ions`
   - `ksp > 0`
   - every ion has `name`, `charge`, `stoich`
   - database length >= 35
   - no duplicate formula/name pairs

3. Add a functional test:
   - ion pool with `Ca2+` and `CO32-` returns calcium carbonate risk
   - ion pool with `Ca2+` and `PO43-` returns calcium phosphate risk

4. Run:
   ```bash
   pytest tests/test_ksp_database.py -q
   ```

5. Commit:
   ```bash
   git add data/ksp_database.json tests/test_ksp_database.py
   git commit -m "data: expand ksp database coverage"
   ```

---

## Batch 4 — Ksp Predictor Cleanup

**Purpose:** Remove placeholder logic and make OH- handling explicit.

**Files:**
- Modify: `core/chemistry/ksp_predictor.py`
- Create: `tests/test_ksp_predictor.py`

**Design:**
- Keep `predict_all_risks(ion_pool, ionic_strength, temp_c)` signature.
- Support optional `H+`, `OH-`, or `pH` in `ion_pool`.
- If a salt requires `OH-` and no `OH-` exists:
  - if `pH` exists, calculate `OH- = 1e-14 / 10^-pH`
  - else if `H+` exists, calculate `OH- = 1e-14 / H+`
  - else skip that salt cleanly

**Steps:**

1. Write tests for:
   - missing required ions skips salt
   - direct `OH-` enables hydroxide prediction
   - `pH` enables hydroxide prediction
   - no `pass` remains in predictor

2. Implement the minimal OH- inference.

3. Run:
   ```bash
   pytest tests/test_ksp_predictor.py tests/test_ksp_database.py -q
   ```

4. Commit:
   ```bash
   git add core/chemistry/ksp_predictor.py tests/test_ksp_predictor.py
   git commit -m "fix: make hydroxide precipitation prediction explicit"
   ```

---

## Batch 5 — Shared Ion Pool Builder

**Purpose:** Remove duplicated salt-to-ion mapping from optimizer and dashboard.

**Files:**
- Create: `core/chemistry/ion_pool.py`
- Modify: `core/ai/optimizer.py`
- Modify: `ui/dashboard.py`
- Create: `tests/test_ion_pool.py`

**Design:**
Create focused helpers:

```python
def add_salt_to_ion_pool(ion_pool: dict[str, float], salt_name: str, concentration: float) -> dict[str, float]
```

```python
def build_ion_pool_from_salts(added_salts) -> dict[str, float]
```

```python
def add_buffer_species_to_ion_pool(ion_pool: dict[str, float], species_concentrations) -> dict[str, float]
```

**Supported salts first:**
- NaCl
- KCl
- CaCl2
- MgCl2
- MgSO4
- Na2SO4
- KH2PO4
- Na2HPO4
- NaHCO3
- Na2CO3
- Ca(NO3)2
- Fe(NO3)3

**Steps:**

1. Write tests for supported salt mapping.

2. Write tests for phosphate, carbonate, bicarbonate species extraction.

3. Implement `core/chemistry/ion_pool.py`.

4. Replace duplicated mapping in `core/ai/optimizer.py`.

5. Replace duplicated mapping in `ui/dashboard.py`.

6. Run:
   ```bash
   pytest tests/test_ion_pool.py tests/test_ksp_predictor.py -q
   python -m compileall core ui models
   ```

7. Commit:
   ```bash
   git add core/chemistry/ion_pool.py core/ai/optimizer.py ui/dashboard.py tests/test_ion_pool.py
   git commit -m "refactor: centralize ion pool construction"
   ```

---

## Batch 6 — Optimizer Cleanup

**Purpose:** Remove dummy/placeholder code and make ranking deterministic.

**Files:**
- Modify: `core/ai/optimizer.py`
- Create: `tests/test_optimizer.py`

**Design:**
- Keep simple heuristic optimizer; do not introduce heavy ML.
- Score components:
  - pH distance from nearest pKa
  - buffer capacity
  - toxicity penalty
  - cost penalty
  - precipitation penalty from max SI
- Return sorted recommendations with stable fields.

**Steps:**

1. Write tests:
   - `recommend_best_buffers` returns a non-empty sorted list for pH 7.4 + NaCl.
   - each recommendation has `name`, `suitability_score`, `buffer_capacity`, `max_saturation_index`, `toxicity_level`, `cost_level`, `notes`.
   - `optimize_buffer_concentration` returns a concentration within `[min_conc, max_conc]`.
   - no non-constructor `pass` remains in optimizer.

2. Remove the dead loop containing `pass`.

3. Replace dummy pKa score line with direct nearest-pKa calculation.

4. Use shared ion pool builder from Batch 5.

5. Run:
   ```bash
   pytest tests/test_optimizer.py -q
   ```

6. Commit:
   ```bash
   git add core/ai/optimizer.py tests/test_optimizer.py
   git commit -m "fix: make optimizer scoring deterministic"
   ```

---

## Batch 7 — Expert Rules Test Coverage

**Purpose:** Verify rule engine behavior against actual YAML knowledge base.

**Files:**
- Create: `tests/test_expert_rules.py`

**Steps:**

1. Add test for phosphate + calcium/magnesium at pH > 6:
   - expect compatibility finding.

2. Add test for bicarbonate open system:
   - expect CO2 drift warning.

3. Add test for cacodylate:
   - expect critical toxicity finding.

4. Add test for conflict resolver:
   - critical/high findings sort before medium/low.

5. Run:
   ```bash
   pytest tests/test_expert_rules.py -q
   ```

6. Commit:
   ```bash
   git add tests/test_expert_rules.py
   git commit -m "test: cover expert rule diagnostics"
   ```

---

## Batch 8 — Reporter Hardening

**Purpose:** Ensure HTML report generation is tested and safe for normal output paths.

**Files:**
- Modify: `ui/reporter.py`
- Create: `tests/test_reporter.py`

**Design:**
- Keep HTML reporter.
- Do not add PDF in this pass unless explicitly requested later.
- Ensure parent output directory is created before writing.
- Remove unused imports and harmless constructor `pass` if desired.

**Steps:**

1. Write a test that:
   - creates a formulation result using `BufferEngine`
   - writes report to `tmp_path / "report.html"`
   - asserts file exists
   - asserts HTML includes buffer name, ionic strength, precipitation section, expert diagnostics section

2. Modify reporter to create output parent directories:
   ```python
   os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
   ```

3. Run:
   ```bash
   pytest tests/test_reporter.py -q
   ```

4. Commit:
   ```bash
   git add ui/reporter.py tests/test_reporter.py
   git commit -m "test: harden html report generation"
   ```

---

## Batch 9 — Dashboard Verification

**Purpose:** Make web UI importable and endpoint-tested.

**Files:**
- Modify: `ui/dashboard.py` if needed
- Create: `tests/test_dashboard.py`

**Steps:**

1. Add FastAPI TestClient tests:
   - `GET /api/buffers` returns 200 and list data
   - `GET /api/templates` returns 200 and list data
   - `POST /api/formulate` returns 200 for a valid phosphate formulation

2. Ensure dashboard does not do path-sensitive imports incorrectly.

3. Run:
   ```bash
   pytest tests/test_dashboard.py -q
   ```

4. Manual verification command:
   ```bash
   uvicorn ui.dashboard:app --host 127.0.0.1 --port 8000
   ```

5. Commit:
   ```bash
   git add ui/dashboard.py tests/test_dashboard.py
   git commit -m "test: verify dashboard api endpoints"
   ```

---

## Batch 10 — CLI Sanity Coverage

**Purpose:** Prevent CLI import/runtime regressions without full interactive automation.

**Files:**
- Create: `tests/test_cli_import.py`
- Modify: `ui/wizard_cli.py` only if import side effects break tests

**Steps:**

1. Add test that imports `ui.wizard_cli` without launching interactive prompts.

2. If import triggers CLI execution, guard execution with:
   ```python
   if __name__ == "__main__":
       main()
   ```

3. Run:
   ```bash
   pytest tests/test_cli_import.py -q
   ```

4. Commit:
   ```bash
   git add ui/wizard_cli.py tests/test_cli_import.py
   git commit -m "test: add cli import safety check"
   ```

---

## Batch 11 — README and PRD Alignment Notes

**Purpose:** Document what is implemented and what is intentionally deferred.

**Files:**
- Modify: `README.md`
- Create: `docs/IMPLEMENTATION_STATUS.md`

**Steps:**

1. Update `README.md` with:
   - install
   - run CLI
   - run dashboard
   - generate report if CLI supports it
   - run tests
   - data source limitations

2. Create `docs/IMPLEMENTATION_STATUS.md` with a PRD checklist:
   - implemented
   - partially implemented
   - deferred

3. Explicitly mark deferred:
   - 200+ Ksp database
   - SQLite/session history
   - PDF export
   - supervised ML training
   - Streamlit rewrite

4. Run:
   ```bash
   python -m compileall core ui models
   pytest -q
   ```

5. Commit:
   ```bash
   git add README.md docs/IMPLEMENTATION_STATUS.md
   git commit -m "docs: document implementation status"
   ```

---

## Batch 12 — Final Verification and Cleanup

**Purpose:** Confirm the improvement pass is complete.

**Files:**
- Modify any files needed for final fixes only.

**Steps:**

1. Search for unfinished markers:
   ```bash
   grep -RIn "TODO\|NotImplemented\|raise NotImplemented\|pass\|\.\.\." core ui models tests docs data 2>/dev/null || true
   ```

2. Allowed findings:
   - `Field(...)` in Pydantic models
   - documentation ellipses only if intentional
   - `pass` only in empty constructors if justified, though prefer removing them

3. Run full verification:
   ```bash
   python -m compileall core ui models
   pytest -q
   ```

4. Run import verification:
   ```bash
   python - <<'PY'
   mods = [
       'core.chemistry.buffer_engine',
       'core.chemistry.ksp_predictor',
       'core.expert.rule_engine',
       'core.ai.optimizer',
       'ui.dashboard',
       'ui.reporter',
   ]
   for mod in mods:
       __import__(mod)
       print('OK', mod)
   PY
   ```

5. Commit final cleanup if any:
   ```bash
   git add .
   git commit -m "chore: complete improvement verification"
   ```

---

# Recommended Execution Order

Execute strictly in this order:

1. Batch 1 — Project Foundation and Dependencies
2. Batch 2 — Core Smoke Tests
3. Batch 3 — Expand Ksp Database
4. Batch 4 — Ksp Predictor Cleanup
5. Batch 5 — Shared Ion Pool Builder
6. Batch 6 — Optimizer Cleanup
7. Batch 7 — Expert Rules Test Coverage
8. Batch 8 — Reporter Hardening
9. Batch 9 — Dashboard Verification
10. Batch 10 — CLI Sanity Coverage
11. Batch 11 — README and PRD Alignment Notes
12. Batch 12 — Final Verification and Cleanup

---

# Notes for Future Scope

Do not include these in the current improvement pass unless explicitly requested:

1. Full SQLite/SQLAlchemy session history.
2. PDF export with ReportLab.
3. Real supervised ML training pipeline.
4. Streamlit migration.
5. 200+ salt database.
6. Full thermodynamic database integration.

These are valid future milestones, but not required for the next MVP completion pass.
