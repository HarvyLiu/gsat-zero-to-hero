<!-- Frozen design output (Social Studies + 國文 map), 2026-11-15. Superseded where docs/design/06-critique.md or the approved plan says so. -->

# Humanities curriculum architecture: 歷史, 地理, 公民與社會, 國文 (beta)

The verified research JSON is the source for everything below. Where research and verification disagree, verification wins. Items marked **(open)** were missing or unverified in the research and are collected in §8.

---

## 0. Decisions that apply to all four subjects

1. **One course file per subject**, each shaped like the reference `course.json` (parts → chapters with slug, title, blurb, objectives, newConcepts, uses, prereqs, activity, sources; parts carry whyHere).
   - Proposed files: `history`, `geography`, `civics`, `chinese`, plus a small `social-integration` course.
   - **Schema extension needed:** a chapter's `prereqs` may name another course's chapter as `"<course>:<slug>"`. The test then:
     - checks that the target exists;
     - checks that the combined graph of all courses has no cycles;
     - resolves `uses` through ancestors anywhere in that combined graph.
   - Concept names live in **one namespace for the whole site**, so each idea is introduced once across the site, not once per subject. Each shared skill gets one owning course and is used everywhere else:

     | Skill | Owner |
     |---|---|
     | Chart reading, ratio and map scale | 數學 bridges (D-3-1…D-9-x, S-6-2, N-6-x) |
     | 經緯度 | 地理 bridge |
     | Timelines | 歷史 bridge |
     | 國中自然 earth processes (Fa/Ia/Ib/Ic/Id-Ⅳ) | 地科 bridges |

2. **Every part after Part 0 ends with a project** (at most 2 new concepts). Projects in these subjects are:
   - 史料工作坊 (source workshops);
   - 歷史考察 E/J/O;
   - 田野實察 ×3;
   - 問題探究 (inquiry) chapters;
   - 法條工作坊 (statute-reading workshops);
   - writing tasks.
3. **Recurring skill strands** are built as components and tagged on exercises so the spaced-review queue can mix them:

   | Subject | Component(s) | Tag |
   |---|---|---|
   | 歷史 | `SourceCard` | H1–H9 |
   | 地理 | `MapRead` / `ChartRead` / `DrawIt` | G1–G9 |
   | 公民 | `LawRef` | C1–C7 |
   | 國文 | — | B1–B5 reading levels, A1–A6 knowledge |
   | all | — | S1–S5 cross-subject |

4. **Which CEEC guide to cite.** The 社會 考試說明 currently posted is the **108.11.08更新** file (`0J305554304528923536 …-1101.pdf`). In it, geography 例題2-3 changed: it now uses Argentina on log–log axes and requires a concave-up curve. The history and civics research cited the older 108年9月 file **(open: re-check history/civics 例題 numbers and codes against the current file)**.
5. **Refutation boxes only for documented misconceptions** (pedagogy finding 3g). A chapter with no sourced misconception gets no refutation box.
6. **Chapter size:** one chapter covers 1–2 學習內容 codes and stays under 35 minutes. Heavy or contested codes are split. Chapter counts are sized from the 課綱 建議節數 (歷史) and 附錄三 periods (地理).
7. **Placement test-out:** every bridge part opens with a placement quiz. Passing at the criterion marks those chapters "熟悉/Familiar" and lets the learner skip them; the prerequisite graph is unchanged.
8. **The new `social-integration` course** handles 合科 items, which were about 56% of items in 114 and about 40% of the score in 115. It comes after the three 社會 cores (prereqs: H12, G12, C12):
   - SI.1 拆解合科題組: which subject's concept is actually being tested (114 試題特色 notes history-looking items that test civics).
   - SI.2 One context, three lenses: an original analogue of 考試說明 例題2 (歷Mb-Ⅴ-3 / 公Df-Ⅴ-2 / 地Be-Ⅴ-1).
   - SI.3 Interleaved mixed set.
   - SI.4 Capstone: an original 110-minute mock section. Past papers are deep-linked by year and question number, never re-hosted.

---

## 1. 歷史

### 1.1 Shape: backbone first, themes second

The order is: Part 0 welcome → Part 1 toolkit → Parts 2–4 the three 國中 chronological backbones (臺灣, 中國與東亞, 世界) → Parts 5–11 the thematic core A→O in the official order → Part 12 exam practice → tracks.

All three backbones come before any theme because the Taiwan themes look forward into the other two (verified):
- Da needs 歷Ib-Ⅳ-1 (甲午), Qc-Ⅳ-2/3 and Lb-Ⅳ-1.
- Ib-Ⅴ-2 needs a communism primer (Qc-Ⅳ-1).
- Ia-Ⅴ-1 needs the Jesuit missions (Ob-Ⅳ-1).

Putting the backbones first also covers the three primers the verifier asked for. The core keeps the official A→O order, which matches publishers' 冊 1/2/3.

### 1.2 Chapter list

Column key: **M** = documented misconception; **←** = cross-course prereq. In P2, "(cand.)" marks concept labels taken from research context that must be checked against the 國中 說明 before course.json is frozen, because per-code 國中 titles were verified only at group level.

**P0 歡迎 / Welcome (1)**

| # | slug | 中文 / English | Codes | New concepts (≤5) | Notes |
|---|---|---|---|---|---|
| H0.1 | hist-welcome | 歷史怎麼學：骨幹先、主題後 / Backbone first, themes second | 社會領綱 structure; 116簡章 scope | 通史, 主題式課程, 分域, 學習內容代碼 | M: "senior history runs dynasty by dynasty"; M: "學測 includes 加深加廣" |

**P1 歷史的工具箱：時間與史料 / Toolkit: time and evidence (bridge, 6)**

| # | slug | 中文 / English | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| H1.1 | hist-timelines | 時間軸與紀年 / Timelines and eras | 國小 Cb-Ⅱ-1, Cb-Ⅲ-1; 歷A-Ⅳ-1 | 時序, 年代圖表, 公元紀年, 民國紀年, 世紀 | The 國小 說明 makes 民國/公元 dating optional, not required |
| H1.2 | hist-periodization | 分期也是一種觀點 / Periodization is a viewpoint | 歷A-Ⅳ-1 | 分期, 紀年系統的比較, 分期的區域與觀點差異 | |
| H1.3 | hist-sources | 史料：過去留下的線索 / Sources | 歷1b-Ⅳ-1, 1b-Ⅳ-2 (group) | 史料, 一手史料, 二手史料, 史料類型, 出處 | M: "closer to the event = more accurate" (例題12) |
| H1.4 | hist-fact-interp | 事實與解釋 / Fact vs interpretation | 歷1c-Ⅳ-1 | 歷史事實, 歷史解釋, 證據, 觀點 | M: "historians using sources must agree" (例題11) |
| H1.5 | hist-cause-change | 因果、變遷與延續 / Cause, change, continuity | 歷1c-Ⅳ-2 (group) | 因果關係, 變遷, 延續, 脈絡 | |
| H1.6 | hist-1-project | Project 史料偵探：替一張老照片寫說明卡 | uses H1.1–1.5 | 史料卡, 依證據定年 | Image from 國家文化記憶庫; licence checked per item |

**P2 臺灣的時間骨幹 / Taiwan backbone (國中, 10)**

| # | slug | 中文 / English | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| H2.1 | hist-tw-prehistory | 史前臺灣 / Prehistoric Taiwan | 歷Ba-Ⅳ-1; 國小 Cb-Ⅲ-2 | 考古發掘, 遺址, 史前文化, 文化資產 | |
| H2.2 | hist-tw-indig-origins | 原住民族的遷徙與傳說 | 歷Ba-Ⅳ-2 | 原住民族, 遷徙, 口傳傳說作為史料 | |
| H2.3 | hist-tw-maritime | 大航海時代的臺灣 | 歷Bb-Ⅳ-1, Bb-Ⅳ-2 | 大航海時代, 東亞海域, 海上多方勢力, 原住民族與外來者的接觸 | ← geo G1.1, G1.2 (map) |
| H2.4 | hist-tw-qing-rule | 清帝國時期（一）統治與經濟 | 歷Ca-Ⅳ-1, Ca-Ⅳ-2 | 清帝國（課綱用語）, 統治政策, 農業與商業 | |
| H2.5 | hist-tw-qing-society | 清帝國時期（二）社會 | 歷Cb-Ⅳ-1, Cb-Ⅳ-2; 國小 Cc-Ⅲ-2 | 漢人社會, 原住民族社會的變化, 族群遷徙與通婚 | |
| H2.6 | hist-tw-japan-1 | 日本帝國時期（一） | 歷Ea-Ⅳ-1~3 | 日本帝國時期／日治時期（two 課綱 terms）, 「理蕃」(cand.), 土地與林野調查 (cand., 115 Q30) | |
| H2.7 | hist-tw-japan-2 | 日本帝國時期（二） | 歷Eb-Ⅳ-1~3 | 近代學校教育 (cand.), 「國語」運動 (cand.), 皇民化 (cand.) | |
| H2.8 | hist-tw-postwar-1 | 當代臺灣（一） | 歷Fa-Ⅳ-1~4 | 戰後, 中華民國統治體制的移入, 二二八事件, 白色恐怖, 臺海兩岸與國際處境 | Contested-topic rules apply (§1.5) |
| H2.9 | hist-tw-postwar-2 | 當代臺灣（二） | 歷Fb-Ⅳ-1, Fb-Ⅳ-2; 國小 Cd-Ⅲ-1, Cd-Ⅲ-2 | 經濟發展, 大眾文化, 民主化 | |
| H2.10 | hist-2-project | Project 地方史小考察：我家附近的四個時代 | 歷D-Ⅳ-1, 歷G-Ⅳ-1 | 地方史, 歷史踏查 | Prepares learners for E/J/O |

**Later parts: titles and codes**

- **P3 中國與東亞的時間骨幹 (國中, 8):**
  - H3.1 商周至隋唐 (Ha-Ⅳ-1,2)
  - H3.2 宋元 (Hb-Ⅳ-1,2)
  - H3.3 明清的東亞 (Ia-Ⅳ-1,2)
  - H3.4 晚清東西接觸、明治維新與甲午戰爭 (Ib-Ⅳ-1,2)
  - H3.5 傳統社會文化的調適 (Ic-Ⅳ-1,2)
  - H3.6 現代國家的興起：中華民國建立、日本帝國擴張 (Ka-Ⅳ-1,2, Kb-Ⅳ-1,2)
  - H3.7 當代東亞：中共建國、冷戰東亞、東南亞國際組織 (La-Ⅳ-1,2, Lb-Ⅳ-1,2)
  - H3.8 Project: 東亞並排年表
- **P4 世界的時間骨幹 (國中, 8):**
  - H4.1 古代文化：非洲、西亞、希臘羅馬 (Na-Ⅳ-1,2)
  - H4.2 佛教、基督教、伊斯蘭教的起源 (Nb-Ⅳ-1~3)
  - H4.3 文藝復興、宗教改革、科學革命與啟蒙 (Oa-Ⅳ-1~3)
  - H4.4 哥倫布、耶穌會、蒙兀兒與東印度公司 (Ob-Ⅳ-1~3)
  - H4.5 美法革命、工業革命、民族主義 (Qa-Ⅳ-1~3)
  - H4.6 帝國擴張與一戰 (Qb-Ⅳ-1~3)
  - H4.7 戰間期、二戰、冷戰兩極 (Qc-Ⅳ-1~3). Owns the concepts 共產主義 and 極權, which Ib-Ⅴ-2 needs.
  - H4.8 Project: 世界史年表與地圖
