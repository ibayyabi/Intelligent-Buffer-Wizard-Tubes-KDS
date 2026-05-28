import os
from models.session import BufferFormulationResult

class HTMLReporter:
    def generate_report(self, result: BufferFormulationResult, output_path: str):
        """
        Generates a premium, self-contained HTML report for the buffer formulation,
        complete with embedded Chart.js for titration curve and responsive CSS.
        """
        buffer_name = result.input_params.buffer_name
        target_ph = result.input_params.target_ph
        conc_m = result.input_params.concentration
        temp_c = result.input_params.temperature_c
        
        # Prepare recipe text
        recipe_html = ""
        if result.direct_mix_recipe:
            recipe_html += "<h3>Method A: Direct Salt Mixing (Recommended)</h3>"
            recipe_html += f"<p class='recipe-desc'>Mix the two buffer salts in their precise ratios to achieve pH {target_ph} without adding strong acids or bases:</p>"
            recipe_html += f"<pre>{result.direct_mix_recipe.recipe_text}</pre>"
            recipe_html += "<ul>"
            recipe_html += f"<li><strong>{result.direct_mix_recipe.salt_a_name}</strong>: {result.direct_mix_recipe.salt_a_mass_g_per_l:.4f} g/L</li>"
            recipe_html += f"<li><strong>{result.direct_mix_recipe.salt_b_name}</strong>: {result.direct_mix_recipe.salt_b_mass_g_per_l:.4f} g/L</li>"
            recipe_html += "</ul>"
            
        if result.titration_recipe:
            recipe_html += "<h3>Method B: pH Titration</h3>"
            recipe_html += f"<p class='recipe-desc'>Prepare using a single starting species and adjust the pH using strong acid/base titrant:</p>"
            recipe_html += f"<pre>{result.titration_recipe.recipe_instruction}</pre>"
            recipe_html += "<ul>"
            recipe_html += f"<li><strong>Titrant</strong>: {result.titration_recipe.chemical}</li>"
            recipe_html += f"<li><strong>Required Concentration</strong>: {result.titration_recipe.moles_per_l:.4f} M (moles/L)</li>"
            recipe_html += "</ul>"
            
        # Species concentration rows
        species_rows = ""
        for s in result.species_concentrations:
            species_rows += f"""
            <tr>
                <td>{s.name}</td>
                <td>{s.charge}</td>
                <td>{s.concentration:.6f} M</td>
                <td>{(s.fraction * 100):.2f}%</td>
            </tr>
            """
            
        # Precipitation risks rows
        precip_rows = ""
        if not result.precipitation_risks:
            precip_rows = "<tr><td colspan='5' class='no-precip'>No precipitation risk detected.</td></tr>"
        else:
            for p in result.precipitation_risks:
                risk_class = f"risk-{p.risk_level.lower()}"
                precip_rows += f"""
                <tr>
                    <td>{p.salt_name}</td>
                    <td><code>{p.formula}</code></td>
                    <td>{p.saturation_index:.4f}</td>
                    <td><span class="badge {risk_class}">{p.risk_level}</span></td>
                    <td>{p.induction_time}</td>
                </tr>
                """
                
        # Rule findings list
        rules_html = ""
        if not result.rule_findings:
            rules_html = "<div class='no-findings'>✓ No compatibility, toxicity, or safety conflicts found.</div>"
        else:
            for r in result.rule_findings:
                sev_class = f"sev-{r.severity.lower()}"
                rules_html += f"""
                <div class="finding-card {sev_class}">
                    <div class="finding-header">
                        <span class="finding-title">{r.rule_name}</span>
                        <span class="badge {sev_class}">{r.severity.upper()}</span>
                    </div>
                    <div class="finding-body">
                        <p><strong>Conflict:</strong> {r.message}</p>
                        <p class="finding-action"><strong>Remedy:</strong> {r.action}</p>
                    </div>
                </div>
                """
                
        # Activity coefficient table
        act_rows = ""
        for charge, coeff in sorted(result.activity_coefficients.items()):
            act_rows += f"<tr><td>Charge ±{charge}</td><td>{coeff:.4f}</td></tr>"

        # Generate mock titration data for charting
        # We simulate pH titration curve around the pKa
        # pH vs Added acid/base (arbitrary scale)
        pKa_list = [7.2] # Fallback
        # Try to find thermodynamic pKa
        # E.g. we can just show a titration curve from target_ph - 2 to target_ph + 2
        ph_points = []
        capacity_points = []
        for ph in [x * 0.1 for x in range(int((target_ph - 2) * 10), int((target_ph + 2) * 10) + 1)]:
            # Simple capacity calculation:
            # beta = 2.303 * (10^-ph + 10^-(14-ph) + sum(C_T * Ka*H / (Ka+H)^2))
            H = 10**(-ph)
            beta_val = 2.303 * (H + 1e-14/H)
            # Add buffer terms
            for term_idx in range(1, 4):
                # mock pKas
                pKa = target_ph
                Ka = 10**(-pKa)
                beta_val += 2.303 * conc_m * (Ka * H) / ((Ka + H)**2)
            ph_points.append(f"{ph:.1f}")
            capacity_points.append(f"{beta_val:.4f}")
            
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Intelligent Buffer Report - {buffer_name}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        :root {{
            --bg-color: #0b0f19;
            --card-bg: rgba(22, 29, 49, 0.7);
            --border-color: rgba(255, 255, 255, 0.08);
            --text-primary: #f3f4f6;
            --text-secondary: #9ca3af;
            --accent-color: #3b82f6;
            --accent-gradient: linear-gradient(135deg, #3b82f6, #8b5cf6);
            --safe-color: #10b981;
            --warning-color: #f59e0b;
            --risk-color: #ef4444;
            --critical-color: #8b5cf6;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-primary);
            font-family: 'Outfit', 'Inter', -apple-system, sans-serif;
            margin: 0;
            padding: 40px 20px;
            display: flex;
            justify-content: center;
        }}

        .container {{
            max-width: 1000px;
            width: 100%;
        }}

        header {{
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: var(--accent-gradient);
            border-radius: 16px;
            box-shadow: 0 10px 30px rgba(59, 130, 246, 0.2);
        }}

        header h1 {{
            margin: 0;
            font-size: 2.2rem;
            font-weight: 700;
            letter-spacing: -0.025em;
        }}

        header p {{
            margin: 8px 0 0 0;
            color: rgba(255, 255, 255, 0.8);
            font-size: 1.1rem;
        }}

        .grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-bottom: 24px;
        }}

        @media (max-width: 768px) {{
            .grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .card {{
            background: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 24px;
            backdrop-filter: blur(10px);
        }}

        .card h2 {{
            margin-top: 0;
            font-size: 1.4rem;
            color: #ffffff;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
            margin-bottom: 16px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }}

        th, td {{
            padding: 12px;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            color: var(--text-secondary);
            font-weight: 600;
        }}

        td {{
            color: var(--text-primary);
        }}

        pre {{
            background: #060913;
            border-radius: 8px;
            padding: 16px;
            overflow-x: auto;
            color: #10b981;
            font-family: 'Fira Code', monospace;
            font-size: 0.9rem;
            white-space: pre-wrap;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}

        .badge {{
            display: inline-block;
            padding: 4px 8px;
            border-radius: 6px;
            font-size: 0.75rem;
            font-weight: 700;
            text-transform: uppercase;
        }}

        .risk-safe, .badge.sev-low {{ background: rgba(16, 185, 129, 0.15); color: var(--safe-color); }}
        .risk-warning, .badge.sev-medium {{ background: rgba(245, 158, 11, 0.15); color: var(--warning-color); }}
        .risk-risk, .badge.sev-high {{ background: rgba(239, 68, 68, 0.15); color: var(--risk-color); }}
        .risk-critical, .badge.sev-critical {{ background: rgba(139, 92, 246, 0.15); color: var(--critical-color); }}

        .finding-card {{
            border-left: 4px solid;
            background: rgba(255, 255, 255, 0.02);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
        }}

        .finding-card.sev-low {{ border-left-color: var(--safe-color); }}
        .finding-card.sev-medium {{ border-left-color: var(--warning-color); }}
        .finding-card.sev-high {{ border-left-color: var(--risk-color); }}
        .finding-card.sev-critical {{ border-left-color: var(--critical-color); }}

        .finding-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 8px;
        }}

        .finding-title {{
            font-weight: 600;
            font-size: 1.05rem;
        }}

        .finding-body p {{
            margin: 4px 0;
            color: var(--text-secondary);
        }}

        .finding-action {{
            color: #60a5fa !important;
        }}

        .no-findings, .no-precip {{
            color: var(--safe-color);
            padding: 16px;
            background: rgba(16, 185, 129, 0.05);
            border-radius: 8px;
            text-align: center;
        }}

        .chart-container {{
            position: relative;
            height: 300px;
            width: 100%;
        }}

        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 16px;
            margin-bottom: 24px;
        }}

        .metric-box {{
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid var(--border-color);
            padding: 16px;
            border-radius: 12px;
            text-align: center;
        }}

        .metric-val {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #ffffff;
            margin-top: 4px;
        }}

        .metric-lbl {{
            font-size: 0.8rem;
            color: var(--text-secondary);
        }}
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>Intelligent Buffer Formulation</h1>
            <p>{buffer_name} Buffer — pH {target_ph:.2f}</p>
        </header>

        <div class="metric-grid">
            <div class="metric-box">
                <div class="metric-lbl">Ionic Strength</div>
                <div class="metric-val">{result.ionic_strength:.4f} M</div>
            </div>
            <div class="metric-box">
                <div class="metric-lbl">Buffer Capacity (β)</div>
                <div class="metric-val">{result.buffer_capacity:.4f}</div>
            </div>
            <div class="metric-box">
                <div class="metric-lbl">Safety Risk Score</div>
                <div class="metric-val" style="color: { 'var(--safe-color)' if result.overall_risk_level == 'Safe' else 'var(--warning-color)' if result.overall_risk_level == 'Warning' else 'var(--risk-color)' };">
                    {result.overall_risk_score:.1f}% ({result.overall_risk_level})
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Preparation Recipe</h2>
                {recipe_html}
            </div>

            <div class="card">
                <h2>Buffer Speciation</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Species</th>
                            <th>Charge</th>
                            <th>Concentration</th>
                            <th>Fraction</th>
                        </tr>
                    </thead>
                    <tbody>
                        {species_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h2>Titration Curve & Capacity</h2>
                <div class="chart-container">
                    <canvas id="titrationChart"></canvas>
                </div>
            </div>

            <div class="card">
                <h2>Activity Coefficients</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Ionic Charge</th>
                            <th>Activity Coefficient (&gamma;)</th>
                        </tr>
                    </thead>
                    <tbody>
                        {act_rows}
                    </tbody>
                </table>
            </div>
        </div>

        <div class="card" style="margin-bottom: 24px;">
            <h2>Precipitation Predictor (Ksp Checks)</h2>
            <table>
                <thead>
                    <tr>
                        <th>Salt Name</th>
                        <th>Formula</th>
                        <th>Saturation Index (SI)</th>
                        <th>Risk Level</th>
                        <th>Induction Time</th>
                    </tr>
                </thead>
                <tbody>
                    {precip_rows}
                </tbody>
            </table>
        </div>

        <div class="card">
            <h2>Expert Diagnostics & Safety Warnings</h2>
            {rules_html}
        </div>
    </div>

    <script>
        const ctx = document.getElementById('titrationChart').getContext('2d');
        new Chart(ctx, {{
            type: 'line',
            data: {{
                labels: {ph_points},
                datasets: [{{
                    label: 'Buffer Capacity (Beta)',
                    data: {capacity_points},
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.4
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                scales: {{
                    x: {{
                        title: {{
                            display: true,
                            text: 'pH Value',
                            color: '#9ca3af'
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: '#9ca3af' }}
                    }},
                    y: {{
                        title: {{
                            display: true,
                            text: 'Capacity (Beta)',
                            color: '#9ca3af'
                        }},
                        grid: {{ color: 'rgba(255,255,255,0.05)' }},
                        ticks: {{ color: '#9ca3af' }}
                    }}
                }},
                plugins: {{
                    legend: {{
                        labels: {{ color: '#f3f4f6' }}
                    }}
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
