import math
from models.session import (
    BufferFormulationInput,
    BufferFormulationResult,
    SpeciesConcentration,
    TitrantRequirement,
    DirectMixRecipe
)
from core.chemistry.ionic_strength import calculate_ionic_strength, get_davies_coefficient
from core.chemistry.speciation import calculate_apparent_pKas, calculate_speciation_fractions

# Salt database mapping buffer name to [species_index] -> (salt_display_name, molecular_weight)
BUFFER_SALTS_DATABASE = {
    "Phosphate": {
        0: ("Phosphoric Acid (85% w/w liquid, d=1.685 g/mL)", 98.0, 1.685 * 0.85),  # Special handling for concentration
        1: ("Sodium Dihydrogen Phosphate (NaH2PO4)", 119.98, None),
        2: ("Disodium Hydrogen Phosphate (Na2HPO4)", 141.96, None),
        3: ("Trisodium Phosphate (Na3PO4)", 163.94, None)
    },
    "Acetate": {
        0: ("Acetic Acid (Glacial liquid, d=1.05 g/mL)", 60.05, 1.05),
        1: ("Sodium Acetate (CH3COONa)", 82.03, None)
    },
    "Tris": {
        0: ("Tris Hydrochloride (Tris-HCl)", 157.60, None),
        1: ("Tris Base", 121.14, None)
    },
    "HEPES": {
        0: ("HEPES Free Acid", 238.30, None),
        1: ("HEPES Sodium Salt", 260.30, None)
    },
    "Bicarbonate": {
        0: ("Carbonic Acid (CO2 dissolved)", 62.03, None),
        1: ("Sodium Bicarbonate (NaHCO3)", 84.01, None),
        2: ("Sodium Carbonate (Na2CO3)", 105.99, None)
    },
    "Citrate": {
        0: ("Citric Acid", 192.12, None),
        1: ("Monosodium Citrate", 214.11, None),
        2: ("Disodium Citrate", 236.09, None),
        3: ("Trisodium Citrate", 258.07, None)
    },
    "Glycine": {
        0: ("Glycine Hydrochloride", 111.53, None),
        1: ("Glycine Free Base", 75.07, None),
        2: ("Sodium Glycinate", 97.05, None)
    },
    "MES": {
        0: ("MES Free Acid", 195.20, None),
        1: ("MES Sodium Salt", 217.20, None)
    },
    "MOPS": {
        0: ("MOPS Free Acid", 209.30, None),
        1: ("MOPS Sodium Salt", 231.20, None)
    },
    "Borate": {
        0: ("Boric Acid", 61.83, None),
        1: ("Sodium Borate (NaB(OH)4)", 101.83, None)
    },
    "Cacodylate": {
        0: ("Cacodylic Acid", 138.01, None),
        1: ("Sodium Cacodylate Trihydrate", 214.03, None)
    },
    "PIPES": {
        0: ("PIPES Free Acid", 302.37, None),
        1: ("PIPES Disodium Salt", 346.33, None)
    }
}

