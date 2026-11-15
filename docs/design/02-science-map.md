<!-- Frozen design output (Science course map), 2026-11-15. Superseded where docs/design/06-critique.md or the approved plan says so. -->

# 自然 curriculum architecture: 物理, 化學, 生物, 地球科學, 探究與實作

All codes, exam items and facts below come from the `verification` blocks (and `research` where noted) in `woe8teuu0.output`. The concept names are draft labels for the concept registry.

**Legend**
- **[B]** bridge (國小/國中)
- **[PROJ]** project chapter, ≤2 new concepts
- **[TK]** exam toolkit: tested skill beyond the 必修 text, cited with evidence
- **[EXT]** enrichment sidebar
- **[PRE]** labelled term preview
- **(n)** number of new concepts
- **←** cross-subject prerequisite

**Misconception status codes**
- **V**: documented; the verification pass re-checked the source.
- **D**: documented; the source was not re-opened.
- **C**: CEEC document (考試說明, 評分原則 or 試題特色).
- **H**: design hypothesis, or a risk inferred from the curriculum. Needs a student-data source before it is used as a refutation text.

## 0. Global rules this design assumes

1. **One concept registry for the whole site** (Math + 自然 + 社會 + 國文).
   - The reference tests (introduce once; uses ⊆ ancestors) then run across subjects.
   - Each shared concept lives in the earliest chapter in the global order (§6c). Edges to other subjects are explicit `prereqs`.
2. **Every science part ends with an inquiry project tagged with 探究 sub-items.** This satisfies the reference "part ends with project" rule and makes 探究 recur (§7). Slugs must contain `project`.
3. **New chapter fields:**
   - `subject`
   - `codes`, stored normalised plus as displayed. Ⅴ vs V is inconsistent: physics and biology use Roman Ⅴ, chemistry mostly ASCII V, the 考試說明 ASCII.
   - `strands`, `examEvidence[{year, q, url}]`, `misconceptions[{id, status}]`, `scopeFlag`
4. **New tests:**
   - every in-scope code maps to ≥1 chapter;
   - every TK chapter has evidence;
   - refutation texts only for misconceptions with status V, D or C;
   - every 探究 sub-item appears in ≥2 projects;
   - no track chapter is a prereq of a core chapter.
5. **Past-item → code mappings are planner inference.** CEEC publishes subject blocks, not per-item codes. Label them as the site's own mapping.

## 1. Shared parts

### SCI-0 自然共同基礎 [B]

Uses Math N-6-6~8 and N-7-6~9.

| Ch | Title | Codes | New concepts |
|---|---|---|---|
| S0.1 | 自然考什麼 / What the paper tests | 簡章註3, 考試說明 | 四科＋探究、占分相當; 第壹／貳部分題組; 國中內容可作背景 (3) |
| S0.2 | 科學如何進步 | Mb-Ⅳ-2, Ma-Ⅳ-1 | 科學知識隨證據修正; 科學史重要發現 (2) |
| S0.3 | 物理量、單位與尺度 | Ea-Ⅳ-1~3, INc-Ⅳ-1~4 | 數值＋單位; 單位換算; 奈米到光年; 數量級估計 (4) |
| S0.4 | 溫度與熱 | Bb-Ⅳ-1~5 | 溫度vs熱量; 熱量單位; 比熱; 傳導對流輻射; 熱膨脹 (5) |
| S0.5 | 粒子模型與三態 | Ab-Ⅳ-1~2 | 粒子模型; 三態粒子排列; 溫度改變狀態 (3) |
| S0.6 | 原子與分子 | Aa-Ⅳ-1, Cb-Ⅳ-1 | 原子; 分子; 原子模型發展（國中） (3) |
| S0.7 | 能量形式與守恆 | Ba-Ⅳ-1 | 能量形式; 能量轉換; 孤立系統守恆 (3) |
| S0.8 | 變因與對照實驗 | Dc-Ⅳ-5/Bc-Ⅳ-1 說明 | 操作／應變／控制變因; 對照組 (4) |
| S0.9 | [PROJ] 保溫杯大挑戰 | 規劃與研究 | 數據紀錄表; 重複測量 (2) |

Some 國中 codes sit in later bridges because each needs a concept that SCI-0 has not taught yet:
- Ba-Ⅳ-2 → BB1.5 (needs photosynthesis)
- Ba-Ⅳ-3 → CB1.6 (needs "chemical reaction")
- Ba-Ⅳ-4 → CB2.5 (needs electricity)
- Ec-Ⅳ-1~2 → PB1.8 (needs force)

### INQ-1 探究與實作 (dedicated short part; no codes)

- **I1.1 探究與實作是什麼.** New: 四面向; 實作學習內容; 七跨科概念 (3)
- **I1.2 發現問題** (觀察現象, 蒐集資訊, 形成或訂定問題, 提出可驗證的觀點).
  - New: 可研究的問題; 資訊可信度; 可驗證觀點 (3)
  - Evidence: 考試說明 金門 tide item; 外傘頂洲 Q1
- **I1.3 規劃與研究** (尋找變因或條件, 擬定研究計畫, 收集資料數據).
  - New: 研究計畫; 以變因關係陳述預測; 定性／定量資料 (3)
  - Evidence: 113 Q43 scoring guide; 112 Q38–39; 外傘頂洲 Q2
- **I1.4 論證與建模** (分析資料和呈現證據, 解釋和推理, 提出結論或解決方案, 建立模型).
  - New: 趨勢與規律; 主張–證據–推理; 模型與限制 (3)
  - Evidence: 尼伯特 buoy item; 115 Q50
- **I1.5 表達與分享** (表達與溝通, 合作與討論, 評價與省思).
  - New: 精確用語; 評價實驗設計; 可重複性 (3)
  - Evidence: 外傘頂洲 item; 115 Q54; 115 Q38
- **I1.6 [PROJ] 紙飛機探究.** Uses all four strands and needs no physics laws. New: 探究報告結構 (1)

### SCI-E 環境、能源與永續（國中共同）[B]

Shared by chemistry, biology and earth science.

| Ch | Codes | New |
|---|---|---|
| SE.1 化石燃料與新興能源 | Nc-Ⅳ-3~4 | 2 |
| SE.2 水與空氣汙染 | Me-Ⅳ-2, Me-Ⅳ-3, Me-Ⅳ-6 | 2 |
| SE.3 溫室效應與氣候變遷 | Me-Ⅳ-4, Nb-Ⅳ-1~3, INg-Ⅳ-2, INg-Ⅳ-7 | 4 |
| SE.4 永續發展 | Na-Ⅳ-1~7 | 2 |
| SE.5 [PROJ] 一週碳足跡 | 論證與建模 | 1 |

## 2. 物理

**Teaching order.** The 課綱 prints the codes in the order B→E→K→M→N and calls that order 只是一個建議. Ours: Mc-3 → Ea → Ke/Kc-1~2 → Eb → Kb → Ka → Kc-3~6/Ka-7 → Mc-1~2 → Ba/Bb/Nc → Kd.

