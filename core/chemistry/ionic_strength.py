import math

def calculate_ionic_strength(concentrations: list[float], charges: list[int]) -> float:
    """
    Calculates the ionic strength I of a solution.
    I = 0.5 * sum(c_i * z_i^2)
    """
    total = 0.0
    for c, z in zip(concentrations, charges):
        total += c * (z ** 2)
    return 0.5 * total

def get_davies_coefficient(charge: int, ionic_strength: float, temp_c: float = 25.0) -> float:
    """
    Calculates the activity coefficient gamma for an ion of a given charge
    using the Davies Equation.
    log10(gamma) = -A * z^2 * (sqrt(I)/(1 + sqrt(I)) - 0.3 * I)
    """
    if charge == 0 or ionic_strength <= 0.0:
        return 1.0
    
    # Clip ionic strength to a maximum of 1.0 to prevent mathematical divergence in Davies equation at high concentrations
    I = min(ionic_strength, 1.0)
    
    # Temperature dependence of A (Debye-Huckel parameter)
    # A ~ 0.509 at 25C (298.15 K)
    temp_k = temp_c + 273.15
    A = 0.5092 * ((298.15 / temp_k) ** 1.5)
    
    sqrt_I = math.sqrt(I)
    log_gamma = -A * (charge ** 2) * (sqrt_I / (1.0 + sqrt_I) - 0.3 * I)
    
    return 10 ** log_gamma
