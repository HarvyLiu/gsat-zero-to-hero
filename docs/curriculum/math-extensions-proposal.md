# Proposal: Math cross-unit lessons + 分科 advanced tools (for owner approval)

Status: **proposal, not yet in `src/data/course/math.json`**. Once you approve it, these chapters are added to the outline. They are then written through the same writer → reviewer → SymPy pipeline.

Sources:
- `research/math-12-electives-2026-11-16.md`: 108課綱 數學領域 PDF, 12年級 tables; CEEC 分科數學考試說明, 114學年度起適用.
- The existing sprint outline.

## A. New part: 跨單元解題 / Cross-unit problem solving

**Where it goes:** after Part 8 (數B專屬) and before the exam-skills part. Learners meet the "many ways" practice before the timed mock papers, so the mocks stay the finale.

**What each chapter does:** about 30 minutes. 5–6 original problems, each solved 2–4 genuinely different ways side by side, followed by "when to prefer which". Every key is SymPy-checked.

**Path rule:** shared chapters use only content on both paths. 數A-only and 數B-only material gets its own chapter.

| Slug | Title (zh / en) | Paths | Example "many ways" problems |
|---|---|---|---|
| `s116x-algebra-meets-graphs` | 代數與圖形的對話 / Algebra meets graphs | both | \|x−a\|<b by algebra vs number-line distance · max/min of a quadratic by completing the square vs graph vs 算幾不等式 · line–circle position by distance vs discriminant · polynomial inequality by sign chart vs graph · symmetric points by formula vs drawing |
| `s116x-counting-and-chance` | 計數與機率的多種算法 / Counting and probability, many ways | both | direct count vs complement vs 取捨原理 · tree diagram vs counting vs conditional-probability table · expected value by full table vs splitting into parts |
| `s116x-sequences-and-growth` | 數列、指數與對數的多種看法 / Sequences, exponents and logs, many views | both | recursion vs general term vs graph · digit counts by logarithm vs bounds · growth by table vs exponential model vs log-scale graph |
| `s116xa-vectors-space-matrices` | 向量、空間與矩陣的多種解法 / Vectors, space and matrices, many ways (數A) | 數A | 3-variable system by elimination vs planes meeting vs matrix · point–plane distance by projection vs formula vs minimizing · triangle area by cross product vs 3×3 determinant vs ½ab sin C · sum formulas by algebra vs unit-circle geometry vs vectors |
| `s116xb-models-and-tables` | 模型、表格與圖形的多種解法 / Models, tables and pictures (數B) | 數B | matrix/table computation vs direct reading · proportion in the plane by similar triangles vs coordinates · periodic model by table vs graph |

## B. New optional part: 選修小技巧 / AST advanced tools (labelled 不考學測)

**What it is:** a track placed after the core, as the plan allows. Each chapter teaches one 12年級 (數甲/數乙) idea **from zero**; the learner is never assumed to know AST material. It then shows exactly which 學測 problems the idea speeds up or double-checks.

**What it never does:** say the idea is needed for 學測. Every 學測 problem remains solvable with 10–11年級 tools, and the chapter says so.

**Codes:** from the verified research. ※ items (e→exp/ln, the derivatives of sin and cos) are excluded, as the 課綱 recommends.

| Slug | Title | 分科 code(s) | Helps with (學測) | Paths |
|---|---|---|---|---|
| `x-sigma-and-infinite-series` | Σ 符號與無窮等比級數 / Σ notation and infinite geometric series | N-12甲-2, N-12乙-2 | repeating decimals (N-10-1), sums (N-10-6) | both |
| `x-derivative-slope` | 導數入門：切線的斜率 / First derivatives: the slope of a tangent | F-12甲-3, F-12乙-3 | cubic graph features and the symmetry centre (F-10-2), tangent lines, double roots and 因式定理 (A-10-2) | both |
| `x-derivative-extrema` | 用導數看增減與極值 / Using derivatives for increase, decrease and extrema | F-12甲-4, F-12乙-4 | cubic shapes and root counts (F-10-2/3), checking quadratic max/min (F-10-1) | both |
| `x-complex-numbers` | 複數與 ω / Complex numbers and ω | N-12甲-3, N-12乙-1, A-12甲-1, A-12乙-2 | remainders on division by x²+x+1 via ω (A-10-2); conjugate roots | both |
| `x-polar-form-rotation` | 極式、棣美弗與旋轉 / Polar form, De Moivre and rotation | N-12甲-3 | sum and multiple-angle formulas as a memory aid and check, with the circular-proof caveat stated (G-11A-5); rotations (F-11A-3) | 數A |
| `x-random-variables-binomial` | 隨機變數與二項分布 / Random variables and the binomial distribution | D-12甲-1/2, D-12乙-1/2 | expected value by linearity (D-10-4); "at least k successes" (D-11A-2/D-11B-2) | both |
| `x-limits-steady-state` | 數列極限與穩定狀態 / Sequence limits and steady states | N-12甲-1 | long-run steady state of a 2×2 transition matrix (F-11A-3) | 數A |
| `x-linear-programming` | 線性規劃 / Linear programming | A-12乙-1 | max/min of ax+by over a region (G-10-2 inequalities) | both |

**Flagged for your decision:** `x-linear-programming`. The research could not verify that 學測 currently asks linear-programming items. The underlying "region of two-variable inequalities" skill is 10年級 content. I suggest keeping it, clearly labelled.

**Left out on purpose:** Riemann sums and integration (F-12甲-5/6/7, F-12乙-5/6) and conic standard forms (G-12甲-1). The research found almost no 學測 use for them, so including them would teach AST content for its own sake.
