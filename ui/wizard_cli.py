import os
import json
import sys
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from rich.text import Text
from rich.prompt import Prompt, Confirm, FloatPrompt, IntPrompt

# Fix import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from models.session import BufferFormulationInput, SaltInput
from core.chemistry.buffer_engine import BufferEngine
from core.chemistry.ksp_predictor import PrecipitationPredictor
from core.expert.knowledge_base import KnowledgeBase
from core.expert.rule_engine import RuleEngine
from core.expert.conflict_resolver import ConflictResolver
from core.ai.fuzzy_classifier import FuzzyRiskClassifier
from core.ai.recommender import FormulationRecommender
from core.ai.optimizer import ConstraintOptimizer
from ui.reporter import HTMLReporter

console = Console()


def build_header_panel() -> Panel:
    return Panel(
        Text("🔮 Intelligent Buffer Wizard 🔮\nExpert Chemistry Solution Designer", justify="center", style="bold white"),
        box=box.DOUBLE,
        border_style="blue",
        expand=False,
    )


class WizardCLI:
    def __init__(self):
        self.project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        
        # Load Databases
        catalog_path = os.path.join(self.project_root, "data", "buffer_catalog.json")
        with open(catalog_path, "r") as f:
            self.catalog_data = json.load(f)["buffers"]
            
        ksp_path = os.path.join(self.project_root, "data", "ksp_database.json")
        with open(ksp_path, "r") as f:
            self.ksp_data = json.load(f)["salts"]
            
        templates_path = os.path.join(self.project_root, "data", "media_templates.json")
        with open(templates_path, "r") as f:
            self.templates_data = json.load(f)["templates"]
            
        rules_dir = os.path.join(self.project_root, "data", "rules")
        
        # Initialize engines
        self.engine = BufferEngine(self.catalog_data)
        self.ksp_predictor = PrecipitationPredictor(self.ksp_data)
        self.kb = KnowledgeBase(rules_dir)
        self.rule_engine = RuleEngine(self.kb)
        self.resolver = ConflictResolver()
        self.fuzzy_classifier = FuzzyRiskClassifier()
        self.recommender = FormulationRecommender(self.templates_data)
        self.optimizer = ConstraintOptimizer(self.engine, self.ksp_predictor)

    def _ask_int_in_range(self, prompt_text: str, min_value: int, max_value: int) -> int:
        while True:
            value = IntPrompt.ask(prompt_text)
            if min_value <= value <= max_value:
                return value
            console.print(f"[bold yellow]Input harus antara {min_value} sampai {max_value}.[/bold yellow]")

    def run(self):
        console.clear()
        console.print(build_header_panel())
        
        # 1. Main Action Selection
        action = Prompt.ask(
            "What would you like to do?",
            choices=["Formulate Buffer", "Search Media Templates", "Buffer Optimizer", "Exit"],
            default="Formulate Buffer"
        )
        
        if action == "Exit":
            console.print("[bold yellow]Goodbye![/bold yellow]")
            return
        elif action == "Search Media Templates":
            self.run_templates_flow()
        elif action == "Buffer Optimizer":
            self.run_optimizer_flow()
        else:
            self.run_formulation_flow()

    def run_templates_flow(self):
        console.print(Panel("🔍 Search and Match Media Templates", style="bold cyan"))
        
        # Show all templates
        table = Table(title="Available Media Templates")
        table.add_column("No", style="dim")
        table.add_column("Template Name", style="bold white")
        table.add_column("Buffer Type", style="cyan")
        table.add_column("pH", style="green")
        
        for idx, t in enumerate(self.templates_data):
            table.add_row(str(idx + 1), t["name"], t["buffer_name"], f"{t['target_ph']:.1f}")
            
        console.print(table)
        
        t_choice = self._ask_int_in_range(
            "Enter template number to view details",
            1,
            len(self.templates_data),
        )
        selected_template = self.templates_data[t_choice - 1]
        
        # Formulate based on template
        console.print(f"\n[bold green]Matching details for: {selected_template['name']}[/bold green]")
        added_salts = [SaltInput(name=k, concentration=v) for k, v in selected_template["salts"].items()]
        
        form_input = BufferFormulationInput(
            buffer_name=selected_template["buffer_name"],
            target_ph=selected_template["target_ph"],
            concentration=selected_template["buffer_concentration"],
            added_salts=added_salts
        )
        
        self.process_and_display(form_input)

    def run_optimizer_flow(self):
        console.print(Panel("⚙️ Constraint-Based Buffer Optimizer", style="bold cyan"))
        
        target_ph = FloatPrompt.ask("Enter target pH")
        
        # Simple inputs for salt addition
        added_salts_list = []
        if Confirm.ask("Do you have added salts in the solution?"):
            while True:
                salt_name = Prompt.ask("Enter salt name (e.g. NaCl, CaCl2) or 'done' to finish").strip()
                if salt_name.lower() == 'done':
                    break
                salt_conc = FloatPrompt.ask(f"Enter concentration of {salt_name} in Molar (M)")
                added_salts_list.append({"name": salt_name, "concentration": salt_conc})
                
        # 1. Recommend best buffers
        console.print("\n[bold yellow]Calculating optimal buffer systems...[/bold yellow]")
        recommendations = self.optimizer.recommend_best_buffers(target_ph, added_salts_list)
        
        if not recommendations:
            console.print("[bold red]No suitable buffers found for this pH in the catalog![/bold red]")
            return
            
        table = Table(title=f"Optimal Buffer Recommendations for pH {target_ph}")
        table.add_column("Rank", style="dim")
        table.add_column("Buffer Name", style="bold white")
        table.add_column("Score (0-100)", style="bold green")
        table.add_column("Toxicity", style="yellow")
        table.add_column("Cost Level", style="cyan")
        table.add_column("Max Sat. Index", style="magenta")
        table.add_column("Capacity (Beta)", style="green")
        
        for idx, rec in enumerate(recommendations):
            table.add_row(
                str(idx + 1),
                rec["name"],
                f"{rec['suitability_score']:.1f}",
                rec["toxicity_level"],
                rec["cost_level"],
                f"{rec['max_saturation_index']:.4f}",
                f"{rec['buffer_capacity']:.4f}"
            )
        console.print(table)
        
        # Pick one and optimize concentration
        choice = Prompt.ask("Would you like to optimize concentration for one of these buffers?", choices=["Yes", "No"], default="Yes")
        if choice == "Yes":
            buf_name = Prompt.ask("Enter the buffer name to optimize", choices=[r["name"] for r in recommendations])
            max_c = FloatPrompt.ask("Enter maximum allowed concentration in Molar (M)", default=0.150)
            console.print(f"\n[bold yellow]Optimizing concentration of {buf_name} to avoid precipitation...[/bold yellow]")
            opt_conc = self.optimizer.optimize_buffer_concentration(buf_name, target_ph, added_salts_list, max_conc=max_c)
            console.print(f"[bold green]Optimal safe concentration found: {opt_conc*1000:.2f} mM ({opt_conc:.4f} M)[/bold green]")
            
            # Formulate the optimized selection
            salts_input = [SaltInput(name=s["name"], concentration=s["concentration"]) for s in added_salts_list]
            form_input = BufferFormulationInput(
                buffer_name=buf_name,
                target_ph=target_ph,
                concentration=opt_conc,
                added_salts=salts_input
            )
            self.process_and_display(form_input)

    def run_formulation_flow(self):
        console.print(Panel("🧪 Interactive Step-by-Step Buffer Formulation", style="bold cyan"))
        
        # Select Buffer
        console.print("[bold white]Available Buffer Systems:[/bold white]")
        for idx, b in enumerate(self.catalog_data):
            console.print(f"  {idx+1}. [bold cyan]{b['name']}[/bold cyan] (pH range: {b['range'][0]} - {b['range'][1]})")
            
        buf_idx = self._ask_int_in_range(
            "\nSelect buffer system (number)",
            1,
            len(self.catalog_data),
        )
        selected_buffer = self.catalog_data[buf_idx - 1]
        buffer_name = selected_buffer["name"]
        
        # Input pH
        min_ph, max_ph = selected_buffer["range"]
        target_ph = FloatPrompt.ask(f"Enter target pH ({min_ph} - {max_ph})", default=sum(selected_buffer["pKa"])/len(selected_buffer["pKa"]))
        
        # Validate range warning
        if not (min_ph <= target_ph <= max_ph):
            console.print(f"[bold yellow]Warning: pH {target_ph} is outside the standard buffering range of {buffer_name} ({min_ph} - {max_ph}).[/bold yellow]")
            if not Confirm.ask("Proceed anyway?"):
                return
                
        # Input concentration
        concentration = FloatPrompt.ask("Enter total buffer concentration in Molar (M) (e.g. 0.05 for 50 mM)", default=0.05)
        
        # Input temperature
        temp_c = FloatPrompt.ask("Enter working temperature (°C)", default=25.0)
        
        # Added Salts
        added_salts = []
        if Confirm.ask("Do you want to add external salts/compounds (e.g., NaCl, CaCl2) to this solution?"):
            while True:
                salt_name = Prompt.ask("Enter salt name (NaCl, KCl, CaCl2, MgCl2, MgSO4) or type 'done' to finish").strip()
                if salt_name.lower() == 'done':
                    break
                salt_conc = FloatPrompt.ask(f"Enter concentration of {salt_name} in Molar (M)")
                added_salts.append(SaltInput(name=salt_name, concentration=salt_conc))
                
        # Environment, application, light exposure
        env = Prompt.ask("Is this an open or closed system (re: CO2 outgassing)?", choices=["closed", "open"], default="closed")
        app = Prompt.ask("Select application context", choices=["biochemistry", "cell_culture", "gel_electrophoresis"], default="biochemistry")
        exp = Prompt.ask("What is the light exposure of the solution?", choices=["dark", "light"], default="dark")
        
        # Create formulation input Pydantic model
        form_input = BufferFormulationInput(
            buffer_name=buffer_name,
            target_ph=target_ph,
            concentration=concentration,
            temperature_c=temp_c,
            added_salts=added_salts,
            environment=env,
            application=app,
            exposure=exp
        )
        
        self.process_and_display(form_input)

    def process_and_display(self, form_input: BufferFormulationInput):
        console.print("\n[bold yellow]Calculating speciation & chemical balances...[/bold yellow]")
        
        try:
            # 1. Run Buffer solver
            res = self.engine.solve_formulation(form_input, 1.0)
            
            # 2. Extract ion pool for Ksp calculations
            ion_pool = {}
            for salt in form_input.added_salts:
                n = salt.name.upper()
                c = salt.concentration
                if n == "NACL":
                    ion_pool["Na+"] = ion_pool.get("Na+", 0.0) + c
                    ion_pool["Cl-"] = ion_pool.get("Cl-", 0.0) + c
                elif n == "KCL":
                    ion_pool["K+"] = ion_pool.get("K+", 0.0) + c
                    ion_pool["Cl-"] = ion_pool.get("Cl-", 0.0) + c
                elif n == "CACL2":
                    ion_pool["Ca2+"] = ion_pool.get("Ca2+", 0.0) + c
                    ion_pool["Cl-"] = ion_pool.get("Cl-", 0.0) + c * 2
                elif n == "MGCL2":
                    ion_pool["Mg2+"] = ion_pool.get("Mg2+", 0.0) + c
                    ion_pool["Cl-"] = ion_pool.get("Cl-", 0.0) + c * 2
                elif n == "MGSO4":
                    ion_pool["Mg2+"] = ion_pool.get("Mg2+", 0.0) + c
                    ion_pool["SO42-"] = ion_pool.get("SO42-", 0.0) + c
                    
            # Inject buffer species into ion pool
            for spec in res.species_concentrations:
                spec_name = spec.name
                if "HPO4" in spec_name or "Hydrogen Phosphate" in spec_name:
                    ion_pool["HPO42-"] = spec.concentration
                elif "PO4" in spec_name or "Trisodium Phosphate" in spec_name:
                    ion_pool["PO43-"] = spec.concentration
                elif "CO3" in spec_name or "Carbonate" in spec_name:
                    ion_pool["CO32-"] = spec.concentration
                elif "HCO3" in spec_name or "Bicarbonate" in spec_name:
                    ion_pool["HCO3-"] = spec.concentration
            
            # 3. Ksp calculations
            res.precipitation_risks = self.ksp_predictor.predict_all_risks(ion_pool, res.ionic_strength, form_input.temperature_c)
            max_si = max([p.saturation_index for p in res.precipitation_risks]) if res.precipitation_risks else -5.0
            
            # 4. Expert system rules
            # Prepare state dictionary for expert system
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
            
            findings = self.rule_engine.evaluate_formulation(state)
            
            # 5. Resolve conflicts & compute overall score
            resolved_findings, expert_score, overall_level = self.resolver.resolve_conflicts(findings)
            
            res.rule_findings = resolved_findings
            
            # 6. Apply Fuzzy Risk Logic to merge SI and Expert Score
            fuzzy_score, fuzzy_level = self.fuzzy_classifier.evaluate_risk(max_si, expert_score)
            res.overall_risk_score = fuzzy_score
            res.overall_risk_level = fuzzy_level
            
            # 7. Print Results Panels
            console.print("\n" + "="*50)
            console.print(Panel(
                f"[bold white]Solution properties for {form_input.buffer_name} Buffer at pH {form_input.target_ph:.2f}[/bold white]\n\n"
                f"  Ionic Strength: [bold cyan]{res.ionic_strength:.4f} M[/bold cyan]\n"
                f"  Buffer Capacity (β): [bold green]{res.buffer_capacity:.4f}[/bold green]\n"
                f"  Overall Hazard Score: [bold]{res.overall_risk_score:.1f}% ({res.overall_risk_level})[/bold]",
                style="green" if res.overall_risk_level == "Safe" else ("yellow" if res.overall_risk_level == "Warning" else "red"),
                title="⚙️ Physical Chemistry Output"
            ))
            
            # Recipe Panel
            recipe_text = ""
            if res.direct_mix_recipe:
                recipe_text += f"[bold cyan]Method A: Salt Direct Mix (Highly Recommended)[/bold cyan]\n"
                recipe_text += f"{res.direct_mix_recipe.recipe_text}\n\n"
            if res.titration_recipe:
                recipe_text += f"[bold cyan]Method B: Titration from starting salt[/bold cyan]\n"
                recipe_text += f"{res.titration_recipe.recipe_instruction}\n"
                
            console.print(Panel(recipe_text.strip(), title="📋 Formulation Recipe Protocols"))
            
            # Speciation Table
            spec_table = Table(title="Speciation Distribution")
            spec_table.add_column("Species Name", style="cyan")
            spec_table.add_column("Charge", justify="right")
            spec_table.add_column("Concentration (M)", justify="right")
            spec_table.add_column("Fraction (%)", justify="right")
            
            for s in res.species_concentrations:
                spec_table.add_row(s.name, str(s.charge), f"{s.concentration:.6f}", f"{s.fraction * 100:.2f}%")
            console.print(spec_table)
            
            # Ksp risks table
            if res.precipitation_risks:
                ksp_table = Table(title="Solubility / Precipitation Risks")
                ksp_table.add_column("Salt Name")
                ksp_table.add_column("Formula")
                ksp_table.add_column("Saturation Index (SI)")
                ksp_table.add_column("Risk Level")
                ksp_table.add_column("Induction Time")
                
                for p in res.precipitation_risks:
                    ksp_table.add_row(
                        p.salt_name, 
                        p.formula, 
                        f"{p.saturation_index:.4f}", 
                        f"[red]{p.risk_level}[/red]" if p.risk_level in ["Risk", "Critical"] else p.risk_level,
                        p.induction_time
                    )
                console.print(ksp_table)
                
            # Warnings
            if res.rule_findings:
                console.print("\n[bold red]⚠️ Diagnostic & Compatibility Warnings:[/bold red]")
                for f in res.rule_findings:
                    console.print(f"  • [bold]{f.rule_name}[/bold] ({f.severity.upper()}): {f.message}\n    [cyan]Remedy:[/cyan] {f.action}")
            else:
                console.print("\n[bold green]✓ No compatibility, toxicity, or safety conflicts found in this formulation.[/bold green]")
                
            # Similarity Recommendations
            recs = self.recommender.recommend_templates(form_input)
            if recs:
                rec_table = Table(title="AI Reference Media Comparison")
                rec_table.add_column("Closest Reference Media", style="bold white")
                rec_table.add_column("Similarity Match", style="cyan")
                rec_table.add_column("Default Buffer Type", style="dim")
                for temp, score in recs:
                    rec_table.add_row(temp["name"], f"{score*100:.1f}%", temp["buffer_name"])
                console.print(rec_table)
                
            # 8. Report Export Selection
            if Confirm.ask("Would you like to export an interactive HTML protocol report?"):
                filename = Prompt.ask("Enter report file name (e.g. report.html)", default="buffer_report.html")
                report_path = os.path.join(self.project_root, filename)
                reporter = HTMLReporter()
                reporter.generate_report(res, report_path)
                console.print(f"[bold green]Report saved to: {report_path}[/bold green]")
                
        except Exception as e:
            console.print(f"[bold red]An error occurred during solving: {e}[/bold red]")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    wizard = WizardCLI()
    wizard.run()
