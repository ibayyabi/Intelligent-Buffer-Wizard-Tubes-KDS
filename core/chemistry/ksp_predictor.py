import math
from models.session import PrecipitationRisk
from core.chemistry.ionic_strength import get_davies_coefficient

class PrecipitationPredictor:
    def __init__(self, ksp_database: list[dict]):
        self.ksp_database = ksp_database

    def _resolve_ion_concentration(self, ion_name: str, ion_pool: dict[str, float]) -> float:
        conc = ion_pool.get(ion_name, 0.0)
        if conc > 0.0:
            return conc

        if ion_name != "OH-":
            return 0.0

        if ion_pool.get("pH", 0.0) > 0.0:
            h_concentration = 10 ** (-ion_pool["pH"])
            return 1e-14 / h_concentration

        h_concentration = ion_pool.get("H+", 0.0)
        if h_concentration > 0.0:
            return 1e-14 / h_concentration

        return 0.0

    def predict_all_risks(
        self, 
        ion_pool: dict[str, float], 
        ionic_strength: float, 
        temp_c: float = 25.0
    ) -> list[PrecipitationRisk]:
        """
        Calculates Saturation Index (SI) and risk for all salts in the database.
        SI = log10(Q_activity / Ksp)
        """
        risks = []
        
        # Calculate activity coefficients for charges 1, 2, 3
        gammas = {
            0: 1.0,
            1: get_davies_coefficient(1, ionic_strength, temp_c),
            2: get_davies_coefficient(2, ionic_strength, temp_c),
            3: get_davies_coefficient(3, ionic_strength, temp_c),
            -1: get_davies_coefficient(1, ionic_strength, temp_c),
            -2: get_davies_coefficient(2, ionic_strength, temp_c),
            -3: get_davies_coefficient(3, ionic_strength, temp_c)
        }
        
        for salt in self.ksp_database:
            salt_name = salt["name"]
            formula = salt["formula"]
            ksp = salt["ksp"]
            ions = salt["ions"]
            
            # Check if all ions are present
            all_present = True
            q_activity = 1.0
            
            for ion in ions:
                ion_name = ion["name"]
                charge = ion["charge"]
                stoich = ion["stoich"]
                
                # Retrieve concentration of this ion, including explicit OH- inference from pH or H+.
                conc = self._resolve_ion_concentration(ion_name, ion_pool)
                
                if conc <= 0.0:
                    all_present = False
                    break
                    
                # Activity = concentration * gamma
                gamma = gammas.get(charge, 1.0)
                if abs(charge) > 3:
                    gamma = get_davies_coefficient(abs(charge), ionic_strength, temp_c)
                    
                activity = conc * gamma
                q_activity *= (activity ** stoich)
                
            if not all_present:
                continue
                
            # Saturation Index
            si = math.log10(q_activity / ksp)
            
            # Classify risk level
            if si < -0.2:
                risk_level = "Safe"
            elif si < 0.0:
                risk_level = "Warning"
            elif si < 1.0:
                risk_level = "Risk"
            else:
                risk_level = "Critical"
                
            # Predict induction time
            if si <= 0.0:
                induction_time = "Stable (No precipitation)"
            elif si < 0.2:
                induction_time = "Days / Weeks"
            elif si < 0.5:
                induction_time = "Hours"
            elif si < 1.0:
                induction_time = "Minutes (10 - 60 min)"
            else:
                induction_time = "Immediate (Seconds)"
                
            risks.append(PrecipitationRisk(
                salt_name=salt_name,
                formula=formula,
                saturation_index=si,
                risk_level=risk_level,
                induction_time=induction_time
            ))
            
        return risks