- **P5 臺灣（一）族群、經濟與文化 (11):**
  - H5.1 A 如何認識過去？(歷A-Ⅴ-1)
  - H5.2 我群界定與原住民族分類 (Ba-Ⅴ-1). M: "原住民族 means only the legally recognized peoples."
  - H5.3 當代原住民族處境與權利伸張 (Ba-Ⅴ-2; the 說明 says to review 國中 policy coverage first)
  - H5.4 早期移民 (Bb-Ⅴ-1)
  - H5.5 戰後來臺移民、婚姻移民與移工 (Bb-Ⅴ-2)
  - H5.6 商貿 (Ca-Ⅴ-1)
  - H5.7 土地問題 (Ca-Ⅴ-2)
  - H5.8 原住民族語言信仰祭儀 (Cb-Ⅴ-1)
  - H5.9 多元信仰 (Cb-Ⅴ-2)
  - H5.10 文學與藝術 (Cb-Ⅴ-3)
  - H5.11 Project 史料工作坊：土地文書
- **P6 臺灣（二）現代國家的形塑 (8):**
  - H6.1 從地方到中央 (Da-Ⅴ-1)
  - H6.2 條約、宣言、決議、公報：文件本身 (Da-Ⅴ-2)
  - H6.3 對臺灣地位的不同解釋 (Da-Ⅴ-2)
  - H6.4 教育、語言與基礎建設 (Da-Ⅴ-3)
  - H6.5 日治人權與政治社會運動 (Db-Ⅴ-1)
  - H6.6 二二八、白色恐怖與轉型正義 (Db-Ⅴ-2; may split)
  - H6.7 戰後社會運動 (Db-Ⅴ-3)
  - H6.8 Project 歷史考察（一）(歷E-Ⅴ-1)
- **P7 中國與東亞（一）國家、社會與人群移動 (10):**
  - H7.1 F 在什麼脈絡中討論中國史？(F-Ⅴ-1)
  - H7.2 傳統政治權威 (Ga-Ⅴ-1)
  - H7.3 戶籍、土地、賦役 (Ga-Ⅴ-2). M: "scoring means memorizing names"; the 說明 says 不必繁言縷述制度.
  - H7.4 (Gb-Ⅴ-1)
  - H7.5 (Gb-Ⅴ-2)
  - H7.6 漢晉至宋元 (Ha-Ⅴ-1)
  - H7.7 明清 (Ha-Ⅴ-2)
  - H7.8 十九世紀以後 (Hb-Ⅴ-1)
  - H7.9 移動的影響 (Hb-Ⅴ-2)
  - H7.10 Project 史料工作坊：並列的紀錄如何暗示判斷 (H8; 資治通鑑 is public domain)
- **P8 中國與東亞（二）現代化 (7):**
  - H8.1 (Ia-Ⅴ-1)
  - H8.2 回應帝國主義 (Ia-Ⅴ-2). Includes the 衝擊—反應 vs China-centred viewpoints of 115 Q43–44.
  - H8.3 (Ia-Ⅴ-3)
  - H8.4 (Ib-Ⅴ-1)
  - H8.5 共產主義在東亞 (Ib-Ⅴ-2)
  - H8.6 區域合作 (Ib-Ⅴ-3)
  - H8.7 Project 歷史考察（二）(歷J-Ⅴ-1)
- **P9 世界（一）歐洲文化與現代世界 (8):**
  - H9.1 K (K-Ⅴ-1)
  - H9.2 神話與哲學 (La-Ⅴ-1; 例題11, H6)
  - H9.3 (La-Ⅴ-2)
  - H9.4 (La-Ⅴ-3)
  - H9.5 宗教改革到啟蒙 (Lb-Ⅴ-1; 例題7, H2)
  - H9.6 (Lb-Ⅴ-2)
  - H9.7 (Lb-Ⅴ-3)
  - H9.8 Project 史料工作坊：兩位史家兩種評價
- **P10 世界（二）文化的交會 (6):**
  - H10.1 (Ma-Ⅴ-1)
  - H10.2 (Ma-Ⅴ-2)
  - H10.3 (Mb-Ⅴ-1)
  - H10.4 (Mb-Ⅴ-2)
  - H10.5 (Mb-Ⅴ-3)
  - H10.6 Project 史料工作坊：殖民貿易商品
- **P11 世界（三）世界變遷與現代性 (6):**
  - H11.1 冷戰 (Na-Ⅴ-1; 例題12, H7)
  - H11.2 (Na-Ⅴ-2)
  - H11.3 (Nb-Ⅴ-1)
  - H11.4 「西方」與「反西方」 (Nb-Ⅴ-2)
  - H11.5 (Nb-Ⅴ-3)
  - H11.6 Project 歷史考察（三）(歷O-Ⅴ-1)
- **P12 學測實戰 (5):**
  - H12.1 非選：等級2/1/0與標準用語. M, as corrected by verification: neither "only the exact term scores" nor "any paraphrase scores" is right. 例題12-2 accepts only 冷戰 for full credit, but 例題14-1 and 9-2 accept equivalent terms.
  - H12.2 合科題組裡的歷史. M: "the history text is just background."
  - H12.3 圖表、地圖與圖像史料 (← math D bridges)
  - H12.4 Interleaved mixed review
  - H12.5 Capstone: original mock 題組
- **Tracks, after the core and labelled 分科測驗 only:** 族群、性別與國家的歷史; 科技、環境與藝術的歷史; 探究與實作：歷史學探究 **(open: their codes are not in the research)**.

**History total: 94 core chapters.** Of these, 32 are bridge (P1–P4) and 57 are core (P5–P11).

### 1.3 How 歷史考察 E/J/O become project chapters

Each 考察 is the last chapter of its 分域 (H6.8, H8.7, H11.6). Every one follows the same template, with at most 2 new concepts (研究問題, 研究成果的呈現):

1. Pick a topic from the 分域's themes (E from B/C/D, J from G/H/I, O from L/M/N). Three options are offered, taken from the 課綱 suggestions:
   - E: 臺灣的「歷史現場」, 不同性別的臺灣歷史人物, 跨國婚姻與移工.
   - J: conflicts between traditional states and societies; modern ethnic conflicts; how peace is possible.
   - O: 科技、環境與未來的世界, 西方為何興起？, 權力與體制如何影響我們？
2. Write a question.
3. Collect at least 3 sources, at least 1 of them primary, from open archives, each with a SourceCard. Licences are checked per item **(open: licences of 國史館 and 國家人權博物館)**.
4. Build a timeline or map. A virtual 歷史踏查 uses open-licensed photos and maps, with an optional real visit.
5. Write a 300–500字 answer that labels fact and interpretation.
6. Self-assess against a rubric keyed to H3/H6/H7/H8.

E/J/O are listed in 考試說明 表1 but have no content of their own; they are tested through skills (e.g., 115 Q38, the evidence value of first-hand sources). The template trains exactly those skills.

### 1.4 The 史料判讀 strand

- Every history chapter has at least one **SourceCard** with fixed fields:
  - who made it, when, why, and for whom;
  - its type (一手/二手; text, image, statistics, oral, object);
  - what it can and cannot show.
- Every source-based exercise carries an H-tag.
- Skill ladder across the parts: H6 (source vs fact vs interpretation) → H3 (reading in context) → H4 (explaining with sources) → H7 (fitness as evidence) → H8 (why interpretations differ) → H9 (public-issue reflection, in the projects).
- Dialogues follow the CEEC sample-item patterns, which are linked and paraphrased, never copied:

  | Pattern | 例題 | Objective |
  |---|---|---|
  | Change and continuity (1913 queue cutting) | 6 | H1 |
  | Two historians' opposite judgments of Alexander | 11 | H6 |
  | Memoir vs a later book | 12 | H7 |
  | Juxtaposed chronicle records | 13 | H8 |

  Each dialogue ends by naming the objective just practised.
- Every original practice source is a public-domain or open-licensed item with recorded provenance.

### 1.5 Editorial rules for contested topics

These apply to 歷Da-Ⅴ-2, Db-Ⅴ-2, Fa-Ⅳ, F-Ⅴ-1 and Nb-Ⅴ-2, and to civics Bd-Ⅴ-1, Dd-Ⅴ-2 and Bg-Ⅴ-2.

1. **Frame with the 課綱's own questions.** Open with the official framing question:
   - 歷A-Ⅴ-1: 誰的歷史？誰留下的史料？誰寫的歷史？
   - 歷F-Ⅴ-1: 可以在什麼樣的脈絡中討論中國史？ and how the meaning of 「中國」 changed.
   - 歷K-Ⅴ-1: 可以在什麼樣的脈絡中討論世界史？
   - 歷2c-Ⅴ-1: 審視重要的歷史爭議事件，理解歷史作為共同記憶的政治意涵.
   - 歷3b-Ⅴ-3: explain why interpretations differ.
   The goal is the skill, not a position.
2. **Use 課綱 wording by default:**
   - 清帝國 (not 滿清)
   - 日本帝國時期的臺灣 (國中) and 日治時期 (高中)
   - 中華民國統治體制的移入與轉變
   - 「理蕃」 and 「國語」運動, in quotation marks
   - 「西方」與「反西方」
   - 原住民族, including 平埔族群
   - 戰後

   Other terms from scholarship or public debate appear only as "其他用法" entries, with a citation, in the term registry (§6). The course never picks one silently.
3. **Type every claim.** In a contested chapter, every sentence is one of three kinds:
   - a documented fact, with a primary-source citation;
   - an attributed interpretation (named author or body, work, year, link), shown in a `Perspective` component;
   - the course's own question.

   Unattributed evaluative adjectives are not allowed.
4. **Show at least two perspectives with equal weight.** Each disputed point shows two or more cited perspectives in parallel cards of the same size, ordered by publication date (not by preference). Each card states what evidence it relies on.
5. **Primary text before interpretation (歷Da-Ⅴ-2).** The 課綱 names only document types (treaties from wars, declarations, resolutions, communiqués). Show the documents themselves, linked to official archive copies and quoted briefly, then the differing readings side by side. The course never asserts a single legal conclusion on 臺灣地位 or sovereignty. Civics Bd-Ⅴ-1 works the same way, using the Constitution and 增修條文 texts. **(open: reuse status of foreign-government documents; link plus short quote until resolved.)**
6. **The teacher character stays neutral.** When the student asks "so which is right?", the teacher goes back to evidence and to H6–H8 ("this is a difference of interpretation; let's see what each one rests on"). The teacher voices no opinion on current party politics.
7. **228, the White Terror and 轉型正義 (歷Db-Ⅴ-2).**
   - Use archival sources (e.g., 國史館 二二八事件檔案資料庫) and testimony with clear provenance.
   - Cover victims of different genders and ethnic groups, effects on families, and truth and reconciliation, as the 國中 說明 lists.
   - Add a content note and no gratuitous detail.
   - Disputed figures appear only as attributed values or ranges, one per source.
8. **Balance checklist for each part:** figures of different genders (the 說明 asks for this repeatedly), several ethnic viewpoints, no stereotypes, current scholarship.
9. **Live legal disputes are dated, not settled.** Example: 114年憲判字第1號 and the 憲法訴訟法 quorum amendment. Show the as-of date and source, and keep the claim "three justices consider it invalid" marked as secondary (CNA).
10. **Review gate.** A contested chapter ships only after a claim-type audit, a second reviewer, a 「爭議地圖」 box (what is disputed and where to read further), and a changelog entry.

