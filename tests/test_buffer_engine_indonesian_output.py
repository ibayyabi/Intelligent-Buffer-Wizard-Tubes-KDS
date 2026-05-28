from core.chemistry.buffer_engine import BufferEngine
from models.session import BufferFormulationInput


def test_direct_mix_recipe_uses_indonesian_output(buffer_catalog):
    engine = BufferEngine(buffer_catalog)
    result = engine.solve_formulation(
        BufferFormulationInput(
            buffer_name="Tris",
            target_ph=8.06,
            concentration=0.05,
        ),
        target_volume_l=1.0,
    )

    assert result.direct_mix_recipe is not None
    recipe = result.direct_mix_recipe.recipe_text
    assert "Timbang" in recipe
    assert "Larutkan" in recipe
    assert "Tambahkan" in recipe
    assert "Verifikasi pH" in recipe
    assert "Measure" not in recipe
    assert "Dissolve" not in recipe


def test_titration_recipe_uses_indonesian_output(buffer_catalog):
    engine = BufferEngine(buffer_catalog)
    result = engine.solve_formulation(
        BufferFormulationInput(
            buffer_name="Phosphate",
            target_ph=7.4,
            concentration=0.02,
        ),
        target_volume_l=1.0,
    )

    assert result.titration_recipe is not None
    recipe = result.titration_recipe.recipe_instruction
    assert "Larutkan" in recipe
    assert "Tambahkan" in recipe
    assert "air deionisasi" in recipe
    assert "Dissolve" not in recipe
    assert "Add all other" not in recipe
