<!-- Frozen design output (Math chapter map (pilot)), 2026-11-15. Superseded where docs/design/06-critique.md or the approved plan says so. -->

# Math course map (pilot): from zero to 學測 數A / 數B, chapter by chapter

## 1. Decisions you need to sign off

**D1. Grade-11 overlap: shared chapters, then two separate tracks.** Where the 11A and 11B 條目 say the same thing, or one is a subset of the other, the common content becomes one chapter tagged `both`:
- N-11A-1 and N-11B-1 are the same.
- G-11A-1 and G-11B-1 are the same.
- D-11A-1 and D-11B-1 are the same.
- G-11B-2 is a subset of G-11A-6.
- G-11A-2 and G-11B-4 share point coordinates, distance and projection.
- S-11A-1 and S-11B-1 share the positions of lines and planes.
- A-11B-1 roughly equals A-11A-3 plus part of A-11A-1.
- F-11B-1 is the sine part of F-11A-1.
- F-11A-4 and F-11B-2 overlap.
- D-11B-2 covers D-11A-2 and D-11A-3 at "basic application" depth.

Content listed in only one track's 條目 goes in that track's own chapters.

Why:
- The no-jump test introduces each concept exactly once, so two "radian" chapters would break it.
- One widget gets built per idea.
- Learners who take both papers (46.09% of 115 candidates took all six subjects) don't repeat chapters.
- 數B learners get a clean path.

Layout:
- The shared Grade-11 parts (17–22) close the core.
- The 數A track (Parts 23–27) and the 數B track (Parts 28–30) run in parallel, like the reference project's `TRACKS`.
- New test rule:
  - A `both`, `bridge` or `數B` chapter has no `數A` ancestor.
  - A `數A` chapter has no `數B` ancestor.
  - An `extension` chapter may have any ancestors.

**D2. Places where I depart from the research `depends_on`.** None of these breaks a dependency; please confirm each.

| # | Change | Why it is safe |
|---|---|---|
| a | A-11A-3 matrix operations (shared, Part 22) come before A-11A-2 (Part 27). | Matrix operations only need matrix × vector. |
| b | The G-11A-6 dot product (shared, Part 18) comes before G-11A-4. | Vector length is taught in the shared `vectors` chapter. |
| c | The exponential and common-log graphs from F-11A-4 (shared, Part 20) come before A-11A-4. | The any-base part of F-11A-4 stays after the log laws. |
| d | F-10-1 is taught before A-10-2. | f(x) is taught before polynomial chapters use it. Neither item depends on the other. |
| e | D-10-2 comes before D-10-1 and D-10-3. | D-10-2 does not depend on D-10-1. |
| f | 三垂線定理 moves to Part 26. | The rest of S-11A-1 is in shared Part 19, which already comes before G-11A-2. |

**D3. Verified fixes and curriculum marks.**
- Fixes applied:
  - A-10-1 comes right after N-10-1 and N-10-2.
  - N-10-7 comes before N-10-6.
  - F-11A-3 comes after D-11A-2.
  - G-10-3's general form is extension only.
  - No Σ appears before the extension part; sums are written out.
- ★＃ and ＃ items become short `-toolbox` chapters of 12–15 minutes:
  - N-10-5, N-10-7 and D-10-1 (★＃);
  - G-10-1 and 三角測量 in G-10-7 (＃).
- ★ content is taught but flagged "not directly tested": the √2 proof and significant digits in N-10-1, and the three-plane test in A-11A-2.
- ※ content goes only in extension track X1.

**Conventions**
- Slugs:
  - Project chapters end in `-project` and capstones in `-capstone`, so the reference test's regex finds them.
  - Projects add at most 2 new concepts.
- Concept keys are English and lowercase. Their zh labels come from the glossary: the 課綱 term is primary and the 樂詞網 variant is an alias, for example 正弦定理 / 正弦定律, 反方陣 / 逆方陣, 轉移方陣 / 轉移矩陣, 最適直線 / 迴歸直線.
- Sources:
  - Every coded chapter cites [L] (NAER 數學領綱 PDF) and [T] (樂詞網).
  - Exam chapters cite [K] (考試說明, 108年9月), [J] (116簡章) and [R] (115數A 評分原則).
  - **M0–M11** are the documented misconceptions in `math.research.common_misconceptions[n]`, each with its source URL.
  - "Low-P" means a low success rate reported in 選才電子報; it is not a coded misconception.
- Minutes (from the pedagogy finding "well under ~35 minutes"):
  - bridge chapters 20, toolboxes 12–15, bridge projects 30;
  - core chapters 28, core projects 35;
  - exam chapters 25, capstones 130 (a 100-minute mock plus self-scoring, an agreed exception to the 35-minute rule).
- Line format below: `slug` zh / en — blurb · [codes] · **new** · **uses** (key items) · **pre** · notes.

## 2. The map

### Part 0 · 歡迎 Welcome [both]
This part is site-wide; the lead planner may move it out of Math.

- `welcome` 歡迎 / Welcome — the characters, how a chapter works, language, progress · new: dialogue interlude; your-turn pause; mastery level · pre: none · 12 min · viz: isometric desk with teal hotspots.
- `what-is-gsat` 學測是什麼 / What is the 學測 — dates 2027-01-22..24, 數A vs 數B, 部定必修 scope, no calculator, formula sheet [J][K] · new: 學測 (GSAT); 級分; 數A and 數B papers; 部定必修 scope · pre: welcome · 12 min.
- `choose-your-route` 選擇你的路線 / Choose your route — placement check to skip bridge chapters; pick A, B or both · new: placement check; track tag; exam countdown planner · uses: 數A and 數B papers · pre: what-is-gsat · 10 min · viz: subway-style route map.

### Part 1 · 銜接：數（國小） Bridge: numbers [bridge]
- `whole-numbers` 整數、數線與運算順序 / Whole numbers, number line, order of operations — [N-3-11, N-5-1 (whole numbers), R-4-1, R-4-2, R-5-2, R-6-1] · new: place value; number line; order of operations; operation laws · pre: choose-your-route.
- `factors-and-primes` 因數、倍數、質因數分解 / Factors and primes — [N-5-3, N-6-1, N-6-2, N-7-1, N-7-2] · new: factor and multiple; prime number; prime factorization; greatest common factor; least common multiple · uses: operation laws · pre: whole-numbers · viz: factor-tree builder.
- `fractions` 分數的意義與等值分數 / What fractions mean — [N-3-9, N-4-5, N-4-6, N-5-4, N-4-8] · new: fraction; equivalent fractions; simplest form; common denominator · uses: number line; greatest common factor; least common multiple · pre: factors-and-primes.
- `fraction-operations` 分數的乘除 / Multiplying and dividing fractions — [N-5-5, N-5-6, N-5-7, N-6-3] · new: fraction multiplication; fraction as a quotient; reciprocal; fraction division · uses: fraction · pre: fractions · M8.
- `decimals` 小數 / Decimals — [N-3-10, N-4-7, N-4-8, N-5-1 (decimals), N-5-8, N-5-9, N-6-4] · new: decimal place value; decimal–fraction conversion; decimal multiplication; decimal division · uses: place value; reciprocal · pre: fraction-operations · M9.
- `rounding-and-estimation` 概數與估算 / Rounding and estimation — [N-5-11] · new: rounding; estimation · uses: decimal place value · pre: decimals.
- `numbers-bridge-project` 專題：不用計算機檢查收據 / Project: check a receipt without a calculator · new: reasonableness check · uses: estimation; decimal multiplication; fraction multiplication · pre: rounding-and-estimation · 30 min.

### Part 2 · 銜接：比、規律、計數（國小） Bridge: ratio, patterns, counting [bridge]
- `ratio-and-percent` 比、比值、百分率 / Ratio and percentage — [N-5-10, N-6-6, N-6-8] · new: ratio; ratio value; percentage; base and compared quantity; percentage change · uses: fraction; decimal division · pre: numbers-bridge-project. The "percentage change" concept is for Civics; its code is unverified.
- `speed-and-units` 速度與單位換算 / Speed and unit conversion — [N-6-7] · new: speed; unit conversion · uses: ratio value · pre: ratio-and-percent.
- `number-patterns` 數量規律 / Number patterns — [R-3-2, R-4-4] · new: number pattern; pattern rule · uses: operation laws · pre: numbers-bridge-project.
- `formulas-with-symbols` 用文字與符號寫公式 / Formulas in words and symbols — [R-4-3, R-5-3, R-6-2, R-6-3] · new: formula; letter for an unknown; quantity relation · uses: pattern rule · pre: number-patterns.
- `first-counting` 加法與乘法原理（初探） / When to add, when to multiply — [R-6-4, N-6-9] · new: addition principle; multiplication principle · uses: operation laws · pre: numbers-bridge-project.
- `ratios-patterns-project` 專題：手搖飲店的配方與菜單 / Project: drink-shop recipes and menu · new: none · uses: ratio; percentage; formula; multiplication principle · pre: speed-and-units, formulas-with-symbols, first-counting · 30 min.

