# Ars Verbi — VCE English Exam Preparation Guide (2027)

[![Deploy site to GitHub Pages](https://github.com/NMO-SOC/ars-verbi/actions/workflows/pages.yml/badge.svg)](https://github.com/NMO-SOC/ars-verbi/actions/workflows/pages.yml)
[![Live site](https://img.shields.io/badge/site-nmo--soc.github.io%2Fars--verbi-7a1f2b)](https://nmo-soc.github.io/ars-verbi/)

A free study website for VCE Units 3/4 English (2027 texts: *Picnic at Hanging Rock* and
*The Lottery and Other Stories*), built by an English teacher for his Year 12 cohort at
South Oakleigh College. Live site:
**https://nmo-soc.github.io/ars-verbi/**

## What it contains

Scene summaries and analyses, quote banks, film technique guides, annotated
high-scoring exemplars, essay frameworks for all three exam sections,
assessors' report takeaways (2024 and 2025), ~200 practice topics, and
interactive study tools including flashcards, quizzes and an exam generator.

## Safety and transparency

- The site is entirely static HTML/CSS/JavaScript — it contains **no
  downloads, no executables, no trackers beyond anonymous page-view counts
  (GoatCounter), and no account system**, and it sets no cookies.
- No API keys exist anywhere in this repository or on the site.

## Disclaimer

This site and repository are provided **free and "as-is"**, in good faith,
for educational purposes, **without warranty of any kind**, express or
implied. While care has been taken with accuracy, content may contain errors
— students should verify anything high-stakes with their teacher. External
links lead to third-party sites outside the author's control. To the maximum
extent permitted by law, the author accepts **no liability** for any loss or
damage arising from use of this site, its tools,
or any linked content.

## Building the site

`build.py` converts the LaTeX booklet (`main.tex`, kept outside this
repository) to HTML with pandoc, adds the extra pages and fragments from
`snippets/` and `sectionc/`, and writes the finished site to `public/`.
Pushing to `main` deploys `public/` to GitHub Pages.
