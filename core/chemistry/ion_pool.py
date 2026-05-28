from typing import Iterable


SALT_ION_MAP: dict[str, list[tuple[str, float]]] = {
    "NACL": [("Na+", 1.0), ("Cl-", 1.0)],
    "KCL": [("K+", 1.0), ("Cl-", 1.0)],
    "CACL2": [("Ca2+", 1.0), ("Cl-", 2.0)],
    "MGCL2": [("Mg2+", 1.0), ("Cl-", 2.0)],
    "MGSO4": [("Mg2+", 1.0), ("SO42-", 1.0)],
    "NA2SO4": [("Na+", 2.0), ("SO42-", 1.0)],
    "KH2PO4": [("K+", 1.0), ("H2PO4-", 1.0)],
    "NA2HPO4": [("Na+", 2.0), ("HPO42-", 1.0)],
    "NAHCO3": [("Na+", 1.0), ("HCO3-", 1.0)],
    "NA2CO3": [("Na+", 2.0), ("CO32-", 1.0)],
    "CA(NO3)2": [("Ca2+", 1.0), ("NO3-", 2.0)],
    "FE(NO3)3": [("Fe3+", 1.0), ("NO3-", 3.0)],
}


def _add_ion(ion_pool: dict[str, float], ion_name: str, concentration: float) -> None:
    ion_pool[ion_name] = ion_pool.get(ion_name, 0.0) + concentration


def add_salt_to_ion_pool(
    ion_pool: dict[str, float],
    salt_name: str,
    concentration: float,
) -> dict[str, float]:
    """Add supported salt dissociation products to an ion pool."""
    normalized_name = salt_name.upper().replace(" ", "")
    ion_entries = SALT_ION_MAP.get(normalized_name)

    if ion_entries is None:
        _add_ion(ion_pool, f"{salt_name}+", concentration)
        _add_ion(ion_pool, f"{salt_name}-", concentration)
        return ion_pool

    for ion_name, stoich in ion_entries:
        _add_ion(ion_pool, ion_name, concentration * stoich)

    return ion_pool


def build_ion_pool_from_salts(added_salts: Iterable) -> dict[str, float]:
    """Build an ion pool from SaltInput-like objects or dictionaries."""
    ion_pool: dict[str, float] = {}
    for salt in added_salts:
        if isinstance(salt, dict):
            salt_name = salt["name"]
            concentration = salt["concentration"]
        else:
            salt_name = salt.name
            concentration = salt.concentration
        add_salt_to_ion_pool(ion_pool, salt_name, concentration)
    return ion_pool


def add_buffer_species_to_ion_pool(
    ion_pool: dict[str, float],
    species_concentrations: Iterable,
) -> dict[str, float]:
    """Add recognized buffer species from speciation results to an ion pool."""
    for species in species_concentrations:
        species_name = species.name.split(" (")[0]
        concentration = species.concentration

        if "Dihydrogen Phosphate" in species_name or "H2PO4" in species_name:
            ion_pool["H2PO4-"] = concentration
        elif "Hydrogen Phosphate" in species_name or "HPO4" in species_name:
            ion_pool["HPO42-"] = concentration
        elif "Trisodium Phosphate" in species_name or "PO4" in species_name:
            ion_pool["PO43-"] = concentration
        elif "Bicarbonate" in species_name or "HCO3" in species_name:
            ion_pool["HCO3-"] = concentration
        elif "Carbonate" in species_name or "CO3" in species_name:
            ion_pool["CO32-"] = concentration

    return ion_pool