### Part 3 · 銜接：圖形、測量、資料（國小） Bridge: shapes, measurement, data [bridge]
- `angles-and-turns` 角、角度與旋轉 / Angles and turning — [N-4-10, S-4-1, S-4-2] · new: angle; degree; rotation direction; right and straight angle · uses: number line · pre: numbers-bridge-project · viz: rotating-ray protractor (Mafs).
- `plane-figures-and-area` 平面圖形與面積 / Plane figures and area — [S-4-5, S-4-7, S-4-8, S-5-1, S-5-2] · new: perpendicular and parallel lines; triangle types; quadrilateral types; area; trapezoid area formula · uses: angle; fraction multiplication · pre: angles-and-turns · M5.
- `circles-and-sectors` 圓與扇形 / Circles and sectors — [S-3-3, S-5-3, S-6-3] · new: circle centre radius diameter; pi; circumference; circle area; sector · uses: area · pre: plane-figures-and-area · M2 (where the sector-area error starts).
- `scale-drawings` 放大縮小與比例尺 / Enlargement and map scale — [S-6-1, S-6-2] · new: scale factor; map scale · uses: ratio value; area · pre: plane-figures-and-area, ratio-and-percent.
- `solids` 立體形體 / Solids — [S-5-5, S-5-6, S-5-7, S-6-4] · new: cube and cuboid; prism and pyramid; cylinder cone and sphere; volume; surface area · uses: circle area · pre: circles-and-sectors · viz: isometric solids with teal hotspots.
- `tables-and-charts` 表格與統計圖 / Tables and charts — [D-3-1, D-4-1, D-5-1, D-6-1] · new: one-way table; two-way table; bar chart; line chart; pie chart · uses: percentage; angle · pre: angles-and-turns, ratio-and-percent.
- `likelihood` 可能性 / How likely — [D-6-2] · new: likelihood · uses: fraction · pre: tables-and-charts · 12 min.
- `shapes-data-bridge-project` 專題：按比例畫房間 / Project: scale floor plan of a room · new: none · uses: map scale; area; bar chart · pre: scale-drawings, solids, likelihood · 30 min.

### Part 4 · 銜接：國中數與代數 Bridge: numbers and algebra [bridge]
- `negative-numbers` 負數 / Negative numbers — [N-7-3, N-7-4] · new: negative number; integer; signed-number arithmetic · uses: number line · pre: numbers-bridge-project.
- `absolute-value-distance` 絕對值是距離 / Absolute value as distance — [N-7-5] · new: absolute value; distance on the number line · uses: negative number · pre: negative-numbers. 國中 does not solve absolute-value equations.
- `integer-exponents` 指數律 / Powers and exponent laws — [N-7-6, N-7-7] · new: power; base and exponent; exponent laws · uses: signed-number arithmetic · pre: negative-numbers.
- `scientific-notation` 科學記號 / Scientific notation — [N-7-8] · new: scientific notation; negative powers of ten · uses: exponent laws; decimal place value · pre: integer-exponents.
- `square-roots` 平方根 / Square roots — [N-8-1, N-8-2] · new: square root; radical sign; perfect square; square-root approximation · uses: power; estimation · pre: integer-exponents, rounding-and-estimation.
- `proportions` 比例式、正反比、連比 / Proportion and continued ratio — [N-7-9, N-9-1] · new: proportion; direct proportion; inverse proportion; continued ratio · uses: ratio value · pre: negative-numbers, ratio-and-percent.
- `linear-equations` 代數式與一元一次方程式 / Expressions and linear equations — [A-7-1, A-7-2, A-7-3] · new: algebraic expression; like terms; linear equation in one variable; solving by balancing · uses: letter for an unknown; formula · pre: negative-numbers, formulas-with-symbols.
- `linear-inequalities` 一元一次不等式 / Linear inequalities — [A-7-7, A-7-8] · new: inequality; solution on the number line; reversing the inequality sign · uses: linear equation in one variable · pre: linear-equations.
- `coordinate-plane` 直角坐標 / Coordinate plane — [G-7-1] · new: coordinate plane; ordered pair; quadrant · uses: negative number · pre: negative-numbers · M4 (root idea: a distance is ≥ 0, a coordinate has a sign).
- `linear-systems` 二元一次聯立方程式 / Two-variable systems — [A-7-4, A-7-5, A-7-6] · new: linear equation in two variables; system of linear equations; substitution and elimination; graph of a linear equation · uses: ordered pair · pre: linear-equations, coordinate-plane.
- `algebra-1-bridge-project` 專題：手機方案比較 / Project: compare phone plans · new: break-even point · uses: system of linear equations; inequality · pre: linear-systems, linear-inequalities, proportions · 30 min.

### Part 5 · 銜接：國中幾何 Bridge: geometry [bridge]
- `geometry-basics` 幾何符號、垂直、中垂線 / Notation, perpendicular bisector — [S-7-1, S-7-3] · new: point line ray segment notation; perpendicular bisector; distance from a point to a line · uses: perpendicular and parallel lines · pre: plane-figures-and-area.
- `angles-and-parallels` 角的關係、平行線、內角和 / Angle relations and parallels — [S-8-1, S-8-2, S-8-3] · new: complementary and supplementary angles; vertical angles; angles formed by parallel lines; angle bisector; polygon interior angle sum · pre: geometry-basics.
- `line-symmetry` 線對稱 / Line symmetry — [S-5-4, S-7-4, S-7-5] · new: line symmetry; line of symmetry; mirror image · uses: perpendicular bisector · pre: geometry-basics.
- `congruent-triangles` 全等三角形 / Congruent triangles — [S-8-4, S-8-5] · new: congruent figures; triangle congruence criteria · pre: angles-and-parallels.
- `triangle-quadrilateral-properties` 三角形與四邊形性質 / Triangle and quadrilateral properties — [S-8-8, S-8-9, S-8-10, S-8-11] · new: isosceles triangle base angles; triangle side inequality; exterior angle theorem; parallelogram properties; special quadrilaterals · uses: triangle congruence criteria; quadrilateral types · pre: congruent-triangles.
- `constructions-and-proof` 尺規作圖與證明 / Constructions and proof — [S-8-12, S-9-11] · new: straightedge-and-compass construction; proof · uses: perpendicular bisector; angle bisector · pre: triangle-quadrilateral-properties · M3 (root habit: justify every claim) · viz: JSXGraph construction board.
- `pythagorean-theorem` 畢氏定理 / Pythagorean theorem — [S-8-6, S-8-7] · new: pythagorean theorem; equilateral triangle area · uses: square root; area · pre: square-roots, plane-figures-and-area.
- `distance-formula` 兩點距離 / Distance formula — [G-8-1] · new: distance formula · uses: pythagorean theorem; coordinate plane · pre: pythagorean-theorem, coordinate-plane.
- `similar-figures` 相似形與比例線段 / Similar figures — [S-9-1, S-9-2, S-9-3] · new: similar figures; triangle similarity criteria; parallel lines cut proportional segments · uses: scale factor; proportion · pre: scale-drawings, proportions, angles-and-parallels.
- `right-triangle-ratios` 直角三角形的邊長比 / Fixed side ratios in right triangles — [S-9-4] · new: side-ratio invariance in similar right triangles; 30-60-90 and 45-45-90 triangles · pre: similar-figures, pythagorean-theorem.
- `circle-properties` 弧長、圓心角、圓周角、切線 / Arcs, angles, tangents — [S-9-5, S-9-6, S-9-7] · new: arc length (degree form); central angle; inscribed angle; tangent perpendicular to radius; chord bisected by perpendicular from centre · uses: sector; circumference · pre: circles-and-sectors, constructions-and-proof.
- `triangle-centres` 外心、內心、重心 / Triangle centres — [S-9-8, S-9-9, S-9-10] · new: circumcentre; incentre; centroid · pre: circle-properties.
- `space-lines-planes-volume` 空間線面、三視圖、表面積與體積 / Space, three views, surface area and volume — [S-7-2, S-9-12, S-9-13] · new: three views; positions of lines and planes in space (intuitive); net of a solid · uses: cube and cuboid; volume · pre: solids, angles-and-parallels.
- `geometry-bridge-project` 專題：證明摺紙的祕密 / Project: prove a paper-folding fact · new: none · uses: proof; similar figures · pre: triangle-centres, right-triangle-ratios, distance-formula, space-lines-planes-volume, line-symmetry · 30 min.

