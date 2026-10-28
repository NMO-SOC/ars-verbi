# Graph Report - ars-verbi  (2026-10-28)

## Corpus Check
- 12 files · ~425,968 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 491 nodes · 754 edges · 25 communities (22 shown, 3 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 80 edges (avg confidence: 0.7)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3bbc7751`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Strategies for Addressing the Requirements
- Language and Word Choice
- Symbols and Motifs (Rainbow's End)
- Reasoning, Logic and Logical Fallacies
- Joe Gillis
- Language and Word Choice
- Analysing Argument (Part 06 hub)
- jszip.min.js
- assets/site.js
- Rhetorical and Structural Devices
- VCAA 2025 English Examination Report
- Appeals to Emotion and Values
- Appeals to Emotion and Values
- Rhetorical and Structural Devices
- Introduction and Context (Rainbow's End)
- Visual Language
- Visual Language
- Week-by-Week Revision Program
- build.py
- site.js
- Rainbow's End Quote Table
- VCE English Exam Prep Guide (site)
- Deploy site to GitHub Pages (workflow)
- 404 Page Not Found

## God Nodes (most connected - your core abstractions)
1. `Rhetorical and Structural Devices` - 24 edges
2. `Rhetorical and Structural Devices` - 24 edges
3. `Week-by-Week Revision Program` - 21 edges
4. `Language and Word Choice` - 21 edges
5. `Language and Word Choice` - 21 edges
6. `Appeals to Emotion and Values` - 18 edges
7. `Appeals to Emotion and Values` - 18 edges
8. `Joe Gillis` - 16 edges
9. `Norma Desmond` - 15 edges
10. `Visual Language` - 15 edges

## Surprising Connections (you probably didn't know these)
- `High-Scoring Vocabulary Bank (public page)` --semantically_similar_to--> `Sentence Starters and Linking Words Table`  [INFERRED] [semantically similar]
  public/vocabulary.html → snippets/ss.html
- `Deploy site to GitHub Pages (workflow)` --semantically_similar_to--> `GitLab Pages job`  [INFERRED] [semantically similar]
  .github/workflows/pages.yml → .gitlab-ci.yml
- `run()` --indirect_call--> `r()`  [INFERRED]
  site.js → public/assets/vendor/jszip.min.js
- `tick()` --indirect_call--> `c()`  [INFERRED]
  site.js → public/assets/vendor/jszip.min.js
- `VCE English Exam Preparation Guide — Website (project)` --conceptually_related_to--> `VCE English Exam Prep Guide (site)`  [INFERRED]
  README.md → HANDOVER.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Sunset Boulevard central relationship web (Joe, Norma, Max, Betty)** — joe_gillis, norma_desmond, max_von_mayerling, betty_schaefer [EXTRACTED 0.95]
- **Rainbow's End Central Character Ensemble Analysis** — nan_dear, gladys_banks, dolly_banks, errol_fisher, papa_dear [INFERRED 0.85]
- **Symbols of Colonial Oppression in Rainbow's End** — symbol_encyclopedias, symbol_hessian, symbol_the_humpy, theme_race_and_racism, rumbalara [INFERRED 0.80]
- **VCE English Exam Three-Section Structure (A/B/C, 20 marks each)** — public_p07_exam_format, public_p07_exam_format_section_a, public_p07_exam_format_section_b, public_p07_exam_format_section_c [EXTRACTED 1.00]
- **Section C Practice and Assessment Ecosystem** — public_p06_sample_analysing_argument_essays, public_p06_section_c_from_previous_exams, public_p09_section_c_mark_allocation, public_p10_general_checklist_for_section_c_response, public_p07_strategies_for_addressing_the_requirements [INFERRED 0.85]
- **Effective Study Techniques Toolkit (Part 13 chapter)** — public_p12_assess_your_current_study_habits, public_p12_create_a_personalised_study_schedule, public_p12_implement_active_recall_and_spaced_repetition, public_p12_develop_a_healthy_study_life_balance, public_p12_collaborate_with_study_groups, public_p12_fine_tune_your_exam_day_strategy [INFERRED 0.75]
- **Effectively Studying For Exams chapter chain (hub + sub-pages + revision program)** — public_part_12_effectively_studying_for_exams, public_p12_organise_your_study_materials, public_p12_seek_help_when_needed, public_p12_utilise_practice_exams_and_past_papers, public_revision_program [INFERRED 0.85]
- **2025 Assessment Report section chain (hub + General/A/B/C + checklist)** — public_part_13_key_takeaways_from_the_2025_assessment_report, public_r25_general, public_r25_section_a, public_r25_section_b, public_r25_section_c, public_r25_checklist [EXTRACTED 1.00]
- **2025 Assessment Report Chapter Cluster** — snippets_r25_hub, snippets_r25_general, snippets_r25_section_a, snippets_r25_section_b, snippets_r25_section_c, snippets_r25_checklist, snippets_report2025 [INFERRED 0.85]

## Communities (25 total, 3 thin omitted)

### Community 0 - "Strategies for Addressing the Requirements"
Cohesion: 0.24
Nodes (20): Exam Format, Section A: Analytical Response to a Text (exam component, 20 marks), Section B: Creating a Text (exam component, 20 marks), Section C: Analysis of Argument and Language (exam component, 20 marks), Strategies for Addressing the Requirements, Section A Mark Allocation, Section B Mark Allocation, Section C Mark Allocation (+12 more)

### Community 1 - "Language and Word Choice"
Cohesion: 0.10
Nodes (21): Allusion, Language and Word Choice, Cliche, Colloquial language, Connotation, Dysphemism, Emotive language, Euphemism (+13 more)

### Community 2 - "Symbols and Motifs (Rainbow's End)"
Cohesion: 0.07
Nodes (38): Assimilation Policy (1950s Australia), Bank Manager, Dolly Banks, Errol Fisher, Ester, Gladys Banks, Leon (Cousin), Mr. Coody (Rent Collector) (+30 more)

### Community 3 - "Reasoning, Logic and Logical Fallacies"
Cohesion: 0.07
Nodes (27): Analysing Argument: Persuasive Techniques (VCE Reference Table), Attack / ad hominem, Bandwagon, Evidence and Support, Reasoning, Logic and Logical Fallacies, Tone, Circular reasoning, Comparison to other jurisdictions (+19 more)

### Community 4 - "Joe Gillis"
Cohesion: 0.09
Nodes (49): America in the 1950s, Artie Green, Betty Schaefer, Cecil B. deMille, Chiaroscuro (film technique), Close-up Shot (film technique), Rainbow's End (VCE text), Fame and Obsession (theme) (+41 more)

### Community 5 - "Language and Word Choice"
Cohesion: 0.10
Nodes (21): Allusion, Language and Word Choice, Cliche, Colloquial language, Connotation, Dysphemism, Emotive language, Euphemism (+13 more)

### Community 6 - "Analysing Argument (Part 06 hub)"
Cohesion: 0.08
Nodes (35): Analysing Visual Language, Analysing Written Language, Table of Linking Words and Phrases, Persuasive Techniques Reference (PDF), Table of Common Persuasive Techniques, Table of Adjectives Describing Tone, Table of Verbs for Authorial Intent, Essay Structure (+27 more)

### Community 7 - "jszip.min.js"
Cohesion: 0.26
Nodes (21): A(), c(), d(), f(), G(), h(), i(), j() (+13 more)

### Community 8 - "assets/site.js"
Cohesion: 0.36
Nodes (5): esc(), load(), pad(), run(), tick()

### Community 9 - "Rhetorical and Structural Devices"
Cohesion: 0.08
Nodes (24): Alliteration, Analogy, Anaphora, Anecdote, Antithesis, Call to action, Rhetorical and Structural Devices, Climactic ordering (+16 more)

### Community 10 - "VCAA 2025 English Examination Report"
Cohesion: 0.71
Nodes (8): VCAA 2025 English Examination Report, Priority Checklist for 2026, 2025 Report: General Exam Advice, Key Takeaways from the 2025 Assessment Report (hub intro), 2025 Report Section A: Analytical Response to a Text, 2025 Report Section B: Creating a Text, 2025 Report Section C: Analysis of Argument and Language, Key Takeaways from the 2025 Assessment Report (full assembled page)

### Community 11 - "Appeals to Emotion and Values"
Cohesion: 0.04
Nodes (45): Analysing Argument: Persuasive Techniques (VCE Reference Table), Appeal to authority / expert opinion, Appeal to common sense, Appeal to family values, Appeal to fear, Appeal to freedom and individual rights, Appeal to group loyalty / belonging, Appeal to guilt or shame (+37 more)

### Community 12 - "Appeals to Emotion and Values"
Cohesion: 0.11
Nodes (18): Appeal to authority / expert opinion, Appeal to common sense, Appeal to family values, Appeal to fear, Appeal to freedom and individual rights, Appeal to group loyalty / belonging, Appeal to guilt or shame, Appeal to hope / optimism (+10 more)

### Community 13 - "Rhetorical and Structural Devices"
Cohesion: 0.08
Nodes (24): Alliteration, Analogy, Anaphora, Anecdote, Antithesis, Call to action, Rhetorical and Structural Devices, Climactic ordering (+16 more)

### Community 14 - "Introduction and Context (Rainbow's End)"
Cohesion: 0.33
Nodes (7): Cummeragunja (Aboriginal settlement), Jane Harrison (playwright), Papa Dear, Introduction and Context (Rainbow's End), Practice Analytical Text Response Topics (Rainbow's End), Rainbow's End (play), Stolen Generations

### Community 15 - "Visual Language"
Cohesion: 0.13
Nodes (15): Caption, Caricature and exaggeration, Visual Language, Colour, Facial expression and body language, Gaze and vectors, Graphs and infographics, Labelling in cartoons (+7 more)

### Community 16 - "Visual Language"
Cohesion: 0.13
Nodes (15): Caption, Caricature and exaggeration, Visual Language, Colour, Facial expression and body language, Gaze and vectors, Graphs and infographics, Labelling in cartoons (+7 more)

### Community 17 - "Week-by-Week Revision Program"
Cohesion: 0.08
Nodes (52): Framework of Ideas (Section B), Th.E.S.A.M.L. essay structure method, VCAA (Victorian Curriculum and Assessment Authority), VCAA 2024 English Assessment Report, VCAA 2025 English Examination Report, VCE English and EAL Study Design 2024–2027, Errol (Rainbow's End), Essay Proofreading Checklist (+44 more)

### Community 18 - "build.py"
Cohesion: 0.19
Nodes (5): _clean(), fix_quotes(), _heading_chain(), nav_html(), shell()

### Community 19 - "site.js"
Cohesion: 0.36
Nodes (5): esc(), load(), pad(), run(), tick()

### Community 22 - "VCE English Exam Prep Guide (site)"
Cohesion: 0.18
Nodes (12): api.anthropic.com (Essay Marker's AI backend, teacher-supplied key), Ask Max (AI assistant), LaTeX/Python build pipeline, Cloudflare Worker API (jolly-waterfall-d01a.nicholas-morlin.workers.dev), assets/embeddings.json (Ask Max retrieval index), Essay Marker, Exam Generator, GoatCounter (nmo.goatcounter.com) — anonymous page-view counts (+4 more)

## Knowledge Gaps
- **255 isolated node(s):** `Deploy site to GitHub Pages (workflow)`, `GitLab Pages job`, `JSZip library (bundled locally in assets/vendor/)`, `Cloudflare Worker API (jolly-waterfall-d01a.nicholas-morlin.workers.dev)`, `GoatCounter (nmo.goatcounter.com) — anonymous page-view counts` (+250 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **3 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Week-by-Week Revision Program` connect `Week-by-Week Revision Program` to `Strategies for Addressing the Requirements`, `Symbols and Motifs (Rainbow's End)`, `Joe Gillis`, `Analysing Argument (Part 06 hub)`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Written Exemplars (Rainbow's End)` connect `Symbols and Motifs (Rainbow's End)` to `Week-by-Week Revision Program`?**
  _High betweenness centrality (0.049) - this node is a cross-community bridge._
- **Why does `Analysing Argument: Persuasive Techniques (VCE Reference Table)` connect `Appeals to Emotion and Values` to `Language and Word Choice`, `Rhetorical and Structural Devices`, `Visual Language`?**
  _High betweenness centrality (0.038) - this node is a cross-community bridge._
- **What connects `Deploy site to GitHub Pages (workflow)`, `GitLab Pages job`, `JSZip library (bundled locally in assets/vendor/)` to the rest of the system?**
  _255 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Language and Word Choice` be split into smaller, more focused modules?**
  _Cohesion score 0.09523809523809523 - nodes in this community are weakly interconnected._
- **Should `Symbols and Motifs (Rainbow's End)` be split into smaller, more focused modules?**
  _Cohesion score 0.07112375533428165 - nodes in this community are weakly interconnected._
- **Should `Reasoning, Logic and Logical Fallacies` be split into smaller, more focused modules?**
  _Cohesion score 0.07407407407407407 - nodes in this community are weakly interconnected._