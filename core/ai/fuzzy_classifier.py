class FuzzyRiskClassifier:
    """
    A custom Fuzzy Logic Risk Classifier.
    Maps Saturation Index (SI) and Expert System Hazard Score (H)
    to fuzzy membership functions and defuzzifies to obtain a unified risk level.
    """
    
    def _triangular_membership(self, x: float, a: float, b: float, c: float) -> float:
        if x <= a or x >= c:
            return 0.0
        if a < x <= b:
            return (x - a) / (b - a)
        if b < x < c:
            return (c - x) / (c - b)
        return 0.0

    def _trapezoidal_membership(self, x: float, a: float, b: float, c: float, d: float) -> float:
        if x <= a or x >= d:
            return 0.0
        if b <= x <= c:
            return 1.0
        if a < x < b:
            return (x - a) / (b - a)
        if c < x < d:
            return (d - x) / (d - c)
        return 0.0

    def evaluate_risk(self, max_si: float, expert_score: float) -> tuple[float, str]:
        # 1. Saturation Index membership functions
        # safe: (-inf, -inf, -0.5, 0.0)
        s_safe = 1.0 if max_si <= -0.5 else (0.0 if max_si >= 0.0 else -max_si / 0.5)
        # warning: (-0.5, -0.2, -0.1, 0.05)
        s_warn = self._trapezoidal_membership(max_si, -0.5, -0.2, -0.1, 0.05)
        # risk: (0.0, 0.2, 0.6, 1.0)
        s_risk = self._trapezoidal_membership(max_si, 0.0, 0.2, 0.6, 1.0)
        # critical: (0.8, 1.2, inf, inf)
        s_crit = 0.0 if max_si <= 0.8 else (1.0 if max_si >= 1.2 else (max_si - 0.8) / 0.4)

        # 2. Expert Score membership functions (range 0 to 100)
        # safe: [0, 0, 10, 25]
        h_safe = 1.0 if expert_score <= 10.0 else (0.0 if expert_score >= 25.0 else (25.0 - expert_score) / 15.0)
        # warning: [10, 20, 30, 45]
        h_warn = self._trapezoidal_membership(expert_score, 10.0, 20.0, 30.0, 45.0)
        # risk: [35, 50, 65, 75]
        h_risk = self._trapezoidal_membership(expert_score, 35.0, 50.0, 65.0, 75.0)
        # critical: [70, 85, 100, 100]
        h_crit = 0.0 if expert_score <= 70.0 else (1.0 if expert_score >= 85.0 else (expert_score - 70.0) / 15.0)

        # 3. Combine fuzzy inputs using max (fuzzy OR)
        mu_safe = max(s_safe, h_safe)
        mu_warn = max(s_warn, h_warn)
        mu_risk = max(s_risk, h_risk)
        mu_crit = max(s_crit, h_crit)

        # 4. Defuzzify using singleton weights (Centroid method)
        # Safe=5, Warning=35, Risk=65, Critical=95
        w_safe = 5.0
        w_warn = 35.0
        w_risk = 65.0
        w_crit = 95.0

        numerator = (mu_safe * w_safe) + (mu_warn * w_warn) + (mu_risk * w_risk) + (mu_crit * w_crit)
        denominator = mu_safe + mu_warn + mu_risk + mu_crit

        if denominator < 1e-5:
            # Fallback based on raw max values
            score = max(expert_score, min(max_si * 50.0 + 30.0, 100.0))
            score = max(0.0, score)
        else:
            score = numerator / denominator

        # Map fuzzy score back to linguistic labels
        if score < 25.0:
            level = "Safe"
        elif score < 55.0:
            level = "Warning"
        elif score < 85.0:
            level = "Risk"
        else:
            level = "Critical"

        return score, level