### Part 6 · 銜接：國中代數 II 與函數 Bridge: polynomials and functions [bridge]
- `polynomials` 多項式與乘法公式 / Polynomials — [A-8-1, A-8-2, A-8-3] · new: polynomial; degree of a polynomial; polynomial arithmetic; square identities · uses: like terms; exponent laws · pre: linear-equations, integer-exponents.
- `factoring` 因式分解 / Factoring — [A-8-4, A-8-5] · new: factoring; common factor extraction; factoring with identities; cross-multiplication factoring · pre: polynomials.
- `quadratic-equations` 一元二次方程式與配方法 / Quadratic equations — [A-8-6, A-8-7] · new: quadratic equation; zero-product solving; completing the square; quadratic formula; discriminant · uses: factoring; square root · pre: factoring, square-roots.
- `sequences` 等差與等比數列 / Arithmetic and geometric sequences — [N-8-3, N-8-4, N-8-5, N-8-6] · new: sequence and general term; arithmetic sequence; geometric sequence; arithmetic series sum · uses: pattern rule; power · pre: number-patterns, integer-exponents, linear-equations.
- `linear-functions` 一次函數 / Linear functions — [F-8-1, F-8-2] · new: function; linear function; constant function; graph of a function · uses: graph of a linear equation; quantity relation · pre: linear-systems, formulas-with-symbols. No f(x) notation yet.
- `quadratic-functions` 二次函數圖形 / Quadratic graphs — [F-9-1, F-9-2] · new: quadratic function; parabola; vertex; axis of a parabola; opening direction · uses: line symmetry; quadratic equation · pre: linear-functions, quadratic-equations, line-symmetry.
- `algebra-2-bridge-project` 專題：投籃的拋物線 / Project: the arc of a basketball shot · new: mathematical model · uses: quadratic function; arithmetic sequence · pre: quadratic-functions, sequences · 30 min.

### Part 7 · 銜接：國中統計與機率 Bridge: statistics and probability [bridge]
- `averages-and-charts` 次數分配、平均數、中位數、眾數 / Frequency, mean, median, mode — [D-7-1, D-7-2] · new: frequency table; histogram; mean; median; mode · uses: bar chart · pre: tables-and-charts.
- `cumulative-frequency` 相對與累積次數 / Relative and cumulative frequency — [D-8-1] · new: relative frequency; cumulative frequency; cumulative frequency polygon · pre: averages-and-charts.
- `quartiles-box-plots` 四分位距與盒狀圖 / Quartiles and box plots — [D-9-1] · new: range; quartile; interquartile range; box plot · pre: cumulative-frequency.
- `probability-basics` 機率與樹狀圖 / Probability and tree diagrams — [D-9-2, D-9-3] · new: probability; equally likely outcomes; classical probability; two-level tree diagram · uses: likelihood; multiplication principle · pre: likelihood, first-counting.
- `stats-probability-bridge-project` 專題：全班睡眠調查 / Project: class sleep survey · new: none · uses: box plot; mean · pre: quartiles-box-plots, probability-basics · 30 min.

### Part 8 · 10年級：數與式 Numbers and expressions [both]
- `real-numbers` 實數 / Real numbers — [N-10-1] · new: real number; rational number as a repeating decimal; irrational number; trichotomy law; decimal estimation of an irrational · uses: square root; decimal–fraction conversion; proof · pre: square-roots, constructions-and-proof · the √2 proof is ★ · viz: number line that zooms into √2.
- `scientific-notation-arithmetic` 科學記號的運算與有效位數 / Calculating in scientific notation — [N-10-1, 備註 ★] · new: multiplying and dividing in scientific notation; adding in scientific notation; significant digits · uses: scientific notation; rounding · pre: real-numbers, scientific-notation.
- `absolute-value-equations` 絕對值方程式與不等式 / Absolute-value equations and inequalities — [N-10-2] · new: absolute-value equation; absolute-value inequality; interval notation; error tolerance · uses: distance on the number line; reversing the inequality sign · pre: real-numbers, absolute-value-distance, linear-inequalities · low-P: 113數A Q17, P = 5%.
- `cubic-identities` 三次乘法公式 / Cubic identities — [A-10-1] · new: cube of a sum or difference; sum and difference of cubes · uses: square identities · pre: real-numbers, polynomials · viz: isometric (a+b)³ cube split into blocks.
- `radicals` 根式與有理化 / Radicals and rationalizing — [A-10-1] · new: simplest radical form; operations on radicals; rationalizing the denominator · uses: irrational number; prime factorization · pre: cubic-identities.
- `rational-expressions` 分式的運算 / Rational expressions — [A-10-1] · new: rational expression; simplifying rational expressions; operations on rational expressions · uses: fraction division; factoring · pre: cubic-identities, factoring.
- `numbers-expressions-project` 專題：產品標示的誤差 / Project: tolerance labels on products · new: none · uses: error tolerance; significant digits · pre: absolute-value-equations, scientific-notation-arithmetic, rational-expressions, radicals.

### Part 9 · 10年級：指數與對數 Exponents and logarithms [both]
- `rational-exponents` 分數與實數指數 / Fractional and real exponents — [N-10-3] · new: n-th root; fractional exponent; real exponent; exponent laws for real exponents · uses: simplest radical form · pre: radicals.
- `am-gm-inequality` 算幾不等式 / AM–GM — [N-10-3] · new: geometric mean; AM–GM inequality · uses: mean; inequality · pre: rational-exponents, averages-and-charts, linear-inequalities · viz: semicircle construction (Mafs).
- `common-logarithms` 常用對數 / Common logarithms — [N-10-4] · new: logarithm base 10; common logarithm; writing a positive number as 10 to the log · uses: real exponent; scientific notation · pre: rational-exponents, scientific-notation-arithmetic.
- `using-log-tables` 用 log2/3/5/7 估算 / Estimating with the given logs — [N-10-4] · new: combining powers of ten to find logs; number of digits from a common log; leading digit from a common log · pre: common-logarithms. The log laws themselves are A-11A-4 (數A only).
- `error-toolbox` 工具箱：誤差 / Toolbox: calculator limits and error — [N-10-5 ★＃] · new: finite-precision calculation; rounding error · uses: significant digits · pre: scientific-notation-arithmetic, common-logarithms · 12 min.
- `exponents-logs-project` 專題：2¹⁰⁰ 有幾位數 / Project: digits of 2¹⁰⁰ · new: order of magnitude · pre: using-log-tables, am-gm-inequality, error-toolbox.

### Part 10 · 10年級：數列與級數 Sequences and series [both]
- `logic-toolbox` 工具箱：命題與邏輯 / Toolbox: logic — [N-10-7 ★＃] · new: proposition; negation; and-or statements; implication; sufficient and necessary conditions · uses: proof · pre: constructions-and-proof · 15 min.
- `recursive-sequences` 遞迴關係 / Recursion — [N-10-6] · new: recursive definition; first-order recurrence · uses: arithmetic sequence; geometric sequence · pre: sequences.
- `series-and-sums` 等比級數與求和公式 / Geometric series and sums — [N-10-6] · new: finite geometric series sum; sum of the first n squares; expanded-sum notation · uses: arithmetic series sum; common logarithm · pre: recursive-sequences, using-log-tables. No Σ.
- `mathematical-induction` 數學歸納法 / Induction — [N-10-6] · new: mathematical induction; base case and inductive step · uses: implication · pre: logic-toolbox, series-and-sums · viz: domino step-through.
- `sequences-project` 專題：存錢計畫 / Project: a savings plan · new: none · uses: first-order recurrence; finite geometric series sum · pre: mathematical-induction.

