import os
from models.session import BufferFormulationResult


class HTMLReporter:
    def _load_shared_dashboard_css(self) -> str:
        """Load shared dashboard stylesheet so report and dashboard use one source of truth."""
        reporter_dir = os.path.dirname(os.path.abspath(__file__))
        css_path = os.path.join(reporter_dir, "static", "styles.css")
        with open(css_path, "r", encoding="utf-8") as f:
            return f.read()

    def generate_report(self, result: BufferFormulationResult, output_path: str):
        """Generate HTML report using the same design system as dashboard."""
        buffer_name = result.input_params.buffer_name
        target_ph = result.input_params.target_ph
        conc_m = result.input_params.concentration
        temp_c = result.input_params.temperature_c

        shared_css = self._load_shared_dashboard_css()

        risk_badge_class = {
            "Safe": "badge-safe",
            "Warning": "badge-warning",
            "Risk": "badge-risk",
            "Critical": "badge-critical",
        }.get(result.overall_risk_level, "badge-warning")

        # Preparation protocols
        recipe_html_parts = []
        if result.direct_mix_recipe:
            recipe_html_parts.append(
                f"""
                <div class="recipe-block">
                    <div class="recipe-title">🧪 Method A: Direct Salt Mixing (Recommended)</div>
                    <pre>{result.direct_mix_recipe.recipe_text}</pre>
                    <ul class="recipe-list">
                        <li><strong>{result.direct_mix_recipe.salt_a_name}</strong>: {result.direct_mix_recipe.salt_a_mass_g_per_l:.4f} g/L</li>
                        <li><strong>{result.direct_mix_recipe.salt_b_name}</strong>: {result.direct_mix_recipe.salt_b_mass_g_per_l:.4f} g/L</li>
                    </ul>
                </div>
                """
            )

        if result.titration_recipe:
            recipe_html_parts.append(
                f"""
                <div class="recipe-block">
                    <div class="recipe-title">⚗️ Method B: pH Titration</div>
                    <pre>{result.titration_recipe.recipe_instruction}</pre>
                    <ul class="recipe-list">
                        <li><strong>Titrant</strong>: {result.titration_recipe.chemical}</li>
                        <li><strong>Required Concentration</strong>: {result.titration_recipe.moles_per_l:.4f} M (moles/L)</li>
                    </ul>
                </div>
                """
            )

        recipe_html = "".join(recipe_html_parts) or "<p style='color:var(--text-secondary);'>No preparation protocol available.</p>"

        # Speciation table rows
        species_rows = ""
        for s in result.species_concentrations:
            species_rows += (
                f"<tr>"
                f"<td>{s.name}</td>"
                f"<td>{s.charge}</td>"
                f"<td>{s.concentration:.6f} M</td>"
                f"<td>{(s.fraction * 100):.2f}%</td>"
                f"</tr>"
            )

        # Activity coefficients table rows
        act_rows = ""
        for charge, coeff in sorted(result.activity_coefficients.items()):
            act_rows += f"<tr><td>Charge ±{charge}</td><td>{coeff:.4f}</td></tr>"

        # Precipitation rows
        precip_rows = ""
        if not result.precipitation_risks:
            precip_rows = (
                "<tr><td colspan='5' style='text-align:center; color:var(--risk-safe);'>"
                "No precipitation risk detected."
                "</td></tr>"
            )
        else:
            for p in result.precipitation_risks:
                badge_class = {
                    "Safe": "badge-safe",
                    "Warning": "badge-warning",
                    "Risk": "badge-risk",
                    "Critical": "badge-critical",
                }.get(p.risk_level, "badge-warning")
                precip_rows += (
                    f"<tr>"
                    f"<td>{p.salt_name}</td>"
                    f"<td><code>{p.formula}</code></td>"
                    f"<td>{p.saturation_index:.4f}</td>"
                    f"<td><span class='badge {badge_class}'>{p.risk_level}</span></td>"
                    f"<td>{p.induction_time}</td>"
                    f"</tr>"
                )

        # Rule findings
        if not result.rule_findings:
            rules_html = "<p style='color:var(--risk-safe);'>✓ No compatibility, toxicity, or safety conflicts found.</p>"
        else:
            rules_parts = []
            for r in result.rule_findings:
                rules_parts.append(
                    f"""
                    <div class="warning-strip {r.severity.lower()}">
                        <div class="warning-header">
                            <div class="warning-title">{r.rule_name}</div>
                            <span class="badge { {'low':'badge-safe','medium':'badge-warning','high':'badge-risk','critical':'badge-critical'}.get(r.severity.lower(),'badge-warning') }">{r.severity.upper()}</span>
                        </div>
                        <p class="warning-desc"><strong>Conflict:</strong> {r.message}</p>
                        <p class="warning-action"><strong>Remedy:</strong> {r.action}</p>
                    </div>
                    """
                )
            rules_html = "".join(rules_parts)

        # Simple capacity-vs-pH curve for quick visual (same data concept as old reporter)
        ph_points = []
        capacity_points = []
        for ph in [x * 0.1 for x in range(int((target_ph - 2) * 10), int((target_ph + 2) * 10) + 1)]:
            h_conc = 10 ** (-ph)
            beta_val = 2.303 * (h_conc + 1e-14 / h_conc)
            for _ in range(3):
                ka = 10 ** (-target_ph)
                beta_val += 2.303 * conc_m * (ka * h_conc) / ((ka + h_conc) ** 2)
            ph_points.append(f"{ph:.1f}")
            capacity_points.append(round(beta_val, 6))

        html_content = f"""<!DOCTYPE html>
<html lang=\"en\">
<head>
    <meta charset=\"UTF-8\">
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\">
    <title>Intelligent Buffer Wizard Report - {buffer_name}</title>

    <link rel=\"preconnect\" href=\"https://fonts.googleapis.com\">
    <link rel=\"preconnect\" href=\"https://fonts.gstatic.com\" crossorigin>
    <link href=\"https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Syne:wght@700;800&family=JetBrains+Mono:wght@400;500;700&display=swap\" rel=\"stylesheet\">
    <script src=\"https://cdn.jsdelivr.net/npm/chart.js\"></script>

    <style>
{shared_css}

/* Report-only layout wrappers while keeping shared design tokens/components */
.report-shell {{
    max-width: 1400px;
    margin: 0 auto;
    padding: 32px;
}}

.report-meta {{
    color: var(--text-secondary);
    font-size: 0.9rem;
    margin-top: 8px;
}}

.report-grid {{
    display: grid;
    grid-template-columns: 1fr;
    gap: 24px;
}}

@media (min-width: 1200px) {{
    .report-grid.two-col {{
        grid-template-columns: 1fr 1fr;
    }}
}}

.chart-container {{
    height: 360px;
}}

.chart-container canvas {{
    width: 100% !important;
    height: 100% !important;
}}

.footer-note {{
    margin-top: 24px;
    color: var(--text-muted);
    font-size: 0.85rem;
}}
    </style>
</head>
<body>
    <nav class=\"navbar\">
        <div class=\"navbar-brand\">Intelligent Buffer Wizard</div>
        <div><span class=\"badge {risk_badge_class}\">REPORT EXPORT</span></div>
    </nav>

    <div class=\"report-shell\">
        <div class=\"panel\" style=\"margin-bottom:24px;\">
            <h2>Formulation Summary</h2>
            <div class=\"report-meta\">Buffer: <strong>{buffer_name}</strong> • Target pH: <strong>{target_ph:.2f}</strong> • Conc: <strong>{conc_m:.4f} M</strong> • Temp: <strong>{temp_c:.1f} °C</strong></div>

            <div class=\"metrics-row\" style=\"margin-top:24px;\">
                <div class=\"metric-card\">
                    <div class=\"metric-label\">Ionic Strength (I)</div>
                    <div class=\"metric-value\">{result.ionic_strength:.4f} M</div>
                </div>
                <div class=\"metric-card teal\">
                    <div class=\"metric-label\">Buffer Capacity (β)</div>
                    <div class=\"metric-value\">{result.buffer_capacity:.4f}</div>
                </div>
                <div class=\"metric-card mint\">
                    <div class=\"metric-label\">Safety Rating</div>
                    <div class=\"metric-value\" style=\"font-size:1.3rem;\">{result.overall_risk_score:.1f}% ({result.overall_risk_level.upper()})</div>
                </div>
            </div>
        </div>

        <div class=\"report-grid two-col\">
            <div class=\"panel\">
                <h2>📋 Preparation Protocols</h2>
                {recipe_html}
            </div>

            <div class=\"panel\">
                <h2>🧪 Chemical Speciation</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Species Name</th>
                            <th>Charge</th>
                            <th>Concentration (M)</th>
                            <th>Fraction (%)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {species_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div class=\"report-grid two-col\" style=\"margin-top:24px;\">
            <div class=\"panel\">
                <h2>📊 Simulation Plot</h2>
                <div class=\"chart-container\">
                    <canvas id=\"capacityChart\"></canvas>
                </div>
            </div>

            <div class=\"panel\">
                <h2>Activity Coefficients (γ)</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Ionic Charge Magnitude</th>
                            <th>Activity Coefficient (γ)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {act_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div class=\"panel\" style=\"margin-top:24px;\">
            <h2>Precipitation Predictor (Ksp Checks)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Salt Compound</th>
                        <th>Formula</th>
                        <th>Saturation Index (SI)</th>
                        <th>Risk Assessment</th>
                        <th>Nucleation Estimate</th>
                    </tr>
                </thead>
                <tbody>
                    {precip_rows}
                </tbody>
            </table>
        </div>

        <div class=\"panel\" style=\"margin-top:24px;\">
            <h2>Expert Diagnostics & Safety Warnings</h2>
            {rules_html}
        </div>

        <p class=\"footer-note\">Generated by Intelligent Buffer Wizard. Advisory use only; validate in laboratory conditions.</p>
    </div>

    <script>
        const ctx = document.getElementById('capacityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {ph_points},
                datasets: [{{
                    label: 'Buffer Capacity (Beta)',
                    data: {capacity_points},
                    borderColor: '#d9925e',
                    backgroundColor: 'rgba(217, 146, 94, 0.10)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.25,
                    pointRadius: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        title: {{ display: true, text: 'pH Value', color: '#94a3b8' }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }},
                    y: {{
                        title: {{ display: true, text: 'Capacity (Beta)', color: '#94a3b8' }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: '#94a3b8' }}
                    }}
                }},
                plugins: {{
                    legend: {{ labels: {{ color: '#f8fafc' }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""

        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"HTML report successfully written to: {output_path}")
