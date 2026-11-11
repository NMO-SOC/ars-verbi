"""Build the downloadable copies of the guide: one PDF and one LaTeX zip per part, and one of each for the whole guide.

Run from build.py after the pages are written. Reads the finished HTML pages in public/, so it needs no
LaTeX install: PDFs are printed by headless Microsoft Edge, and LaTeX is converted by pandoc.

Left out on purpose: the Section C past-exam papers (VCAA material) - the page p06-section-c-from-previous-exams.html.
"""
import glob
import html as htmllib
import os
import re
import shutil
import subprocess
import zipfile

from bs4 import BeautifulSoup

EXCLUDE_PAGES = {"p06-section-c-from-previous-exams.html"}
EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]
DROP_SELECTORS = [".part-label", ".page-toc", ".prevnext", ".done-btn", "button", "script", "style",
                  "nav", ".anchor-link", ".ch-pos", "form", ".tool-bar", ".exam-banner", "#toc-fab",
                  "object", "iframe", "embed", ".pdf-embed-bar"]


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
        title = a.get_text(" ", strip=True)
        title = re.sub(r"^\d+\s*", "", title)
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
    # the chapter's own heading stays; internal links become plain text
    for a in main.find_all("a"):
        h = a.get("href", "")
        if h.endswith(".html") or h.startswith("#"):
            a.unwrap()
    return "".join(str(c) for c in main.children)


def image_list(fragment):
    return re.findall(r'<img[^>]+src="([^"]+)"', fragment)


def to_document(title, body, latex=False, public=None):
    """Full HTML document. LaTeX copies drop SVG images and use PNGs where a WebP was made."""
    if latex:
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
        body = re.sub(r"<img[^>]+>", fix, body)
    body = body.replace('src="assets/', 'src="../assets/')
    return ('<!doctype html><html lang="en-AU"><head><meta charset="utf-8"><title>%s</title>'
            '<link rel="stylesheet" href="../assets/style.css"></head><body><main class="content">%s</main>'
            '</body></html>') % (htmllib.escape(title), body)


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


def make_tex(work, public, stem):
    """pandoc: <stem>-latex.html -> <stem>.tex, then zip the .tex with the images it uses."""
    src = "%s-latex.html" % stem
    tex = "%s.tex" % stem
    subprocess.run(["pandoc", "-s", "-f", "html", "-t", "latex", "--wrap=none",
                    "-V", "geometry:margin=2.2cm", "-V", "fontsize=11pt", "-V", "papersize=a4",
                    "-o", tex, src], cwd=work, check=True)
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


def build_one(edge, public, work, out_dir, slug, title, fragments):
    body = "".join("<h1>%s</h1>%s" % (htmllib.escape(t), f) for t, f in fragments)
    html_pdf = os.path.join(work, slug + ".html")
    html_tex = os.path.join(work, slug + "-latex.html")
    open(html_pdf, "w", encoding="utf-8").write(to_document(title, body, latex=False, public=public))
    open(html_tex, "w", encoding="utf-8").write(to_document(title, body, latex=True, public=public))
    pdf = os.path.join(out_dir, slug + ".pdf")
    ok_pdf = print_pdf(edge, html_pdf, pdf) if edge else False
    tex_text = make_tex(work, public, slug)
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
    parts = read_structure(public)
    entries = []
    everything = []
    for p in parts:
        frags = []
        for href, label in p["chapters"]:
            frag = chapter_fragment(public, href)
            if frag:
                frags.append((label, frag))
        if not frags:
            continue
        slug = p["file"][:-5]  # e.g. part-02-picnic-at-hanging-rock
        entries.append(build_one(edge, public, work, out_dir, slug, p["title"], frags))
        everything.extend(frags)
    entries.append(build_one(edge, public, work, out_dir, "whole-guide", "VCE English Exam Preparation Guide", everything))
    shutil.rmtree(work, ignore_errors=True)
    return entries


def downloads_body(entries):
    rows = []
    for e in entries:
        pdf = ('<a href="%s">PDF</a> (%d KB)' % (e["pdf"], e["pdf_kb"])) if e["pdf"] else "PDF not built"
        rows.append('<tr><td>%s</td><td>%s</td><td><a href="%s">LaTeX zip (.tex + images)</a> (%d KB)</td></tr>'
                    % (htmllib.escape(e["title"]), pdf, e["zip"], e["zip_kb"]))
    return (
        '<h1>Downloads</h1>'
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