### Part 11 · 10年級：直線與圓 Lines and circles [both]
- `coordinate-symmetry-toolbox` 工具箱：坐標對稱 / Toolbox: symmetry in coordinates — [G-10-1 ＃] · new: reflection in the x-axis; reflection in the y-axis; reflection in y = x; symmetry about the origin · uses: mirror image · pre: coordinate-plane, line-symmetry · 12 min.
- `slope` 斜率與點斜式 / Slope — [G-10-2] · new: slope; steepness as absolute slope; point-slope form · uses: linear function; absolute value · pre: linear-functions, absolute-value-equations.
- `parallel-perpendicular-lines` 平行、垂直與平移 / Parallel and perpendicular lines — [G-10-2] · new: general form of a line; parallel-line slope condition; perpendicular-line slope condition; translation of points and lines · uses: angles formed by parallel lines · pre: slope, angles-and-parallels.
- `point-line-distance` 點到直線距離 / Point-to-line distance — [G-10-2, including the △OPQ 備註] · new: point-to-line distance formula; distance between parallel lines; triangle area from coordinates · uses: distance formula · pre: parallel-perpendicular-lines, distance-formula · M5.
- `two-variable-inequalities` 二元一次不等式 / Two-variable inequalities — [G-10-2] · new: half-plane; region of a system of linear inequalities · uses: inequality; general form of a line · pre: parallel-perpendicular-lines, linear-inequalities. Linear programming is 12乙.
- `circle-equation` 圓的標準式 / Standard equation of a circle — [G-10-3] · new: standard equation of a circle; point inside on or outside a circle · uses: distance formula · pre: distance-formula, circles-and-sectors · M0 · general form goes to X1.
- `lines-and-circles` 直線與圓 / Lines meeting circles — [G-10-4] · new: line–circle position; algebraic test with the discriminant; geometric test with centre distance; tangent line equation · uses: discriminant; tangent perpendicular to radius · pre: circle-equation, point-line-distance, quadratic-equations, circle-properties · no two-circle relations · viz: drag a line while d vs r and the discriminant update live.
- `lines-circles-project` 專題：基地臺與道路 / Project: a cell tower and a road · new: none · pre: lines-and-circles, two-variable-inequalities.

### Part 12 · 10年級：三角比 Trigonometric ratios [both]
- `generalized-angles` 廣義角與斜角 / Generalized angles — [G-10-5] · new: directed angle; standard position and terminal side; coterminal angles; angle of inclination · uses: rotation direction; slope · pre: slope, angles-and-turns. Angles start limited to −180°..360°.
- `polar-coordinates` 極坐標 / Polar coordinates — [G-10-5] · new: polar coordinates; pole and polar axis · uses: terminal side · pre: generalized-angles, distance-formula · M1 · viz: polar grid paper.
- `trig-ratios` 銳角三角比 / Acute trig ratios — [G-10-6] · new: sine ratio; cosine ratio; tangent ratio; special-angle values; estimating trig ratios by measuring · uses: side-ratio invariance · pre: right-triangle-ratios, generalized-angles.
- `trig-any-angle` 廣義角三角比 / Trig ratios of any angle — [G-10-6] · new: trig ratios from a terminal-side point; signs of trig ratios by quadrant; sin²θ + cos²θ = 1; polar-to-rectangular conversion · uses: quadrant · pre: trig-ratios, polar-coordinates · M4, M1 · viz: unit-circle widget.
- `law-of-sines` 正弦定理 / Law of sines — [G-10-7] · new: law of sines; triangle area ½ab sin C · uses: circumcentre; inscribed angle · pre: trig-any-angle, triangle-centres.
- `law-of-cosines` 餘弦定理與正射影 / Law of cosines — [G-10-7] · new: law of cosines; projection of a segment; solving a triangle · pre: law-of-sines.
- `slope-and-angles` 斜率與夾角 / Slope and the angle between lines — [G-10-7] · new: slope as tangent of inclination; angle between two lines · uses: angle of inclination · pre: trig-any-angle, parallel-perpendicular-lines.
- `triangulation-toolbox` 工具箱：三角測量 / Toolbox: triangulation — [G-10-7 ＃] · new: angle of elevation and depression; triangulation in a cuboid section · uses: positions of lines and planes in space (intuitive) · pre: law-of-cosines, space-lines-planes-volume · M6 · 15 min · viz: isometric cuboid cross-section.
- `trig-ratios-project` 專題：測量旗桿與山高 / Project: measure a flagpole and a hill · new: none · pre: triangulation-toolbox, slope-and-angles.

### Part 13 · 10年級：多項式與函數 Polynomials and functions [both]
- `function-notation` f(x) 與圖形變換 / f(x) and graph shifts — [F-10-1] · new: function notation f(x); domain and range; horizontal shift f(x−h); reflection f(−x) · uses: reflection in the y-axis · pre: linear-functions, coordinate-symmetry-toolbox.
- `quadratic-function-extremes` 二次函數配方與最值 / Completing the square for functions — [F-10-1] · new: vertex form by completing the square; extreme values on a closed interval · uses: completing the square; vertex · pre: function-notation, quadratic-functions.
- `section-formula` 分點公式與內插法 / Section formula and interpolation — [F-10-1] · new: section formula on the number line; linear interpolation · uses: proportion · pre: function-notation, proportions.
- `polynomial-division` 多項式除法與綜合除法 / Polynomial division — [A-10-2] · new: polynomial division algorithm; synthetic division by x − a · pre: function-notation, polynomials. Synthetic division only by x − a.
- `remainder-factor-theorems` 餘式與因式定理 / Remainder and factor theorems — [A-10-2] · new: remainder theorem; factor theorem; polynomial in powers of (x − a) · uses: factoring · pre: polynomial-division, factoring.
- `cubic-functions` 三次函數圖形特徵 / Cubic graphs — [F-10-2] · new: cubic function; end behaviour from the leading term; symmetry centre of a cubic; local linear approximation · uses: symmetry about the origin; cube of a sum or difference · pre: remainder-factor-theorems, quadratic-function-extremes, cubic-identities · M11 · viz: Mafs sliders with zoom to the local line.
- `polynomial-inequalities` 多項式不等式 / Polynomial inequalities — [F-10-3] · new: sign chart for a factored polynomial; solving polynomial inequalities from a graph · uses: interval notation; factor theorem · pre: cubic-functions, absolute-value-equations.
- `polynomials-project` 專題：無蓋紙盒 / Project: an open-top box · new: none · pre: polynomial-inequalities, section-formula.

### Part 14 · 10年級：數據分析 Data analysis [both]
The formula sheet prints σ, r and the regression line.
- `standard-deviation` 標準差 / Standard deviation — [D-10-2] · new: deviation from the mean; variance; standard deviation · uses: mean; expanded-sum notation · pre: quartiles-box-plots, series-and-sums.
- `percentiles` 百分位數 / Percentiles — [D-10-2] · new: percentile; definitions of statistics can differ; choosing a suitable statistic · uses: quartile · pre: quartiles-box-plots · 20 min.
- `standardization` 標準化 / Standardizing data — [D-10-2] · new: linear transformation of data; standard score · pre: standard-deviation. Note: 115數A Q9 gave a T-score formula to substitute into.
- `scatter-correlation` 散布圖與相關係數 / Scatter and correlation — [D-10-2] · new: two-variable data; scatter plot; correlation coefficient; positive and negative correlation · pre: standardization, coordinate-plane.
- `best-fit-line` 最適直線 / The best-fit line — [D-10-2] · new: best-fit line; predicting with the best-fit line · uses: point-slope form · pre: scatter-correlation, slope.
- `data-analysis-project` 專題：身高與臂展 / Project: height vs arm span · new: none · pre: best-fit-line, percentiles.

### Part 15 · 10年級：排列組合 Counting [both]
- `sets-toolbox` 工具箱：集合 / Toolbox: sets — [D-10-1 ★＃] · new: set notation; subset and universal set; intersection union and complement; Venn diagram · uses: interval notation; region of a system of linear inequalities; special quadrilaterals · pre: polynomial-inequalities, two-variable-inequalities, triangle-quadrilateral-properties · 12 min.
- `systematic-counting` 有系統的窮舉 / Systematic listing — [D-10-3] · new: systematic enumeration; multi-level tree diagram · uses: addition principle; two-level tree diagram · pre: sets-toolbox, probability-basics.
- `inclusion-exclusion` 取捨原理 / Inclusion–exclusion — [D-10-3] · new: inclusion–exclusion principle · pre: systematic-counting.
- `permutations` 直線排列 / Permutations — [D-10-3] · new: factorial; permutation; arrangements with restrictions · pre: systematic-counting · low-P: 114數B Q15, P = 25%.
- `combinations` 組合 / Combinations — [D-10-3] · new: combination; choosing versus arranging · pre: permutations.
- `binomial-expansion` 二項式展開 / Binomial expansion — [D-10-3] · new: binomial expansion; binomial coefficient · pre: combinations, cubic-identities.
- `counting-project` 專題：密碼規則 / Project: password rules · new: none · pre: binomial-expansion, inclusion-exclusion.

### Part 16 · 10年級：機率 Probability [both]
- `sample-spaces` 樣本空間與事件 / Sample spaces — [D-10-4] · new: sample space; event; complementary event; mutually exclusive events · pre: sets-toolbox, probability-basics.
- `compound-probability` 複合事件機率 / Compound events — [D-10-4] · new: properties of probability; probability of a union; counting-based probability · pre: sample-spaces, counting-project.
- `expected-value` 期望值 / Expected value — [D-10-4] · new: expected value; fair game · pre: compound-probability · low-P: 114數A Q15, P = 16%.
- `probability-project` 專題：夜市遊戲公平嗎 / Project: is the night-market game fair? · new: none · pre: expected-value.

