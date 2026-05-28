from pathlib import Path

from core.ai.optimizer import ConstraintOptimizer
from core.chemistry.buffer_engine import BufferEngine
from core.chemistry.ksp_predictor import PrecipitationPredictor


def make_optimizer(buffer_catalog, ksp_database):
    engine = BufferEngine(buffer_catalog)
    predictor = PrecipitationPredictor(ksp_database)
    return ConstraintOptimizer(engine, predictor)


def test_recommend_best_buffers_returns_sorted_recommendations(buffer_catalog, ksp_database):
    optimizer = make_optimizer(buffer_catalog, ksp_database)

    recommendations = optimizer.recommend_best_buffers(
        target_ph=7.4,
        added_salts=[{"name": "NaCl", "concentration": 0.150}],
    )

    assert recommendations
    scores = [item["suitability_score"] for item in recommendations]
    assert scores == sorted(scores, reverse=True)


def test_recommendations_have_stable_fields(buffer_catalog, ksp_database):
    optimizer = make_optimizer(buffer_catalog, ksp_database)

    recommendations = optimizer.recommend_best_buffers(
        target_ph=7.4,
        added_salts=[{"name": "NaCl", "concentration": 0.150}],
    )

    required_fields = {
        "name",
        "suitability_score",
        "buffer_capacity",
        "max_saturation_index",
        "toxicity_level",
        "cost_level",
        "notes",
    }
    assert recommendations
    for recommendation in recommendations:
        assert required_fields <= set(recommendation)
        assert 0.0 <= recommendation["suitability_score"] <= 100.0
        assert recommendation["buffer_capacity"] > 0


def test_optimize_buffer_concentration_returns_value_within_bounds(buffer_catalog, ksp_database):
    optimizer = make_optimizer(buffer_catalog, ksp_database)

    concentration = optimizer.optimize_buffer_concentration(
        buffer_name="Phosphate",
        target_ph=7.4,
        added_salts=[{"name": "NaCl", "concentration": 0.150}],
        min_conc=0.005,
        max_conc=0.050,
    )

    assert 0.005 <= concentration <= 0.050


def test_optimizer_contains_no_pass_placeholder():
    source = Path("core/ai/optimizer.py").read_text(encoding="utf-8")

    assert "pass" not in source
