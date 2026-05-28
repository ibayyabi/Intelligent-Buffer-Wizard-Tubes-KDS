import json
from pathlib import Path

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
RULES_DIR = DATA_DIR / "rules"


@pytest.fixture(scope="session")
def project_root() -> Path:
    return PROJECT_ROOT


@pytest.fixture(scope="session")
def buffer_catalog() -> list[dict]:
    with (DATA_DIR / "buffer_catalog.json").open("r", encoding="utf-8") as f:
        return json.load(f)["buffers"]


@pytest.fixture(scope="session")
def ksp_database() -> list[dict]:
    with (DATA_DIR / "ksp_database.json").open("r", encoding="utf-8") as f:
        return json.load(f)["salts"]


@pytest.fixture(scope="session")
def media_templates() -> list[dict]:
    with (DATA_DIR / "media_templates.json").open("r", encoding="utf-8") as f:
        return json.load(f)["templates"]


@pytest.fixture(scope="session")
def rules_dir() -> Path:
    return RULES_DIR


@pytest.fixture(scope="session")
def rule_files() -> dict[str, dict]:
    loaded = {}
    for path in sorted(RULES_DIR.glob("*.yaml")):
        with path.open("r", encoding="utf-8") as f:
            loaded[path.name] = yaml.safe_load(f)
    return loaded