### Parts 17–22 · 11年級共同 Shared Grade 11 [both]
These parts end the core; after them the path branches.

**Part 17 · 弧度與正弦函數 Radians and the sine function**
- `radians` 弧度量 / Radians — [N-11A-1, N-11B-1] · new: radian; degree–radian conversion; arc length s = rθ; sector area ½r²θ · uses: arc length (degree form); directed angle · pre: generalized-angles, circle-properties · M2.
- `sine-function` 正弦函數 / The sine function — [F-11A-1 (sine part), F-11B-1] · new: sine function of a real variable; periodic function and period; amplitude; frequency · uses: horizontal shift f(x−h); trig ratios from a terminal-side point · pre: radians, trig-any-angle, function-notation · M6 · viz: unit circle tracing a wave.
- `periodic-models` 週期現象模型 / Periodic models — [F-11A-1, F-11B-1] · new: sinusoidal model; reading a model from data · uses: mathematical model · pre: sine-function, algebra-2-bridge-project.
- `radians-sine-project` 專題：一年的日照長度 / Project: a year of day length · new: none · pre: periodic-models. The data source still needs citing.

**Part 18 · 平面向量 Plane vectors**
- `vectors` 向量 / Vectors — [G-11A-1, G-11B-1] · new: vector; magnitude of a vector; components of a vector; position vector; zero vector · uses: translation of points and lines · pre: parallel-perpendicular-lines, distance-formula.
- `vector-arithmetic` 向量加減與係數積 / Vector arithmetic — [G-11A-1, G-11B-1] · new: vector addition; vector subtraction; scalar multiple of a vector; parallel vectors · pre: vectors · M3.
- `linear-combinations` 線性組合 / Linear combinations — [G-11A-1, G-11B-1] · new: linear combination; unique coefficients in a two-vector basis; collinear points via vectors · uses: section formula on the number line · pre: vector-arithmetic, section-formula · viz: skewed grid (Mafs).
- `dot-product` 正射影與內積 / Projection and dot product — [G-11A-6 (part), G-11B-2] · new: dot product; dot product in components; vector projection; angle between two vectors · uses: law of cosines; projection of a segment · pre: linear-combinations, law-of-cosines.
- `perpendicular-vectors` 垂直、平行與法向量 / Perpendicular vectors and normal vectors — [G-11A-6, G-11B-2] · new: perpendicularity by zero dot product; direction vector of a line; normal vector of a line · uses: general form of a line · pre: dot-product · M11 (115數A Q14) · whether the normal vector is in 數B scope needs a boundary check.
- `plane-vectors-project` 專題：渡河的船 / Project: a boat crossing a river · new: none · pre: perpendicular-vectors.

**Part 19 · 空間 Space**
- `lines-and-planes-in-space` 空間中的直線與平面 / Lines and planes in space — [S-11A-1, S-11B-1 (common part)] · new: determining a plane; skew lines; line–plane and plane–plane positions; line perpendicular to a plane; dihedral angle (right angles only) · pre: space-lines-planes-volume, triangulation-toolbox · viz: isometric cuboid with teal hotspots.
- `space-coordinates` 空間坐標 / Space coordinates — [G-11A-2, G-11B-4 (part)] · new: three-dimensional coordinate system; distance between points in space; projection of a point onto axes and coordinate planes · pre: lines-and-planes-in-space.
- `space-project` 專題：教室坐標化 / Project: the classroom in 3D coordinates · new: none · pre: space-coordinates.

**Part 20 · 指數與對數函數 Exponential and log functions**
- `exponential-functions` 指數函數、成長與衰退 / Exponential growth and decay — [F-11A-4 (part), F-11B-2 (part)] · new: exponential function; graph of an exponential function; growth and decay by a constant ratio; half-life; compound interest · uses: real exponent; first-order recurrence · pre: rational-exponents, recursive-sequences, function-notation.
- `logarithmic-functions` 常用對數函數與對數尺度 / Log function and log scales — [F-11A-4 (part), F-11B-2 (part)] · new: common logarithmic function; log graph as reflection of 10^x in y = x; logarithmic scale · pre: exponential-functions, common-logarithms, coordinate-symmetry-toolbox.
- `exp-log-project` 專題：假設藥量的衰退 / Project: decay of a hypothetical dose · new: none · pre: logarithmic-functions.

**Part 21 · 機率（11年級） Probability (Grade 11)**
- `subjective-objective-probability` 主觀與客觀機率 / Subjective and objective probability — [D-11A-1, D-11B-1] · new: subjective probability; objective probability from data; checking a probability assignment · uses: relative frequency · pre: expected-value, data-analysis-project.
- `conditional-probability` 條件機率與列聯表 / Conditional probability — [D-11A-2, D-11A-3 (乘法公式), D-11B-2] · new: conditional probability; contingency table; multiplication rule · uses: two-way table; Venn diagram · pre: subjective-objective-probability, tables-and-charts · low-P: 115數B Q7, P = 37%.
- `independent-events` 獨立事件 / Independence — [D-11A-2, D-11B-2] · new: independent events; independent versus mutually exclusive · pre: conditional-probability.
- `bayes-theorem` 貝氏定理 / Bayes — [D-11A-3, D-11B-2] · new: law of total probability; Bayes' theorem · uses: multi-level tree diagram · pre: conditional-probability, systematic-counting · viz: 100-person icon array.
- `probability-11-project` 專題：快篩陽性的意義 / Project: what a positive rapid test means · new: none · pre: bayes-theorem, independent-events. Uses hypothetical rates, labelled as such.

**Part 22 · 矩陣 Matrices**
- `matrices` 矩陣與資料表 / Matrices as data tables — [A-11A-3, A-11B-1] · new: matrix; matrix entries rows and columns; matrix addition and scalar multiplication · uses: two-way table · pre: plane-vectors-project, tables-and-charts.
- `matrix-vector-product` 矩陣乘向量＝線性組合 / Matrix × vector — [A-11A-1 (part), A-11B-1] · new: square matrix; matrix–vector product; linear system in matrix form · pre: matrices, linear-combinations, linear-systems · M11 (115數A Q5).
- `matrix-multiplication` 矩陣乘法 / Matrix multiplication — [A-11A-3, A-11B-1] · new: matrix multiplication; identity matrix; matrix multiplication is not commutative · pre: matrix-vector-product.
- `inverse-matrix` 二階反方陣 / 2×2 inverse — [A-11A-3, A-11B-1] · new: inverse matrix; the number ad − bc; solving a system with an inverse · pre: matrix-multiplication.
- `matrices-project` 專題：飲料店帳本 / Project: a drink chain's ledger · new: none · pre: inverse-matrix.

### Parts 23–27 · 數A track [數A]
**Part 23 · 三角函數與公式 Trig functions and formulas**
- `cos-tan-graphs` 餘弦、正切函數圖形 / Cosine and tangent graphs — [F-11A-1] · new: cosine function graph; tangent function graph; vertical asymptote of tangent · pre: radians-sine-project · ※ cot/sec/csc go to X1.
- `sum-difference-formulas` 和差角公式 / Sum and difference formulas — [G-11A-5] · new: cosine difference formula; sine and cosine sum formulas; tangent sum formula · pre: cos-tan-graphs. Only the sum formulas are on the 數A formula sheet.
- `double-half-angle` 倍角與半角 / Double and half angles — [G-11A-5] · new: double-angle formulas; half-angle formulas · pre: sum-difference-formulas · low-P: 115數A Q17, P = 6%.
- `combining-sine-cosine` 正餘弦疊合 / Combining sine and cosine — [F-11A-2] · new: a sin x + b cos x = r sin(x + φ); amplitude of a combined wave · uses: polar-to-rectangular conversion · pre: sum-difference-formulas · lowest reported P: 112數A Q12, P = 21% · viz: two waves with a phasor arrow.
- `trig-a-project` 專題：兩個聲波相加 / Project: adding two sound waves · new: none · pre: combining-sine-cosine, double-half-angle.

**Part 24 · 對數律 Laws of logarithms**
- `laws-of-logarithms` 對數律與換底 / Log laws and change of base — [A-11A-4] · new: product quotient and power laws of logarithms; logarithm in any base; change of base · uses: combining powers of ten to find logs · pre: exp-log-project, using-log-tables. The 備註 says not to over-practise.
- `exponential-equations` 指數方程與任意底對數函數 / Exponential equations — [A-11A-4, F-11A-4 (part)] · new: solving exponential equations with logarithms; a^x as 10^(kx); graph of y = log_a x · pre: laws-of-logarithms.
- `logs-a-project` 專題：殘留量何時低於標準 / Project: when does a residue fall below the limit? · new: none · pre: exponential-equations.

