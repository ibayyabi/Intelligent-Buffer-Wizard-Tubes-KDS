def test_core_classes_importable():
    from core.ai.fuzzy_classifier import FuzzyRiskClassifier
    from core.ai.optimizer import ConstraintOptimizer
    from core.ai.recommender import FormulationRecommender
    from core.chemistry.buffer_engine import BufferEngine
    from core.chemistry.ksp_predictor import PrecipitationPredictor
    from core.expert.knowledge_base import KnowledgeBase
    from core.expert.rule_engine import RuleEngine
    from ui.reporter import HTMLReporter

    assert BufferEngine is not None
    assert PrecipitationPredictor is not None
    assert KnowledgeBase is not None
    assert RuleEngine is not None
    assert FuzzyRiskClassifier is not None
    assert FormulationRecommender is not None
    assert ConstraintOptimizer is not None
    assert HTMLReporter is not None
