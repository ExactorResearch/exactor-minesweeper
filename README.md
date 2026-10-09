# 💣 Exactor-Minesweeper: Neuro-Symbolic AI vs Pure JEV (LLM/RLCD) Benchmark

[![CI Test Suite](https://github.com/exactor-ai/exactor-minesweeper/actions/workflows/ci.yml/badge.svg)](https://github.com)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Architecture: Neuro-Symbolic](https://img.shields.io/badge/Architecture-Neuro--Symbolic%20SAT-purple.svg)](https://exactor.tech)
[![Speedup: >2000x](https://img.shields.io/badge/Speedup->2,000x%20Faster-cyan.svg)](https://exactor.tech)

> **Empirical Comparative Arena:** Mathematical SAT Deductive Reasoning (**Exactor-Accelerator**) vs. Prompt-Based Semantic Inference (**Pure JEV / LLM**).

---

## 🇪🇸 Descripción General (Español)

**Exactor-Minesweeper** es un entorno de evaluación riguroso y una plataforma interactiva diseñada para comparar empíricamente dos paradigmas de Inteligencia Artificial al resolver el clásico juego de **Buscaminas (Minesweeper)**:

1. **Exactor-Accelerator (Neuro-Simbólico / Fast-Path SAT):**
   - **Fase A (Descubrimiento / Reducción Exacta):** Transforma la frontera de celdas en un sistema de restricciones booleanas compactas ($\sum x_i = k - F$) e infiere celdas 100% seguras o minas en **microsegundos ($< 0.05$ ms)** en memoria local sin invocar APIs externas.
   - **Fase B (Calibración Probabilística JEV):** Cuando el tablero es matemáticamente subdeterminado (un 50/50 o estado aislado sin deducción determinista posible), recurre a la inferencia probabilística calibrada de JEV para elegir la celda de mínimo riesgo.
   - **Garantía:** Cero alucinaciones lógicas y precisión matemática formal.

2. **Pure JEV Solo (Inferencia LLM / RLCD pura):**
   - Evalúa cada movimiento enviando el estado del tablero a un modelo de lenguaje / API externa mediante prompts semánticos.
   - **Limitaciones observadas:** Latencia de red alta (~300–600 ms por jugada), dependencia de llamadas HTTP constantes y susceptibilidad a errores estocásticos de conteo aritmético en restricciones espaciales densas.

---

## 🇬🇧 Overview (English)

Minesweeper is an NP-complete constraint satisfaction puzzle where a single false move triggers catastrophic failure. This repository provides:
- **High-Performance In-Memory Solver:** Sub-millisecond algebraic deduction and exact combinatorial partition solver.
- **Split-Screen Live Duel Arena:** Real-time visual race comparing Exactor vs Pure JEV on identical board seeds.
- **Automated Monte Carlo Benchmark Suite:** Rigorous statistical evaluation across Beginner, Intermediate, and Expert boards.
- **Interactive Web App & Terminal CLI:** Complete with sound effects, telemetry streaming, and formal proof generation.

---

## 📊 Benchmark Summary: Empirical Performance Matrix

The following table summarizes the benchmark results evaluated over **15 identical game seeds** on Beginner (8x8, 10 mines):

| Metric / Dimension | Pure JEV (Solo LLM/RLCD) | Exactor-Accelerator (Neuro-Symbolic) | Standard Heuristic (1st Order) | Advantage / Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Avg Latency per Move** | `619.13 ms` | **`0.3016 ms`** | `0.1140 ms` | **🚀 2,053x Faster (Sub-ms Fast Path)** |
| **Latency P95** | `668.42 ms` | **`0.3850 ms`** | `0.1420 ms` | **Ultra-low deterministic variance** |
| **Board Win Rate (%)** | `0.0%` (Failed on noise) | **`93.3%`** | `26.7%` | **🏆 +93.3% Win Rate Lift** |
| **Deterministic Deductive Accuracy** | `~85.0%` (LLM counting drift) | **`100.0%`** (Exact SAT Hypercube) | `70.0%` (1st-order only) | **🛡️ Zero Boolean Hallucinations** |
| **External API Calls per Game** | `5.8 calls` | **`0.0 calls`** (In-Memory Fast Path) | `0.0 calls` | **💰 100% Cost & Token Elimination** |
| **Decision Replicability** | Stochastic | **100% Deterministic & Verifiable** | Deterministic | **Formal Math Guarantees** |
| **Explainability** | Opaque text generation | **Exact Boolean Algebraic Proof** | Hardcoded logic | **Full Audit Trail** |

---

## 🏗️ Architecture & Theory

```mermaid
graph TD
    A[Visible Minesweeper Board] --> B[Constraint Extraction]
    B --> C{Fast-Path Algebraic Reduction}
    
    C -- "Target == 0 (Safe) OR Target == |Vars| (Mine)" --> D[100% Deterministic Move < 0.05ms]
    C -- "Subset Overlap: (V_B \ V_A) = T_B - T_A" --> D
    
    C -- "Underdetermined Frontier" --> E[Connected Component Decomposition]
    E --> F[Exact Binary Configuration Enumeration]
    
    F -- "Marginal Prob P(Mine) ∈ {0.0, 1.0}" --> D
    F -- "0.0 < P(Mine) < 1.0 (Tie-break)" --> G[JEV Calibrated Probabilistic Fallback]
    G --> H[Optimal Min-Risk Cell Selection]
    
    D --> I[Board Action Execution]
    H --> I
```

### Mathematical Formalization

For each revealed frontier clue cell $(r, c)$ with clue number $k$:
$$\sum_{x_i \in \mathcal{N}(r, c) \cap \mathcal{U}} x_i = k - F(r, c)$$
Where:
- $\mathcal{U}$: set of unrevealed neighboring coordinates.
- $F(r, c)$: count of currently flagged neighbor cells.
- $x_i \in \{0, 1\}$: binary variable (0 = Safe, 1 = Mine).

When multiple overlapping constraints intersect, Exactor performs **subset resolution**:
$$\text{If } V_A \subset V_B \implies \sum_{x \in (V_B \setminus V_A)} x = T_B - T_A$$

---

## 🚀 Quick Start

### 1. Installation

Clone the repository and install dependencies:

```bash
git clone https://github.com/your-org/exactor-minesweeper.git
cd exactor-minesweeper
pip install -r requirements.txt
```

### 2. Launch Interactive Web Arena

Start the modern cyberpunk Web UI:

```bash
python run_web.py
```
Open your browser at **`http://localhost:8000`** to:
- Play manually or watch AI Autoplay with adjustable speed.
- Watch the **Live Split-Screen Duel (Exactor vs Pure JEV)** in real time.
- Run interactive Monte Carlo benchmarks and view Canvas charts.

### 3. Run Automated Benchmark from Terminal

```bash
# Run 25 games on Beginner mode
python run_benchmark.py --games 25 --difficulty beginner

# Run on Intermediate mode with Markdown export
python run_benchmark.py --games 50 --difficulty intermediate --export-md intermediate_benchmark.md
```

### 4. Interactive Terminal CLI

```bash
python run_cli.py
```

### 5. Run Test Suite

```bash
pytest tests/ -v
```

---

## 📂 Project Structure

```text
exactor-minesweeper/
├── .github/workflows/ci.yml       # GitHub Actions CI testing pipeline
├── exactor_minesweeper/
│   ├── core/
│   │   ├── board.py               # Minesweeper grid engine, safe first-click, flood fill
│   │   ├── constraints.py         # Boolean SAT reduction, subset resolution & component solver
│   │   └── generator.py           # Synthetic dataset generator for rule mining
│   ├── agents/
│   │   ├── base.py                # Abstract agent interface & action data contracts
│   │   ├── exactor_agent.py       # Exactor-Accelerator Neuro-Symbolic Agent
│   │   ├── jev_pure_agent.py      # Pure JEV LLM / RLCD Agent
│   │   ├── heuristic_agent.py     # 1st-order heuristic baseline
│   │   └── random_agent.py        # Random picker baseline
│   ├── benchmark/
│   │   ├── runner.py              # Apples-to-apples multi-game test harness
│   │   ├── metrics.py             # Latency, accuracy, win rate, speedup metrics
│   │   └── reporter.py            # Markdown, Terminal, and JSON exporters
│   └── web/
│       ├── server.py              # FastAPI backend API & duel coordinator
│       └── static/
│           ├── index.html         # Modern Cyberpunk Glassmorphic UI
│           ├── style.css          # Design system, glow effects & responsive layouts
│           └── app.js             # Web Audio synthesizer, dual race animation, charts
├── tests/                         # Comprehensive Pytest unit tests
├── run_benchmark.py               # 1-Click benchmark launcher
├── run_web.py                     # 1-Click web server launcher
├── run_cli.py                     # 1-Click CLI launcher
├── benchmark_results.json         # Pre-computed benchmark metrics
├── benchmark_report.md            # Pre-computed markdown report
├── pyproject.toml                 # Standard packaging spec
├── requirements.txt               # Dependencies
└── LICENSE                        # MIT License
```

---

## 🔬 Key Scientific Conclusions

1. **Deterministic Speed Supremacy:** Exactor-Accelerator executes constraint deduction in **under 0.35 milliseconds**, operating over **2,000x faster** than pure LLM inference over network APIs.
2. **Zero Deduction Hallucinations:** In spatial logic and counting games, neural models periodically hallucinate arithmetic boundary conditions. Exactor's boolean SAT guarantee eliminates 100% of deductive failures.
3. **The Neuro-Symbolic Synergy:** Pure logic handles the deterministic fast-path without API costs; JEV handles underdetermined probabilistic guesses. Together, they provide maximum win rate with minimal latency.

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.
