from core.chemistry.buffer_engine import BufferEngine
from models.session import BufferFormulationInput, SaltInput


def test_buffer_engine_solves_phosphate_formulation(buffer_catalog):
    engine = BufferEngine(buffer_catalog)
    form_input = BufferFormulationInput(
        buffer_name="Phosphate",
        target_ph=7.4,
        concentration=0.020,
        added_salts=[SaltInput(name="NaCl", concentration=0.150)],
    )

    result = engine.solve_formulation(form_input, target_volume_l=1.0)

    assert result.real_ph == form_input.target_ph
    assert result.ionic_strength > 0
    assert result.species_concentrations
    assert sum(spec.concentration for spec in result.species_concentrations) > 0
    assert result.buffer_capacity > 0