**Part 25 · 向量進階 Vectors in depth**
- `area-determinant` 面積與二階行列式 / Area and 2×2 determinants — [G-11A-6] · new: 2×2 determinant; determinant as signed parallelogram area · uses: the number ad − bc; triangle area from coordinates · pre: inverse-matrix, point-line-distance, dot-product.
- `cauchy-inequality` 柯西不等式 / Cauchy–Schwarz — [G-11A-6] · new: Cauchy–Schwarz inequality; equality case of Cauchy · pre: dot-product.
- `space-vectors` 空間向量 / Space vectors — [G-11A-3] · new: space vector components; linear combination in space · pre: space-project, linear-combinations.
- `triangle-inequality` 三角不等式 / Triangle inequality — [G-11A-4] · new: vector triangle inequality; real-number triangle inequality as a special case · uses: triangle side inequality · pre: space-vectors, triangle-quadrilateral-properties.
- `space-dot-product` 空間內積 / Dot product in space — [G-11A-7] · new: dot product in space; Cauchy–Schwarz in space · pre: triangle-inequality, cauchy-inequality, perpendicular-vectors.
- `cross-product` 外積 / Cross product — [G-11A-7] · new: cross product; cross product is perpendicular to both vectors; cross product length as parallelogram area · pre: space-dot-product, area-determinant.
- `determinant-3x3` 三階行列式與體積 / 3×3 determinants and volume — [G-11A-8] · new: 3×3 determinant; scalar triple product; parallelepiped volume · uses: volume · pre: cross-product · viz: isometric parallelepiped.
- `vectors-a-project` 專題：帳篷的容積與頂篷面積 / Project: a tent's volume and roof area · new: none · pre: determinant-3x3.

**Part 26 · 空間中的平面與直線 Planes and lines in space**
- `three-perpendiculars` 三垂線定理 / Three perpendiculars — [S-11A-1] · new: theorem of three perpendiculars · uses: dihedral angle · pre: lines-and-planes-in-space.
- `plane-equations` 平面方程式 / Plane equations — [G-11A-9] · new: normal vector of a plane; equation of a plane; angle between two planes · uses: normal vector of a line · pre: three-perpendiculars, cross-product.
- `point-plane-distance` 點到平面距離 / Point-to-plane distance — [G-11A-9] · new: point-to-plane distance formula; distance between parallel planes · pre: plane-equations.
- `lines-in-space` 空間直線方程式 / Lines in space — [G-11A-10] · new: parametric equations of a line in space; symmetric (ratio) form; line–plane relations by equation · pre: point-plane-distance.
- `space-distances` 點線距與歪斜線距離 / Distances in space — [G-11A-10] · new: point-to-line distance in space; distance between skew lines · pre: lines-in-space · low-P: 115數A Q20, P = 2%.
- `planes-lines-project` 專題：兩條纜車線的最近距離 / Project: closest approach of two cable-car lines · new: none · pre: space-distances.

**Part 27 · 方程組與矩陣應用 Systems and matrix applications**
- `cramers-rule` 克拉瑪公式與解的個數 / Cramer's rule — [A-11A-1] · new: Cramer's rule; unique infinitely many or no solutions · pre: area-determinant, matrix-vector-product.
- `gaussian-elimination` 三元一次與高斯消去 / Gaussian elimination — [A-11A-2] · new: system of three linear equations; augmented matrix; Gaussian elimination · uses: equation of a plane · pre: cramers-rule, plane-equations · ★ for the three-plane test; no rank.
- `linear-transformations` 線性變換 / Linear transformations — [F-11A-3] · new: linear transformation; rotation matrix; reflection and scaling matrices; composing transformations · pre: matrices-project, sum-difference-formulas.
- `transition-matrices` 二階轉移方陣 / Transition matrices — [F-11A-3] · new: transition matrix; state vector after n steps · uses: conditional probability · pre: linear-transformations, probability-11-project. This placement keeps the verified F-11A-3 fix.
- `matrices-a-project` 專題：旋轉角色與天氣鏈 / Project: rotate a sprite; a two-state weather chain · new: none · pre: transition-matrices, gaussian-elimination.

### Parts 28–30 · 數B track [數B]
**Part 28 · 成長模型 Growth models**
- `average-growth-rate` 平均成長／衰退率 / Average growth rate — [F-11B-2] · new: average growth rate; average decline rate · uses: geometric mean · pre: exp-log-project, am-gm-inequality, using-log-tables · low-P: 113數B Q11, P = 31%.
- `continuous-compounding` 連續複利、e、ln / Continuous compounding — [F-11B-2] · new: continuous compounding; the number e; natural logarithm · uses: compound interest · pre: average-growth-rate. These items are not in 11A; optional for 數A learners.
- `growth-b-project` 專題：減碳目標算得到嗎 / Project: can a city meet its carbon target? (hypothetical data) · new: none · pre: continuous-compounding, radians-sine-project.

**Part 29 · 空間、地球、圓錐曲線 Space, the globe, conics**
- `shortest-surface-path` 長方體表面最短路徑 / Shortest path on a box's surface — [S-11B-1] · new: shortest path on a surface via a net · uses: net of a solid · pre: lines-and-planes-in-space.
- `globe-circles` 大圓、小圓、經緯線 / Great circles and latitude — [S-11B-1] · new: great circle and small circle; meridian and parallel of latitude; radius of a latitude circle · uses: radian; cosine ratio · pre: shortest-surface-path, radians · low-P: 115數B Q4 P = 44%, 113數B Q16 P = 15% · viz: D3 orthographic globe with Natural Earth data.
- `latitude-longitude-coordinates` 經緯度→空間坐標 / Latitude and longitude to (x, y, z) — [G-11B-4] · new: coordinates of a point on a sphere from latitude and longitude · pre: globe-circles, space-coordinates.
- `conic-sections` 平面截圓錐 / Conic sections as slices of a cone — [S-11B-2] · new: double cone and generator line; conic section; circle ellipse parabola and hyperbola by slice angle · uses: parabola · pre: lines-and-planes-in-space, quadratic-functions · M10 · no standard equations (those are G-12甲-1) · viz: 3D cone with a draggable cutting plane.
- `space-b-project` 專題：沿緯線或沿大圓飛 / Project: fly along a parallel or a great circle? · new: none · pre: latitude-longitude-coordinates, conic-sections.

**Part 30 · 比例與透視 Proportion and perspective**
- `proportion-in-design` 設計中的比例 / Proportion in design — [G-11B-3] · new: proportional reasoning in plane design · pre: similar-figures, section-formula, lines-and-planes-in-space.
- `one-point-perspective` 單點透視與消失點 / One-point perspective — [G-11B-3, S-11B-1] · new: one-point perspective; vanishing point; horizon line · pre: proportion-in-design · M7 · low-P: 115數B Q17, P = 3% · these terms come from past items, not the 條目 text.
- `perspective-b-project` 專題：等距門的透視走廊 / Project: a perspective corridor with evenly spaced doors · new: none · pre: one-point-perspective.

### Part 31 · 考試技能 Exam skills [both, except the two capstones]
Chapters 1–8 can be started any time after Part 16. The planner should surface them early.
- `exam-paper-tour` 認識試卷 / Tour of the paper — the 111–115 layout (數A 6/6/5 + 15, 數B 7/5/5 + 15); 116 is unconfirmed [J][K] · new: paper sections and points; time budget · pre: what-is-gsat · 25 min.
- `fill-in-answers` 選填劃記 / Bubbling fill-in answers · new: digit-by-digit bubbling; all-blanks-correct rule · uses: simplest form; rationalizing the denominator · pre: exam-paper-tour, radicals.
- `multiple-select-strategy` 多選計分與策略 / Multiple-select scoring · new: (n − 2k)/n scoring rule; expected score of marking an option · uses: expected value · pre: exam-paper-tour, expected-value. The marking rule is derived in the chapter: mark an option when you think it is more likely right than wrong, then check the floor at 0.
- `formula-sheet` 善用公式頁 / Using the formula sheet · new: formula-sheet lookup; estimating with given √ and log values · pre: exam-paper-tour, best-fit-line, law-of-cosines, series-and-sums, using-log-tables. The chapter notes that the 數A sheet also prints the sum formulas.
- `calculator-free-arithmetic` 不用計算機 / Calculator-free arithmetic · new: simplify before computing; magnitude check · uses: reasonableness check · pre: exam-paper-tour, radicals, scientific-notation-arithmetic.
- `written-reasoning` 混合題推理寫法 / Writing reasoning to the 評分原則 standard [R] · new: reasoning chain; partial-credit rules · uses: implication · pre: exam-paper-tour, logic-toolbox · M3, M6, M0.
- `context-items` 素養題轉譯 / Context items into math · new: translation checklist; drawing your own figure · uses: mathematical model · pre: written-reasoning, data-analysis-project, algebra-2-bridge-project · M0.
- `review-plan` 交錯練習與考前計畫 / Interleaving and the final-weeks plan · new: interleaved practice; spaced review · uses: exam countdown planner · pre: context-items, choose-your-route.
- `mock-a-capstone` 數A 模擬卷 / Capstone: 數A practice paper — original items plus links to 111–115 數A [數A] · new: none · pre: review-plan, fill-in-answers, multiple-select-strategy, formula-sheet, calculator-free-arithmetic, all five 數A project chapters · 130 min.
- `mock-b-capstone` 數B 模擬卷 / Capstone: 數B practice paper [數B] · new: none · pre: review-plan, the same skills chapters, growth-b-project, space-b-project, perspective-b-project · 130 min.