### 1.6 Coverage: all 51 in_gsat history codes

| Codes | Chapters |
|---|---|
| A-Ⅴ-1 | H5.1 |
| Ba-Ⅴ-1, Ba-Ⅴ-2 | H5.2, H5.3 |
| Bb-Ⅴ-1, Bb-Ⅴ-2 | H5.4, H5.5 |
| Ca-Ⅴ-1, Ca-Ⅴ-2 | H5.6, H5.7 |
| Cb-Ⅴ-1~3 | H5.8–H5.10 |
| Da-Ⅴ-1 | H6.1 |
| Da-Ⅴ-2 | H6.2–H6.3 |
| Da-Ⅴ-3 | H6.4 |
| Db-Ⅴ-1~3 | H6.5–H6.7 |
| E-Ⅴ-1 | H6.8 |
| F-Ⅴ-1 | H7.1 |
| Ga-Ⅴ-1, Ga-Ⅴ-2 | H7.2, H7.3 |
| Gb-Ⅴ-1, Gb-Ⅴ-2 | H7.4, H7.5 |
| Ha-Ⅴ-1, Ha-Ⅴ-2 | H7.6, H7.7 |
| Hb-Ⅴ-1, Hb-Ⅴ-2 | H7.8, H7.9 |
| Ia-Ⅴ-1~3 | H8.1–H8.3 |
| Ib-Ⅴ-1~3 | H8.4–H8.6 |
| J-Ⅴ-1 | H8.7 |
| K-Ⅴ-1 | H9.1 |
| La-Ⅴ-1~3 | H9.2–H9.4 |
| Lb-Ⅴ-1~3 | H9.5–H9.7 |
| Ma-Ⅴ-1, Ma-Ⅴ-2 | H10.1, H10.2 |
| Mb-Ⅴ-1~3 | H10.3–H10.5 |
| Na-Ⅴ-1, Na-Ⅴ-2 | H11.1, H11.2 |
| Nb-Ⅴ-1~3 | H11.3–H11.5 |
| O-Ⅴ-1 | H11.6 |

All 51 codes are covered, and every `depends_on` points to an earlier chapter.

---

## 2. 地理

### 2.1 Shape

技能 → 系統 → 視野, with maps (Ac) taught before GIS (Ab), following the 龍騰/師大附中 sequence and the conceptual dependency.

- **田野實察** sits exactly where the 課綱 table puts it: after Bb, after Cb and after Ci.
- **Both either/or regions are core**, because CEEC says items 不偏版 and how either/or content is examined is unconfirmed:
  - Cc: 東南亞 (main case) and 南亞 (parallel case).
  - Ch: 中南美洲 and 漠南非洲.
- **國中 world-region primers** (地Ba–Bi-Ⅳ) are placed just in time, as the first chapter before each 視野 region.
- **國中自然 prerequisites** come from the 地科 bridges (cross-course). The 高中 地科 chapters are "see also" links only, because the two subjects run in parallel.

### 2.2 Chapter list

**P0 (1)**

| # | slug | Title | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| G0.1 | geo-welcome | 地理在學測 / Geography on the GSAT | 116簡章; 考試說明 (108.11.08) | 地理技能, 地理系統, 地理視野, 測驗目標 G1–G9 | M: "學測 includes the electives"; M: "it's pure reading comprehension" |

**P1 橋接：從地圖上找到臺灣 (國中, 8)**

| # | slug | Title | Codes | New concepts | ← |
|---|---|---|---|---|---|
| G1.1 | geo-latlong | 經緯度：地球上的地址 | 地Aa-Ⅳ-1 | 經線, 緯線, 經度, 緯度, 經緯度座標系統 | math G-7-1 |
| G1.2 | geo-land-sea | 海陸分布與臺灣的位置 | 地Aa-Ⅳ-2, Aa-Ⅳ-3 | 海陸分布, 大洲, 大洋, 臺灣的地理位置 | |
| G1.3 | geo-tw-landforms | 臺灣的地形、海岸與海域 | 地Ab-Ⅳ-1~3 | 地形分類, 海岸分類, 臺灣主要地形, 領海, 經濟海域 | 地科 bridge Ia-Ⅳ |
| G1.4 | geo-tw-climate | 天氣、氣候與臺灣的水 | 地Ac-Ⅳ-1~3 | 天氣, 氣候, 臺灣氣候特色, 水資源分布 | 地科 bridges Ib-Ⅳ, Id-Ⅳ |
| G1.5 | geo-tw-population | 臺灣的人口 | 地Ad-Ⅳ-1~3 | 人口成長, 人口分布, 人口組成, 多元族群 | |
| G1.6 | geo-tw-economy | 臺灣的產業與貿易 | 地Ae-Ⅳ-1~3 | 農業, 工業, 國際貿易 | |
| G1.7 | geo-tw-settlement | 聚落、交通與都市化 | 地Af-Ⅳ-1~3 | 聚落體系, 交通網絡, 都市化, 區域發展差異 | |
| G1.8 | geo-1-project | Project 我的縣市小檔案 (one map + two charts) | uses | 開放資料, 資料出處標示 | math D bridges |

**P2 地理技能 (10)**

| # | slug | Title | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| G2.1 | geo-traditions | 地理學的傳統與觀點 | Aa-Ⅴ-1 | 地理學的傳統, 地理觀點, 尺度 | Labels to confirm against the 說明 |
| G2.2 | geo-research-q | 研究問題與資料蒐集 | Aa-Ⅴ-2, Aa-Ⅴ-3 | 研究問題, 資料來源, 資料蒐集方法 | 111 Q20 (telephone-directory inquiry) |
| G2.3 | geo-data-display | 資料整理、分析與展示 | Aa-Ⅴ-4 | 資料整理, 資料分析, 資料展示 | ← math D-7-1/2 |
| G2.4 | geo-map-elements | 地圖的本質與要素 | Ac-Ⅴ-1 | 地圖的選擇與簡化, 地圖要素, 圖例 | ← math S-6-2 (比例尺 is owned by math) |
| G2.5 | geo-projections | 地圖投影的變形與合宜應用 | Ac-Ⅴ-1 (附錄三) | 地圖投影, 投影變形, 投影的合宜應用 | M: "projections are names to memorise" |
| G2.6 | geo-map-types | 地圖的種類與用途 | Ac-Ⅴ-2 | 普通地圖, 主題地圖, 分級符號地圖, 流線圖 | Labels to check in 樂詞網 高中以下地理學名詞 |
| G2.7 | geo-contours | 等高線、暈渲與數值地形 | Ac-Ⅴ-3 | 等高線, 等高距, 暈渲圖, 數值地形模型, 地形剖面 | 114 Q52 (44% correct), Q53; 115 Q54 |
| G2.8 | geo-gis-data | 地理資訊的組成與特性 | Ab-Ⅴ-1 | 地理資訊, 空間資料, 屬性資料 | Labels to confirm |
| G2.9 | geo-gis-functions | 地理資訊系統的功能 | Ab-Ⅴ-2 | 地理資訊系統, 疊圖分析 (cand.), 遙感探測, 航空照片 | M: "GIS = remote sensing" (例題3-1); 115 Q19 |
| G2.10 | geo-2-project | Project 問題探究：如何租好屋 | Ab-Ⅴ-3, Aa-Ⅴ-5 | 問題探究步驟 | |

**Later parts**

- **P3 系統（一）氣候與地形 (11):**
  - G3.1 氣候要素 (Ba-Ⅴ-1; climograph)
  - G3.2 大氣環流與洋流 (Ba-Ⅴ-2)
  - G3.3 氣候類型 (Ba-Ⅴ-3; 例題1-1)
  - G3.4 自然景觀帶 (Ba-Ⅴ-4)
  - G3.5 問題探究：氣候與水資源 (Ba-Ⅴ-5; 例題5-2, 例題20)
  - G3.6 地形營力 (Bb-Ⅴ-1)
  - G3.7 流水與冰河 (Bb-Ⅴ-2)
  - G3.8 風與波浪 (Bb-Ⅴ-2)
  - G3.9 地形辨識 (Bb-Ⅴ-3; 例題17)
  - G3.10 問題探究：地形與人類生活 (Bb-Ⅴ-4; 例題4-3, 22)
  - G3.11 Project **田野實察（一）**: a virtual study of one river basin
- **P4 系統（二）人口、聚落、都市 (8):**
  - G4.1 (Bc-Ⅴ-1)
  - G4.2 人口移動 (Bc-Ⅴ-2; 例題3-4, push–pull diagram)
  - G4.3 環境負載力 (Bc-Ⅴ-3; 115 Q63 line graph). Note the term mismatch: 課綱 環境負載力 vs 樂詞網 負載力.
  - G4.4 聚落與運輸 (Bd-Ⅴ-1, Bd-Ⅴ-2)
  - G4.5 中地體系與問題探究 (Bd-Ⅴ-3, Bd-Ⅴ-4)
  - G4.6 都市化與等級大小 (Be-Ⅴ-1). M, **corrected:** the Argentina log–log curve must be concave up (凹口向上). The research's older misconception text (Venezuela, concave-down) is superseded.
  - G4.7 地價、土地利用、內部結構 (Be-Ⅴ-2, Be-Ⅴ-3)
  - G4.8 Project 問題探究：都市機能與城鄉 (Be-Ⅴ-4; plot a rank-size curve)
- **P5 系統（三）產業與世界體系 (10):**
  - G5.1 Bridge: 農業與食品安全 (地Cb-Ⅳ-1,2)
  - G5.2 (Bf-Ⅴ-1)
  - G5.3 農業區位 (Bf-Ⅴ-2)
  - G5.4 工業／服務業區位與分工 (Bf-Ⅴ-2). M: "垂直分工, 垂直整合, 水平分工 and 水平整合 are interchangeable" (114 Q58).
  - G5.5 (Bf-Ⅴ-3)
  - G5.6 問題探究：產業變遷 (Bf-Ⅴ-4; 例題16 is coded Bf-Ⅴ-4)
  - G5.7–G5.9 (Bg-Ⅴ-1~3)
  - G5.10 Project 問題探究：區域發展的反思 (Bg-Ⅴ-4; flow map)
- **P6 視野（一）臺灣與東亞 (10):**
  - G6.1 Bridge: 臺灣地名文化 (地Ca-Ⅳ-1~3)
  - G6.2 (Ca-Ⅴ-1)
  - G6.3 原住民族與南島語族 (Ca-Ⅴ-2; 111 Q64 one-arrow rule)
  - G6.4 (Ca-Ⅴ-3)
  - G6.5 (Ca-Ⅴ-4)
  - G6.6 Bridge: 中國與東北亞概說 (地Ba-Ⅳ, Bb-Ⅳ, Bd-Ⅳ)
  - G6.7 (Cb-Ⅴ-1, Cb-Ⅴ-2)
  - G6.8 (Cb-Ⅴ-3)
  - G6.9 (Cb-Ⅴ-4)
  - G6.10 Project **田野實察（二）**: my township through place names and population data
- **P7 視野（二）東南亞與南亞 (8):**
  - G7.1 Bridge (地Be-Ⅳ-1~4)
  - G7.2–G7.4 東南亞 (Cc-Ⅴ-1~3; 例題18)
  - G7.5 問題探究1 東南亞國協 (Cc-Ⅴ-4)
  - G7.6 南亞個案：環境與文化景觀 (Cc-Ⅴ-1, Cc-Ⅴ-2)
  - G7.7 南亞個案：經濟 (Cc-Ⅴ-3)
  - G7.8 Project 問題探究2 南亞新興經濟體 (Cc-Ⅴ-4), comparing the two cases
