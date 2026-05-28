import math

def calculate_apparent_pKas(thermo_pKas: list[float], acid_charge: int, activity_coeffs: dict[int, float]) -> list[float]:
    """
    Corrects thermodynamic pKas for ionic activity to find apparent pKas.
    pK_a' = pK_a - log10(gamma_{acid}) + log10(gamma_{base})
    """
    apparent_pKas = []
    for k, pKa in enumerate(thermo_pKas):
        # Dissociation k goes from species k (charge z_acid) to species k+1 (charge z_base)
        # Note: 0-indexed in code:
        # species index 0 has charge = acid_charge
        # species index k has charge = acid_charge - k
        # species index k+1 has charge = acid_charge - (k+1)
        z_acid = acid_charge - k
        z_base = acid_charge - (k + 1)
        
        gamma_acid = activity_coeffs.get(abs(z_acid), 1.0)
        gamma_base = activity_coeffs.get(abs(z_base), 1.0)
        
        # pKa' = pKa - log10(gamma_acid) + log10(gamma_base)
        apparent_pKa = pKa - math.log10(gamma_acid) + math.log10(gamma_base)
        apparent_pKas.append(apparent_pKa)
        
    return apparent_pKas

def calculate_speciation_fractions(apparent_pKas: list[float], pH: float) -> list[float]:
    """
    Calculates the fractional abundance of each species of a polyprotic system at a given pH.
    Uses log-sum-exp trick for numerical stability.
    """
    N = len(apparent_pKas)
    # L_j = j * pH - sum(apparent_pKa_1 to apparent_pKa_j)
    L = [0.0] * (N + 1)
    
    cumulative_pKa_sum = 0.0
    for j in range(1, N + 1):
        cumulative_pKa_sum += apparent_pKas[j - 1]
        L[j] = j * pH - cumulative_pKa_sum
        
    # Log-sum-exp trick for numerical stability
    L_max = max(L)
    
    # exp_terms = 10^(L_j - L_max)
    exp_terms = [10 ** (Lj - L_max) for Lj in L]
    sum_exp = sum(exp_terms)
    
    fractions = [term / sum_exp for term in exp_terms]
    return fractions
