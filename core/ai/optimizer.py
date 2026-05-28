import math
from models.session import BufferFormulationInput, SaltInput
from core.chemistry.buffer_engine import BufferEngine
from core.chemistry.ksp_predictor import PrecipitationPredictor
from core.chemistry.ion_pool import build_ion_pool_from_salts, add_buffer_species_to_ion_pool

class ConstraintOptimizer:
    def __init__(self, buffer_engine: BufferEngine, precip_predictor: PrecipitationPredictor):
        self.engine = buffer_engine
        self.precip_predictor = precip_predictor
        
        # Relative metrics: (toxicity [1=Safe to 10=Critical], cost_factor [1=Low to 15=Very High])
        self.buffer_metrics = {
            "Phosphate": (1.0, 1.0),
            "Acetate": (1.0, 1.0),
            "Bicarbonate": (1.0, 1.0),
            "Glycine": (1.0, 1.0),
            "Citrate": (1.0, 1.5),
            "HEPES": (1.0, 8.0),
            "MES": (1.0, 10.0),
            "MOPS": (1.0, 10.0),
            "PIPES": (1.0, 12.0),
            "Tris": (2.5, 2.0),
            "Borate": (5.0, 2.0),
            "Cacodylate": (10.0, 12.0)
        }

    def recommend_best_buffers(self, target_ph: float, added_salts: list[dict], target_volume_l: float = 1.0) -> list[dict]:
        """
        Evaluates all buffers in the catalog and ranks them based on:
        1. Buffer Capacity proximity to pH (pK_a matching)
        2. Toxicity score
        3. Cost factor
        4. Precipitation risks
        """
        results = []
        salts_input = [SaltInput(name=s["name"], concentration=s["concentration"]) for s in added_salts]
        
        for name, buffer_data in self.engine.catalog.items():
            # Check if pH is in range of this buffer
            ph_min, ph_max = buffer_data["range"]
            if not (ph_min <= target_ph <= ph_max):
                continue
                
            # Default test concentration: 20 mM
            test_input = BufferFormulationInput(
                buffer_name=name,
                target_ph=target_ph,
                concentration=0.020,
                added_salts=salts_input
            )
            
            try:
                # Solve formulation to check capacity and precipitation
                res = self.engine.solve_formulation(test_input, target_volume_l)
                
                # Check precipitation risk
                ion_pool = build_ion_pool_from_salts(test_input.added_salts)
                add_buffer_species_to_ion_pool(ion_pool, res.species_concentrations)
                        
                precip_risks = self.precip_predictor.predict_all_risks(ion_pool, res.ionic_strength, 25.0)
                max_si = max([r.saturation_index for r in precip_risks]) if precip_risks else -5.0
                
                # Fetch metrics
                toxicity, cost = self.buffer_metrics.get(name, (2.0, 3.0))
                
                # Score components (lower score is better suitability)
                # 1. Capacity score: distance of pH from closest apparent pKa
                pKa_diffs = [abs(target_ph - pKa) for pKa in res.activity_coefficients.get(0, 1.0) * 0.0 + res.buffer_capacity * 0.0 + 1.0] # Dummy lookup
                # Let's find closest thermodynamic pKa
                closest_pKa = min(buffer_data["pKa"], key=lambda x: abs(target_ph - x))
                ph_dist = abs(target_ph - closest_pKa)
                
                capacity_penalty = ph_dist * 20.0
                toxicity_penalty = (toxicity - 1.0) * 15.0
                cost_penalty = (cost - 1.0) * 5.0
                
                # Heavy penalty if max_si > 0 (precipitation likely)
                precip_penalty = 100.0 if max_si >= 0.0 else 0.0
                if -0.2 <= max_si < 0.0:
                    precip_penalty = 30.0
                    
                suitability_score = 100.0 - (capacity_penalty + toxicity_penalty + cost_penalty + precip_penalty)
                suitability_score = max(0.0, suitability_score)
                
                results.append({
                    "name": name,
                    "suitability_score": suitability_score,
                    "buffer_capacity": res.buffer_capacity,
                    "max_saturation_index": max_si,
                    "toxicity_level": "Safe" if toxicity <= 1.0 else ("Medium" if toxicity <= 4.0 else "Critical"),
                    "cost_level": "Low" if cost <= 2.0 else ("Medium" if cost <= 8.0 else "High"),
                    "notes": buffer_data["notes"]
                })
            except Exception as e:
                # If solver fails, skip
                print(f"Skipping buffer {name} due to calculation error: {e}")
                continue
                
        results.sort(key=lambda x: x["suitability_score"], reverse=True)
        return results

    def optimize_buffer_concentration(
        self, 
        buffer_name: str, 
        target_ph: float, 
        added_salts: list[dict], 
        min_conc: float = 0.005, 
        max_conc: float = 0.200
    ) -> float:
        """
        Finds the maximum concentration within limits that avoids precipitation (SI < 0)
        and balances capacity.
        """
        salts_input = [SaltInput(name=s["name"], concentration=s["concentration"]) for s in added_salts]
        
        # Simple bisection search to find the optimal concentration
        low = min_conc
        high = max_conc
        best_conc = min_conc
        
        for _ in range(12):  # 12 iterations gives excellent precision (range / 2^12)
            mid = (low + high) / 2.0
            test_input = BufferFormulationInput(
                buffer_name=buffer_name,
                target_ph=target_ph,
                concentration=mid,
                added_salts=salts_input
            )
            
            try:
                res = self.engine.solve_formulation(test_input, 1.0)
                
                ion_pool = build_ion_pool_from_salts(test_input.added_salts)
                add_buffer_species_to_ion_pool(ion_pool, res.species_concentrations)
                        
                precip_risks = self.precip_predictor.predict_all_risks(ion_pool, res.ionic_strength, 25.0)
                max_si = max([r.saturation_index for r in precip_risks]) if precip_risks else -5.0
                
                # If no precipitation risk, we can try higher concentration
                if max_si < -0.05:
                    best_conc = mid
                    low = mid
                else:
                    # Too close to precipitation, lower concentration
                    high = mid
            except Exception:
                # On error, assume unstable and decrease concentration
                high = mid
                
        return best_conc