Why this order:
- The Eb 說明 says the third law 呼應前章節基本交互作用, so Ke comes before Eb.
- PKc-Ⅴc-2 moves after Coulomb's law (correction).
- Light Doppler is revisited only after light is shown to be a wave (correction).
- Ba comes after Kc because fields carry energy.
- Kd comes after interference because the electron double slit is likened to Young's experiment.
- PMc-Ⅴc-4 is woven through every chapter (說明: 不必另成一個單元).
- Lenz's law and dimensional analysis are TK (corrections).

### Bridge parts

**PHY-B1 力與運動（國中）**

| Ch | Codes | New |
|---|---|---|
| PB1.1 描述運動 | Eb-Ⅳ-8 | 3 |
| PB1.2 加速度 | Eb-Ⅳ-9, Eb-Ⅳ-11 | 3 |
| PB1.3 力、力矩、平衡 | Eb-Ⅳ-1~2 | 4 |
| PB1.4 摩擦力 | Eb-Ⅳ-3~4 | 3 |
| PB1.5 牛頓定律（國中） | Eb-Ⅳ-10~13 | 3 |
| PB1.6 質量、重量、萬有引力 | Kb-Ⅳ-1~2 | 2 |
| PB1.7 壓力、浮力、簡單機械 | Eb-Ⅳ-5~7 | 4 |
| PB1.8 大氣與氣體壓力 | Ec-Ⅳ-1~2 | 3 |
| PB1.9 功、功率、力學能 | Ba-Ⅳ-5~7 | 4 |
| PB1.10 [PROJ] 斜面小車 | — | 1 |

**PHY-B2 波、光、電與磁（國中）**

| Ch | Codes | New |
|---|---|---|
| PB2.1 波的特徵（含 v=fλ） | Ka-Ⅳ-1~2 | 4 |
| PB2.2 聲音 | Ka-Ⅳ-3~5 | 3 |
| PB2.3 直進、光速、反射 | Ka-Ⅳ-6~8 | 4 |
| PB2.4 折射、透鏡、色散 | Ka-Ⅳ-9~11 | 4 |
| PB2.5 靜電 | Kc-Ⅳ-1~2 | 3 |
| PB2.6 磁、電流磁效應、安培右手 | Kc-Ⅳ-3~5 | 4 |
| PB2.7 感應電流、發電機 | Kc-Ⅳ-6 | 2 |
| PB2.8 電路與歐姆 | Kc-Ⅳ-7~8 | 4 |
| PB2.9 電力、安全、發電 | Mc-Ⅳ-5~7, Ma-Ⅳ-4 | 3 |
| PB2.10 [PROJ] 磁鐵進出線圈（只觀察） | — | 1 |

### PHY-1 尺度、物質與交互作用

- **P1.1 物理學是什麼.** PMc-Ⅴc-3; the PMc-Ⅴc-4 strand starts here as a 人物卡 in every chapter. New: 科學態度; 物理範疇與發展; 現代挑戰跨領域 (3)
- **P1.2 尺度與單位.** PEa-Ⅴc-1~3. New: SI基本量; 導出量; 原子10⁻¹⁰m／原子核10⁻¹⁵m (3)
- **P1.3 原子、原子核與夸克.** PKe-Ⅴc-1 (說明1-1~1-6). New: 原子核（質子中子）; 電子與電中性; 夸克（不需種類電量）; 聲光熱電源自粒子交互作用 (4). This is the canonical home of p/n/e.
- **P1.4 重力與電力：平方反比.** New: 場; 萬有引力定律; 電場（單一點電荷）; 庫侖定律 (4)
- **P1.5 原子穩定與核力.** PKc-Ⅴc-2, PKe-Ⅴc-2~3. New: 電吸引使原子穩定; 強作用力; 弱作用力（中子衰變）; [TK] α／β衰變式與對應作用力 (112 Q52) (4)
- **P1.6 四種基本交互作用.** New: 日常的力本質為電磁; 四種交互作用統整 (2)
- **P1.7 [PROJ] 尺度與交互作用地圖.** Strand: 建立模型. New: 尺度階梯 (1)

P1.4–P1.6 together cover {PKe-Ⅴc-1~3, PKc-Ⅴc-1~2}. The split by individual code is open.

### PHY-2 從伽利略到牛頓

- **P2.1** PEb-Ⅴc-1~2. New: 伽利略前的運動爭論; 伽利略的研究推理 (2)
- **P2.2** PEb-Ⅴc-3. New: 克卜勒一／二／三定律; 由觀測歸納 (4)
- **P2.3** PEb-Ⅴc-4. New: 第一定律（高中）; 淨力決定加速度方向; 運動方程定軌跡（文字） (3)
- **P2.4** PEb-Ⅴc-4. New: 施力者／受力者; 第三定律對應基本交互作用 (2)
- **P2.5** PEb-Ⅴc-5. New: 正向力; 彈力; 摩擦改變運動; 自由體圖 (4)
- **P2.6** PKb-Ⅴc-1~2. New: 演繹vs歸納; 牛頓＋平方反比→克卜勒; 重力場中運動（定性） (3)
- **P2.7 [PROJ]** 力學能守恆與運動. This is the 課綱 demo experiment under Eb. New: 以數據檢驗守恆 (1)

### Later physics parts

**PHY-3 波與光**

| Ch | Codes | New |
|---|---|---|
| P3.1 聲波都卜勒 | PKa-1~2 | 2 |
| P3.2 光本質之爭 | PKa-3 | 2 |
| P3.3 折射與司乃耳（圖示法） | PKa-4 | 3 |
| P3.4 干涉繞射惠更斯 | PKa-5~6 | 4 |
| P3.5 [PROJ] 雙狹縫（demo） | — | 1 |

**PHY-4 電磁統一**

| Ch | Codes | New |
|---|---|---|
| P4.1 法拉第感應 | PKc-3 | 3 |
| **P4.2 [TK] 冷次定律** | — | 2 |
| P4.3 馬克士威與電磁波 | PKc-4~5 | 3 |
| P4.4 光是電磁波；電磁波譜 | PKc-6, PKa-7 | 3 |
| P4.5 用電安全與應用 | PMc-1~2 | 3 |
| P4.6 [PROJ] 磁鐵穿線圈 I–t 圖 | — | 1 |

- P4.4 also revisits light Doppler.
- P4.5: the 課綱 has no 說明 for PMc-1~2. Source the content from the 考試說明 sample tags (夢溪筆談; induction cooker).

**PHY-5 能量**

| Ch | Codes | New |
|---|---|---|
| P5.1 能量形式、尺度、普遍守恆 | PBa-1~2 | 4 |
| **P5.2 [TK] 因次分析與符號式** | — | 3 |
| P5.3 絕對溫度與平均動能 | PBb-1~2 | 3 |
| P5.4 熱能與熱 | PBb-3~4 | 4 |
| P5.5 能量品質 | PNc-3~4 | 2 |
| P5.6 質能與核能 | PBa-3~4, PNc-1~2 | 4 |
| P5.7 [PROJ] 能源方案估算 | — | 1 |