### Part 32 · Track X1：學測以外的延伸 Beyond the 學測 text [extension]
- `circle-general-form` 圓的一般式 / General form of a circle — [G-10-3, labelled extension] · new: general form of a circle equation; condition for a real circle · pre: circle-equation · 20 min.
- `sigma-notation` Σ 符號預習 / Σ preview — [N-12甲-2, N-12乙-2, Σ part] · new: sigma notation; index of summation · pre: series-and-sums, standard-deviation · 20 min.
- `reciprocal-trig-functions` cot、sec、csc（※） / Reciprocal trig functions — [F-11A-1 ※] · new: cotangent secant and cosecant · pre: cos-tan-graphs (needs 數A) · 20 min.
- `cauchy-correlation` 柯西與相關係數範圍（※） / Why |r| ≤ 1 — [G-11A-7 ※] · new: correlation as cosine of deviation vectors · pre: cauchy-inequality, scatter-correlation (needs 數A) · 20 min.
- `newton-interpolation` 牛頓插值（延伸） / Newton interpolation — [A-11A-2 optional link] · new: Newton interpolation polynomial · pre: gaussian-elimination (needs 數A) · 20 min.
- `beyond-gsat-project` 專題：延伸挑戰 / Project: extension challenges · new: none · pre: circle-general-form, sigma-notation. This project is reachable from 數B.

### Part 33 · Track X2：12年級預習（分科 數甲／數乙） Grade-12 preview [extension, outline only]
Tags: 甲 = 數甲 only, 乙 = 數乙 only, 甲乙 = both.

Chapters:
1. `infinite-geometric-series` [甲乙; N-12甲-2, N-12乙-2]
2. `sequence-limits` [甲]
3. `complex-numbers` [甲乙]
4. `de-moivre` [甲]
5. `imaginary-roots` [乙]
6. `conic-equations` [甲; G-12甲-1]
7. `linear-programming` [乙; A-12乙-1]
8. `functions-and-limits` [甲乙]
9. `derivatives` [甲乙]
10. `derivative-applications` [甲乙; second derivative in 乙]
11. `integrals` [甲: Riemann sums; 乙: linear and quadratic functions only]
12. `random-variables` [甲乙]
13. `binomial-geometric-distributions` [甲: binomial and geometric; 乙: binomial only]
14. `grade12-preview-project`

All chapters require `sigma-notation`; about 28 min each. Of the 12甲/12乙 codes, only N-12甲-2, N-12乙-2, G-12甲-1 and A-12乙-1 have known content. The research gives only group-level summaries for the rest, so their per-code mapping and concepts are an open item (O6).

## 3. Coverage proof

### 10年級: all 23 codes placed

| Code | Chapters |
|---|---|
| N-10-1 | real-numbers, scientific-notation-arithmetic |
| N-10-2 | absolute-value-equations |
| A-10-1 | cubic-identities, radicals, rational-expressions |
| N-10-3 | rational-exponents, am-gm-inequality |
| N-10-4 | common-logarithms, using-log-tables |
| N-10-5 ★＃ | error-toolbox |
| N-10-7 ★＃ | logic-toolbox |
| N-10-6 | recursive-sequences, series-and-sums, mathematical-induction |
| G-10-1 ＃ | coordinate-symmetry-toolbox |
| G-10-2 | slope, parallel-perpendicular-lines, point-line-distance, two-variable-inequalities |
| G-10-3 | circle-equation (general form in X1 circle-general-form) |
| G-10-4 | lines-and-circles |
| G-10-5 | generalized-angles, polar-coordinates |
| G-10-6 | trig-ratios, trig-any-angle |
| G-10-7 | law-of-sines, law-of-cosines, slope-and-angles, triangulation-toolbox |
| A-10-2 | polynomial-division, remainder-factor-theorems |
| F-10-1 | function-notation, quadratic-function-extremes, section-formula |
| F-10-2 | cubic-functions |
| F-10-3 | polynomial-inequalities |
| D-10-1 ★＃ | sets-toolbox |
| D-10-2 | standard-deviation, percentiles, standardization, scatter-correlation, best-fit-line |
| D-10-3 | systematic-counting, inclusion-exclusion, permutations, combinations, binomial-expansion |
| D-10-4 | sample-spaces, compound-probability, expected-value |

### 11A: all 23 codes placed (S = shared chapter, A = 數A chapter)

| Code | Chapters |
|---|---|
| N-11A-1 | radians (S) |
| S-11A-1 | lines-and-planes-in-space (S), three-perpendiculars (A) |
| G-11A-1 | vectors, vector-arithmetic, linear-combinations (S) |
| G-11A-2 | space-coordinates (S) |
| G-11A-3 | space-vectors |
| G-11A-4 | triangle-inequality |
| G-11A-5 | sum-difference-formulas, double-half-angle |
| G-11A-6 | dot-product, perpendicular-vectors (S); area-determinant, cauchy-inequality (A) |
| G-11A-7 | space-dot-product, cross-product (※ part in X1 cauchy-correlation) |
| G-11A-8 | determinant-3x3 |
| G-11A-9 | plane-equations, point-plane-distance |
| G-11A-10 | lines-in-space, space-distances |
| A-11A-1 | matrix-vector-product (S), cramers-rule (A) |
| A-11A-2 | gaussian-elimination |
| A-11A-3 | matrices, matrix-multiplication, inverse-matrix (S) |
| A-11A-4 | laws-of-logarithms, exponential-equations |
| F-11A-1 | sine-function, periodic-models (S); cos-tan-graphs (A); ※ part in X1 |
| F-11A-2 | combining-sine-cosine |
| F-11A-3 | linear-transformations, transition-matrices |
| F-11A-4 | exponential-functions, logarithmic-functions (S); exponential-equations (A) |
| D-11A-1 | subjective-objective-probability (S) |
| D-11A-2 | conditional-probability, independent-events (S) |
| D-11A-3 | conditional-probability, bayes-theorem (S) |

### 11B: all 12 codes placed

| Code | Chapters |
|---|---|
| N-11B-1 | radians |
| S-11B-1 | lines-and-planes-in-space (S), shortest-surface-path, globe-circles, one-point-perspective |
| S-11B-2 | conic-sections |
| G-11B-1 | vectors, vector-arithmetic, linear-combinations |
| G-11B-2 | dot-product, perpendicular-vectors |
| G-11B-3 | proportion-in-design, one-point-perspective |
| G-11B-4 | space-coordinates (S), latitude-longitude-coordinates |
| A-11B-1 | matrices, matrix-vector-product, matrix-multiplication, inverse-matrix |
| F-11B-1 | sine-function, periodic-models |
| F-11B-2 | exponential-functions, logarithmic-functions (S); average-growth-rate, continuous-compounding |
| D-11B-1 | subjective-objective-probability |
| D-11B-2 | conditional-probability, independent-events, bayes-theorem |

### Bridge codes: all 132 placed

