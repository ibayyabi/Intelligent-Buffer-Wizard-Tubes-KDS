from core.chemistry.buffer_engine import BufferEngine
from models.session import BufferFormulationInput, SaltInput
from ui.reporter import HTMLReporter


def test_html_reporter_writes_report_to_nested_output_path(buffer_catalog, tmp_path):
    engine = BufferEngine(buffer_catalog)
    form_input = BufferFormulationInput(
        buffer_name="Phosphate",
        target_ph=7.4,
        concentration=0.020,
        added_salts=[SaltInput(name="NaCl", concentration=0.150)],
    )
    result = engine.solve_formulation(form_input, target_volume_l=1.0)
    output_path = tmp_path / "nested" / "report.html"

    HTMLReporter().generate_report(result, str(output_path))

    assert output_path.exists()
    html = output_path.read_text(encoding="utf-8")
    assert "Phosphate" in html
    assert "Ionic Strength" in html
    assert "Precipitation Predictor" in html
    assert "Expert Diagnostics" in html
