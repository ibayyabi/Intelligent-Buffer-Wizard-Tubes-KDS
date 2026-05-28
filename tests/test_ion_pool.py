from types import SimpleNamespace

from core.chemistry.ion_pool import (
    add_buffer_species_to_ion_pool,
    add_salt_to_ion_pool,
    build_ion_pool_from_salts,
)
from models.session import SaltInput


def test_add_salt_to_ion_pool_maps_supported_salts():
    ion_pool = {}

    add_salt_to_ion_pool(ion_pool, "NaCl", 0.150)
    add_salt_to_ion_pool(ion_pool, "CaCl2", 0.002)
    add_salt_to_ion_pool(ion_pool, "MgSO4", 0.001)
    add_salt_to_ion_pool(ion_pool, "Fe(NO3)3", 0.0005)

    assert ion_pool["Na+"] == 0.150
    assert ion_pool["Cl-"] == 0.154
    assert ion_pool["Ca2+"] == 0.002
    assert ion_pool["Mg2+"] == 0.001
    assert ion_pool["SO42-"] == 0.001
    assert ion_pool["Fe3+"] == 0.0005
    assert ion_pool["NO3-"] == 0.0015


def test_build_ion_pool_from_salts_accepts_models_and_dicts():
    ion_pool = build_ion_pool_from_salts([
        SaltInput(name="Na2SO4", concentration=0.010),
        {"name": "NaHCO3", "concentration": 0.020},
    ])

    assert ion_pool["Na+"] == 0.040
    assert ion_pool["SO42-"] == 0.010
    assert ion_pool["HCO3-"] == 0.020


def test_add_buffer_species_to_ion_pool_extracts_phosphate_and_carbonate_species():
    ion_pool = {}
    species = [
        SimpleNamespace(name="Sodium Dihydrogen Phosphate", concentration=0.010),
        SimpleNamespace(name="Disodium Hydrogen Phosphate", concentration=0.020),
        SimpleNamespace(name="Trisodium Phosphate", concentration=0.001),
        SimpleNamespace(name="Sodium Bicarbonate", concentration=0.030),
        SimpleNamespace(name="Sodium Carbonate", concentration=0.004),
    ]

    add_buffer_species_to_ion_pool(ion_pool, species)

    assert ion_pool["H2PO4-"] == 0.010
    assert ion_pool["HPO42-"] == 0.020
    assert ion_pool["PO43-"] == 0.001
    assert ion_pool["HCO3-"] == 0.030
    assert ion_pool["CO32-"] == 0.004
