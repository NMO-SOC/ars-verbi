# Graph Report - ars-verbi  (2026-10-27)

## Corpus Check
- 14 files · ~407,289 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 565 nodes · 869 edges · 33 communities (23 shown, 10 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 90 edges (avg confidence: 0.71)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `1b20895b`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Exam Assessment Criteria (Part 09)
- Week-by-Week Revision Program
- Symbols and Motifs (Rainbow's End)
- Language and Word Choice
- Joe Gillis
- renderResult(s, raw, rEl) — renders marking result UI
- Analysing Argument (Part 06 hub)
- jszip.min.js
- assets/site.js
- Rhetorical and Structural Devices
- Week-by-Week Revision Program
- Language and Word Choice
- Appeals to Emotion and Values
- Rhetorical and Structural Devices
- Appeals to Emotion and Values
- Visual Language
- Visual Language
- Effectively Studying For Exams (hub, displayed as Part 13)
- build.py
- site.js
- Personal Journeys (Section B Framework option)
- Rainbow's End (Section A text option)
- VCE English Exam Prep Guide (site)
- Sunset Boulevard (Section A text option)
- Deploy site to GitHub Pages (workflow)
- saveAI() — persists AI provider config to localStorage
- switchTab(t) — switches Section A/B/C tab
- toggleEl(id) — toggles criteria accordion detail
- toggleFilter(type, btn) — toggles feedback-type highlight filter
- toggleTheme() — toggles dark/light mode
- 404 Page Not Found

## God Nodes (most connected - your core abstractions)
1. `Week-by-Week Revision Program` - 24 edges
2. `Rhetorical and Structural Devices` - 24 edges
3. `Rhetorical and Structural Devices` - 24 edges
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
- **Section prompt builders sharing a common calibration fragment** — marker_source_builda, marker_source_buildb, marker_source_buildc, marker_source_calib [EXTRACTED 1.00]
- **Essay Marker's pluggable AI backend (dispatch + two providers)** — marker_source_askai, handover_anthropic_api, marker_source_github_models_api [EXTRACTED 1.00]
- **Sunset Boulevard central relationship web (Joe, Norma, Max, Betty)** — joe_gillis, norma_desmond, max_von_mayerling, betty_schaefer [EXTRACTED 0.95]
- **Rainbow's End Central Character Ensemble Analysis** — nan_dear, gladys_banks, dolly_banks, errol_fisher, papa_dear [INFERRED 0.85]
- **Part 04 Essay-Writing Instructional Pipeline** — public_p04_introduction, public_p04_what_is_needed_in_an_essay, public_p04_planning, public_p04_analytical_text_response_structure, public_p04_proofreading [EXTRACTED 1.00]
- **Symbols of Colonial Oppression in Rainbow's End** — symbol_encyclopedias, symbol_hessian, symbol_the_humpy, theme_race_and_racism, rumbalara [INFERRED 0.80]
- **VCE English Exam Three-Section Structure (A/B/C, 20 marks each)** — public_p07_exam_format, public_p07_exam_format_section_a, public_p07_exam_format_section_b, public_p07_exam_format_section_c [EXTRACTED 1.00]
- **Section C Practice and Assessment Ecosystem** — public_p06_sample_analysing_argument_essays, public_p06_section_c_from_previous_exams, public_p09_section_c_mark_allocation, public_p10_general_checklist_for_section_c_response, public_p07_strategies_for_addressing_the_requirements [INFERRED 0.85]
- **Effective Study Techniques Toolkit (Part 13 chapter)** — public_p12_assess_your_current_study_habits, public_p12_create_a_personalised_study_schedule, public_p12_implement_active_recall_and_spaced_repetition, public_p12_develop_a_healthy_study_life_balance, public_p12_collaborate_with_study_groups, public_p12_fine_tune_your_exam_day_strategy [INFERRED 0.75]
- **Effectively Studying For Exams chapter chain (hub + sub-pages + revision program)** — public_part_12_effectively_studying_for_exams, public_p12_organise_your_study_materials, public_p12_seek_help_when_needed, public_p12_utilise_practice_exams_and_past_papers, public_revision_program [INFERRED 0.85]
- **Prompt-type worked examples built on Sunset Boulevard characters** — public_prompt_types, concept_norma_desmond, concept_joe_gillis, concept_sunset_boulevard_text [EXTRACTED 1.00]
- **2025 Assessment Report section chain (hub + General/A/B/C + checklist)** — public_part_13_key_takeaways_from_the_2025_assessment_report, public_r25_general, public_r25_section_a, public_r25_section_b, public_r25_section_c, public_r25_checklist [EXTRACTED 1.00]
- **Rainbow's End Analytical Toolkit (Quotes, Symbols, Devices)** — snippets_quotetable, snippets_symboltable, snippets_tracker [INFERRED 0.80]
- **VCE Prompt-Type Analysis Method (Discuss/Extent/Agree/How Does)** — snippets_prompt_types, snippets_prompt_types_re, concept_argument_evidence_technique_effect, concept_four_prompt_types [INFERRED 0.85]
- **2025 Assessment Report Chapter Cluster** — snippets_r25_hub, snippets_r25_general, snippets_r25_section_a, snippets_r25_section_b, snippets_r25_section_c, snippets_r25_checklist, snippets_report2025 [INFERRED 0.85]

## Communities (33 total, 10 thin omitted)

### Community 0 - "Exam Assessment Criteria (Part 09)"
Cohesion: 0.12
Nodes (42): Framework of Ideas (Section B), VCAA (Victorian Curriculum and Assessment Authority), VCAA 2024 English Assessment Report, VCAA 2025 English Examination Report, VCE English and EAL Study Design 2024–2027, VCE English Exam Preparation Guide (homepage), Sample Analysing Argument Essays, Section C Annotation Categories (Structure & evidence, Audience positioning, Language & technique, Ideas & interpretation) (+34 more)

### Community 1 - "Week-by-Week Revision Program"
Cohesion: 0.06
Nodes (53): Joe Gillis (character, Sunset Boulevard), Norma Desmond (character, Sunset Boulevard), 'Discuss' prompt type, 'Do you agree?' prompt type, 'How does…' prompt type, 'To what extent do you agree?' prompt type, Rainbow's End (VCE text), Sunset Boulevard (VCE text) (+45 more)

### Community 2 - "Symbols and Motifs (Rainbow's End)"
Cohesion: 0.06
Nodes (41): Assimilation Policy (1950s Australia), Bank Manager, Cummeragunja (Aboriginal settlement), Dolly Banks, Errol Fisher, Ester, Jane Harrison (playwright), Leon (Cousin) (+33 more)

### Community 3 - "Language and Word Choice"
Cohesion: 0.04
Nodes (48): Analysing Argument: Persuasive Techniques (VCE Reference Table), Allusion, Attack / ad hominem, Bandwagon, Evidence and Support, Language and Word Choice, Reasoning, Logic and Logical Fallacies, Tone (+40 more)

### Community 4 - "Joe Gillis"
Cohesion: 0.09
Nodes (48): America in the 1950s, Artie Green, Betty Schaefer, Cecil B. deMille, Chiaroscuro (film technique), Close-up Shot (film technique), Fame and Obsession (theme), Film Noir (+40 more)

### Community 5 - "renderResult(s, raw, rEl) — renders marking result UI"
Cohesion: 0.10
Nodes (31): api.anthropic.com (Essay Marker's AI backend, teacher-supplied key), Essay Marker, aiCfg() — reads AI provider config from localStorage, aiProviderHelp() — updates settings modal help text, annotate(text, comments) — inline highlight builder, askAI(prompt, files) — dispatches to Anthropic or GitHub Models, buildA() — Section A marking prompt builder, buildB() — Section B marking prompt builder (+23 more)

### Community 6 - "Analysing Argument (Part 06 hub)"
Cohesion: 0.10
Nodes (24): Analysing Visual Language, Analysing Written Language, Table of Linking Words and Phrases, Persuasive Techniques Reference (PDF), Table of Common Persuasive Techniques, Table of Adjectives Describing Tone, Table of Verbs for Authorial Intent, Essay Structure (+16 more)

### Community 7 - "jszip.min.js"
Cohesion: 0.26
Nodes (21): A(), c(), d(), f(), G(), h(), i(), j() (+13 more)

### Community 8 - "assets/site.js"
Cohesion: 0.31
Nodes (5): esc(), load(), pad(), run(), tick()

### Community 9 - "Rhetorical and Structural Devices"
Cohesion: 0.08
Nodes (24): Alliteration, Analogy, Anaphora, Anecdote, Antithesis, Call to action, Rhetorical and Structural Devices, Climactic ordering (+16 more)

### Community 10 - "Week-by-Week Revision Program"
Cohesion: 0.18
Nodes (23): VCAA 2025 English Examination Report, Argument -> Evidence -> Technique -> Effect Paragraph Structure, Four VCE Prompt Types (Discuss / To What Extent / Do You Agree / How Does), Th.E.S.A.M.L. Paragraph Method, Audience (Creating Texts), Personal Journeys, Practice Stimuli, Purpose (Creating Texts) (+15 more)

### Community 11 - "Language and Word Choice"
Cohesion: 0.04
Nodes (48): Analysing Argument: Persuasive Techniques (VCE Reference Table), Allusion, Attack / ad hominem, Bandwagon, Evidence and Support, Language and Word Choice, Reasoning, Logic and Logical Fallacies, Tone (+40 more)

### Community 12 - "Appeals to Emotion and Values"
Cohesion: 0.11
Nodes (18): Appeal to authority / expert opinion, Appeal to common sense, Appeal to family values, Appeal to fear, Appeal to freedom and individual rights, Appeal to group loyalty / belonging, Appeal to guilt or shame, Appeal to hope / optimism (+10 more)

### Community 13 - "Rhetorical and Structural Devices"
Cohesion: 0.08
Nodes (24): Alliteration, Analogy, Anaphora, Anecdote, Antithesis, Call to action, Rhetorical and Structural Devices, Climactic ordering (+16 more)

### Community 14 - "Appeals to Emotion and Values"
Cohesion: 0.11
Nodes (18): Appeal to authority / expert opinion, Appeal to common sense, Appeal to family values, Appeal to fear, Appeal to freedom and individual rights, Appeal to group loyalty / belonging, Appeal to guilt or shame, Appeal to hope / optimism (+10 more)

### Community 15 - "Visual Language"
Cohesion: 0.13
Nodes (15): Caption, Caricature and exaggeration, Visual Language, Colour, Facial expression and body language, Gaze and vectors, Graphs and infographics, Labelling in cartoons (+7 more)

### Community 16 - "Visual Language"
Cohesion: 0.13
Nodes (15): Caption, Caricature and exaggeration, Visual Language, Colour, Facial expression and body language, Gaze and vectors, Graphs and infographics, Labelling in cartoons (+7 more)

### Community 17 - "Effectively Studying For Exams (hub, displayed as Part 13)"
Cohesion: 0.25
Nodes (14): Assess your current study habits, SMART Goals, Collaborate with study groups, Create a personalised study schedule, Develop a healthy study-life balance, Pomodoro Method, Fine-tune your exam day strategy, Implement active recall and spaced repetition (+6 more)

### Community 18 - "build.py"
Cohesion: 0.19
Nodes (5): _clean(), fix_quotes(), _heading_chain(), nav_html(), shell()

### Community 19 - "site.js"
Cohesion: 0.31
Nodes (5): esc(), load(), pad(), run(), tick()

### Community 22 - "VCE English Exam Prep Guide (site)"
Cohesion: 0.22
Nodes (10): Ask Max (AI assistant), LaTeX/Python build pipeline, Cloudflare Worker API (jolly-waterfall-d01a.nicholas-morlin.workers.dev), assets/embeddings.json (Ask Max retrieval index), Exam Generator, GoatCounter (nmo.goatcounter.com) — anonymous page-view counts, fonts.googleapis.com / gstatic.com (typefaces), JSZip library (bundled locally in assets/vendor/) (+2 more)

## Knowledge Gaps
- **278 isolated node(s):** `Deploy site to GitHub Pages (workflow)`, `GitLab Pages job`, `JSZip library (bundled locally in assets/vendor/)`, `Cloudflare Worker API (jolly-waterfall-d01a.nicholas-morlin.workers.dev)`, `GoatCounter (nmo.goatcounter.com) — anonymous page-view counts` (+273 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **10 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Week-by-Week Revision Program` connect `Week-by-Week Revision Program` to `Exam Assessment Criteria (Part 09)`, `Joe Gillis`, `Analysing Argument (Part 06 hub)`, `Week-by-Week Revision Program`, `Effectively Studying For Exams (hub, displayed as Part 13)`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Analysing Argument (Part 06 hub)` connect `Analysing Argument (Part 06 hub)` to `Exam Assessment Criteria (Part 09)`, `Week-by-Week Revision Program`?**
  _High betweenness centrality (0.032) - this node is a cross-community bridge._
- **Why does `Written Exemplars (Rainbow's End)` connect `Week-by-Week Revision Program` to `Symbols and Motifs (Rainbow's End)`?**
  _High betweenness centrality (0.030) - this node is a cross-community bridge._
- **What connects `Deploy site to GitHub Pages (workflow)`, `GitLab Pages job`, `JSZip library (bundled locally in assets/vendor/)` to the rest of the system?**
  _278 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Exam Assessment Criteria (Part 09)` be split into smaller, more focused modules?**
  _Cohesion score 0.11614401858304298 - nodes in this community are weakly interconnected._
- **Should `Week-by-Week Revision Program` be split into smaller, more focused modules?**
  _Cohesion score 0.0602322206095791 - nodes in this community are weakly interconnected._
- **Should `Symbols and Motifs (Rainbow's End)` be split into smaller, more focused modules?**
  _Cohesion score 0.05975609756097561 - nodes in this community are weakly interconnected._