- **P8 視野（三）澳紐與伊斯蘭世界 (7):**
  - G8.1 Bridge (地Bc-Ⅳ)
  - G8.2 (Cd-Ⅴ-1, Cd-Ⅴ-2)
  - G8.3 (Cd-Ⅴ-3, Cd-Ⅴ-4)
  - G8.4 Bridge (地Bf-Ⅳ)
  - G8.5 (Ce-Ⅴ-1, Ce-Ⅴ-2; 例題15)
  - G8.6 資源爭奪 (Ce-Ⅴ-3; 例題21 with the revised stem)
  - G8.7 Project 問題探究 (Ce-Ⅴ-4)
- **P9 視野（四）歐洲與美國 (8):**
  - G9.1 Bridge (地Bh-Ⅳ)
  - G9.2 (Cf-Ⅴ-1, Cf-Ⅴ-2)
  - G9.3 歐盟 (Cf-Ⅴ-3)
  - G9.4 (Cf-Ⅴ-4)
  - G9.5 Bridge 美洲 (地Bi-Ⅳ)
  - G9.6 (Cg-Ⅴ-1, Cg-Ⅴ-2)
  - G9.7 (Cg-Ⅴ-3)
  - G9.8 Project 問題探究 (Cg-Ⅴ-4)
- **P10 視野（五）南方區域 (7):**
  - G10.1 (Ch-Ⅴ-1)
  - G10.2 中南美洲 (Ch-Ⅴ-2, Ch-Ⅴ-3)
  - G10.3 中南美洲 (Ch-Ⅴ-4, Ch-Ⅴ-5). 例題2 may serve as an illustration only; it is not coded Ch.
  - G10.4 Bridge 漠南非洲 (地Bg-Ⅳ)
  - G10.5 漠南非洲 (Ch-Ⅴ-2, Ch-Ⅴ-3)
  - G10.6 漠南非洲 (Ch-Ⅴ-4, Ch-Ⅴ-5)
  - G10.7 Project: compare the two regions
- **P11 全球化 (4):**
  - G11.1 (Ci-Ⅴ-1, Ci-Ⅴ-2; 例題19)
  - G11.2 (Ci-Ⅴ-3, Ci-Ⅴ-4)
  - G11.3 問題探究 (Ci-Ⅴ-5)
  - G11.4 Project **田野實察（三）capstone**: global flows and my hometown
- **P12 學測實戰 (4):**
  - G12.1 作圖題 (legend symbol at the right size and position, graduated-symbol map with legend, line graph, exactly the number of arrows asked for). M: "a rough mark is enough"; M: "extra arrows are harmless."
  - G12.2 非選：概念詞＋因果 within 20–35字. M: "vague everyday wording is enough."
  - G12.3 合科中的地理. M: "geography only appears in the geography section."
  - G12.4 Capstone: original mock 題組
- **Tracks (分科 only):** 空間資訊科技, 社會環境議題, 探究與實作：地理與人文社會科學研究 **(open: codes)**.

**Geography total: 96 core chapters.**

Coverage of all 77 codes:

| Codes | Chapters |
|---|---|
| Aa-Ⅴ-1 / -2, -3 / -4 / -5 | G2.1 / G2.2 / G2.3 / G2.10 |
| Ac-Ⅴ-1 / -2 / -3 | G2.4–G2.5 / G2.6 / G2.7 |
| Ab-Ⅴ-1 / -2 / -3 | G2.8 / G2.9 / G2.10 |
| Ba-Ⅴ-1~5 | G3.1–G3.5 |
| Bb-Ⅴ-1~4 | G3.6–G3.10 |
| Bc-Ⅴ-1~3 | G4.1–G4.3 |
| Bd-Ⅴ-1~4 | G4.4–G4.5 |
| Be-Ⅴ-1~4 | G4.6–G4.8 |
| Bf-Ⅴ-1~4 | G5.2–G5.6 |
| Bg-Ⅴ-1~4 | G5.7–G5.10 |
| Ca-Ⅴ-1~4 | G6.2–G6.5 |
| Cb-Ⅴ-1~4 | G6.7–G6.9 |
| Cc-Ⅴ-1~4 | G7.2–G7.8 (both cases) |
| Cd-Ⅴ-1~4 | G8.2–G8.3 |
| Ce-Ⅴ-1~4 | G8.5–G8.7 |
| Cf-Ⅴ-1~4 | G9.2–G9.4 |
| Cg-Ⅴ-1~4 | G9.6–G9.8 |
| Ch-Ⅴ-1~5 | G10.1–G10.6 (both regions) |
| Ci-Ⅴ-1~5 | G11.1–G11.3 |
| 田野實察 ×3 | G3.11, G6.10, G11.4 |

### 2.3 Map and chart-reading strand

- **Every chapter has a `MapRead` or `ChartRead` block** with a fixed three-step routine from CEEC's 115 advice: read the map → infer (what causes this pattern, who is affected) → state a view.
- **Map-type ladder across the parts:**
  1. general map → thematic map (P1–P2);
  2. contour map, hillshade, DTM, landform photo, satellite image (P2–P3);
  3. climograph (P3);
  4. population pyramid, push–pull diagram, rank-size on log axes (P4);
  5. flow map / 線量圖 (P5, P11);
  6. place-name distribution map (P6);
  7. statistical charts throughout.
- **`DrawIt` tasks**, one or more per part:
  - legend symbol inside a contour ring (114 Q53);
  - graduated-symbol map with legend (112 Q62);
  - line graph (115 Q63);
  - rank-size curve (例題2-3, Argentina);
  - push–pull diagram (例題3-4);
  - a single arrow (111 Q64, where drawing two or more scored 0).
- **G1–G9 progression:** recognise concepts (G1–G2) → apply and read data (G3–G6) → judge issues and propose (G7–G9).

### 2.4 Virtual 田野實察 projects

Each follows the Aa-Ⅴ steps: question → data → analysis → presentation.

1. Choose one's own township, using 內政部 boundaries.
2. Pull open data: a CWA station for climate, data.gov.tw tables for population or land use.
3. Make a map with MapLibre or d3-geo and two charts with Observable Plot.
4. Write a 200字 conclusion with source attributions.
5. Optionally go outside, with safety notes.

Each project introduces at most 2 new concepts. The 課綱 leaves periods 依實際教學自行配置.

### 2.5 Open datasets by part

| Part | Dataset | Licence / notes |
|---|---|---|
| All | Natural Earth (world coastlines, countries, rivers, relief) | Public domain. **Owner decision:** de facto layers vs the Taiwan point-of-view file `ne_10m_admin_0_countries_twn` (v5.1.1); the site must say which it uses. |
| P1, P2, P6, field studies | 內政部國土測繪中心 鄉鎮市區界線 (data.gov.tw/dataset/7441), 直轄市、縣市界線 (7442) | 政府資料開放授權條款 v1. Attribution is mandatory: agency, year, dataset name and version, licence statement, https://data.gov.tw/license. |
| P1, P2 | 臺灣通用電子地圖 MBTiles (data.gov.tw/dataset/33384) | Open-data licence; WMTS terms unverified |
| P3, field studies | 中央氣象署 氣象觀測站逐時資料 (data.gov.tw/dataset/9176) | Bulk download needs membership on opendata.cwa.gov.tw; attribution; no logos |
| P5, civics P9 | 主計總處 statistics (data.gov.tw/dataset/10928) | Open-data licence |
| P2–P3 | Elevation data for contours and hillshade; satellite imagery | **(open)** no verified source |
| P1, P4, P6 | Taiwan population, land use, place names | **(open)** specific datasets not identified |
| P4, P7–P11 | World city sizes, region statistics, trade flows | **(open)** no verified source |
| Rendering | MapLibre GL JS (BSD-3; keep `localIdeographFontFamily` local), d3-geo for static SVG, Observable Plot | — |

### 2.6 Seasons misconception

The correct idea is verified (自然 Id-Ⅳ-3: the seasons come mainly from axial tilt), but how common the wrong belief is among Taiwanese students is not documented. Under rule 0.5 it gets no refutation box. The 地科 bridge teaches the correct idea, and geography only uses it.

---

## 3. 公民與社會

### 3.1 Order of the 32 項目 (all `depends_on` checked)

1. A: Aa → Ab → Ac → Ad
2. Society: Bb → Bc
3. State and government: Be → Bd (both before law, because Bf-Ⅴ depends on Be-Ⅴ)
4. Law: Bf → Bg → Bh → Bi → Bk → Bj
5. Governance and participation: Ca → Cb → Cc
6. Economics: Bl → Bm → Bn → Bo → Ce → Cf → Cg → Bq (micro, then macro)
7. Labour: Cd (needs Bj-Ⅴ-1, Bg and Ce; Ce/Cf/Cg come before Cd, as verification corrected)
8. D: Da → Db → Dc → Dd → De → Df (Df needs Bn, Bo, Ce and Dd)

The verified final_units list places Bq directly after Bo. Both placements satisfy the dependencies; Bq comes after Cg here so supply and demand flow straight into the market mechanism.

**Bridges are placed just in time.** The 國中-only Ba (個人、家庭與部落) is needed by Bb-Ⅴ-1 and Bj-Ⅴ-4. The 國中-only Bp (貨幣的功能) is needed by Bq and trade.

### 3.2 Chapter list

**P0 (1)**

| # | slug | Title | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| C0.1 | civ-welcome | 公民在學測 | 116簡章; 考試說明 | 條目問題, 延伸探究, 測驗目標 C1–C7 | M: "延伸探究 is tested knowledge" |

**P1 橋接：公民的起點 (9)**

| # | slug | Title | Codes | New concepts |
|---|---|---|---|---|
| C1.1 | civ-citizen | 公民與公民德性 | 公Aa-Ⅳ-1, Aa-Ⅳ-2 | 公民, 公民德性 |
| C1.2 | civ-power-rights | 權力與權利 | 公Ab-Ⅳ-1, Ab-Ⅳ-2 | 權力, 權利, 校園中的權利 |
| C1.3 | civ-human-rights | 人權與人性尊嚴 | 公Ad-Ⅳ-1, Ad-Ⅳ-2 | 人權, 人性尊嚴, 人權的普世性 |
| C1.4 | civ-constitution-basics | 憲法、法律與政府入門 | 國小 Ac-Ⅲ-1~4 | 憲法, 法律, 立法機關, 中央與地方政府, 國家權力 |
| C1.5 | civ-rule-of-law | 法治與法律位階 | 公Bf-Ⅳ-1, Bf-Ⅳ-2, Bg-Ⅳ-1 | 法治, 人治, 命令, 法律位階, 憲法作為權利保障書 |
| C1.6 | civ-kinship | 個人、家庭與部落（一）（國中限定） | 公Ba-Ⅳ-1~3 (split to confirm) | 親屬關係, 親子間的權利義務, 部落 |
| C1.7 | civ-family | 個人、家庭與部落（二） | 公Ba-Ⅳ-4, Ba-Ⅳ-5 | 家庭型態, 公權力與家庭, 家庭中的平等 |
| C1.8 | civ-norms-bridge | 社會規範與法律 | 公Bc-Ⅳ-1~3 | 社會規範, 法律與其他規範的差異, 規範的變遷 |
| C1.9 | civ-1-project | Project 一條校規的體檢 | uses | 規範分析表 |

**P2 公民身分與認同 (11)**

