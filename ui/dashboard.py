import os
import json
import sys
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Dict, Any

# Adjust paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.session import BufferFormulationInput, SaltInput, BufferFormulationResult
from core.chemistry.buffer_engine import BufferEngine
from core.chemistry.ksp_predictor import PrecipitationPredictor
from core.chemistry.ion_pool import build_ion_pool_from_salts, add_buffer_species_to_ion_pool
from core.expert.knowledge_base import KnowledgeBase
from core.expert.rule_engine import RuleEngine
from core.expert.conflict_resolver import ConflictResolver
from core.ai.fuzzy_classifier import FuzzyRiskClassifier
from core.ai.recommender import FormulationRecommender
from core.ai.optimizer import ConstraintOptimizer

app = FastAPI(title="Intelligent Buffer Wizard Dashboard")

# Mount static files for custom premium styling
static_dir = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Initialize backends
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

catalog_path = os.path.join(PROJECT_ROOT, "data", "buffer_catalog.json")
with open(catalog_path, "r") as f:
    catalog_data = json.load(f)["buffers"]
    
ksp_path = os.path.join(PROJECT_ROOT, "data", "ksp_database.json")
with open(ksp_path, "r") as f:
    ksp_data = json.load(f)["salts"]
    
templates_path = os.path.join(PROJECT_ROOT, "data", "media_templates.json")
with open(templates_path, "r") as f:
    templates_data = json.load(f)["templates"]
    
rules_dir = os.path.join(PROJECT_ROOT, "data", "rules")

engine = BufferEngine(catalog_data)
ksp_predictor = PrecipitationPredictor(ksp_data)
kb = KnowledgeBase(rules_dir)
rule_engine = RuleEngine(kb)
resolver = ConflictResolver()
fuzzy_classifier = FuzzyRiskClassifier()
recommender = FormulationRecommender(templates_data)
optimizer = ConstraintOptimizer(engine, ksp_predictor)

class OptimizeRequest(BaseModel):
    target_ph: float
    added_salts: List[SaltInput]

@app.get("/api/buffers")
def get_buffers():
    return catalog_data

@app.get("/api/templates")
def get_templates():
    return templates_data

@app.post("/api/formulate", response_model=BufferFormulationResult)
def formulate_buffer(form_input: BufferFormulationInput):
    try:
        # Solve physical chemistry
        res = engine.solve_formulation(form_input, 1.0)
        
        # Build ion pool
        ion_pool = build_ion_pool_from_salts(form_input.added_salts)
        add_buffer_species_to_ion_pool(ion_pool, res.species_concentrations)
                
        # Ksp Precipitation calculations
        res.precipitation_risks = ksp_predictor.predict_all_risks(ion_pool, res.ionic_strength, form_input.temperature_c)
        max_si = max([p.saturation_index for p in res.precipitation_risks]) if res.precipitation_risks else -5.0
        
        # Expert system rule execution
        state = {
            "buffer_type": form_input.buffer_name,
            "target_ph": form_input.target_ph,
            "concentration": form_input.concentration,
            "ions_present": list(ion_pool.keys()),
            "environment": form_input.environment,
            "application": form_input.application,
            "exposure": form_input.exposure,
            "ion_pool": ion_pool
        }
        findings = rule_engine.evaluate_formulation(state)
        
        # Resolve findings
        resolved_findings, expert_score, overall_level = resolver.resolve_conflicts(findings)
        res.rule_findings = resolved_findings
        
        # Apply fuzzy logic merge
        fuzzy_score, fuzzy_level = fuzzy_classifier.evaluate_risk(max_si, expert_score)
        res.overall_risk_score = fuzzy_score
        res.overall_risk_level = fuzzy_level
        
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/optimize")
def optimize_formulation(req: OptimizeRequest):
    try:
        # Find best buffer recommendations
        salts_dict = [{"name": s.name, "concentration": s.concentration} for s in req.added_salts]
        recs = optimizer.recommend_best_buffers(req.target_ph, salts_dict)
        return recs
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/", response_class=HTMLResponse)
def get_dashboard():
    # Serve index.html template file
    template_path = os.path.join(os.path.dirname(__file__), "templates", "index.html")
    with open(template_path, "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)
