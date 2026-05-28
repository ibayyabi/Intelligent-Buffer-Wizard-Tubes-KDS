from core.expert.conflict_resolver import ConflictResolver
from core.expert.knowledge_base import KnowledgeBase
from core.expert.rule_engine import RuleEngine
from models.session import RuleFinding


def make_rule_engine(rules_dir):
    return RuleEngine(KnowledgeBase(str(rules_dir)))


def test_phosphate_calcium_magnesium_rule_fires_above_ph_6(rules_dir):
    engine = make_rule_engine(rules_dir)

    findings = engine.evaluate_formulation({
        "buffer_type": "Phosphate",
        "target_ph": 7.4,
        "ions_present": ["Ca2+", "Mg2+"],
    })

    rule_ids = {finding.rule_id for finding in findings}
    assert "COMP_001" in rule_ids


def test_bicarbonate_open_system_rule_fires(rules_dir):
    engine = make_rule_engine(rules_dir)

    findings = engine.evaluate_formulation({
        "buffer_type": "Bicarbonate",
        "environment": "open",
        "ions_present": [],
    })

    rule_ids = {finding.rule_id for finding in findings}
    assert "COMP_002" in rule_ids


def test_cacodylate_toxicity_rule_fires_as_critical(rules_dir):
    engine = make_rule_engine(rules_dir)

    findings = engine.evaluate_formulation({
        "buffer_type": "Cacodylate",
        "ions_present": [],
    })

    matching = [finding for finding in findings if finding.rule_id == "TOX_001"]
    assert len(matching) == 1
    assert matching[0].severity == "critical"


def test_conflict_resolver_sorts_deduplicates_and_scores_findings():
    resolver = ConflictResolver()
    findings = [
        RuleFinding(
            rule_id="LOW_001",
            rule_name="Low",
            severity="low",
            message="Low message",
            action="Low action",
        ),
        RuleFinding(
            rule_id="CRIT_001",
            rule_name="Critical",
            severity="critical",
            message="Critical message",
            action="Critical action",
        ),
        RuleFinding(
            rule_id="HIGH_001",
            rule_name="High",
            severity="high",
            message="High message",
            action="High action",
        ),
        RuleFinding(
            rule_id="HIGH_001",
            rule_name="High duplicate",
            severity="high",
            message="Duplicate message",
            action="Duplicate action",
        ),
    ]

    resolved, score, level = resolver.resolve_conflicts(findings)

    assert [finding.severity for finding in resolved] == ["critical", "high", "low"]
    assert [finding.rule_id for finding in resolved].count("HIGH_001") == 1
    assert score == 67.0
    assert level == "Critical"
