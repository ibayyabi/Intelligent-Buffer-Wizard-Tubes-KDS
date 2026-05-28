from models.session import RuleFinding
from typing import List, Tuple

class ConflictResolver:
    SEVERITY_ORDER = {
        "critical": 0,
        "high": 1,
        "medium": 2,
        "low": 3
    }
    
    SEVERITY_WEIGHTS = {
        "critical": 40.0,
        "high": 25.0,
        "medium": 10.0,
        "low": 2.0
    }

    def resolve_conflicts(self, findings: List[RuleFinding]) -> Tuple[List[RuleFinding], float, str]:
        """
        Prioritizes, sorts, and filters expert system findings.
        Calculates a hazard score and overall risk level.
        """
        # Sort findings: critical first, then high, medium, low
        sorted_findings = sorted(
            findings, 
            key=lambda f: self.SEVERITY_ORDER.get(f.severity, 4)
        )
        
        # Deduplicate findings by rule_id
        seen_ids = set()
        deduped_findings = []
        for f in sorted_findings:
            if f.rule_id not in seen_ids:
                seen_ids.add(f.rule_id)
                deduped_findings.append(f)
                
        # Calculate risk score
        score = 0.0
        for f in deduped_findings:
            score += self.SEVERITY_WEIGHTS.get(f.severity, 0.0)
            
        score = min(score, 100.0)
        
        # Determine overall risk level
        if any(f.severity == "critical" for f in deduped_findings):
            overall_level = "Critical"
        elif any(f.severity == "high" for f in deduped_findings):
            overall_level = "Risk"
        elif any(f.severity == "medium" for f in deduped_findings):
            overall_level = "Warning"
        else:
            overall_level = "Safe"
            
        return deduped_findings, score, overall_level
