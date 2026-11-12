"""Build the offline copies of the guide: a PDF and a LaTeX zip for each part, and for the whole guide.

Run from build.py after the pages are written (python build.py --downloads). Reads the finished HTML pages
in public/, so it needs no LaTeX install: PDFs are printed by headless Microsoft Edge, and LaTeX is
converted by pandoc.

Left out on purpose: the Section C past-exam papers (VCAA material) - the page p06-section-c-from-previous-exams.html.
"""
import html as htmllib
import os
import re
import shutil
import subprocess
import zipfile

from bs4 import BeautifulSoup

GUIDE_TITLE = "VCE English Exam Preparation Guide"
GUIDE_SUBTITLE = "Offline version of this site"
EXCLUDE_PAGES = {"p06-section-c-from-previous-exams.html"}
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
DROP_SELECTORS = [".part-label", ".page-toc", ".prevnext", ".done-btn", "button", "script", "style",
                  "nav", ".anchor-link", ".ch-pos", "form", ".tool-bar", ".exam-banner", "#toc-fab",
                  "object", "iframe", "embed", ".pdf-embed-bar"]

# print layout for the PDFs: a cover for the whole guide, a title page for each part,
# and each chapter starts on a new page
PRINT_CSS = """
@page { size: A4; margin: 2.2cm 2cm; }
.dl-cover, .dl-part-title { page-break-after: always; height: 23cm; display: flex; flex-direction: column;
  justify-content: center; }
.dl-cover h1 { font-size: 2.8rem; margin: 0 0 .3em; }
.dl-part-title h1 { font-size: 2.4rem; margin: 0 0 .3em; }
.dl-cover p, .dl-part-title p { color: #6b665e; margin: 0 0 .6em; font-size: 1.05rem; }
.dl-chapter { page-break-before: always; }
.dl-part-title + .dl-chapter { page-break-before: auto; }
.dl-chapter h1 { margin-top: 0; }
/* the site's print stylesheet hides every h1; the offline copies need their headings */
.content .dl-cover h1, .content .dl-part-title h1, .content .dl-chapter h1 { display: block !important; }
"""


def slugify(s):
    s = re.sub(r"[^a-z0-9]+", "-", htmllib.unescape(s).lower()).strip("-")
    return s[:70]


def read_structure(public):
    """Parts and their chapters in sidebar order, from the sidebar of the home page."""
    soup = BeautifulSoup(open(os.path.join(public, "index.html"), encoding="utf-8").read(), "html.parser")
    parts = []
    for li in soup.select("li.grp"):
        a = li.select_one("summary a")
        if not a:
            continue
        href = a["href"]
        if not href.startswith("part-"):  # Study Tools is interactive, not a part
            continue
        title = re.sub(r"^\d+\s*", "", a.get_text(" ", strip=True))
        chapters = []
        for ca in li.select("ul.subnav a"):
            ch = ca["href"]
            if ch in EXCLUDE_PAGES or not ch.endswith(".html"):
                continue
            chapters.append((ch, ca.get_text(" ", strip=True)))
        if chapters:
            parts.append({"file": href, "title": title, "chapters": chapters})
    return parts


def chapter_fragment(public, href):
    soup = BeautifulSoup(open(os.path.join(public, href), encoding="utf-8").read(), "html.parser")
    main = soup.find("main", class_="content") or soup.find("main")
    if main is None:
        return ""
    for sel in DROP_SELECTORS:
        for el in main.select(sel):
            el.decompose()
    # internal links become plain text
    for a in main.find_all("a"):
        h = a.get("href", "")
        if h.endswith(".html") or h.startswith("#"):
            a.unwrap()
    return "".join(str(c) for c in main.children)


def fix_latex_images(body, public):
    """LaTeX copies drop SVG images and use the PNG where a WebP was made."""
    def fix(m):
        tag = m.group(0)
        src = re.search(r'src="([^"]+)"', tag).group(1)
        if src.endswith(".svg"):
            return ""
        if src.endswith(".webp"):
            png = src[:-5] + ".png"
            if os.path.exists(os.path.join(public, png)):
                tag = tag.replace(src, png)
        return tag
    return re.sub(r"<img[^>]+>", fix, body)


def chapter_html(label, frag):
    inner = frag if "<h1" in frag[:400] else "<h1>%s</h1>%s" % (htmllib.escape(label), frag)
    return '<section class="dl-chapter">%s</section>' % inner


def pdf_document(title, groups, public, cover):
    """groups: [(part title, [(chapter label, fragment)])]"""
    parts = []
    if cover:
        parts.append('<section class="dl-cover"><p>%s</p><h1>%s</h1>'
                     '<p>Units 3/4 English &middot; 2027 examination &middot; South Oakleigh College</p></section>'
                     % (htmllib.escape(GUIDE_SUBTITLE), htmllib.escape(GUIDE_TITLE)))
    for part_title, chapters in groups:
        parts.append('<section class="dl-part-title"><p>Part</p><h1>%s</h1></section>'
                     % htmllib.escape(part_title))
        for label, frag in chapters:
            parts.append(chapter_html(label, frag))
    body = "".join(parts).replace('src="assets/', 'src="../assets/')
    return ('<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>%s</title>'
            '<link rel="stylesheet" href="../assets/style.css"><style>%s</style></head>'
            '<body><main class="content">%s</main></body></html>') % (htmllib.escape(title), PRINT_CSS, body)