**PHY-6 量子**

| Ch | Codes | New |
|---|---|---|
| P6.1 光子與光電效應 | PKd-1~2 | 4 |
| P6.2 光譜與能階 | PKd-3~4 | 3 |
| P6.3 物質波 | PKd-5~7 | 3 |
| P6.4 [PROJ] 光譜指紋 | — | 1 |

**Physics totals:** 20 bridge chapters (62 concepts) + 36 core chapters (99 concepts) = **56 chapters**.

## 3. 化學

**Teaching order.** Adapted from 翰林 rather than copied (correction).
- CEc-Vc-1 is merged into the states chapter (說明: 與其他章節合併說明).
- The mole comes after bonding. That is allowed, and it leaves time for Math N-10-1.
- CBa comes after balancing and the mole, because a thermochemical equation needs a balanced equation.
- pH waits for N-10-4.
- CJe-Vc-2 is taught with CMc-Vc-3 (課綱).
- CMb-Vc-1 is woven through.

### Bridge parts

**CHE-B1 物質與反應**

| Ch | Codes | New |
|---|---|---|
| CB1.1 分類 | Ab-Ⅳ-3~4, Aa-Ⅳ-3 | 3 |
| CB1.2 符號與命名 | Aa-Ⅳ-4~5 | 3 |
| CB1.3 原子量分子量 | Aa-Ⅳ-2 | 2 |
| CB1.4 同素異形／同分異構 | Cb-Ⅳ-2~3 | 2 |
| CB1.5 分離 | Ca-Ⅳ-1~2 | 4 |
| CB1.6 反應與吸放熱 | Ja-Ⅳ-1~4, Ba-Ⅳ-3 | 5 |
| CB1.7 [PROJ] 密閉 vs 開放 | — | 1 |

CB1.3: in 國中 "mole" is a term only, so it is not counted as a concept here.

**CHE-B2 溶液、酸鹼、氧化還原、有機**

| Ch | Codes | New |
|---|---|---|
| CB2.1 電解質離子 | Jb-Ⅳ-1~2 | 3 |
| CB2.2 濃度與沉澱 | Jb-Ⅳ-3~4 | 4 |
| CB2.3 酸鹼鹽 | Jd-Ⅳ-1~6 | 5 |
| CB2.4 得失氧 | Jc-Ⅳ-1~4 | 3 |
| CB2.5 電池電解 | Jc-Ⅳ-5~7, Ba-Ⅳ-4 | 2 |
| CB2.6 速率與平衡 | Je-Ⅳ-1~3 | 3 |
| CB2.7 有機入門 | Jf-Ⅳ-1~4 | 4 |
| CB2.8 [PROJ] 紫甘藍指示劑 | — | 1 |

### CHE-1 物質的分類與組成

- **C1.1** CAb-Vc-1, CEc-Vc-1. New: 溫壓決定狀態; 三相圖（H₂O、CO₂）; 三相點; 氣壓源自分子碰撞 (4)
- **C1.2** CCa-Vc-1. New: 蒸餾; 萃取 (2)
- **C1.3** CCa-Vc-1. New: 色層分析／TLC; 硬水軟化; 海水純化 (3). [EXT] sidebar: 再結晶.
- **C1.4** CAa-Vc-1, CJa-Vc-1 (laws). New: 拉瓦節元素與氧化觀; 定比; 倍比 (3)
- **C1.5** CAa-Vc-2. New: 道耳頓原子說; 原子說解釋三定律 (2)
- **C1.6** CAa-Vc-3~4, ← P1.3. New: 原子序; 質量數; 同位素（C、H；元素名＋質量數）; 價電子 Z=1–18 (4)
- **C1.7** CAb-Vc-2. New: 依原子序排列; 族與週期; 週期趨勢; 金屬／類金屬／非金屬 (4)
- **C1.8** CCb-Vc-1~2. New: 共價鍵與路易士結構（五分子）; 離子鍵（NaCl、MgO）; 金屬鍵; 共價網狀固體 (4)
- **C1.9** CAb-Vc-3, CCa-Vc-2. New: 離子vs分子化合物性質; 由鍵結推性質 (2)
- **C1.10 [PROJ]** 未知白色固體鑑定 (1)

### CHE-2 化學計量與能量

- **C2.1** CJa-Vc-1. New: 分子式; 實驗式; 百分組成 (3)
- **C2.2** CJa-Vc-3. **Gate: N-10-1.** New: 莫耳; 亞佛加厥數; 莫耳質量 (3)
- **C2.3** CJa-Vc-2, ← A-7-2~4. New: 觀察法; 代數法 (2)
- **C2.4** CJa-Vc-3. New: 係數比＝莫耳比; 質量–莫耳換算列式 (2). No yield, no gas volume.
- **C2.5** CBa-Vc-1~2. New: 能量變化圖; 熱化學反應式; 化學情境能量守恆 (3)
- **C2.6 [PROJ]** 燃料放熱比較. Original, modelled on the 114 fuel set. (1)

### Later chemistry parts

**CHE-3 溶液與常見反應**

| Ch | Codes | New |
|---|---|---|
| C3.1 溶液分類、廷得耳 | CJb-1 | 2 |
| C3.2 體積莫耳濃度、稀釋 | CJb-3 | 3 |
| C3.3 溶解度與溶解平衡 [EXT 再結晶] | CJb-2, CJe-1 | 3 |
| C3.4 水自解離、阿瑞尼斯 | CJd-1~2 | 3 |
| C3.5 pH、強弱、指示劑 | CJd-2~4 | 4 |
| C3.6 電子轉移 | CJc-1 | 3 |
| C3.7 常見氧化劑還原劑 | CJc-2 | 3 |
| **C3.8 [TK] 離子方程式原子＋電荷守恆** | — | 2 |
| C3.9 [PROJ] 香蕉萃取鉀鹽 | — | 1 |

- C3.5: **gate N-10-4**.
- C3.9 is modelled on the pattern of 115 Q25–27.

**CHE-4 生活、科技與永續**

| Ch | Codes | New |
|---|---|---|
| C4.1 接觸面積與奈米材料 | CJe-2, CMc-3 | 3 |
| C4.2 生物分子 | CJf-1 | 2 |
| C4.3 界面活性劑 | CJf-2~3 | 2 |
| C4.4 水處理與藥物 | CMa-1, CMc-1~2 | 3 |
| C4.5 化學發展與科學家 | CMb-1~2 | 2 |
| C4.6 環境汙染 | CMe-1~4 | 4 |
| C4.7 永續、循環、能源 | CNa-1~4, CNc-1 | 3 |
| C4.8 [PROJ] 界面活性劑效果 | — | 1 |

C4.2 depends on BB1.3 and B3.6.

**Chemistry totals:** 15 bridge chapters (45 concepts) + 33 core chapters (87 concepts) = **48 chapters**.

## 4. 生物

