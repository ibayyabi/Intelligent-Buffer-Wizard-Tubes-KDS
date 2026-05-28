# Intelligent Buffer Wizard — Technical Overview

Proyek ini jauh lebih dari sekadar kalkulator matematis. Berikut breakdown arsitektur komprehensifnya:

---

## 🧠 Lapisan Sistem (Architecture Layers)

```
┌─────────────────────────────────────────────────────┐
│                  PRESENTATION LAYER                  │
│         CLI (Rich/Textual) / Web UI (Streamlit)      │
├─────────────────────────────────────────────────────┤
│                APPLICATION LAYER                     │
│    Expert System Engine │ Wizard Flow │ Reporter     │
├──────────────┬──────────────────────┬───────────────┤
│  DOMAIN      │   CHEMISTRY ENGINE   │  AI/ML LAYER  │
│  KNOWLEDGE   │  Buffer Calc, Ksp,   │  Fuzzy Logic  │
│  BASE        │  Ionic Strength,     │  Rule Engine  │
│  (JSON/YAML) │  Activity Coeff.     │  Predictor    │
├──────────────┴──────────────────────┴───────────────┤
│                   DATA LAYER                         │
│    SQLite / JSON DB │ ChemData │ History & Sessions  │
└─────────────────────────────────────────────────────┘
```

---

## 🔬 Bukan Hanya Matematika — Ini yang Membedakannya

### 1. **Chemistry Engine** (Inti Perhitungan)
Ini memang fondasi, tapi levelnya jauh di atas kalkulator biasa:

```python
# Bukan sekadar pH = pKa + log([A-]/[HA])
# Tapi memperhitungkan:

class BufferEngine:
    def calculate_real_pH(self, buffer: BufferSystem) -> float:
        """
        Koreksi aktivitas ion menggunakan Davies Equation,
        bukan Henderson-Hasselbalch naif
        """
        ionic_strength = self._calc_ionic_strength()
        activity_coeff = self._davies_equation(ionic_strength)
        # Iterasi konvergen karena I bergantung pada spesiasi
        return self._iterative_solve(activity_coeff)

    def _davies_equation(self, I: float) -> float:
        # γ = 10^(-A·z²·(√I/(1+√I) - 0.3I))
        ...
```

### 2. **Expert System / Rule-Based Engine**
Sistem pakar berbasis aturan kimia yang disimpan terstruktur:

```python
# knowledge_base/rules.yaml
rules:
  - id: R001
    name: "Phosphate-Calcium Conflict"
    condition:
      ions_present: ["Ca2+", "Mg2+"]
      buffer_type: "phosphate"
    consequence:
      risk: "HIGH_PRECIPITATION"
      action: "SUGGEST_HEPES_OR_TRIS"
      ksp_check: ["Ca3(PO4)2", "MgHPO4"]

  - id: R002
    name: "CO2-Bicarbonate Equilibrium"
    condition:
      buffer: "bicarbonate"
      environment: "open_system"
    consequence:
      warning: "pH drift due to CO2 outgassing"
      correction: "pCO2_adjustment_required"
```

```python
class ExpertEngine:
    def diagnose(self, formulation: dict) -> List[Expert Finding]:
        fired_rules = []
        for rule in self.knowledge_base.rules:
            if self._evaluate_condition(rule, formulation):
                fired_rules.append(self._fire_rule(rule))
        return self._prioritize_conflicts(fired_rules)
```

### 3. **Ksp Precipitation Predictor**
Multi-ion, bukan single-pair:

```python
class PrecipitationPredictor:
    def predict_all_risks(self, ion_pool: dict) -> PrecipRiskMap:
        """
        Cek ion product (Q) vs Ksp untuk SEMUA pasangan ion
        dalam larutan kompleks secara simultan
        """
        risks = {}
        for salt, ksp_data in self.ksp_database.items():
            Q = self._calc_ion_product(salt, ion_pool)
            saturation_index = math.log10(Q / ksp_data['ksp'])
            risks[salt] = {
                'SI': saturation_index,          # < 0: aman
                'status': self._classify(SI),    # > 0: presipitasi
                'induction_time': self._predict_nucleation_time(SI)
            }
        return PrecipRiskMap(risks)
```

