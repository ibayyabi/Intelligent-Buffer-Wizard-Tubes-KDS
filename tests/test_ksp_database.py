from core.chemistry.ksp_predictor import PrecipitationPredictor


def test_ksp_database_schema_and_size(ksp_database):
    assert len(ksp_database) >= 35

    seen = set()
    for salt in ksp_database:
        assert set(salt) >= {"name", "formula", "ksp", "ions"}
        assert isinstance(salt["name"], str) and salt["name"]
        assert isinstance(salt["formula"], str) and salt["formula"]
        assert salt["ksp"] > 0
        assert isinstance(salt["ions"], list) and salt["ions"]

        identity = (salt["name"], salt["formula"])
        assert identity not in seen
        seen.add(identity)

        for ion in salt["ions"]:
            assert set(ion) >= {"name", "charge", "stoich"}
            assert isinstance(ion["name"], str) and ion["name"]
            assert isinstance(ion["charge"], int)
            assert ion["stoich"] > 0


def test_ksp_database_predicts_calcium_carbonate(ksp_database):
    predictor = PrecipitationPredictor(ksp_database)
    risks = predictor.predict_all_risks(
        {"Ca2+": 0.01, "CO32-": 0.01},
        ionic_strength=0.02,
        temp_c=25.0,
    )

    formulas = {risk.formula for risk in risks}
    assert "CaCO3" in formulas


def test_ksp_database_predicts_calcium_phosphate(ksp_database):
    predictor = PrecipitationPredictor(ksp_database)
    risks = predictor.predict_all_risks(
        {"Ca2+": 0.01, "PO43-": 0.01},
        ionic_strength=0.02,
        temp_c=25.0,
    )

    formulas = {risk.formula for risk in risks}
    assert "Ca3(PO4)2" in formulas