**Teaching order.**
- The 課綱 spine 細胞→遺傳→演化→多樣性 is kept, with BMb/BMc woven in.
- The 國中 bridge is mandatory: the 課程手冊 (p.474) says 國中 and 高中 were 合併設計, 均須完整學習完.
- DNA appears in B2.1 and B2.3 only as a flagged [PRE] (correction).
- B4.2 also depends on B3.8 (correction).
- B4.5 depends on E2.5, because 115 Q34 uses a 地質年代表.
- BDa-Ⅴc-2 is split into three chapters to stay within ≤5 concepts.

### Bridge parts

**BIO-B1**

| Ch | Codes | New |
|---|---|---|
| BB1.1 國小生態與植物 | INa-Ⅲ-10, INb-Ⅲ-7 | 3 |
| BB1.2 細胞 | Da-Ⅳ-1~2 | 3 |
| BB1.3 層次與醣蛋白脂 | Da-Ⅳ-3, Fc-Ⅳ-2 | 2 |
| BB1.4 染色體與分裂 | Da-Ⅳ-4 | 2 |
| BB1.5 酵素、呼吸、光合 | Bc-Ⅳ-1~4, Ba-Ⅳ-2 | 4 |
| BB1.6 [PROJ] 動植物細胞比較 | — | 1 |

**BIO-B2**

| Ch | Codes | New |
|---|---|---|
| BB2.1 | Db-Ⅳ-1~2 | 2 |
| BB2.2 | Db-Ⅳ-3~4 | 2 |
| BB2.3 | Db-Ⅳ-6~7 | 2 |
| BB2.4 | Dc-Ⅳ-1~5 | 4 |
| BB2.5 [PROJ] 反應時間 | — | 1 |

**BIO-B3**

| Ch | Codes | New |
|---|---|---|
| BB3.1 | Ga-Ⅳ-1~3 | 4 |
| BB3.2 | Ga-Ⅳ-4~6, Mb-Ⅳ-1 | 3 |
| BB3.3 化石、分類、學名 | Gb-Ⅳ-1, Gc-Ⅳ-1 | 3 |
| BB3.4 生態系、碳循環 | Gc-Ⅳ-2~4, Bd-Ⅳ-1~3, Fc-Ⅳ-1 | 5 |
| BB3.5 | La-Ⅳ-1, Lb-Ⅳ-1~3, Ma-Ⅳ-2, Db-Ⅳ-8 | 5 |
| BB3.6 [PROJ] 塑膠微粒 | — | 1 |

BB3.6 uses the context of 考試說明 bio samples 4–5.

### BIO-1 細胞

- **B1.1** BMb-Ⅴc-1. New: 細胞學說; 形成是科學過程; 病毒無細胞構造 (3). Evidence: 113 Q3, 115 Q30.
- **B1.2** BDa-Ⅴc-1. New: 四種玻片法; 形態與功能相關; 測微器 (3). Evidence: 112 Q13, 113 Q1.
- **B1.3** BDa-Ⅴc-2. New: 原核; 真核; 胞器 (3)
- **B1.4** BDa-Ⅴc-2. New: 核糖體; 內質網; 高基氏體 (3)
- **B1.5** BDa-Ⅴc-2. New: 粒線體; 葉綠體; 液泡 (3)
- **B1.6** BDa-Ⅴc-3. New: ATP 直接能量來源 (1). [PRE] 核糖／嘌呤, from the 115 Q32 options.
- **B1.7** BDa-Ⅴc-4. New: 細胞內光合–呼吸能量關係; 有機物化學能供代謝; [PRE] 發酵; [PRE] 光反應／固碳反應 (4). Evidence: 114 Q2, 115 Q29.
- **B1.8 [PROJ]** 真核細胞模型 (說明 2-4) (1)

### BIO-2 細胞週期與分裂

- **B2.1** BDa-Ⅴc-5. New: 細胞週期; 間期／分裂期（不細分）; [PRE] DNA 於間期複製 (3)
- **B2.2** BDa-Ⅴc-6~7. New: 核分裂＋質分裂; 有絲分裂（不命名各期）; 兩種核分裂（名稱） (3). Evidence: 114 Q1.
- **B2.3** BDa-Ⅴc-8. New: 減數分裂; n／2n; 減數分裂前亦複製 (3)
- **B2.4** BDa-Ⅴc-9. New: 受精卵有絲分裂; 細胞分化（簡介） (2)
- **B2.5 [PROJ]** 洋蔥根尖. Evidence: 115 Q28. (1)

### Later biology parts

**BIO-3 遺傳**

| Ch | Codes | New |
|---|---|---|
| B3.1 孟德爾實驗推理 | BGa-1, BMb-2 | 3 |
| B3.2 獨立分配（棋盤計數） | BGa-1 | 2 |
| B3.3 延伸 | BGa-2 | 3 |
| B3.4 染色體學說與性染色體 | BGa-3, BMb-3 | 3 |
| B3.5 性聯遺傳與系譜 | BGa-4 | 3 |
| B3.6 核酸 | BGa-5 | 3 |
| B3.7 中心法則 | BGa-6 | 4 |
| B3.8 表徵與環境 | BGa-7 | 2 |
| B3.9 基因轉殖 | BMc-1 | 2 |
| B3.10 [PROJ] DNA 粗萃取 | — | 1 |

- B3.6 is the canonical home of 核酸. Its detergent step is explained through membrane lipids (BB1.3), so it does not need chemistry.
- B3.10: no chicken blood, per the 課綱.

**BIO-4 演化**

| Ch | Codes | New |
|---|---|---|
| B4.1 | BGb-1 | 1 |
| B4.2 天擇 | BMb-4, BGb-2 | 4 |
| B4.3 | BGb-3 | 2 |
| B4.4 同源同功、親緣樹、三域、病毒 | BGb-4 | 4 |
| B4.5 多樣性 | BGb-5 | 2 |
| B4.6 [PROJ] 建親緣樹 | — | 1 |

**Biology totals:** 17 bridge chapters (47 concepts) + 29 core chapters (73 concepts) = **46 chapters**.

## 5. 地球科學

**Teaching order.** The 領綱 says its order is not a teaching order, and the 課程手冊 recommends an Earth-system frame. We start with space and scale (Ed-1, Fb, Id), as the research's suggested beginner sequence does.
- Ha-1 comes after Ed-1 (depends_on).
- Hb-2 needs isotopes (CAa-Vc-4, correction) and P1.5.
- EIc-Vc-1 comes before EIb-Vc-7 (correction).
- **Deviation:** EEd-Vc-2~4 is deferred to EAR-4. These chapters need the EM spectrum (PKc-Ⅴc-6), inverse-square (P1.4) and Kelvin (P5.3). Teaching those inline would break introduce-once.
- Md and Nb come last (depends_on: Ib, Ia-4, Fa-5, Ha-3, Hb-1).

### Bridge parts

**EAR-B1**

| Ch | Codes | New |
|---|---|---|
| EB1.1 | Ed-Ⅳ-1~2 | 3 |
| EB1.2 | Fb-Ⅳ-1~4 | 4 |
| EB1.3 四季 | Id-Ⅳ-1~3 | 3 |
| EB1.4 | Fa-Ⅳ-1~2 | 2 |
| EB1.5 | Fa-Ⅳ-3~5 | 3 |
| EB1.6 [PROJ] 日出方位 | — | 1 |