### 4. **AI/ML Layer — Ini yang Membuat "Intelligent"**

```python
# Fuzzy Logic untuk klasifikasi risiko yang tidak binary
class FuzzyRiskClassifier:
    """
    Daripada: "presipitasi YA/TIDAK"
    Gunakan:  "risiko rendah/sedang/tinggi/kritis"
    dengan membership functions
    """

# Supervised Learning dari data historis
class FormulationRecommender:
    """
    Ditraining dari dataset formulasi buffer yang sudah terbukti
    (PBS, HBSS, MEM, DMEM, dll)
    Memberikan rekomendasi berbasis similarity
    """

# Constraint Solver
class ConstraintOptimizer:
    """
    Optimasi multi-objektif:
    - Maksimalkan kapasitas buffer
    - Minimalkan toksisitas
    - Minimalkan biaya reagen
    - Hindari zona presipitasi
    """
```

---

## 📦 Stack Teknologi Python

| Layer | Library | Fungsi |
|---|---|---|
| **Chemistry** | `chempy`, `sympy` | Spesiasi kimia, persamaan simbolik |
| **Numerik** | `scipy`, `numpy` | Solver iteratif, optimasi |
| **Expert System** | `experta` / custom | Rule engine, inference |
| **Fuzzy Logic** | `scikit-fuzzy` | Klasifikasi risiko non-binary |
| **ML/Rekomendasi** | `scikit-learn` | KNN similarity, clustering |
| **Database** | `SQLite` + `SQLAlchemy` | Ksp DB, session history |
| **Visualisasi** | `matplotlib`, `plotly` | pH curve, risk heatmap |
| **UI Terminal** | `rich`, `textual` | TUI interaktif |
| **Web UI** | `streamlit` | Dashboard opsional |
| **Validasi** | `pydantic` | Schema validasi input |
| **Report** | `reportlab`/`jinja2` | PDF/HTML export |

---

## 🗂️ Struktur Proyek

```
intelligent_buffer_wizard/
├── core/
│   ├── chemistry/
│   │   ├── buffer_engine.py       # Henderson-Hasselbalch + koreksi aktivitas
│   │   ├── ksp_predictor.py       # Saturation Index, multi-ion
│   │   ├── speciation.py          # Distribusi spesies kimia
│   │   └── ionic_strength.py      # Davies/Debye-Hückel
│   ├── expert/
│   │   ├── rule_engine.py         # Inference engine
│   │   ├── knowledge_base.py      # Loader rules YAML
│   │   └── conflict_resolver.py   # Prioritas konflik
│   └── ai/
│       ├── fuzzy_classifier.py    # Fuzzy risk
│       ├── recommender.py         # Formulasi similarity
│       └── optimizer.py           # Multi-objective opt
├── data/
│   ├── ksp_database.json          # ~200+ garam
│   ├── buffer_catalog.json        # pKa, range, kompatibilitas
│   ├── media_templates.json       # PBS, HBSS, MEM, DMEM...
│   └── rules/
│       ├── compatibility.yaml
│       ├── precipitation.yaml
│       └── toxicity.yaml
├── ui/
│   ├── wizard_cli.py              # Step-by-step TUI
│   ├── dashboard.py               # Streamlit web
│   └── reporter.py                # PDF/HTML output
├── models/
│   └── session.py                 # Pydantic schemas
└── tests/
    └── ...                        # Unit + integration tests
```

---

## 🎯 Fitur Unggulan yang Membuat Proyek Ini Menarik

1. **Wizard Mode** → User dipandu langkah demi langkah seperti setup wizard
2. **Real-time Conflict Detection** → Peringatan instan saat ion konflik diinput
3. **Visual pH Titration Curve** → Plot interaktif kapasitas buffer
4. **Precipitation Risk Heatmap** → Matrix ion vs ion dengan color coding
5. **Media Template Library** → 20+ media kultur siap pakai (PBS, DMEM, dll)
6. **"What-If" Simulator** → "Bagaimana jika suhu naik 10°C? pH bergeser berapa?"
7. **PDF Report Generator** → Laporan lengkap dengan protokol pembuatan
8. **Session History & Comparison** → Bandingkan beberapa formulasi