def latex_document(title, groups, public):
    """Parts become chapters and their chapter headings become sections, so each starts on a new page."""
    parts = []
    for part_title, chapters in groups:
        parts.append("<h1>%s</h1>" % htmllib.escape(part_title))
        for label, frag in chapters:
            inner = frag if "<h1" in frag[:400] else "<h1>%s</h1>%s" % (htmllib.escape(label), frag)
            parts.append(inner.replace("<h1", "<h2").replace("</h1>", "</h2>"))
    body = fix_latex_images("".join(parts), public).replace('src="assets/', 'src="../assets/')
    return ('<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>%s</title></head>'
            '<body><main class="content">%s</main></body></html>') % (htmllib.escape(title), body)


def find_edge():
    for p in EDGE_CANDIDATES:
        if os.path.exists(p):
            return p
    return None


def print_pdf(edge, html_path, pdf_path):
    if os.path.exists(pdf_path):
        os.remove(pdf_path)
    cmd = [edge, "--headless", "--disable-gpu", "--no-pdf-header-footer",
           "--print-to-pdf=" + os.path.abspath(pdf_path),
           "file:///" + os.path.abspath(html_path).replace("\\", "/")]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=300)
    return os.path.exists(pdf_path)


def make_tex(work, stem, title, subtitle=None):
    """pandoc: <stem>-latex.html -> <stem>.tex (report class, parts as chapters, title page)."""
    src = "%s-latex.html" % stem
    tex = "%s.tex" % stem
    args = ["pandoc", "-s", "-f", "html", "-t", "latex", "--wrap=none",
            "-V", "documentclass=report", "-V", "geometry:margin=2.2cm", "-V", "fontsize=11pt",
            "-V", "papersize=a4", "--top-level-division=chapter", "-M", "title=" + title]
    if subtitle:
        args += ["-M", "subtitle=" + subtitle]
    subprocess.run(args + ["-o", tex, src], cwd=work, check=True)
    text = open(os.path.join(work, tex), encoding="utf-8").read().replace("../assets/", "assets/")
    open(os.path.join(work, tex), "w", encoding="utf-8").write(text)
    return text


def zip_tex(work, public, stem, tex_text, out_zip):
    imgs = set(re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", tex_text))
    with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as z:
        z.write(os.path.join(work, stem + ".tex"), stem + ".tex")
        for rel in sorted(imgs):
            src = os.path.join(public, rel)
            if os.path.exists(src):
                z.write(src, rel)


def build_one(edge, public, work, out_dir, slug, title, groups, cover, subtitle=None):
    html_pdf = os.path.join(work, slug + ".html")
    html_tex = os.path.join(work, slug + "-latex.html")
    open(html_pdf, "w", encoding="utf-8").write(pdf_document(title, groups, public, cover))
    open(html_tex, "w", encoding="utf-8").write(latex_document(title, groups, public))
    pdf = os.path.join(out_dir, slug + ".pdf")
    ok_pdf = print_pdf(edge, html_pdf, pdf) if edge else False
    tex_text = make_tex(work, slug, title, subtitle)
    zip_path = os.path.join(out_dir, slug + "-latex.zip")
    zip_tex(work, public, slug, tex_text, zip_path)
    return {"title": title, "slug": slug,
            "pdf": ("downloads/%s.pdf" % slug) if ok_pdf else None,
            "zip": "downloads/%s-latex.zip" % slug,
            "pdf_kb": os.path.getsize(pdf) // 1024 if ok_pdf else 0,
            "zip_kb": os.path.getsize(zip_path) // 1024}


def make_downloads(public):
    out_dir = os.path.join(public, "downloads")
    work = os.path.join(public, "_dl")
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    os.makedirs(work, exist_ok=True)
    edge = find_edge()
    if not edge:
        print("downloads: Microsoft Edge not found, PDFs will be skipped")
    entries = []
    everything = []
    for p in read_structure(public):
        chapters = []
        for href, label in p["chapters"]:
            frag = chapter_fragment(public, href)
            if frag:
                chapters.append((label, frag))
        if not chapters:
            continue
        slug = p["file"][:-5]  # e.g. part-02-picnic-at-hanging-rock
        groups = [(p["title"], chapters)]
        entries.append(build_one(edge, public, work, out_dir, slug, p["title"], groups, cover=False))
        everything.append((p["title"], chapters))
    entries.append(build_one(edge, public, work, out_dir, "whole-guide", GUIDE_TITLE, everything, cover=True,
                             subtitle=GUIDE_SUBTITLE))
    shutil.rmtree(work, ignore_errors=True)
    return entries


def downloads_body(entries):
    rows = []
    for e in entries:
        pdf = ('<a href="%s">PDF</a> (%d KB)' % (e["pdf"], e["pdf_kb"])) if e["pdf"] else "PDF not built"
        rows.append('<tr><td>%s</td><td>%s</td><td><a href="%s">LaTeX zip (.tex + images)</a> (%d KB)</td></tr>'
                    % (htmllib.escape(e["title"]), pdf, e["zip"], e["zip_kb"]))
    return (
        '<h1>Offline version of this site</h1>'
        '<p>Each part of the guide is available as a PDF for reading or printing, or as a LaTeX zip if you want to '
        'edit it. The LaTeX zip contains the .tex file and the images it uses. Compile it with pdfLaTeX or XeLaTeX.</p>'
        '<p>The Section C past-exam papers are not included, because they are the VCAA&rsquo;s material.</p>'
        '<table><thead><tr><th>Part</th><th>PDF</th><th>LaTeX</th></tr></thead><tbody>%s</tbody></table>'
        % "".join(rows))


if __name__ == "__main__":
    import sys
    entries = make_downloads(sys.argv[1])
    for e in entries:
        print(e["slug"], e["pdf_kb"], "KB pdf", e["zip_kb"], "KB zip")
