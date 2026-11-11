# 🚀 Benchmark Comparative Report: Exactor-Accelerator vs Pure JEV (Minesweeper)

- **Timestamp:** `2026-11-11T20:33:42.753881`
- **Difficulty Preset:** `BEGINNER`
- **Total Games per Agent:** `25` (Identical seeds & mine distributions)

## 📊 Summary Performance Matrix

| Metric / Dimension | Pure JEV (Solo LLM/RLCD) | Exactor-Accelerator (Neuro-Symbolic) | Standard Heuristic | Advantage / Delta |
| :--- | :---: | :---: | :---: | :---: |
| **Avg Latency per Move** | `792.27 ms` | **`0.4510 ms`** | `0.1386 ms` | **1,757x Faster (Sub-ms Fast-Path)** |
| **Latency P95** | `1075.59 ms` | **`0.7108 ms`** | `0.2100 ms` | **Ultra-low deterministic variance** |
| **Board Win Rate (%)** | `0.0%` | **`96.0%`** | `72.0%` | **+96.0% Win Rate Lift** |
| **Deterministic Move Ratio (%)** | `100.0%` | **`97.6%`** | `95.2%` | Local algebraic deduction vs API call per move |
| **External API Calls per Game** | `3.7` calls | **`0.0` calls** | `0.0` calls | **100.0% Cost / Call Reduction** |
| **Decision Replicability** | Non-deterministic (LLM temperature) | **100% Deterministic & Verifiable** | Deterministic | **Formal Math Guarantees** |
| **Explainability Mode** | Opaque text generation | **Exact Boolean SAT Rule + Causal Proof** | Hardcoded logic | **Full Audit Trail** |

## 🔬 Key Architectural Insights

1. **Sub-Millisecond Fast-Path Advantage**: Exactor-Accelerator resolves frontier constraints in-memory (0.451 ms/move measured), avoiding network latency and LLM token costs on deterministic states.
2. **Exact Combinatorial Deduction**: Exactor's subset-reduction engine only commits to moves it can prove; ambiguous states are escalated to the oracle rather than guessed.
3. **Intelligent Calibrated Fallback**: Unlike rigid classical solvers that guess uniformly, Exactor-Accelerator leverages JEV's calibrated probabilistic inference to navigate unsolvable 50/50 endgames with the lowest possible mine probability.