| # | slug | Title | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| C2.1 | civ-citizenship-hist | 公民身分的演變 | Aa-Ⅴ-1 | 公民身分的擴張, 普遍的公民身分 | |
| C2.2 | civ-tw-civic-rights | 臺灣公民權的發展與實踐 | Aa-Ⅴ-2 | 公民權利的發展, 公民權利的實踐 | ← hist H6.1 |
| C2.3 | civ-capacity-bridge | 行為能力與法定代理人 | 公Bj-Ⅳ-2; 民法§12, §13 | 成年, 行為能力, 限制行為能力, 無行為能力, 法定代理人 | Time-sensitive register (TS-1) |
| C2.4 | civ-legal-personality | 權利能力：自然人與法人 | Ab-Ⅴ-1 | 權利能力, 自然人, 法人 | |
| C2.5 | civ-indig-capacity | 部落與原住民族的權利能力 | Ab-Ⅴ-2 | 部落的權利能力, 原住民族的權利能力 | ← hist H5.3 |
| C2.6 | civ-duty-accountability | 法律義務與權責相符 | Ab-Ⅴ-3, Ab-Ⅴ-4 | 法律義務, 法律責任, 權責相符, 學生自治 | |
| C2.7 | civ-state-govt-bridge | 國家與政府的區別 | 公Bd-Ⅳ-1 | 國家, 政府 | |
| C2.8 | civ-sovereignty-identity | 主權、公民身分與國族認同 | Ac-Ⅴ-1, Ac-Ⅴ-2 | 國家主權, 國族認同 | |
| C2.9 | civ-multi-identity | 多元認同與國家政策 | Ac-Ⅴ-3 (例題3) | 多元認同, 認同政策 | |
| C2.10 | civ-hr-covenants | 國際人權公約與國內法化 | Ad-Ⅴ-1, Ad-Ⅴ-2 | 國際人權公約, 聯合國人權機制, 非政府組織, 施行法 | |
| C2.11 | civ-2-project | Project 公約條文 → 施行法 → 生活案例 | uses (law.moj texts) | — | |

**Later parts**

- **P3 社會生活與國家 (9):**
  - C3.1 Bridge: 團體與結社 (公Bb-Ⅳ-1/2; these appear in depends_on but not in final_bridging_prereqs, so confirm)
  - C3.2 (Bb-Ⅴ-1)
  - C3.3 (Bc-Ⅴ-1). M: "a change in law immediately changes behaviour" (surname custom, 例題23).
  - C3.4 (Bc-Ⅴ-2)
  - C3.5 Bridge: 權力分立與政府組成 (公Be-Ⅳ-1~3)
  - C3.6 憲法如何界定國家主權及其爭議 (Bd-Ⅴ-1; contested-topic rules apply)
  - C3.7 民主政府體制比較 (Be-Ⅴ-1; 增修條文 facts, TS-9)
  - C3.8 中央與地方 (Be-Ⅴ-2)
  - C3.9 Project: 體制比較卡
- **P4 法律（一）體系、憲法與行政 (9):**
  - C4.1 (Bf-Ⅴ-1)
  - C4.2 (Bf-Ⅴ-2)
  - C4.3 基本權與限制、比例原則 (Bg-Ⅴ-1; 112 Q66)
  - C4.4 憲法規範公權力、憲法法庭 (Bg-Ⅴ-2). M: "constitutional questions are still answered by 釋字." Uses TS-12.
  - C4.5 Bridge (公Bh-Ⅳ-1/2)
  - C4.6 (Bh-Ⅴ-1)
  - C4.7 正當程序 (Bh-Ⅴ-2; 例題29)
  - C4.8 行政救濟 (Bh-Ⅴ-3; 114 Q34)
  - C4.9 Project 法條工作坊: an original red-line parking scenario (115 Q26–27 style)
- **P5 法律（二）刑事與少年 (8):**
  - C5.1 Bridge (公Bi-Ⅳ-1~3)
  - C5.2 (Bi-Ⅴ-1)
  - C5.3 罪刑法定 (Bi-Ⅴ-2; 刑法§1, 例題25). M: "a court can punish an immoral act no law forbids."
  - C5.4 (Bi-Ⅴ-3)
  - C5.5 (Bi-Ⅴ-4)
  - C5.6 Bridge (公Bk-Ⅳ-1)
  - C5.7 (Bk-Ⅴ-1). M: "minors are never punished" (刑法§18).
  - C5.8 Project: one original case followed through the criminal process
- **P6 法律（三）民事 (6):**
  - C6.1 Bridge (公Bj-Ⅳ-1, 3, 4, 5; 國小 Ad-Ⅲ-1)
  - C6.2 契約自由的限制 (Bj-Ⅴ-1)
  - C6.3 所有權 (Bj-Ⅴ-2; ← hist H5.7)
  - C6.4 (Bj-Ⅴ-3)
  - C6.5 繼承 (Bj-Ⅴ-4; ← C1.6, ← math fractions bridge). M: "siblings can no longer inherit." Uses TS-11.
  - C6.6 Project: an original inheritance calculation with fractions
- **P7 民主治理與參與 (9):**
  - C7.1 Bridge (公Ca-Ⅳ-1~3, Cb-Ⅳ-1/2)
  - C7.2 Bridge (公Cc-Ⅳ-1~3)
  - C7.3 (Ca-Ⅴ-1; 112 Q44)
  - C7.4 課責 (Ca-Ⅴ-2)
  - C7.5 (Cb-Ⅴ-1; 例題27, 115 Q3)
  - C7.6 (Cb-Ⅴ-2; 例題26, 112 Q60, 114 Q46)
  - C7.7 選舉 (Cc-Ⅴ-1). M: "18 is the age of majority, so 18-year-olds can vote." Uses TS-3/4.
  - C7.8 公投等參與管道 (Cc-Ⅴ-2; 例題24). Three M's: referendum vs constitutional-amendment thresholds; "referendums are held on a fixed date"; "an online poll equals a referendum." Uses TS-5–8.
  - C7.9 Project: an original referendum timeline worked through against the statute text
- **P8 經濟（一）(12):**
  - C8.1 Bridge: 選擇與機會成本 (公Bl-Ⅳ-1~3; 國小 Da-Ⅱ-1, Db-Ⅱ-1). Required, not optional: 113 Q49 tested 機會成本 directly.
  - C8.2 Bridge (公Bl-Ⅳ-4, Bl-Ⅳ-5)
  - C8.3 Bridge (公Bm-Ⅳ-1/2, Bn-Ⅳ-1~4)
  - C8.4 Bridge 貨幣的功能（國中限定） (公Bp-Ⅳ-1~4)
  - C8.5 (Bl-Ⅴ-1)
  - C8.6 (Bm-Ⅴ-1, Bm-Ⅴ-2; 例題5)
  - C8.7 (Bn-Ⅴ-1, Bn-Ⅴ-2; 例題4, 115 Q6)
  - C8.8 需求曲線 (Bo-Ⅴ-1, Bo-Ⅴ-2; ← math G-7-1, F-8-1/2)
  - C8.9 需求 vs 需求量 (Bo-Ⅴ-3). M: "a price rise shifts the demand curve left."
  - C8.10 (Bo-Ⅴ-4, Bo-Ⅴ-5)
  - C8.11 (Bo-Ⅴ-6)
  - C8.12 Project: build a supply-and-demand schedule and plot it
- **P9 經濟（二）市場、外部成本、所得、勞動 (10):**
  - C9.1 (Ce-Ⅴ-1)
  - C9.2 (Ce-Ⅴ-2, Ce-Ⅴ-3; 114 Q31)
  - C9.3 價格管制 (Ce-Ⅴ-4). The minimum wage appears here only as a price-floor example; labour-market effects are 分科-only (公Fb-Ⅴ-3). M: "price controls always help." Uses TS-13.
  - C9.4 Bridge (公Cf-Ⅳ-1~3)
  - C9.5 (Cf-Ⅴ-1, Cf-Ⅴ-2)
  - C9.6 (Cg-Ⅴ-1, Cg-Ⅴ-2)
  - C9.7 國民所得與 GDP (Bq-Ⅴ-1~3; 主計總處 data; ← math percent bridge)
  - C9.8 Bridge (公Cd-Ⅳ-1~3)
  - C9.9 勞動權益與最低工資法 (Cd-Ⅴ-1, Cd-Ⅴ-2). M: "基本工資 is still the legal term." Uses TS-13/14.
  - C9.10 Project: read an economy from 主計總處 tables
- **P10 理想（一）(8):**
  - C10.1 Bridge (公Da-Ⅳ, Db-Ⅳ, Dc-Ⅳ)
  - C10.2 (Da-Ⅴ-1)
  - C10.3 (Da-Ⅴ-2; ← hist H6.6)
  - C10.4 (Da-Ⅴ-3)
  - C10.5 (Db-Ⅴ-1; 114 Q62)
  - C10.6 (Db-Ⅴ-2; 115 Q1)
  - C10.7 (Dc-Ⅴ-1, Dc-Ⅴ-2; 114 Q1)
  - C10.8 Project: weigh one social-security scheme on fairness, responsibility and efficiency
- **P11 理想（二）(9):**
  - C11.1 Bridge (公Dd-Ⅳ, De-Ⅳ; 國小 Ae-Ⅲ-3)
  - C11.2 (Dd-Ⅴ-1)
  - C11.3 臺灣與兩岸 (Dd-Ⅴ-2; 例題28; contested-topic rules apply)
  - C11.4 (Dd-Ⅴ-3)
  - C11.5 (De-Ⅴ-1)
  - C11.6 AI 與倫理法律 (De-Ⅴ-2; 114 Q43–46)
  - C11.7 (Df-Ⅴ-1, Df-Ⅴ-2; 例題2)
  - C11.8 WTO (Df-Ⅴ-3)
  - C11.9 Project: original cross-subject trade analysis
- **P12 學測實戰 (5):**
  - C12.1 非選 (3-point 等級 rubric: concept, then justification)
  - C12.2 法條情境題
  - C12.3 圖表題
  - C12.4 合科. M: "a history or geography context means it isn't a civics question."
  - C12.5 Capstone
- **Tracks (分科 only):**
  - 現代社會與經濟 (公Ea-Ⅴ-1~4, Eb-Ⅴ-1~3, Fa-Ⅴ-1~4, Fb-Ⅴ-1~4, Fc-Ⅴ-1~4, Fd-Ⅴ-1~3, Fe-Ⅴ-1~3)
  - 民主政治與法律 (公Ga-Ⅴ-1~2, Gb-Ⅴ-1~2, Gc-Ⅴ-1~3, Ha-Ⅴ-1~2, Hb-Ⅴ-1~3, Hc-Ⅴ-1~2, Hd-Ⅴ-1~2)
  - 探究與實作：公共議題與社會探究 (no codes)

  Write these in current legal terms (最低工資, 憲法法庭判決), not the outdated 領綱 wording in Fb-Ⅴ-3 and Ha-Ⅴ-1.

**Civics total: 106 core chapters.**

Coverage of all 78 codes in the 32 項目:

