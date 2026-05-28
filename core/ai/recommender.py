import math
from models.session import BufferFormulationInput

class FormulationRecommender:
    def __init__(self, templates: list[dict]):
        self.templates = templates

    def recommend_templates(self, user_input: BufferFormulationInput, top_n: int = 3) -> list[tuple[dict, float]]:
        """
        Calculates similarity between user formulation and standard templates.
        Returns a sorted list of tuples (template_dict, similarity_score).
        Similarity score is between 0.0 and 1.0.
        """
        recommendations = []
        
        user_buffer = user_input.buffer_name
        user_ph = user_input.target_ph
        user_salts = {s.name.upper(): s.concentration for s in user_input.added_salts}
        
        # Add buffer concentration as a salt-like concentration if needed
        # E.g. Phosphate
        
        for temp in self.templates:
            temp_name = temp["name"]
            temp_ph = temp["target_ph"]
            temp_buffer = temp["buffer_name"]
            temp_salts = {k.upper(): v for k, v in temp["salts"].items()}
            
            # 1. pH Similarity
            # Score decays exponentially with distance
            ph_sim = math.exp(-abs(user_ph - temp_ph))
            
            # 2. Buffer Type Similarity
            buffer_sim = 1.0 if user_buffer.lower() == temp_buffer.lower() else 0.0
            
            # 3. Salt Concentration Similarity
            # Gather all unique salts in both user_input and template
            all_salt_keys = set(user_salts.keys()).union(set(temp_salts.keys()))
            
            if not all_salt_keys:
                salt_sim = 1.0
            else:
                salt_diff_sum = 0.0
                for salt_key in all_salt_keys:
                    c_user = user_salts.get(salt_key, 0.0)
                    c_temp = temp_salts.get(salt_key, 0.0)
                    
                    max_c = max(c_user, c_temp, 1e-6)
                    salt_diff_sum += abs(c_user - c_temp) / max_c
                    
                salt_sim = math.exp(-salt_diff_sum / len(all_salt_keys))
                
            # Combined similarity score (weighted average)
            # Higher weight on buffer name matching and pH matching
            similarity = 0.3 * ph_sim + 0.4 * buffer_sim + 0.3 * salt_sim
            
            recommendations.append((temp, similarity))
            
        # Sort by similarity in descending order
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:top_n]