**EAR-B2**

| Ch | Codes | New |
|---|---|---|
| EB2.1 疊置截切 | Hb-Ⅳ-1~2 | 3 |
| EB2.2 | Ia-Ⅳ-1~4 | 4 |
| EB2.3 風向＝來向 | Ib-Ⅳ-1~4 | 4 |
| EB2.4 | Ib-Ⅳ-5~6 | 2 |
| EB2.5 | Ic-Ⅳ-1~4 | 3 |
| EB2.6 | Md-Ⅳ-2~5 | 3 |
| EB2.7 [PROJ] 地質剖面 | — | 1 |

EB2.1: cite the 附錄 說明, not the code text (correction).

### EAR-1 宇宙尺度與天空規律

- **E1.1** EEd-Vc-1. New: 天體階層; 恆星以下天體; 光行時間 (3)
- **E1.2** EEd-Vc-1. New: 星系退行→膨脹; 霹靂說 (2)
- **E1.3** EFb-Vc-1. New: 天球（無座標）; 周日運動; 緯度差異; 周年運動 (4)
- **E1.4** EId-Vc-1. New: 二分二至軌跡; 正午仰角變化 (2)
- **E1.5 [PROJ]** 三地星空模擬 (1)

### EAR-2 起源與固體地球

- **E2.1** EHa-Vc-1. New: 太陽星雲說; 小天體 (2)
- **E2.2** EHa-Vc-2. New: 距離與液態水; 大氣與磁層; 類地行星比較 (3)
- **E2.3** EHa-Vc-3, ← BB1.5, CB2.4. New: 早期大氣; 生命改變大氣; 大氧化事件 (3). Evidence: 113 Q50–53.
- **E2.4** EFa-Vc-1~2, ← PB2.1. New: P／S 波; 波速–深度圖; 軟流圈; 液態外核證據 (4)
- **E2.5** EHb-Vc-1. New: 指準化石對比; 地質年代表 (2)
- **E2.6** EHb-Vc-2, ← C1.6, P1.5. New: 半衰期; 母子元素; 依半衰期選定年 (3). Evidence: 115 Q54–56.
- **E2.7** EIa-Vc-1 (3)
- **E2.8** EIa-Vc-2~3 (3)
- **E2.9** EIa-Vc-4 (2)
- **E2.10 [PROJ]** 隕石定年選同位素 (1)

### Later earth-science parts

**EAR-3 大氣與海洋**

| Ch | Codes | New |
|---|---|---|
| E3.1 | EFa-3 | 2 |
| E3.2 | EFa-4~5 | 3 |
| E3.3 飽和濕度 | EIb-1~3 | 4 |
| E3.4 成雲 | EIb-4 | 3 |
| E3.5 三力與風 | EIb-5 | 5 |
| E3.6 天氣圖 | EIb-6 | 4 |
| E3.7 海流 | EIc-1 | 2 |
| E3.8 聖嬰 | EIb-7 | 2 |
| E3.9 波浪海岸 | EIc-2 | 3 |
| E3.10 潮汐 | EIc-3~4 | 3 |
| E3.11 [PROJ] 潮位作圖求潮差 | — | 1 |

**EAR-4 恆星**

| Ch | Codes | New |
|---|---|---|
| E4.1 星等 | EEd-2 | 4 |
| E4.2 多波段 | EEd-3 | 2 |
| E4.3 星色溫度 | EEd-4 | 1 |
| E4.4 [PROJ] | — | 1 |

E4.2 depends on P4.4; E4.3 depends on P5.3.

**EAR-5 災害資源氣候**

| Ch | Codes | New |
|---|---|---|
| E5.1 | EMd-1~2 | 3 |
| E5.2 | EMd-3 | 2 |
| E5.3 規模震度預警 | EMd-4 | 4 |
| E5.4 | ENa-1~3 | 3 |
| E5.5 | ENb-1~2 | 2 |
| E5.6 | ENb-3~4 | 3 |
| E5.7 [PROJ] 氣候資料圖 | — | 1 |

**Earth-science totals:** 13 bridge chapters (36 concepts) + 37 core chapters (96 concepts) = **50 chapters**.

## 6. Cross-subject prerequisites

### 6a. Math → science

No 必修 science chapter needs grade-11 math, vectors or trigonometric functions.

| Need | Math source | Science chapters |
|---|---|---|
| Read scientific notation, exponents | 國中 N-7-6~8 | S0.3, P1.2, EB1.1 |
| Ratio and proportion, inverse-square | N-6-6~8, N-7-9 | P1.4, P2.2, P5.3, C2.4, C3.2, B3.1, E4.1 |
| Linear equations | A-7-2~4 | C2.3, C3.8, E3.4 |
| Coordinates and graphs | G-7-1, F-8-1~2 | PB1.1–1.2, C3.3, E3.3, all plotting projects |
| Probability, tree diagrams, multiplication principle | D-9-2~3, R-6-4/N-6-9 | B3.1–3.3 (D-10-3/4 optional depth) |
| Repeated halving (1/2)ⁿ | N-7-6 + 國中 等比 (N-8-3~6) | E2.6 |
| Similar triangles | S-9-1~4 | P3.3 (diagram method) |
| **Scientific-notation arithmetic, significant figures** | **N-10-1** | **C2.2 mole, C3.4 Kw, P5.6 E=mc² / fission estimate (115 Q17–18), P6.1 E=hν, E1.1 light-travel time** |
| **Common logarithms** | **N-10-4** | **C3.5 pH, E5.3 規模** |
| Real exponents | N-10-3 | Optional depth only: non-integer half-lives in E2.6, the magnitude formula in E4.1 (open) |
| Best-fit line | D-10-2 | X.3; 112 Q2 distributions (optional) |
| Exponential models | F-11A-4 / F-11B-2 | Optional "and more" boxes only |

Answering "what math do the physics photon and energy items need": E=hν needs proportion plus N-10-1. E=mc² and the fission estimate need N-10-1 and order-of-magnitude estimation (N-10-5 toolbox). Kelvin and average kinetic energy need only proportion.

Two physics bridging open items close against the verified Math list: scientific notation (N-7-8) and proportion (N-7-9). The 國中 math code for exponential decay is still unresolved; F-11A-4 and F-11B-2 (grade 11) do cover decay models.

### 6b. Science → science edges

- P1.3 → C1.6
- C1.6 + P1.5 → E2.6
- P1.4, P4.4, P5.3 → EAR-4
- PB1.6, PB1.9, PB2.7 → E3.10 (tidal power)
- PB2.1 → E2.4
- PB1.3/1.5 → E3.5
- PB2.8 → CB2.5
- BB1.5, CB2.4 → E2.3
- BB3.3 → EB2.1
- E2.5 → B4.5
- BB1.3 + B3.6 → C4.2
- BB1.5, CB1.6, CB2.5 → P5.1
- E1.2 → P4.4 (backlink for light Doppler)
- SE.x → C4.6–4.7 and E5.4–5.6