| Codes | Chapters |
|---|---|
| Aa-Ⅴ-1~2 | C2.1–C2.2 |
| Ab-Ⅴ-1~4 | C2.4–C2.6 |
| Ac-Ⅴ-1~3 | C2.8–C2.9 |
| Ad-Ⅴ-1~2 | C2.10 |
| Bb-Ⅴ-1 | C3.2 |
| Bc-Ⅴ-1~2 | C3.3–C3.4 |
| Bd-Ⅴ-1 | C3.6 |
| Be-Ⅴ-1~2 | C3.7–C3.8 |
| Bf-Ⅴ-1~2 | C4.1–C4.2 |
| Bg-Ⅴ-1~2 | C4.3–C4.4 |
| Bh-Ⅴ-1~3 | C4.6–C4.8 |
| Bi-Ⅴ-1~4 | C5.2–C5.5 |
| Bk-Ⅴ-1 | C5.7 |
| Bj-Ⅴ-1~4 | C6.2–C6.5 |
| Ca-Ⅴ-1~2 | C7.3–C7.4 |
| Cb-Ⅴ-1~2 | C7.5–C7.6 |
| Cc-Ⅴ-1~2 | C7.7–C7.8 |
| Bl-Ⅴ-1 | C8.5 |
| Bm-Ⅴ-1~2 | C8.6 |
| Bn-Ⅴ-1~2 | C8.7 |
| Bo-Ⅴ-1~6 | C8.8–C8.11 |
| Ce-Ⅴ-1~4 | C9.1–C9.3 |
| Cf-Ⅴ-1~2 | C9.5 |
| Cg-Ⅴ-1~2 | C9.6 |
| Bq-Ⅴ-1~3 | C9.7 |
| Cd-Ⅴ-1~2 | C9.9 |
| Da-Ⅴ-1~3 | C10.2–C10.4 |
| Db-Ⅴ-1~2 | C10.5–C10.6 |
| Dc-Ⅴ-1~2 | C10.7 |
| Dd-Ⅴ-1~3 | C11.2–C11.4 |
| De-Ⅴ-1~2 | C11.5–C11.6 |
| Df-Ⅴ-1~3 | C11.7–C11.8 |

### 3.3 Time-sensitive facts register (`time-sensitive.json`)

Laws were checked on 全國法規資料庫 with data cutoff 115-11-06. Every entry carries: fact, value on exam day (2027-01-22..24), legal basis, official URL, checked-on date, status, and what triggers a re-check.

| ID | Fact | Value on exam day | Basis / source | Status, re-check trigger |
|---|---|---|---|---|
| TS-1 | Age of majority | 18 (in force 112-01-01) | 民法§12; §13 (under 7 無行為能力; minors 7+ 限制) — law.moj B0000001 | verified |
| TS-2 | Constitutional amendment procedure | 1/4 propose, 3/4 attend, 3/4 agree, half-year notice, then referendum with yes > half of eligible voters | 增修條文§12 (A0000002) | verified |
| TS-3 | Voting / candidacy age | 選舉權 20; 被選舉權 23; 4 months' residence | 憲法§130; 選罷法§14, §15(1) | verified. **(open)** contents of 選罷法 amendments 112-06-09, 114-02-18, 115-01-21 and 115-07-01 (the last changed only §26) |
| TS-4 | 2022 修憲複決 to lower the voting age | Failed: about 564.7萬 yes vs 501.6萬 no; about 962萬 yes needed | 報導者 (secondary) | **(open)** 中選會 primary page; exact threshold unverified |
| TS-5 | Referendum age | 18, not under guardianship | 公投法§7 (D0020050) | verified |
| TS-6 | Referendum date rule | Vote 3–6 months after the case is announced as established, on the same day as any national election in that window; referendum day is a holiday | 公投法§23 (114-12-03) | verified. Older materials that give a fixed date are outdated. |
| TS-7 | Referendum pass threshold | yes > no and yes ≥ 1/4 of eligible voters | 公投法§29 | verified |
| TS-8 | 罪刑法定; criminal responsibility by age | Under 14 不罰; 14 to under 18 得減輕; 80 and over 得減輕 | 刑法§1, §18 (C0000001) | verified |
| TS-9 | Government structure | §2: emergency decree ratified within 10 days; §3; §4: 113 seats (73+6+34), 5% threshold, at least half of each party list women; §5: 15 大法官, 8-year non-renewable terms; §7: 29 監察委員 | 增修條文 (94-06-10) | verified |
| TS-10 | Minimum Wage Act | Enacted 112-12-27; §4 rates, §9 CPI basis, §10 Q3 meeting, §18 maps 基本工資 references to 最低工資 | laws.mol.gov.tw FL102659 | verified. **(open)** effective date (113-01-01 not confirmed) |
| TS-11 | 特留分 | **Pre-amendment §1223 applies on exam day.** The amendment (promulgated 115-08-17, in force 6 months later) removes siblings; 配偶, 直系血親卑親屬 and 父母 keep 1/2 of 應繼分, 祖父母 1/3; 應繼分 articles unchanged | law.moj B0000001 §1223 and 沿革 | verified. **(open)** exact in-force date (about mid-Feb 2027); re-check before the 117 sitting |
| TS-12 | 憲法訴訟法 and 114年憲判字第1號 | Full text 108-01-04, in force 3 years later; amended 112-06-21 and 114-01-23 (§§4, 30, 95; 10/9 quorum). Judgment of 2025-12-19 declared the 2025 amendment unconstitutional; **validity disputed** | law.moj A0030159; cons.judicial.gov.tw press release | Primary for dates; the dispute is secondary (CNA). Present as live. |
| TS-13 | Minimum wage | 2026: NT$29,500/month, NT$196/hour. **From 2027-01-01, before the exam: NT$30,900, NT$205** | 勞動部 2026-09-24; announced 2026-10-16 (CNA) | **(open)** explicit 行政院 approval not seen |
| TS-14 | Terminology | 最低工資 replaces 基本工資; 憲法法庭判決 replaces 釋字 | as above | verified |
| TS-15 | Exam logistics | 社會 116-01-24, 12:50–14:40; 國綜 1/23 12:50–14:20; 國寫 15:20–16:50 | 116簡章 | verified |

Test idea: every chapter that cites a TS fact must reference its register ID. The build lists entries whose re-check trigger date has passed.

### 3.4 How lessons cite statutes (`LawRef`)

- **Format.**
  - zh: 「民法§12」 (law, article, and paragraph or subparagraph where needed).
  - en: the official law.moj ENG name and article, e.g. "Civil Code Art. 12（民法第12條）".
- **Link** to the article page `https://law.moj.gov.tw/LawClass/LawSingle.aspx?pcode=…&flno=…`, or to the 沿革 page when the change history matters.
- **Quote the article text verbatim** in a callout. Statutes and agency translations are not copyrightable (著作權法§9). EN pages show the law.moj ENG translation next to the Chinese text.
- **Every `LawRef` carries `asOf`** (the check date) and the 修正日期; time-sensitive ones also link to their TS-ID.
- **Keep three kinds of material visibly separate:**
  - 法條 (statute text);
  - 憲法法庭判決 (case number, date, link);
  - 學說 or commentary (named author and source).
- **延伸探究 material** sits in a box labelled 「情境素材，非測驗知識」 (per the 考試說明).
- **Scenario items** are original. CEEC items are deep-linked, not reproduced. A "not legal advice" note goes in the footer.

---

## 4. 國文 (beta)

### 4.1 Shape

Bridges (注音 → 部首/部件 → 標點/句型 → 造字原則 → 國中文言) → skill strands → the 15篇, each placed after the genre or text-type unit it exemplifies (this follows the verified depends_on) → 國綜 混合題 → 國寫.

- **文言 exposure grows gradually:** short excerpts in P3 and P5, full texts from P8 on. This mirrors the official ramp: 國中 10–20% rising to 25–35%, 高中 35–45%.
- **Short writing drills** (摘要, 改寫) run from P2 on, so writing practice is spaced out before the 國寫 parts.

### 4.2 Chapter list

**P0 (1)**

| # | slug | Title | Codes | New concepts | Notes |
|---|---|---|---|---|---|
| Z0.1 | zh-welcome | 國綜與國寫 (90 minutes each; 國文 = 國綜×0.5 + 國寫) | 116簡章; 國文考試說明 | 國綜, 國寫, 混合題, 級分 | M: "國綜 only tests the 課文"; M: "the 國學常識 elective is tested" |

**P1 橋接：字的聲音與形狀 (7)**

| # | slug | Title | Codes | New concepts |
|---|---|---|---|---|
| Z1.1 | zh-zhuyin | 注音符號 | Aa-I-1~4 (group; per-code split to confirm) | 注音符號, 聲母, 韻母, 拼讀 |
| Z1.2 | zh-tones | 聲調 | Aa-I-x | 聲調, 四聲, 輕聲 (cand.) |
| Z1.3 | zh-radicals | 部首與部件 | Ab-Ⅱ-3, Ab-Ⅲ-3 | 部首, 部件, 表音功能, 表義功能 |
| Z1.4 | zh-polyphony | 多音字與多義字 | Ab-Ⅱ-4, Ab-Ⅲ-4 | 多音字, 多義字, 語境 |
| Z1.5 | zh-four-principles | 象形、指事、會意、形聲 | Ab-Ⅳ-3 | 象形, 指事, 會意, 形聲 |
| Z1.6 | zh-dictionaries | 查字辭典（教育部《重編國語辭典修訂本》） | Ab-Ⅱ-10, Ab-Ⅲ-7, Ab-Ⅳ-1, Ab-Ⅳ-2 (group) | 部首檢字, 注音檢字, 數位辭典, 常用字 |
| Z1.7 | zh-1-project | Project 一字卡 (sound, form, meaning, components) | uses | 字卡 |

**P2 橋接：詞、句、標點與篇章 (8)**

| # | slug | Title | Codes | New concepts |
|---|---|---|---|---|
| Z2.1 | zh-word-classes | 詞類 | Ab-Ⅱ-8, Ab-Ⅲ-8 | 詞類, 名詞, 動詞, 形容詞, 副詞 |
| Z2.2 | zh-word-formation | 構詞與量詞 | Ab-Ⅱ-7, Ab-Ⅱ-9 | 構詞, 量詞, 量詞的搭配 |
| Z2.3 | zh-punctuation | 標點符號的用法與效果 | Ac-Ⅱ-1, Ac-Ⅲ-1, Ac-Ⅳ-1 | 標點符號, 標點的用法, 標點的效果 **(open: authoritative rule source)** |
| Z2.4 | zh-sentence-types | 基本句型 | Ac-Ⅱ-2, Ac-Ⅱ-3, Ac-Ⅲ-2, Ac-Ⅳ-2 | 敘事句, 有無句, 判斷句, 表態句 |
| Z2.5 | zh-complex-sentences | 複句與文句邏輯 | Ac-Ⅲ-3, Ac-Ⅳ-3 | 複句, 關聯詞, 語意邏輯關係 |
| Z2.6 | zh-text-structure | 意義段、結構、主旨 | Ad-Ⅱ-1, Ad-Ⅲ-1, Ad-Ⅲ-2, Ad-Ⅳ-1 | 意義段, 篇章結構, 主旨, 寓意 |
| Z2.7 | zh-reading-strategies | 摘要、推論、自我提問 | 5-Ⅲ-6, 5-Ⅲ-8, 5-Ⅳ-2, 5-Ⅳ-4 | 摘要, 推論, 自我提問 |
| Z2.8 | zh-2-project | Project 結構圖＋50字摘要 | uses | — |

**Later parts**