class BufferEngine:
    def __init__(self, buffer_catalog: list[dict]):
        self.catalog = {b["name"]: b for b in buffer_catalog}

    def solve_formulation(self, input_params: BufferFormulationInput, target_volume_l: float = 1.0) -> BufferFormulationResult:
        buffer_name = input_params.buffer_name
        if buffer_name not in self.catalog:
            raise ValueError(f"Buffer '{buffer_name}' not found in catalog.")
            
        buffer_data = self.catalog[buffer_name]
        thermo_pKas = buffer_data["pKa"]
        acid_charge = buffer_data["acid_charge"]
        C_T = input_params.concentration
        target_ph = input_params.target_ph
        temp_c = input_params.temperature_c
        
        # Calculate added salts ionic strength
        # E.g., NaCl adds Na+ and Cl-, CaCl2 adds Ca2+ and 2 Cl-
        added_conc = []
        added_charges = []
        
        # Mapping salt names to ionic constituent concentrations
        for salt in input_params.added_salts:
            name = salt.name.upper()
            conc = salt.concentration
            if name == "NACL":
                added_conc.extend([conc, conc])
                added_charges.extend([1, -1])
            elif name == "KCL":
                added_conc.extend([conc, conc])
                added_charges.extend([1, -1])
            elif name == "CACL2":
                added_conc.extend([conc, conc * 2])
                added_charges.extend([2, -1])
            elif name == "MGCL2":
                added_conc.extend([conc, conc * 2])
                added_charges.extend([2, -1])
            elif name == "MGSO4":
                added_conc.extend([conc, conc])
                added_charges.extend([2, -2])
            elif name == "NA2SO4":
                added_conc.extend([conc * 2, conc])
                added_charges.extend([1, -2])
            elif name == "KH2PO4":
                added_conc.extend([conc, conc])
                added_charges.extend([1, -1])
            elif name == "NA2HPO4":
                added_conc.extend([conc * 2, conc])
                added_charges.extend([1, -2])
            elif name == "NAHCO3":
                added_conc.extend([conc, conc])
                added_charges.extend([1, -1])
            elif name == "NA2CO3":
                added_conc.extend([conc * 2, conc])
                added_charges.extend([1, -2])
            elif name == "CA(NO3)2":
                added_conc.extend([conc, conc * 2])
                added_charges.extend([2, -1])
            elif name == "FE(NO3)3":
                added_conc.extend([conc, conc * 3])
                added_charges.extend([3, -1])
            else:
                # Fallback: assume 1:1 salt
                added_conc.extend([conc, conc])
                added_charges.extend([1, -1])
                
        I_added = calculate_ionic_strength(added_conc, added_charges)
        
        # Iteratively solve the speciation and ionic strength
        # We assume the starting form of buffer is the acid form (j=0) for titration,
        # but for speciation solving we just want the final species at target pH.
        I = I_added + 0.01  # Initial guess
        max_iter = 100
        tolerance = 1e-6
        
        activity_coeffs = {}
        apparent_pKas = []
        fractions = []
        
        for _ in range(max_iter):
            # Compute activity coefficients for z=0, 1, 2, 3
            activity_coeffs = {
                0: 1.0,
                1: get_davies_coefficient(1, I, temp_c),
                2: get_davies_coefficient(2, I, temp_c),
                3: get_davies_coefficient(3, I, temp_c)
            }
            
            # Recalculate apparent pKas
            apparent_pKas = calculate_apparent_pKas(thermo_pKas, acid_charge, activity_coeffs)
            
            # Recalculate fractions
            fractions = calculate_speciation_fractions(apparent_pKas, target_ph)
            
            # Recalculate ionic strength contribution of the buffer species
            # Species j has charge z_j = acid_charge - j
            buffer_conc = []
            buffer_charges = []
            for j, f in enumerate(fractions):
                c_j = f * C_T
                z_j = acid_charge - j
                buffer_conc.append(c_j)
                buffer_charges.append(z_j)
                
            I_buffer = calculate_ionic_strength(buffer_conc, buffer_charges)
            
            # Estimate titrant contribution to ionic strength
            # Charge balance: delta_Q = Q_final - Q_initial
            # Let's assume we titrate from the species closest to pH to avoid overestimating titrant
            # Or we titrate from the free acid form (j=0).
            # If we titrate from j=0, we add NaOH to reach target pH.
            Q_final = sum(f * C_T * (acid_charge - j) for j, f in enumerate(fractions))
            Q_initial_acid = C_T * acid_charge
            delta_Q_acid = Q_final - Q_initial_acid
            
            # Titrant concentration
            C_titrant = abs(delta_Q_acid)
            I_titrant = 0.5 * C_titrant * (1**2 + 1**2) # E.g. Na+ and OH- or Cl- and H+ (each charge 1)
            
            I_new = I_added + I_buffer + I_titrant
            
            if abs(I_new - I) < tolerance:
                I = I_new
                break
            I = I_new
            
        # Compile species concentrations
        species_concs = []
        for j, f in enumerate(fractions):
            c_j = f * C_T
            z_j = acid_charge - j
            # Determine species formula name if available
            name = f"Species H_{len(thermo_pKas)-j}A" if len(thermo_pKas) > 1 else ("HA" if j == 0 else "A-")
            if buffer_name in BUFFER_SALTS_DATABASE and j in BUFFER_SALTS_DATABASE[buffer_name]:
                name = BUFFER_SALTS_DATABASE[buffer_name][j][0].split(" (")[0]
            species_concs.append(SpeciesConcentration(
                name=name,
                charge=z_j,
                concentration=c_j,
                fraction=f
            ))
            
        # Determine titration recipe starting from the most logical salt
        # If pH < middle of buffer range, start with acid form. If pH > middle, start with basic form.
        # Let's say we always provide a titration starting from the species closest to pH.
        # But wait! A standard recipe uses the most common salt available.
        # Let's determine the starting species:
        # For a monoprotic buffer (like Tris or HEPES), we either start with Tris-HCl (acid, j=0) or Tris Base (base, j=1).
        # Let's assume we start with the acid form (j=0) for buffers with acid_charge=0, and base form (j=1) for acid_charge=1.
        # Or better: let's start with the most common salt form.
        # Let's define the default starting species index for each buffer:
        # Phosphate: start with NaH2PO4 (j=1).
        # Acetate: start with Sodium Acetate (j=1) or Acetic Acid (j=0).
        # Tris: start with Tris Base (j=1).
        # HEPES: start with HEPES Free Acid (j=0).
        # Citrate: start with Citric Acid (j=0) or Trisodium Citrate (j=3).
        default_start_index = 0
        if buffer_name == "Phosphate":
            default_start_index = 1  # NaH2PO4
        elif buffer_name == "Tris":
            default_start_index = 1  # Tris Base
        elif buffer_name == "Bicarbonate":
            default_start_index = 1  # NaHCO3
        elif buffer_name == "Glycine":
            default_start_index = 1  # Glycine Base
            
        # Calculate Titrant requirements
        z_start = acid_charge - default_start_index
        Q_start = C_T * z_start
        Q_final = sum(f * C_T * (acid_charge - j) for j, f in enumerate(fractions))
        delta_Q = Q_final - Q_start
        
        chemical = "None"
        moles_per_l = 0.0
        recipe_text = ""
        
        # MW of starting salt
        start_salt_name = f"Species {default_start_index}"
        start_salt_mw = 100.0
        is_liquid = False
        density_val = None
        
        if buffer_name in BUFFER_SALTS_DATABASE and default_start_index in BUFFER_SALTS_DATABASE[buffer_name]:
            start_salt_name, start_salt_mw, density_val = BUFFER_SALTS_DATABASE[buffer_name][default_start_index]
            is_liquid = density_val is not None
            
        mass_start = C_T * start_salt_mw * target_volume_l
        
        if delta_Q < -1e-5:
            # We need to add base (NaOH)
            chemical = "NaOH"
            moles_per_l = -delta_Q
            moles_needed = moles_per_l * target_volume_l
            # Assume 1M NaOH stock or solid NaOH
            mass_naoh = moles_needed * 39.997
            vol_naoh_1m = moles_needed * 1000.0  # mL of 1M NaOH
            recipe_text = (
                f"1. Dissolve {mass_start:.4f} g of {start_salt_name} (MW: {start_salt_mw:.2f}) in ~80% of the target volume of deionized water ({target_volume_l*0.8:.2f} L).\n"
                f"2. Add approximately {vol_naoh_1m:.2f} mL of 1.0 M NaOH (or {mass_naoh:.4f} g of solid NaOH) to adjust the pH to {target_ph:.2f}.\n"
                f"3. Add all other specified salts (NaCl, CaCl2, etc.) and stir until dissolved.\n"
                f"4. Add deionized water to bring the final volume to {target_volume_l:.2f} L. Re-verify the pH."
            )
        elif delta_Q > 1e-5:
            # We need to add acid (HCl)
            chemical = "HCl"
            moles_per_l = delta_Q
            moles_needed = moles_per_l * target_volume_l
            # Assume 1M HCl stock
            vol_hcl_1m = moles_needed * 1000.0
            recipe_text = (
                f"1. Dissolve {mass_start:.4f} g of {start_salt_name} (MW: {start_salt_mw:.2f}) in ~80% of the target volume of deionized water ({target_volume_l*0.8:.2f} L).\n"
                f"2. Add approximately {vol_hcl_1m:.2f} mL of 1.0 M HCl to adjust the pH to {target_ph:.2f}.\n"
                f"3. Add all other specified salts (NaCl, CaCl2, etc.) and stir until dissolved.\n"
                f"4. Add deionized water to bring the final volume to {target_volume_l:.2f} L. Re-verify the pH."
            )
        else:
            recipe_text = (
                f"1. Dissolve {mass_start:.4f} g of {start_salt_name} (MW: {start_salt_mw:.2f}) in ~95% of the target volume of deionized water.\n"
                f"2. Add all other specified salts and stir until dissolved.\n"
                f"3. pH is already at the target of {target_ph:.2f}. Add water to bring the final volume to {target_volume_l:.2f} L."
            )
            
        titrant = TitrantRequirement(
            chemical=chemical,
            moles_per_l=moles_per_l,
            recipe_instruction=recipe_text
        )
        
        # Calculate Direct Mix Recipe if possible (mixing the two salt forms flanking the target pH)
        # Find the two species flanking target pH (i.e. where pH is close to apparent pKa)
        # Let's find species j and j+1.
        direct_recipe = None
        if buffer_name in BUFFER_SALTS_DATABASE and len(thermo_pKas) >= 1:
            # Find the active pKa closest to target pH
            closest_pKa_idx = 0
            min_diff = abs(target_ph - apparent_pKas[0])
            for k in range(1, len(apparent_pKas)):
                diff = abs(target_ph - apparent_pKas[k])
                if diff < min_diff:
                    min_diff = diff
                    closest_pKa_idx = k
            
            # The two species flanking this pKa are closest_pKa_idx (acid) and closest_pKa_idx + 1 (base)
            idx_a = closest_pKa_idx
            idx_b = closest_pKa_idx + 1
            
            if idx_a in BUFFER_SALTS_DATABASE[buffer_name] and idx_b in BUFFER_SALTS_DATABASE[buffer_name]:
                name_a, mw_a, liq_a = BUFFER_SALTS_DATABASE[buffer_name][idx_a]
                name_b, mw_b, liq_b = BUFFER_SALTS_DATABASE[buffer_name][idx_b]
                
                # We normalize the fractions of these two species so they sum to 1
                f_a = fractions[idx_a]
                f_b = fractions[idx_b]
                total_f = f_a + f_b
                if total_f > 1e-4:
                    norm_f_a = f_a / total_f
                    norm_f_b = f_b / total_f
                    
                    conc_a = norm_f_a * C_T
                    conc_b = norm_f_b * C_T
                    
                    mass_a = conc_a * mw_a * target_volume_l
                    mass_b = conc_b * mw_b * target_volume_l
                    
                    # Special printing if a component is glacial liquid acetic acid or 85% phosphoric acid
                    label_a = f"{mass_a:.4f} g"
                    label_b = f"{mass_b:.4f} g"
                    if liq_a is not None:
                        vol_a = mass_a / liq_a
                        label_a = f"{vol_a:.4f} mL"
                    if liq_b is not None:
                        vol_b = mass_b / liq_b
                        label_b = f"{vol_b:.4f} mL"
                        
                    direct_recipe_text = (
                        f"1. Measure {label_a} of {name_a} and {label_b} of {name_b}.\n"
                        f"2. Dissolve both in ~90% of the target volume of deionized water ({target_volume_l*0.9:.2f} L).\n"
                        f"3. Add all other specified salts (NaCl, CaCl2, etc.) and stir until dissolved.\n"
                        f"4. Add deionized water to bring the final volume to {target_volume_l:.2f} L. Verify pH is {target_ph:.2f}."
                    )
                    
                    direct_recipe = DirectMixRecipe(
                        salt_a_name=name_a,
                        salt_a_mass_g_per_l=mass_a,
                        salt_b_name=name_b,
                        salt_b_mass_g_per_l=mass_b,
                        recipe_text=direct_recipe_text
                    )
                    
        # Calculate Buffer Capacity Beta
        # beta = 2.303 * ([H+] + [OH-] + sum( C_T * (Ka' * [H+]) / (Ka' + [H+])^2 ))
        H_act = 10**(-target_ph)
        gamma_1 = activity_coeffs.get(1, 1.0)
        h_conc = H_act / gamma_1
        oh_conc = 1e-14 / (H_act * gamma_1)
        
        beta_sum = h_conc + oh_conc
        for apparent_pKa in apparent_pKas:
            Ka = 10**(-apparent_pKa)
            term = (Ka * H_act) / ((Ka + H_act) ** 2)
            beta_sum += C_T * term
            
        beta = 2.303 * beta_sum
        
        return BufferFormulationResult(
            input_params=input_params,
            real_ph=target_ph, # Iterative solver adjusts activity-based quantities to make the real pH match target
            ionic_strength=I,
            activity_coefficients={k: v for k, v in activity_coeffs.items()},
            species_concentrations=species_concs,
            titration_recipe=titrant,
            direct_mix_recipe=direct_recipe,
            precipitation_risks=[],
            rule_findings=[],
            overall_risk_score=0.0,
            overall_risk_level="Safe",
            buffer_capacity=beta
        )