### 6c. Canonical homes for shared concepts

| Concept | Home |
|---|---|
| 能量守恆 | S0.7 (P5.1 adds universality) |
| 氣體壓力 | PB1.8 |
| 質子／中子／電子 | P1.3 |
| 同位素 | C1.6 |
| α／β衰變 | P1.5 |
| 平方反比 | P1.4 |
| 電磁波譜 | P4.4 |
| 絕對溫度 | P5.3 |
| 醣蛋白脂 | BB1.3 |
| 核酸 | B3.6 |
| 碳循環 | BB3.4 |
| 化石 | BB3.3 |
| 地質年代表 | E2.5 |
| 溫室效應, 永續發展 | SE.3, SE.4 |
| 硬水軟化 | C1.3 |

Coordinate 永續, 氣候變遷 and 板塊 with the 地理 architect so they are not introduced twice.

## 6d. Recommended global order (Math interleaved)

1. 數學 bridges (國小→國中)
2. SCI-0
3. INQ-1
4. PHY-B1 → PHY-B2
5. **數學 N-10-1** (+N-10-2, A-10-1)
6. CHE-B1 → CHE-B2
7. BIO-B1 → BIO-B2 → BIO-B3
8. EAR-B1 → EAR-B2
9. SCI-E
10. PHY-1
11. CHE-1
12. EAR-1
13. BIO-1
14. PHY-2
15. CHE-2 (gate N-10-1 ✓)
16. BIO-2
17. **數學 N-10-3, N-10-4**
18. EAR-2 (C1.6 ✓, P1.5 ✓)
19. CHE-3 (N-10-4 ✓)
20. PHY-3
21. EAR-3
22. BIO-3
23. PHY-4
24. BIO-4 (E2.5 ✓)
25. PHY-5
26. EAR-4 (P1.4, P4.4, P5.3 ✓)
27. CHE-4 (B3.6 ✓)
28. PHY-6
29. EAR-5 (N-10-4 ✓)
30. 數學 D-10-2 (if not done yet) → X
31. INQ-2
32. Optional tracks

The round-robin keeps all four sciences on a spaced, interleaved rotation (pedagogy 3b/3c). The remaining 10th-grade math parts can float freely around this sequence.

## 7. 探究與實作

**Three layers:**
1. **INQ-1**, a dedicated part early in the order. It teaches the 4 strands and their 14 sub-items with a neutral context (paper planes).
2. **Recurring tasks.** Every part project is an inquiry task tagged with strand sub-items. Where possible it reuses a 課綱 demo or 探討活動:
   - physics: 力學能, 雙狹縫, 電磁感應;
   - chemistry: TLC, solubility curve, indicators, surfactants;
   - biology: slides, cell model, root tip, DNA extraction, peppered moth;
   - earth: wet/dry bulb thermometer, CWA tide/typhoon/earthquake data.

   Chapter-level TryIt/Predict prompts also carry strand tags.
3. **INQ-2 跨科探究整合**, a capstone placed after all cores. Each chapter follows a documented cross-subject 題組 pattern, using original items with links to the CEEC originals:

| Ch | Theme | Pattern | New |
|---|---|---|---|
| I2.1 | 潮汐發電 地×物 | 115 Q50–53 | 1 |
| I2.2 | 隕石定年 地×化×物 | 115 Q54–56 | 0 |
| I2.3 | 大氧化事件 地×化×生 | 113 Q50–53 | 0 |
| I2.4 | 都卜勒血流 物×生 | 111 Q49–54 | 1 |
| I2.5 | 光觸媒與能帶 物×化 | 114 Q50–54; CEEC suggests bridging band terms via energy levels | 1 |
| I2.6 | 捕蠅草實驗設計 物×生 | 113 Q40–43 | 0 |
| I2.7 | [PROJ] 自選議題完整探究 | — | 1 |

**Strand coverage across projects (each sub-item ≥2):**
- **發現問題:** PB2.10, CB2.8, BB1.6, BB3.6, EB1.6, P5.7, E5.7
- **規劃與研究:** S0.9, PB1.10, CB1.7, C1.10, C3.9, C4.8, BB2.5, B2.5, B3.10, E2.10
- **論證與建模:** P1.7, P2.7, P3.5, P4.6, P6.4, C2.6, B1.8, B4.6, EB2.7, E1.5, E3.11, E4.4, SE.5
- **表達與分享:** P1.7, P4.6, CB1.7, B3.10, BB3.6, E2.10, E5.7
- Every strand: I1.6 and I2.7

合作與討論 can only be simulated online: critique peer or sample answers. This is a known limitation.

## 8. Exam toolkit

Subject-specific TK chapters sit right after their prerequisites. Format skills for all of 自然 go in **X 題型實戰**, placed after the cores.

| Item | Where | Why beyond text | Evidence |
|---|---|---|---|
| 冷次定律推理 | P4.2 | 冷次 is absent from the whole 自然領綱 | 113 Q46(b), 115 Q53(a) 評分原則; 113 Q44–46 I–t sketch |
| 因次分析・符號式 | P5.2 | Elective 力學一 (PEa-Va-1 說明1-5) | 112 Q37–40 framing; Q40 penalised wrong dimensions and number substitution |
| 離子方程式 原子＋電荷守恆 | C3.8 | 說明 excludes redox balancing | 111 Q57-2 (Cr₂O₇²⁻/Fe²⁺/H⁺, all six coefficients); Q57-1 naming 氧化還原 |
| 衰變反應式 | P1.5 | Whether the 必修 text includes it is unverified | 112 Q52 |
| 再結晶 [EXT] | C1.3/C3.3 | 課綱: 必修不涉及 | 112, 114 options (翰林; secondary source) |
| Term previews [PRE] | B1.6, B1.7 | Mechanisms are elective | 115 Q29, 115 Q32 |
| X.1 卷面、計分、多選、連連看 (3) | X | Format | 116簡章 (n−2k)/n; 114 first 連連看 |
| X.2 無計算機估算・有效位數 (2) | X | Format | Calculators banned (簡章); 115 Q17–18 (Q18 P=21%) |
| X.3 作圖：描點、連線、由圖求量、示意圖 (3) | X | Format | 115 Q50 (about half got the tidal range right); 115 Q53; 113 Q46; 115 Q49; 114 curve drawing; 2B pencil |
| X.4 讀圖讀表 (2) | X | Format | 115 chemistry: more than half chart items; 112 chemistry 80%; 113 Q22–23 |
| X.5 限字說明・精確用語 (2) | X | Format | 115 Q54 (20 字); 115 Q38; 113 Q38; 112 Q57; 112 Q50; 113 Q41 |
| X.6 列式、過程、題給符號 (2) | X | Format | 115 Q53 "I<0" scored 0; 111 Q57 partial-credit rules; 111 Q38 all-or-nothing |
| X.7 跨科題組拆解 (1) | X | Format | One 地科 cross-subject 題組 every year, 112–115 |
| X.8 陌生情境・超綱名詞 (1) | X | Format | 114 Q50–54; 115 Q37–39 (gene regulation given as data) |
| X.9 [PROJ] 原創模擬題組 | X | — | — |
| 系譜／親緣樹 drills (in scope) | B3.5, B4.4, X.4 | — | 111 Q46–48, 112 Q50, 114 Q4, 115 Q31/36/39 |