- **P3 橋接：走進文言與文類 (8):**
  - Z3.1 (Ab-Ⅳ-6)
  - Z3.2 虛字與古今義變入門 (Ab-Ⅳ-7). The 課綱 publishes no 虛字 list, so the course's core list is sourced character by character from MOE dictionary entries.
  - Z3.3 古典詩文入門 (Ad-Ⅲ-4, Ad-Ⅳ-3, Ad-Ⅳ-4)
  - Z3.4 (Ad-Ⅳ-2)
  - Z3.5 五種文本 (Ba–Be-Ⅳ, Bd-Ⅲ-2)
  - Z3.6 書法入門 (Ab-Ⅳ-8)
  - Z3.7 寫作歷程 (6-Ⅱ-3, 6-Ⅳ-2)
  - Z3.8 Project: a short public-domain 文言 passage plus our own 白話 rewrite
- **P4 字音字形字義與語詞, A1–A2 (6):**
  - Z4.1 六書 (Ab-Ⅴ-1, 4-Ⅴ-1)
  - Z4.2 錯別字 (例題1; 115 Q2)
  - Z4.3 字音 (例題2; 115 Q1)
  - Z4.4 字義依語境 (例題3)
  - Z4.5 語詞與成語 (A2; Ab-Ⅳ-4/5; 例題4)
  - Z4.6 Project: hunt the miswritten characters in one's own writing, checked against the dictionary
- **P5 文言詞句與語法, A3 (7):**
  - Z5.1 (Ab-Ⅴ-2)
  - Z5.2 虛字 (Ab-Ⅴ-3)
  - Z5.3 古今義變與一字多義 (Ab-Ⅴ-3; 115 Q25 type)
  - Z5.4 詞性活用
  - Z5.5 句型與被動句
  - Z5.6 語意邏輯與量詞 (例題5; 115 Q14–15)
  - Z5.7 Project: a table of one character's meanings across texts
- **P6 文句、篇章、表現手法 (5):**
  - Z6.1 (Ac-Ⅴ-1)
  - Z6.2 (Ad-Ⅴ-1, 5-Ⅴ-1)
  - Z6.3 表現手法（一）常見修辭 (A4; taught through examples, not just terms, per 例題6) **(open: no 修辭格 code found)**
  - Z6.4 寫作手法與文學美感 (Ba-Ⅴ-3)
  - Z6.5 Project 文意重組 (115 Q5 type, using a public-domain passage)
- **P7 文類 (6):**
  - Z7.1 (Ad-Ⅴ-2)
  - Z7.2 韻文：辭賦、古體、樂府、近體 (Ad-Ⅴ-3)
  - Z7.3 詞、散曲、戲曲 (Ad-Ⅴ-3)
  - Z7.4 非韻文 (Ad-Ⅴ-4; 例題7, 9)
  - Z7.5 書法鑑賞 (Ab-Ⅴ-4; in_gsat = partial)
  - Z7.6 Project: genre map
- **P8 選文（一）(8):**
  - Z8.1 燭之武退秦師 (附錄四 項次1)
  - Z8.2 桃花源記 (6)
  - Z8.3 虯髯客傳 (8; both 虯 and 虬 were accepted in 114 grading)
  - Z8.4 赤壁賦 (9; after Z7.2 辭賦)
  - Z8.5 晚遊六橋待月記 (10)
  - Z8.6 勞山道士 (12)
  - Z8.7 畫菊自序 (15)
  - Z8.8 Project: compare one character's meaning across texts (115 Q25 type)
- **P9 文本表述 (6):**
  - Z9.1 記敘 (Ba-Ⅴ-1, Ba-Ⅴ-2)
  - Z9.2 抒情 (Bb-Ⅴ-1~4)
  - Z9.3 說明與圖表 (Bc-Ⅴ-1~3; 例題14)
  - Z9.4 議論 (Bd-Ⅴ-1, Bd-Ⅴ-2)
  - Z9.5 應用 (Be-Ⅴ-1~3; 例題13)
  - Z9.6 Project: open one topic in all five text types
- **P10 選文（二）(7):**
  - Z10.1 諫逐客書 (3)
  - Z10.2 鴻門宴 (4)
  - Z10.3 出師表 (5). 「表」 is classed as 奏議, under Ad-Ⅴ-4 and not Be-Ⅴ-2, per the correction.
  - Z10.4 師說 (7)
  - Z10.5 勸和論 (13)
  - Z10.6 鹿港乘桴記 (14)
  - Z10.7 Project: take apart three argumentative texts
- **P11 文化內涵與文學常識 (9):**
  - Z11.1 (Ca-Ⅴ-1~3)
  - Z11.2 (Cb-Ⅴ-1~4)
  - Z11.3 (Cc-Ⅴ-1, Cc-Ⅴ-2)
  - Z11.4 先秦諸子與文化經典 (A6; 例題12)
  - Z11.5 中華文化基本教材導讀 (篇目 vary by textbook; beta caveat)
  - Z11.6 作家、作品、體類、流派 (A5; 例題8, 10, 11). M: "國學常識 is tested."
  - Z11.7 大同與小康 (2)
  - Z11.8 項脊軒志 (11)
  - Z11.9 Project: a review map of all 15 texts (era × genre × text type)
- **P12 國綜實戰 (5):**
  - Z12.1 閱讀層次 B1–B5
  - Z12.2 多文本對讀 (5-Ⅴ-2, 5-Ⅴ-3)
  - Z12.3 圖表文本 (Bc-Ⅴ-3)
  - Z12.4 混合題作答: convergent answers, every required dimension, key terms written correctly. M: "混合題 answers are mini 國寫 essays." Example error: 113 杏人核/河馬迴.
  - Z12.5 Capstone: original 混合題 set with scoring notes
- **P13 國寫：知性 (6):**
  - Z13.1 審題 (examples: 114 擬社會互動 miswritten as 擬社會運動; 115 the ethical 「臉」)
  - Z13.2 文字與圖表統整
  - Z13.3 約80字短答. M: "copying the passage is fine."
  - Z13.4 約400字論述 (Bd-Ⅴ, 6-Ⅴ-3)
  - Z13.5 三等六級評分原則
  - Z13.6 Project: write a 知性 answer and self-assess
- **P14 國寫：情意 (5):**
  - Z14.1 依序回應提問 (115 pattern)
  - Z14.2 具體經驗 (6-Ⅴ-2)
  - Z14.3 間接抒情 (Bb-Ⅴ-4)
  - Z14.4 分段與完篇 (6-Ⅴ-4, 6-Ⅴ-5). M: "an unfinished essay can still score A" (capped at B+).
  - Z14.5 Project: write a 情意 essay and self-assess on the 25-point scale
- **Track (beyond 學測; 分科 has no 國文):** the 加深加廣 courses 語文表達與傳播應用, 各類文學選讀, 專題閱讀與研究, 國學常識, plus 學習表現 categories 1 and 2 (listening and speaking, not tested on paper).

**國文 total: 94 core chapters.**

Coverage. Stage Ⅴ 學習內容 has 33 codes by count from final_units **(open: confirm the count against the ODT)**:

| Codes | Chapters |
|---|---|
| Ab-Ⅴ-1~4 | Z4.1, Z5.1, Z5.2–Z5.3, Z7.5 |
| Ac-Ⅴ-1 | Z6.1 |
| Ad-Ⅴ-1~4 | Z6.2, Z7.1, Z7.2–Z7.3, Z7.4 |
| Ba-Ⅴ-1~3 | Z9.1, Z6.4 |
| Bb-Ⅴ-1~4 | Z9.2 |
| Bc-Ⅴ-1~3 | Z9.3 |
| Bd-Ⅴ-1~2 | Z9.4 |
| Be-Ⅴ-1~3 | Z9.5 |
| Ca-Ⅴ-1~3 | Z11.1 |
| Cb-Ⅴ-1~4 | Z11.2 |
| Cc-Ⅴ-1~2 | Z11.3–Z11.4 |

| CEEC objectives | Chapters |
|---|---|
| A1 | Z4.2–Z4.4 |
| A2 | Z4.5 |
| A3 | Z5.4–Z5.6 |
| A4 | Z6.3–Z6.4 |
| A5 | Z11.6 |
| A6 | Z11.3–Z11.4 |
| B1–B5 | P12 |

The 15篇 are in P8, P10 and P11. 國寫 知性 and 情意 are P13 and P14.

### 4.3 Presenting the 15篇 legally

1. **原文.** All 15 authors died long ago, far past the 著作權法§30 term of life plus 50 years. Publish **our own transcription and punctuation**, checked against a cited base edition, and record the base text in provenance. If a 維基文庫 transcription is reused verbatim, that block is marked CC BY-SA 4.0 with attribution and share-alike. ctext.org and 異體字字典 are link-only.
2. **語譯 and English translation:** always the course's own, labelled 「本站自譯 / course translation」. Never copy textbook 語譯 or 注釋, which may carry their own protection.
3. **注釋.** Our own notes, plus quoted entries from MOE 《重編國語辭典修訂本》 (CC BY-ND 3.0 TW). Dictionary entries are shown verbatim in a separate box, with no edits and no 簡化字 conversion, and attributed with: 教育部, dictionary name, version, URL.
4. **Reader layout.** An aligned reader with tabs or columns 原文 | 注釋 | 語譯 (EN pages add an English gloss). Toggleable `<ruby>` 注音 for rare characters and 破音字, using `ruby-position: over`, not inter-character.
5. **Modern 白話文** inside lessons and practice: summaries, analysis and short necessary quotes only (§52 with the §65 factors, cite per §64), plus links to legitimate full texts. Check the author's death year before quoting.
6. **Past papers.** Deep-link CEEC by year, subject and question number. Passages inside exam items stay protected when used separately (TIPO 93年 ruling), so do not re-host.
7. **國綜 混合題 and 國寫 rubrics.** Link the CEEC 評分原則 and 選才電子報 articles and paraphrase them; non-profit use with attribution, no large-scale copying. State the band numbers as facts (e.g., 25-point scale: A+ 25–22 … C 5–1). Write **original model answers at several levels**, labelled original and annotated against the rubric dimensions. Never reproduce CEEC sample essays.

### 4.4 How the English version works

- An EN page is **English explanation wrapped around Chinese text that is never translated away.** 原文, exam-style items and answer options stay in 正體中文. The English translation is a secondary layer.
- The zh term appears beside the English at first use. Chinese runs inside EN pages are wrapped in `lang="zh-TW"` so fonts, screen readers and Pagefind treat them correctly.
- Dialogues are in English and quote the Chinese.
- Learners always answer in Chinese, because 簡章附錄三 requires 正體中文 except for 專有名詞. 國寫 prompts stay in Chinese, with the 審題 explanation and rubric commentary in English and the 等級 labels quoted in Chinese.
- English names for 國綜/國寫/課綱 terms are **course-proposed**: only GSAT, AST and CEEC are verified. They are flagged in the UI (§6).

---

## 5. Cross-subject prerequisites and links

**Hard prerequisites** (cross-course `prereqs`):

