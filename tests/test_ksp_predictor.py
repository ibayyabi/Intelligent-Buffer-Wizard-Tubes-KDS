from pathlib import Path

from core.chemistry.ksp_predictor import PrecipitationPredictor


HYDROXIDE_DB = [
    {
        "name": "Magnesium Hydroxide",
        "formula": "Mg(OH)2",
        "ksp": 5.61e-12,
        "ions": [
            {"name": "Mg2+", "charge": 2, "stoich": 1},
            {"name": "OH-", "charge": -1, "stoich": 2},
        ],
    }
]


def test_missing_required_ions_skip_salt():
    predictor = PrecipitationPredictor(HYDROXIDE_DB)

    risks = predictor.predict_all_risks({"Mg2+": 0.01}, ionic_strength=0.01)

    assert risks == []


def test_direct_hydroxide_enables_hydroxide_prediction():
    predictor = PrecipitationPredictor(HYDROXIDE_DB)

    risks = predictor.predict_all_risks(
        {"Mg2+": 0.01, "OH-": 0.001},
        ionic_strength=0.01,
    )

    assert len(risks) == 1
    assert risks[0].formula == "Mg(OH)2"


def test_ph_enables_hydroxide_prediction():
    predictor = PrecipitationPredictor(HYDROXIDE_DB)

    risks = predictor.predict_all_risks(
        {"Mg2+": 0.01, "pH": 11.0},
        ionic_strength=0.01,
    )

    assert len(risks) == 1
    assert risks[0].formula == "Mg(OH)2"


def test_hydrogen_concentration_enables_hydroxide_prediction():
    predictor = PrecipitationPredictor(HYDROXIDE_DB)

    risks = predictor.predict_all_risks(
        {"Mg2+": 0.01, "H+": 1e-11},
        ionic_strength=0.01,
    )

    assert len(risks) == 1
    assert risks[0].formula == "Mg(OH)2"


def test_predictor_contains_no_pass_placeholder():
    source = Path("core/chemistry/ksp_predictor.py").read_text(encoding="utf-8")

    assert "pass" not in source