| Codes | Chapter |
|---|---|
| N-3-11, N-5-1, R-4-1, R-4-2, R-5-2, R-6-1 | whole-numbers |
| N-5-3, N-6-1, N-6-2, N-7-1, N-7-2 | factors-and-primes |
| N-3-9, N-4-5, N-4-6, N-5-4, N-4-8 | fractions |
| N-5-5, N-5-6, N-5-7, N-6-3 | fraction-operations |
| N-3-10, N-4-7, N-4-8, N-5-1, N-5-8, N-5-9, N-6-4 | decimals |
| N-5-11 | rounding-and-estimation |
| N-5-10, N-6-6, N-6-8 | ratio-and-percent |
| N-6-7 | speed-and-units |
| R-3-2, R-4-4 | number-patterns |
| R-4-3, R-5-3, R-6-2, R-6-3 | formulas-with-symbols |
| R-6-4, N-6-9 | first-counting |
| N-4-10, S-4-1, S-4-2 | angles-and-turns |
| S-4-5, S-4-7, S-4-8, S-5-1, S-5-2 | plane-figures-and-area |
| S-3-3, S-5-3, S-6-3 | circles-and-sectors |
| S-6-1, S-6-2 | scale-drawings |
| S-5-5, S-5-6, S-5-7, S-6-4 | solids |
| D-3-1, D-4-1, D-5-1, D-6-1 | tables-and-charts |
| D-6-2 | likelihood |
| N-7-3, N-7-4 | negative-numbers |
| N-7-5 | absolute-value-distance |
| N-7-6, N-7-7 | integer-exponents |
| N-7-8 | scientific-notation |
| N-8-1, N-8-2 | square-roots |
| N-7-9, N-9-1 | proportions |
| A-7-1, A-7-2, A-7-3 | linear-equations |
| A-7-7, A-7-8 | linear-inequalities |
| G-7-1 | coordinate-plane |
| A-7-4, A-7-5, A-7-6 | linear-systems |
| S-7-1, S-7-3 | geometry-basics |
| S-8-1, S-8-2, S-8-3 | angles-and-parallels |
| S-5-4, S-7-4, S-7-5 | line-symmetry |
| S-8-4, S-8-5 | congruent-triangles |
| S-8-8, S-8-9, S-8-10, S-8-11 | triangle-quadrilateral-properties |
| S-8-12, S-9-11 | constructions-and-proof |
| S-8-6, S-8-7 | pythagorean-theorem |
| G-8-1 | distance-formula |
| S-9-1, S-9-2, S-9-3 | similar-figures |
| S-9-4 | right-triangle-ratios |
| S-9-5, S-9-6, S-9-7 | circle-properties |
| S-9-8, S-9-9, S-9-10 | triangle-centres |
| S-7-2, S-9-12, S-9-13 | space-lines-planes-volume |
| A-8-1, A-8-2, A-8-3 | polynomials |
| A-8-4, A-8-5 | factoring |
| A-8-6, A-8-7 | quadratic-equations |
| N-8-3, N-8-4, N-8-5, N-8-6 | sequences |
| F-8-1, F-8-2 | linear-functions |
| F-9-1, F-9-2 | quadratic-functions |
| D-7-1, D-7-2 | averages-and-charts |
| D-8-1 | cumulative-frequency |
| D-9-1 | quartiles-box-plots |
| D-9-2, D-9-3 | probability-basics |

**Unplaced codes:** none. The only exception is the 12甲/12乙 per-code split (O6).

## 4. Totals

| Block | Parts | Chapters | Minutes |
|---|---|---|---|
| Part 0 | 0 | 3 | 34 |
| Bridges | 1–7 | 7 + 6 + 8 + 11 + 14 + 7 + 5 = **58** | ≈ 1,222 (20.4 h) |
| 10年級 | 8–16 | 7 + 6 + 5 + 8 + 9 + 8 + 6 + 7 + 4 = **60** | ≈ 1,655 (27.6 h) |
| Shared Grade 11 | 17–22 | 4 + 6 + 3 + 3 + 5 + 5 = **26** | ≈ 770 (12.8 h) |
| 數A track | 23–27 | 5 + 3 + 8 + 6 + 5 = **27** | ≈ 791 (13.2 h) |
| 數B track | 28–30 | 3 + 5 + 3 = **11** | ≈ 329 (5.5 h) |
| Exam skills | 31 | **10** (8 skills + 2 capstones) | 200 + 2 × 130 |
| Extensions | 32–33 | 6 + 14 = **20** | ≈ 130 + 400 |
| **Total** | 34 parts | **215** | ≈ 96 h |

Paths, lesson time only (spaced review and practice come on top):

| Path | Chapters | Hours |
|---|---|---|
| 數B from zero | 167 | ≈ 72 |
| 數A from zero | 183 | ≈ 80 |
| Both papers | 195 | ≈ 88 |
| 數B, skipping bridges by placement | — | ≈ 52 |
| 數A, skipping bridges by placement | — | ≈ 60 |

The exam is 68 days away (counting from 2026-11-15). The 數B path from zero therefore needs about 65 minutes of lessons a day, so the placement check and the planner are essential.

## 5. Math chapters other subjects need (schedule these early)

| Math chapter | Needed by | Basis in the research |
|---|---|---|
| scientific-notation (N-7-8) | 化學; 物理, 生物 and 地科 scale work | 化學 bridge verified; the others are unverified or science-coded |
| scientific-notation-arithmetic (N-10-1) | 化學 (mole, concentration) | verified: N-10-1 rather than 國中, may run in parallel |
| common-logarithms (N-10-4) | 化學 pH; 地理 rank-size log axes | verified / added |
| logarithmic-functions (log scale) | 地理 (deeper log axes) | optional link |
| ratio-and-percent, speed-and-units | 化學 (N-6-6..8 verified); 公民 percentage change; 物理 | 公民 and 物理 codes unverified |
| proportions (N-7-9) | 化學 (verified); 物理 inverse-square; 生物 ratios | 物理 and 生物 unverified |
| linear-equations, linear-systems | 化學 (A-7-2..4) | verified |
| fraction-operations | 公民 特留分 | unverified |
| tables-and-charts, averages-and-charts, coordinate-plane | 地理 | verified |
| tables-and-charts, coordinate-plane, linear-functions | 公民 (charts, supply and demand) | unverified |
| scale-drawings, similar-figures | 地理 map scale (S-6-2, S-9-1) | verified / added |
| probability-basics | 生物 genetics ratios | unverified |
| sequences (repeated halving), exponential-functions (half-life) | 地科 half-life | math code unverified; use the bridge chapter for 10th-grade 地科 |
| globe-circles (數B) | 地理 | S-11B-1 備註 says 留意地理課的需求; recommend it as optional for 數A learners |

The data model must allow prereq edges from other subjects into these math slugs. All of them already sit in the bridges or early in 10年級, except the log and globe chapters.

## 6. Open items

| # | Open item |
|---|---|
| O1 | Where a research bridge group is split across chapters, I assigned codes per chapter from the topic wording. Check every 條目's wording in [L] before data entry, especially N-5-8/N-5-9, S-4-5…S-5-2, A-8-x, S-8-x and S-9-x. |
| O2 | Is the discriminant at 國中 depth inside A-8-7? If not, move the concept to `lines-and-circles`. |
| O3 | Which formulas exactly count as N-10-6's 常用的求和公式? |
| O4 | 選填 answer conventions (simplest form, rationalized answers) need checking against the papers' 作答說明. |
| O5 | Which percentile definition does CEEC use? The research says definitions can differ. |
| O6 | Per-code content of 12甲/12乙 is not in the research. |
| O7 | The D2 deviations need sign-off. |
| O8 | Normal vector of a line inside 數B scope: boundary check. |
| O9 | Real data for projects (day length; any real-world rates) needs cited sources; otherwise label the numbers hypothetical. |
| O10 | Can JSXGraph View3D (MIT option) handle the cone-slicing and parallelepiped widgets? |
| O11 | The 116 paper layout is unconfirmed; exam chapters should say "the 111–115 papers had…". |
| O12 | The 樂詞網 category attribution of some term pairs is unverified. |

## 7. Test additions for the new project

| Rule | Detail |
|---|---|
| Track purity | As in D1. |
| Code coverage | Every in-scope code and every bridge code appears in at least one chapter's `codes`. |
| Marks | `marks` covers ★, ＃ and ※. ※ appears only in `extension` chapters. ＃ chapters are toolboxes of ≤15 min. |
| Projects | Each part ends with a project; Part 31 ends with two capstones. |
| Minutes | ≤ 35, except capstones. |
| Cross-subject prereqs | Allowed only into existing math slugs. |

### Critical Files for Implementation
- C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\a673455e-fcf2-49cf-bfaa-b16e3c4f2485\tasks\woe8teuu0.output (math: `verification.final_units`, `final_bridging_prereqs`; `research.common_misconceptions`, `terminology`)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\src\data\course.json (schema to mirror; read only)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\curriculum.test.ts (no-jump rules to extend with track purity and code coverage; read only)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\src\data\curriculum.ts (TRACKS and neighbours model to adapt for the 數A/數B branch; read only)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\course.json (to create: the math course data built from this map)