| From | To | Codes |
|---|---|---|
| 數學 bridges | 地理 G1.1, G1.8, G2.3, G2.4 | G-7-1 coordinate plane; D-3-1…D-6-2 and D-7-1/2 charts and averages; group 「比、比值、百分率、速度、比例尺」 (N-5-10, N-6-6~8, S-6-1, S-6-2); S-9-1 similar figures |
| 數學 bridges | 公民 C6.5, C8.8, C9.7, C12.3 | fractions bridge (N-3-9…N-6-3) for 特留分; percent bridge; G-7-1 and F-8-1/F-8-2 linear graphs for supply and demand; statistics bridges. These replace civics' "unverified" math codes with codes verified in the math research. |
| 數學 | 地理 G4.6 (log axis) | Proposal: geography teaches 「對數刻度（每格×10）」 on top of math bridge N-7-6~8 (exponents, scientific notation), with math N-10-4 常用對數 as see-also. **Lead decision:** if the math N-10-4 chapter introduces log axes, geography should depend on that chapter instead. |
| 數學 bridges | 歷史 H12.3 | D bridges |
| 地科 bridges | 地理 G1.3, G1.4, P3 | 自然 Fa-Ⅳ-1~4, Ia-Ⅳ-1~4, Ib-Ⅳ-1~6, Ic-Ⅳ-1~4, Id-Ⅳ-1~3 (owned by the 地科 course) |
| 地理 G1.1–G1.2 | 歷史 H2.3 | 地Aa-Ⅳ-1/2 (in the history research's bridge list) |
| 歷史 | 公民 | none required |

**See-also links** (parallel grade 10–11 content, so not hard prerequisites):

- **地科 ↔ 地理:**
  - EIb-Vc-5 (wind forces) and EIc-Vc-1 (surface currents) ↔ G3.2
  - EIb-Vc-7 (El Niño) ↔ G3.2–G3.3
  - EIa-Vc-2/3/4 (plates) ↔ G3.6, G6.2
  - EIc-Vc-2 (waves and coasts) ↔ G3.8
  - EMd-Vc (typhoons, earthquakes) ↔ G6.2
  - ENb-Vc (climate change) ↔ G3.5, P11
  - 探究與實作 strands ↔ Aa-Ⅴ methods
- **Concept ownership the lead must decide:** wave and coastal landforms, atmospheric circulation and currents are taught by both 地科 and 地理.
- **歷史 ↔ 地理:**
  - 歷Ba-Ⅴ ↔ 地Ca-Ⅴ-2
  - 歷Bb-Ⅴ ↔ 地Ca-Ⅴ-3
  - 歷Hb-Ⅴ ↔ 地Bc-Ⅴ-2 (push–pull)
  - 歷Ib-Ⅴ-3 (ASEAN, APEC) ↔ 地Cc-Ⅴ-4(1)
  - 歷La/Lb ↔ 地Cf-Ⅴ-2/4
  - 歷Ma ↔ 地Ce
  - 歷Mb-Ⅴ-2/3 ↔ 地Ch-Ⅴ-3/4 (colonial economy)
  - 歷Nb-Ⅴ-3 ↔ 地Ci
- **歷史 ↔ 公民:**
  - 歷Da-Ⅴ-1 ↔ 公Aa-Ⅴ-2, Be-Ⅴ
  - 歷Da-Ⅴ-2 ↔ 公Bd-Ⅴ-1, Dd-Ⅴ-2 (same editorial rules)
  - 歷Db-Ⅴ-2 ↔ 公Da-Ⅴ-2 (轉型正義; mapping 115 Q32–33 to Da is an inference)
  - 歷Db-Ⅴ-3 ↔ 公Cc-Ⅴ-2
  - 歷Ba-Ⅴ-2 (姓名權, 例題14-3) ↔ 公Ab-Ⅴ-2
  - 歷Lb-Ⅴ-2 ↔ 公Ce
  - 歷Lb-Ⅴ-3 ↔ 公Ca, De-Ⅴ-1
  - 歷Ca-Ⅴ-2 ↔ 公Bj-Ⅴ-2 (114 Q54–56 used 交易成本 and 所有權) **(open: 交易成本 has no 必修 civics code in final_units)**
  - 114 Q62 Tang relief ↔ 公Db-Ⅴ-1
- **地理 ↔ 公民:**
  - 地Bf (分工) ↔ 公Bn-Ⅴ
  - 地Bg, Ci ↔ 公Dd, Df
  - 地Bc-Ⅴ-3 and Cd-Ⅴ-4 ↔ 公Cg, Dd-Ⅴ-3
  - 地Ce-Ⅴ-3 ↔ 公Ce (115 Q64–65 oil supply)
  - 例題2 spans all three subjects and is used in SI.2
- **國文 ↔ others:**
  - 國文 Bc-Ⅴ-3 and 國寫 知性 charts ↔ math D
  - 國文 Cc-Ⅴ-1 諸子 ↔ 歷Ga-Ⅴ-1
  - 臺灣古典散文 ↔ 歷 B/C, see-also only

---

## 6. Terminology without 樂詞網 term sets (歷史, 公民, 國文)

**Principle.** The zh term is the one that matters, because the exam is in Chinese, and its authority is the 課綱 wording, plus the 考試說明 for exam terms and the statute text for law. The English term is a learning aid with recorded provenance.

**English sources, in priority order:**

- **歷史:**
  1. Proper names as published by the responsible Taiwan agency (原民會 English site for the 16 peoples and the Pingpu Peoples; 國家人權博物館 English for White Terror terms). Use these only as evidence of the name; do not copy text, since site licences are unverified.
  2. 樂詞網 academic sets that contain the term, recording the set name and flagging that it is not a 高中以下 set (the research found 冷戰 and 文藝復興 in 行政學名詞, 教育大辭書 and 視覺藝術名詞).
  3. A cited scholarly reference work **(open: choose one)**.
  4. Course-proposed rendering.

  English Wikipedia can corroborate common usage but is never the sole source. The research leaned on it for 228 and "History of Taiwan" headings, so those entries need replacement or flagging.
- **公民:**
  1. law.moj ENG official translations of statute names and terms (not copyrightable under §9).
  2. 樂詞網 法律學名詞, 經濟學名詞 and 社會學名詞 sets.
  3. Agency English pages (主計總處 for GDP/GNI, 勞動部 for minimum wage, 憲法法庭 for judgments) — unverified.
  4. Course-proposed. About 30 civics renderings are currently unverified (e.g., 比例原則, 特留分, 應繼分, 媒體近用).
- **國文:**
  - zh: 課綱, 考試說明, and MOE 重編國語辭典修訂本 for definitions (verbatim, CC BY-ND).
  - English: no official source for 國綜/國寫/課綱 terms (CEEC's English page is outdated). Renderings are course-proposed; check literary-genre terms in 樂詞網 if a literature set exists **(open)**.
- **地理:** 樂詞網 高中以下地理學名詞 first, noting mismatches with 課綱 wording (環境負載力 vs 負載力).

**Provenance record** (`src/data/terms/{subject}.json`):

```
{ id, subject, zh, en,
  zhSource: { kind: curriculum|ceec|statute|moe-dict|agency, title, url, locator: "歷Da-Ⅴ-3 說明" | "民法§12", checked },
  enSource: { kind: naer-terms|law-moj-eng|agency-en|reference-work|course-proposed, set: "法律學名詞-刑法", url, checked },
  status: verified|proposed|needs-review,
  alternatives: [{ zh, en, note, source }],   // e.g. 日本帝國時期 / 日治時期 (both 課綱)
  introducedIn: "<course>:<slug>", notes }
```

**Rendering rules:**
- EN first use shows 「English（中文）」.
- `course-proposed` terms get a dotted underline with the tooltip "course translation, not official".
- MOE dictionary quotes carry their required attribution.

**Tests:**
- every `<Term id>` resolves to a registry entry;
- every `zhSource.url` is https;
- every contested-name entry has `alternatives` or an explicit "none";
- the build generates a review report listing all `proposed` and `needs-review` terms.

---

## 7. Totals

| Course | Parts (core) | Core chapters | Of which bridge | Projects | in_gsat codes covered |
|---|---|---|---|---|---|
| 歷史 | 13 (P0–P12) | 94 | 32 | 12 | 51/51 |
| 地理 | 13 | 96 | 17 | 12 (incl. 田野實察 ×3) | 77/77 + 3 checkpoints |
| 公民 | 13 | 106 | 25 | 12 | 78/78 (32/32 項目) |
| 國文 | 15 | 94 | 23 | 14 | 33/33 Stage Ⅴ codes + A1–A6, B1–B5, 15篇, 國寫 ×2 |
| 社會 integration | 1 | 4 | — | 1 | — |
| **Total** | | **394** | | | |

Tracks (分科 / beyond 學測) are separate: history 3, geography 3, civics 3, 國文 1.

For scale: the reference project has 239 chapters. A phased release, with each subject's P0–P2 first, is advisable.

---

## 8. Open items

1. **Codes missing:** 加深加廣 codes for the 歷史 and 地理 tracks are not in the research.
2. **國中/國小 per-code titles** were verified only at group level for: history Parts 2–4; geography P1 and the region primers; civics Ba-Ⅳ-1~5 and Bb-Ⅳ; 國文 Aa-I. Concept labels marked "(cand.)" or "to confirm" must be checked against the 課綱 text before course.json is frozen.
3. **考試說明 version:** re-check history and civics 例題 numbers and codes against the 108.11.08 file (geography found three changes there). History 112/113 and civics 113 試題特色 pages were not opened. Exam-item-to-code mappings without an official code must be labelled "inferred" in the UI.
4. **Licences unverified:**
   - 國史館 (claimed open-data licence);
   - 國家文化記憶庫 (per item);
   - 國家人權博物館;
   - 原民會;
   - NAER 課綱 PDF reuse;
   - 國土測繪 WMTS;
   - the CWA API;
   - foreign treaty texts (for 歷Da-Ⅴ-2);
   - whether 著作權法§9(1)(5) covers 學測 papers (link-only until resolved).
5. **Datasets not identified:**
   - elevation data for contours and hillshade;
   - satellite imagery;
   - Taiwan population, land-use and place-name tables;
   - world city sizes and regional statistics;
   - trade-flow data;
   - a licensed character-component dataset for a 六書 explorer (異體字字典 is link-only).
6. **Civics facts:**
   - exact 2022 複決 threshold (needs the 中選會 page);
   - contents of the 選罷法 amendments;
   - effective date of the 最低工資法;
   - 行政院 approval of the 2027 rate;
   - in-force date of the §1223 amendment;
   - vote count and dissent in 114年憲判字第1號;
   - where to teach 交易成本.
7. **國文:**
   - whether the 113.07.29 update of the 考試說明 set changed the 國文 guide;
   - 中華文化基本教材 篇目;
   - A/B/C 類 lists and grade placement of the 15篇;
   - 國寫 Q2 word limits for 113–115;
   - the 修辭格 code;
   - an authoritative punctuation-rule source;
   - any 課綱 revision after 107年1月;
   - the exact Stage Ⅴ code count.
8. **Terminology:** all history English renderings attributed to 樂詞網 are unverified (the queries hit an encoding problem); about 30 civics terms are unverified; every 國文 rendering is a proposal.
9. **Owner and lead decisions:**
   - Natural Earth de facto vs Taiwan point-of-view boundaries;
   - which course owns overlapping concepts (地科/地理 coastal landforms, atmospheric circulation, currents; math/地理 log axes);
   - whether to approve the cross-course `prereqs` schema and the shared concept namespace.
10. **Exam treatment of the either/or regions** is unconfirmed, so this plan covers both cases in the core.

### Critical files for implementation
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\src\data\course.json (schema to mirror; read-only)
- C:\Users\spp_l\Downloads\Claudechats\projects\ASMClearningPlayground\tests\curriculum.test.ts (no-jump rules to extend with cross-course prerequisites; read-only)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\courses\history.json, geography.json, civics.json, chinese.json (new outlines per subject)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\time-sensitive.json (new register, §3.3) and C:\Users\spp_l\Downloads\Claudechats\projects\學測\src\data\terms\ (new provenance registry, §6)
- C:\Users\spp_l\Downloads\Claudechats\projects\學測\tests\curriculum.test.ts (new: combined graph across courses, project-at-end-of-part, ≤5 new concepts, TS-ID and term-registry checks)