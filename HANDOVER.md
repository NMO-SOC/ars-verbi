# VCE English Exam Prep Guide — Intranet Deployment Handover

Prepared by Mr N. Morlin (English) — for IT deployment onto the school web server.

## What this is

A fully static website (~100 HTML pages + assets): the Units 3/4 English exam
preparation guide with interactive study tools for the 2026 Year 12 cohort.
No server-side code, no database, no accounts. Everything in the zip is plain
HTML/CSS/JS and can be served by any web server (IIS, Apache, nginx).

## Deployment

1. Unzip so that `index.html` sits at the root of the chosen site/virtual directory.
2. Set `index.html` as the default document.
3. Ensure these MIME types are served (IIS sometimes needs .json added):
   - `.json` → `application/json`
   - `.docx` → `application/vnd.openxmlformats-officedocument.wordprocessingml.document`
4. No rewrites, no execute permissions, no special headers required.
5. Relative paths are used throughout — the site works from a subdirectory
   (e.g. `https://intranet/english/`) as long as files keep their structure.

## External services the site touches (all optional)

| Service | Used for | If blocked/offline |
|---|---|---|
| fonts.googleapis.com / gstatic.com | Typefaces | Site falls back to system fonts, fully functional |
| nmo.goatcounter.com | Anonymous page-view counts | Silently does nothing |

The Exam Generator's JSZip library is bundled locally (`assets/vendor/`) — no
CDN dependency.

## Content updates

The HTML is generated from a LaTeX/Python build pipeline maintained by
Mr Morlin — do not hand-edit the HTML files, as changes would be overwritten
by the next build. For content corrections, contact Mr Morlin; he rebuilds and
supplies a fresh zip.

## Privacy notes

- The site sets no cookies and collects no personal data itself.
- GoatCounter records anonymous page-view counts only.

Contact: Mr Morlin, English faculty.

## Usage and search data

- **Page views:** GoatCounter dashboard at https://nmo.goatcounter.com (log in with the site owner's account). It shows the most and least visited pages.
- **What students search for:** each search on the results page is logged there as an event. `search/<words>` found results; `search-no-results/<words>` found nothing, which is the best list of content to add next. Searches are anonymous: GoatCounter stores no names or IP addresses.
- **Broken links:** `.github/workflows/link-check.yml` runs `check_links.py` on the 1st of each month and opens a GitHub issue if anything is broken. Run it any time from the Actions tab ("Monthly link check" → Run workflow).
- **What's new on the home page:** edit the `WHATS_NEW` list in `build.py` (newest first; the top 4 show).
- **Booklet source:** `main.tex` is backed up in the private repo NMO-SOC/yr12-english-booklet-2027. Commit and push there after editing it.