X has 9 chapters with 16 concepts; INQ-2 has 7 chapters with 4.

## 9. Optional tracks (labelled 不考學測), placed after the core

Each track ships first as a 3–5-chapter preview part.

- **物理選修 (分科):**
  - 力學一: PEa-Ⅴa-1, PEb-Ⅴa-1~9, PKb-Ⅴa-1~4, PMb-Ⅴa-1~2, PMc-Ⅴa-1
  - 力學二與熱學 (← 力學一): PEb-Ⅴa-10~15, PBa-Ⅴa-1~5, PBb-Ⅴa-1~3
  - 波動、光及聲音 (← 力學一): PKa-Ⅴa-1~13, PMc-Ⅴa-1~2
  - 電磁一 (← 力學一, 力學二): PKc-Ⅴa-1~3, 7~15
  - 電磁二與量子 (← 電磁一, 力學二): PKc-Ⅴa-4~6, PKd-Ⅴa-1~8, PKe-Ⅴa-1~3
- **化學選修 (分科):** five courses using the research code sets: 物質與能量; 物質構造與反應速率; 化學反應與平衡一; 化學反應與平衡二; 有機化學與應用科技. CJb-Va-3 is listed in two courses, so it needs one home.
- **生物選修 (分科):** 細胞與遺傳; 生命起源與植物; 動物體; 生態演化多樣性. BMc-Ⅴa-1 is in two courses (needs one home); BMb-Ⅴa-8 is unmapped.
- **地科選修:** 地質與環境; 大氣、海洋及天文. Not on any 大考. The split of codes between the two courses is not in the research.
- The math needed for the tracks was not researched (open).

## 10. Coverage: every in-scope code → chapter

**物理 49/49**

| Codes | Chapter(s) |
|---|---|
| PMc-3 | P1.1 |
| PMc-4 | strand, anchored in P1.1 |
| PEa-1~3 | P1.2 |
| PKe-1 | P1.3 (+P1.4–1.6) |
| PKe-2~3, PKc-1~2 | P1.4–1.6 |
| PEb-1~2 | P2.1 |
| PEb-3 | P2.2 |
| PEb-4 | P2.3–2.4 |
| PEb-5 | P2.5 |
| PKb-1~2 | P2.6 |
| PKa-1~2 | P3.1 |
| PKa-3 | P3.2 |
| PKa-4 | P3.3 |
| PKa-5~6 | P3.4 |
| PKc-3 | P4.1 (+P4.2) |
| PKc-4~5 | P4.3 |
| PKc-6, PKa-7 | P4.4 |
| PMc-1~2 | P4.5 |
| PBa-1~2 | P5.1 |
| PBb-1~2 | P5.3 |
| PBb-3~4 | P5.4 |
| PNc-3~4 | P5.5 |
| PBa-3~4, PNc-1~2 | P5.6 |
| PKd-1~2 | P6.1 |
| PKd-3~4 | P6.2 |
| PKd-5~7 | P6.3 |

**化學 46/46**

| Codes | Chapter(s) |
|---|---|
| CAb-1, CEc-1 | C1.1 |
| CCa-1 | C1.2–1.3 |
| CAa-1, CJa-1 | C1.4 (CJa-1 also C2.1) |
| CMb-1 | woven, anchored in C1.4 and C4.5 |
| CAa-2 | C1.5 |
| CAa-3~4 | C1.6 |
| CAb-2 | C1.7 |
| CCb-1~2 | C1.8 |
| CAb-3, CCa-2 | C1.9 |
| CJa-3 | C2.2, C2.4 |
| CJa-2 | C2.3 (+C3.8) |
| CBa-1~2 | C2.5 |
| CJb-1 | C3.1 |
| CJb-3 | C3.2 |
| CJb-2, CJe-1 | C3.3 |
| CJd-1~2 | C3.4 |
| CJd-2~4 | C3.5 |
| CJc-1 | C3.6 |
| CJc-2 | C3.7 |
| CJe-2, CMc-3 | C4.1 |
| CJf-1 | C4.2 |
| CJf-2~3 | C4.3 |
| CMa-1, CMc-1~2 | C4.4 |
| CMb-2 | C4.5 |
| CMe-1~4 | C4.6 |
| CNa-1~4, CNc-1 | C4.7 |

**生物 26/26**

| Codes | Chapter(s) |
|---|---|
| BMb-1 | B1.1 |
| BDa-1 | B1.2 |
| BDa-2 | B1.3–1.5, B1.8 |
| BDa-3 | B1.6 |
| BDa-4 | B1.7 |
| BDa-5 | B2.1 |
| BDa-6~7 | B2.2 |
| BDa-8 | B2.3 |
| BDa-9 | B2.4 |
| BGa-1 | B3.1–3.2 |
| BMb-2 | B3.1 |
| BGa-2 | B3.3 |
| BGa-3, BMb-3 | B3.4 |
| BGa-4 | B3.5 |
| BGa-5 | B3.6 |
| BGa-6 | B3.7 |
| BGa-7 | B3.8 |
| BMc-1 | B3.9 |
| BGb-1 | B4.1 |
| BMb-4, BGb-2 | B4.2 |
| BGb-3 | B4.3 |
| BGb-4 | B4.4 |
| BGb-5 | B4.5 |

**地科 42/42**

| Codes | Chapter(s) |
|---|---|
| EEd-1 | E1.1–1.2 |
| EFb-1 | E1.3 |
| EId-1 | E1.4 |
| EHa-1 | E2.1 |
| EHa-2 | E2.2 |
| EHa-3 | E2.3 |
| EFa-1~2 | E2.4 |
| EHb-1 | E2.5 |
| EHb-2 | E2.6 |
| EIa-1 | E2.7 |
| EIa-2~3 | E2.8 |
| EIa-4 | E2.9 |
| EFa-3 | E3.1 |
| EFa-4~5 | E3.2 |
| EIb-1~3 | E3.3 |
| EIb-4 | E3.4 |
| EIb-5 | E3.5 |
| EIb-6 | E3.6 |
| EIc-1 | E3.7 |
| EIb-7 | E3.8 |
| EIc-2 | E3.9 |
| EIc-3~4 | E3.10 |
| EEd-2 | E4.1 |
| EEd-3 | E4.2 |
| EEd-4 | E4.3 |
| EMd-1~2 | E5.1 |
| EMd-3 | E5.2 |
| EMd-4 | E5.3 |
| ENa-1~3 | E5.4 |
| ENb-1~2 | E5.5 |
| ENb-3~4 | E5.6 |

**探究 14/14 sub-items** → I1.2–I1.5, plus the projects (§7).

