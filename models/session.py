from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Literal

class SaltInput(BaseModel):
    name: str = Field(..., description="Name of the salt or ion added, e.g. 'NaCl', 'CaCl2'")
    concentration: float = Field(..., description="Concentration in Molar (M)")

class BufferFormulationInput(BaseModel):
    buffer_name: str = Field(..., description="Name of the buffer system, e.g. 'Phosphate'")
    target_ph: float = Field(..., description="Target pH of the solution")
    concentration: float = Field(..., description="Total concentration of the buffer system in Molar (M)")
    temperature_c: float = Field(25.0, description="Temperature in Celsius")
    added_salts: List[SaltInput] = Field(default_factory=list, description="List of other salts added to the formulation")
    environment: Literal["closed", "open"] = Field("closed", description="Environment type for bicarbonate systems")
    application: str = Field("biochemistry", description="Application context, e.g., 'cell_culture', 'gel_electrophoresis'")
    exposure: Literal["dark", "light"] = Field("dark", description="Exposure to light")

class SpeciesConcentration(BaseModel):
    name: str = Field(..., description="Name/formula of the species")
    charge: int = Field(..., description="Electrical charge of the species")
    concentration: float = Field(..., description="Concentration of the species in Molar (M)")
    fraction: float = Field(..., description="Fraction of the total buffer concentration")

class TitrantRequirement(BaseModel):
    chemical: Literal["HCl", "NaOH", "None"] = Field(..., description="Titrant chemical needed")
    moles_per_l: float = Field(..., description="Moles of titrant needed per Liter of solution")
    recipe_instruction: str = Field(..., description="Human-readable recipe instructions for titration")

class PrecipitationRisk(BaseModel):
    salt_name: str = Field(..., description="Name of the compound")
    formula: str = Field(..., description="Chemical formula")
    saturation_index: float = Field(..., description="Saturation Index (log10(Q/Ksp))")
    risk_level: Literal["Safe", "Warning", "Risk", "Critical"] = Field(..., description="Risk level classification")
    induction_time: str = Field(..., description="Estimated nucleation/induction time")

class RuleFinding(BaseModel):
    rule_id: str = Field(..., description="Identifier of the rule")
    rule_name: str = Field(..., description="Name of the rule")
    severity: Literal["low", "medium", "high", "critical"] = Field(..., description="Severity level of the conflict")
    message: str = Field(..., description="Warning message detailing the conflict")
    action: str = Field(..., description="Suggested correction or action")

class DirectMixRecipe(BaseModel):
    salt_a_name: str
    salt_a_mass_g_per_l: float
    salt_b_name: str
    salt_b_mass_g_per_l: float
    recipe_text: str

class BufferFormulationResult(BaseModel):
    input_params: BufferFormulationInput = Field(..., description="The inputs used to generate this formulation")
    real_ph: float = Field(..., description="Calculated actual pH, corrected for ionic activity")
    ionic_strength: float = Field(..., description="Total ionic strength of the solution in M")
    activity_coefficients: Dict[int, float] = Field(..., description="Activity coefficients keyed by ionic charge absolute value")
    species_concentrations: List[SpeciesConcentration] = Field(..., description="Detailed speciation breakdown")
    titration_recipe: Optional[TitrantRequirement] = Field(None, description="Recipe for preparation via titration")
    direct_mix_recipe: Optional[DirectMixRecipe] = Field(None, description="Recipe for preparation via mixing salt forms directly")
    precipitation_risks: List[PrecipitationRisk] = Field(default_factory=list, description="Calculated precipitation risks")
    rule_findings: List[RuleFinding] = Field(default_factory=list, description="Fired expert system warnings")
    overall_risk_score: float = Field(..., description="Calculated numerical risk score [0, 100]")
    overall_risk_level: Literal["Safe", "Warning", "Risk", "Critical"] = Field(..., description="Overall classified risk level")
    buffer_capacity: float = Field(..., description="Buffer capacity beta (dC_base / dpH)")

class SessionHistory(BaseModel):
    history: List[BufferFormulationResult] = Field(default_factory=list, description="List of previous formulations in the current session")
