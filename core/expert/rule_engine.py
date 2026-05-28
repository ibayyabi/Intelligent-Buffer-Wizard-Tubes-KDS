from core.expert.knowledge_base import KnowledgeBase, Rule
from models.session import RuleFinding

class RuleEngine:
    def __init__(self, knowledge_base: KnowledgeBase):
        self.kb = knowledge_base

    def evaluate_formulation(self, state: dict) -> list[RuleFinding]:
        """
        Evaluates the current solution state against all rules in the knowledge base.
        Returns a list of RuleFinding objects.
        """
        findings = []
        for rule in self.kb.rules:
            if self._evaluate_condition(rule.condition, state):
                findings.append(RuleFinding(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=rule.consequence["message"],
                    action=rule.consequence["action"]
                ))
        return findings

    def _evaluate_condition(self, condition: dict, state: dict) -> bool:
        """
        Checks if a rule's condition is met by the formulation state.
        """
        # 1. Check buffer_type
        if "buffer_type" in condition:
            if state.get("buffer_type") != condition["buffer_type"]:
                return False

        # 2. Check ions_present: all ions in condition must be present in state
        if "ions_present" in condition:
            state_ions = state.get("ions_present", [])
            for ion in condition["ions_present"]:
                if ion not in state_ions:
                    return False

        # 3. Check ph_min and ph_max
        if "ph_min" in condition:
            if state.get("target_ph", 7.0) < condition["ph_min"]:
                return False
        if "ph_max" in condition:
            if state.get("target_ph", 7.0) > condition["ph_max"]:
                return False

        # 4. Check environment (e.g. open/closed)
        if "environment" in condition:
            if state.get("environment") != condition["environment"]:
                return False

        # 5. Check application (e.g. cell_culture)
        if "application" in condition:
            if state.get("application") != condition["application"]:
                return False

        # 6. Check exposure (e.g. light/dark)
        if "exposure" in condition:
            if state.get("exposure") != condition["exposure"]:
                return False

        # 7. Check concentration threshold
        if "concentration_gt" in condition:
            if state.get("concentration", 0.0) <= condition["concentration_gt"]:
                return False

        # 8. Check concentration product threshold for precipitation
        if "concentration_product_min" in condition:
            ions = condition.get("ions_present", [])
            if len(ions) >= 2:
                ion_pool = state.get("ion_pool", {})
                prod = 1.0
                for ion in ions:
                    prod *= ion_pool.get(ion, 0.0)
                if prod < condition["concentration_product_min"]:
                    return False

        return True