**Totals**
- **163/163 in-scope codes placed; none unplaced.** Flags: PMc-4 and CMb-1 are woven strands; the per-code split inside physics unit 4 is open.
- About 199 bridging codes (國小/國中) are placed in the B parts.
- **Chapters:** PHY 56, CHE 48, BIO 46, EAR 50, shared 36 (SCI-0 9, INQ-1 6, SCI-E 5, X 9, INQ-2 7) = **236 chapters**.
- **New concepts:** core 355, bridges 190, shared 76 = 621 (all ≤5 per chapter, ≤2 per project).
- Planning risk: on 2026-11-15 the exam is 68 days away. Use pre-question diagnostics (pedagogy 3f) to let learners skip bridges.

## 11. Misconceptions → chapters

**物理**

| Misconception | Chapter(s) | Status |
|---|---|---|
| impetus (~80%; 2002 thesis, older 國中-focused data) | PB1.5, P2.3 | V |
| resting object always has friction (~40%); friction = maximum static friction (~70%) | PB1.4, P2.5 | V |
| a push must overcome weight | P2.5 | V |
| friction depends on area or speed | PB1.4 | D (ff0290 thesis) |
| action–reaction confusion; velocity vs acceleration | PB1.2, P2.4 | D (163192) |
| net force sets the direction of motion; FBD errors | P2.3, P2.5 | D |
| naming laws ≠ explaining (115 Q53) | P4.2 | C |
| leaving-coil curve drawn as a copy (113 Q46) | P4.2, P4.6 | C |
| refraction side, reflected amplitude (115 Q49) | P3.3, X.3 | C |
| "time" vs "time interval"; predictions written as events (113 Q43) | I1.3 | C |
| numbers substituted for symbols; wrong dimensions (112 Q40) | P5.2, X.6 | C |
| bare "α decay" answer (112 Q52) | P1.5 | C |

**化學**

| Misconception | Chapter(s) | Status |
|---|---|---|
| only 氧化反應 named (111 Q57) | C3.6, C3.8 | C |
| balancing errors (111 Q57-2) | C2.3, C3.8 | C |
| oxygen-only definition of redox carried over from 國中 | C3.6 | H (curriculum-derived; teach the upgrade, but no refutation framing yet) |
| strong = concentrated | C3.5 | H |
| atomic weight = grams of one atom | CB1.3, C2.2 | H |
| Kw is the same at any temperature | C3.4 | H |
| isotopes are different elements | C1.6 | H |
| NaCl is made of molecules | C1.9 | H |
| colloid = dilute solution | C3.1 | H |

**生物**

| Misconception | Chapter(s) | Status |
|---|---|---|
| 慢慢適應 (112 Q57) | B4.2 | C |
| teleological / Lamarckian evolution (thesis, 295 高一 students) | B4.2 | D |
| plants respire only at night | BB1.5, B1.7 | H (source PDF unreadable) |
| homologous vs analogous (113 Q41) | B4.4 | C |
| colour-blindness carrier errors (考試說明 sample 1) | B3.5 | C |
| incomplete pedigree reasoning (112 Q50) | B3.5 | C |
| tree branches filled with locations / wrong order (111 Q48) | B4.4 | C |
| flower ploidy (sample 3) | B2.3 | C |
| 女性 instead of 雌性 (115 Q38) | B3.8, X.5 | C |
| missing variable relationship (113 Q38) | I1.4, X.5 | C |
| meiosis without DNA replication | B2.3 | C, but a CEEC discussion prompt, not a measured error: use as a pre-question |
| genetics concepts "understood once memorised" (48-study review) | BIO-3 | D |

**地科**

| Misconception | Chapter(s) | Status |
|---|---|---|
| "skip 地科"; "探究 is a separate section"; "ignore 國中"; "地科 is on 分科" | S0.1, I1.1 (orientation FAQs) | C (簡章, 考試說明) |
| Andromeda is in the Milky Way; constellation stars at equal distance | E1.1 | C |
| wind direction = where it blows to; strongest wind at typhoon centre (state Northern Hemisphere) | EB2.3, E5.1 | C |
| weathering or uranium content shows age | E2.5–2.6 | C |
| C-14 can date meteorites | E2.6 | C (verify the exact half-life value; research gives "about 6,000 y") |
| S waves pass through the whole Earth | E2.4 | H |
| rising air cools by meeting cold air | E3.4 | H |
| tides caused mainly by the Sun | E3.10 | H |
| seasons caused by distance from the Sun | EB1.3 | H |
| recent warming is natural | E5.6 | H |
| 規模 = 震度 | E5.3 | H; CWA definitions also needed |

Every H item is sourced only to the 課綱's correct statement, not to student data.

## 12. Open items

1. Per-code splits inside multi-code groups: physics unit 4; Ka-Ⅳ-6~11; Jc-Ⅳ-1~7; Eb-Ⅳ-1~4; Ib-Ⅳ-1~6; Me/Na/Nb/INg; ENb-1~4.
2. Content questions the research does not answer:
   - Is 國中 等比數列 within N-8-3~6? (Exact code unknown.)
   - Does EEd-Vc-2 need the magnitude–brightness formula (log/exponent)?
   - Does the 圖示法 for Snell's law need sin (G-10-6)?
   - Does the 國中 bridge include F=ma, W=Fd, KE formulas? (Needed by P5.2.)
   - Does Aa-Ⅳ-1 already teach the nucleus? (Decides whether P1.3 teaches it new or as review.)
3. Exam facts not confirmed:
   - Does the 自然 paper print a periodic table or constants?
   - Is 112 Q52 decay-equation writing within the 必修 text?
   - Did the 111 Q57-2 stem give hints?
   - Which of 115 Q17/18 is the fission item?
   - Was 112 Q32 a blood-flow context?
   - Which code does 115 Q5 map to?
   - Is the 116 layout 36+6 (inferred, not fixed)?
4. 樂詞網 English terms for physics and biology were not re-checked.
5. Theses not re-opened: ff0290, 163192, and the teleology thesis.
6. Two NAER 領綱 URLs appear (…高級中等學校─…odt vs …高級中等校-…pdf). Verify that both resolve before adding them to the bibliography.
7. The PhET chemistry sim licence is unverified.
8. Math needs for the elective tracks were not researched.
9. Concept homes shared with 社會 (永續, 氣候, 板塊) need agreeing with the 地理 architect.

### Critical Files for Implementation
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\src\data\course.json (schema to mirror: parts, chapters, newConcepts, uses, prereqs, sources)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\curriculum.test.ts (no-jump tests to extend across subjects and code coverage)
- C:\Users\spp_l\AppData\Local\Temp\claude\3d48607dacc5350a\a673455e-fcf2-49cf-bfaa-b16e3c4f2485\tasks\woe8teuu0.output (codes, depends_on, corrections, exam evidence)
- C:\Users\spp_l\.claude\plans\lets-talk-together-on-fizzy-cherny.md (plan to merge this into)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\course.json (to be created: the global concept registry and science parts)