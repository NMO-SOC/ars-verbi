#!/usr/bin/env python3
"""Build a multi-page static website (part hubs + chapter subpages) from the VCE booklet."""
import os, re, shutil, json, html, urllib.parse
from bs4 import BeautifulSoup

SRC = r"C:\Users\NMO\Claude\Projects\VCE Textbook\2027 Yr12 Booklet\12 Booklet 2027"
BUILD = r"C:\Users\NMO\Claude\Projects\VCE Textbook\ars-verbi"

def section_class(fname):
    # Section A = part 4 and its chapters, Section B = part 5, Section C = part 6, plus the matching
    # marking-criteria and checklist pages. Text parts (Picnic, Lottery) keep the default colour.
    if fname.startswith(("part-04-", "p04-", "p09-section-a-", "p10-general-checklist-for-section-a", "p11-section-a-")):
        return "sec-a"
    if fname.startswith(("part-05-", "p05-", "p09-section-b-", "p10-general-checklist-for-section-b", "p11-section-b-")):
        return "sec-b"
    if fname.startswith(("part-06-", "p06-", "p09-section-c-", "p10-general-checklist-for-section-c", "p11-section-c-")):
        return "sec-c"
    return ""

PUBLIC = os.path.join(BUILD, "public")
IMG_DIR = os.path.join(PUBLIC, "assets", "img")
PDF_DIR = os.path.join(PUBLIC, "assets", "pdf")
FILES_DIR = os.path.join(PUBLIC, "assets", "files")
def copy_if_changed(a, b):
    try:
        if os.path.exists(b) and os.path.getsize(b) == os.path.getsize(a): return
    except OSError: pass
    shutil.copy(a, b)

SITE_TITLE = "VCE English Exam Preparation Guide"

for d in (PUBLIC, IMG_DIR, PDF_DIR, FILES_DIR):
    os.makedirs(d, exist_ok=True)

# ---------------- preprocess LaTeX ----------------
tex = open(os.path.join(SRC, "main.tex"), encoding="utf-8").read()
# replace the exe-download generator text with a pointer to the web tool
tex = re.sub(r"(\\section\{English Exam Generator\}).*?(?=\\clearpage)",
             r"\1\nThe exam generator now runs directly on this site. It assembles a complete three-section practice paper from the question banks and downloads it as a Word document in the authentic task-book format.\n\n\\href{ZZFILE::__EXAMGEN__}{Open the Exam Generator}\n\n", tex, flags=re.S)

# Th.E.S.A.M.L body paragraph method: replace with styled layout
tex = re.sub(r"\\paragraph\{Th\}.*?Link back to your contention\.", "\n\nZZSAML\n\n", tex, count=1, flags=re.S)

# script section: link out instead of hosting the PDF
tex = tex.replace("Click the link below to open the Script:\\\\  \n\\textattachfile{SBScript.pdf}{Open SBScript.pdf}",
                  "The full script is available online:\n\n\\href{https://www.dailyscript.com/scripts/sunset_bld_3_21_49.html}{Read the Sunset Boulevard script at Daily Script}")
tex = re.sub(r"\\textattachfile\{SBScript\.pdf\}\{[^}]*\}",
             r"\\href{https://www.dailyscript.com/scripts/sunset_bld_3_21_49.html}{Read the Sunset Boulevard script at Daily Script}", tex)

tex = tex.replace("\\subsection{Stimuli List II}", "")

# unwrap \resizebox so pandoc keeps the tables inside
tex = re.sub(r"\\resizebox\{\\textwidth\}\{!\}\{\s*(\\begin\{tabular\}.*?\\end\{tabular\})\s*\}",
             r"\1", tex, flags=re.S)

# refresh the practice exams intro to match the web version
tex = tex.replace("This section of the book contains practice exams. These are not the previous VCAA exams which one may find on the official website. These exams have been specially made in order to assist you with better preparation for the exam.",
                  "This section gathers everything you need for timed practice: links to official VCAA past examinations, externally hosted practice papers, the school's purchased trial exams, and a generator that assembles a fresh exam on demand.")

# remove the seven copyrighted practice exam sections (site keeps the generator instead)
tex = re.sub(r"\\section\{Practice Exam I\}.*?(?=\\section\{English Exam Generator\})", "", tex, flags=re.S)

tex = re.sub(r"\\includepdf(\[[^\]]*\])?\s*\{([^}]+)\}",
             lambda m: "\n\nZZPDFEMBED %s ZZEND\n\n" % (m.group(2).strip() if m.group(2).strip().lower().endswith(".pdf") else m.group(2).strip() + ".pdf"), tex)
tex = re.sub(r"\\textattachfile\{([^}]+)\}\{([^}]+)\}",
             lambda m: r"\href{ZZFILE::%s}{%s}" % (m.group(1).strip(), m.group(2).strip()), tex)
tex = re.sub(r"\\addcontentsline\{exp\}\{examples\}\{([^}]+)\}",
             lambda m: "\n\nZZEXP %s ZZEXPEND\n\n" % m.group(1), tex)
open(os.path.join(BUILD, "_pre.tex"), "w", encoding="utf-8").write(tex)
os.system('cd "%s" && pandoc "%s/_pre.tex" -f latex -t html5 --section-divs --wrap=none -o "%s/_body.html"' % (SRC, BUILD, BUILD))
try:
    import lxml  # noqa
    _PARSER = "lxml"
except ImportError:
    _PARSER = "html.parser"
soup = BeautifulSoup(open(os.path.join(BUILD, "_body.html"), encoding="utf-8").read(), _PARSER)

# ---------------- assets ----------------
copied = set()
for img in soup.find_all("img"):
    base = os.path.basename(img.get("src", ""))
    sp = os.path.join(SRC, base)
    if os.path.exists(sp):
        if base not in copied:
            copy_if_changed(sp, os.path.join(IMG_DIR, base)); copied.add(base)
        img["src"] = "assets/img/" + urllib.parse.quote(base)
        img["loading"] = "lazy"; img["class"] = ["content-img"]
n_imgs = len(copied)
# favicon + social logo (no-space filename)
try:
    from PIL import Image
    _logo = Image.open(os.path.join(SRC, "SOC LOGO_VERTICAL.png")).convert("RGBA")
    _bgw = Image.new("RGBA", _logo.size, (255, 255, 255, 255))
    _bgw.paste(_logo, (0, 0), _logo)
    _sq = _bgw.convert("RGB")
    _w, _h = _sq.size
    _side = max(_w, _h)
    _canvas = Image.new("RGB", (_side, _side), (255, 255, 255))
    _canvas.paste(_sq, ((_side - _w) // 2, (_side - _h) // 2))
    _canvas.resize((48, 48)).save(os.path.join(PUBLIC, "assets", "favicon.png"))
    _canvas.resize((180, 180)).save(os.path.join(PUBLIC, "assets", "apple-touch-icon.png"))
    _canvas.resize((512, 512)).save(os.path.join(IMG_DIR, "soc-logo.png"))
except Exception as _e:
    print("icon generation skipped:", _e)

for a in soup.find_all("a", href=True):
    if a["href"] == "ZZFILE::__EXAMGEN__":
        a["href"] = "exam-generator.html"
        a["class"] = ["btn-inline"]
        continue
    if a["href"].startswith("ZZFILE::"):
        fn = a["href"].split("::", 1)[1]
        if os.path.exists(os.path.join(SRC, fn)):
            copy_if_changed(os.path.join(SRC, fn), os.path.join(FILES_DIR, fn))
        a["href"] = "assets/files/" + urllib.parse.quote(fn)
        a["class"] = ["file-dl"]; a["download"] = ""

pdf_pat = re.compile(r"ZZPDFEMBED\s+(\S+?\.pdf)\s+ZZEND", re.I)
copied_pdfs = set()
for p in soup.find_all(["p", "div"]):
    m = pdf_pat.search(p.get_text())
    if not m: continue
    fname = m.group(1)
    INLINE_FRAGS = {"QuoteTableSummary.pdf": "quotetable.html",
                    "Tracker.pdf": "tracker.html",
                    "SS.pdf": "ss.html",
                    "PJ1.pdf": "pj1.html",
                    "PJ2.pdf": "pj2.html"}
    if fname in INLINE_FRAGS and os.path.exists(os.path.join(BUILD, "snippets", INLINE_FRAGS[fname])):
        frag = open(os.path.join(BUILD, "snippets", INLINE_FRAGS[fname]), encoding="utf-8").read()
        p.replace_with(BeautifulSoup(frag, "html.parser"))
        copied_pdfs.add(fname)
        continue
    if os.path.exists(os.path.join(SRC, fname)) and fname not in copied_pdfs:
        copy_if_changed(os.path.join(SRC, fname), os.path.join(PDF_DIR, fname)); copied_pdfs.add(fname)
    enc = urllib.parse.quote(fname)
    p.replace_with(BeautifulSoup(
        '<div class="pdf-embed"><div class="pdf-embed-bar"><span class="pdf-name">%s</span>'
        '<a class="pdf-open" href="assets/pdf/%s" target="_blank" rel="noopener">Open in new tab &#8599;</a>'
        '<a class="pdf-dl" href="assets/pdf/%s" download>Download &#8595;</a></div>'
        '<iframe class="pdf-frame" src="assets/pdf/%s#view=FitH" loading="lazy" title="%s"></iframe></div>'
        % (html.escape(fname), enc, enc, enc, html.escape(fname)), "html.parser"))

for _t in soup.find_all("table"):
    if not _t.find("thead") and "qt-table" not in (_t.get("class") or []):
        _t["class"] = _t.get("class", []) + ["no-thead"]

# paragraph breaks: LaTeX \\ inside paragraphs became <br>; give them real spacing
for _br in soup.find_all("br"):
    if _br.parent and _br.parent.name == "p":
        _sp = soup.new_tag("span"); _sp["class"] = "pbr"
        _br.replace_with(_sp)

# strip duplicate auto-generated figure label ids
_seen_ids = set()
for _el in soup.find_all(id=True):
    if _el["id"] in _seen_ids:
        del _el["id"]
    else:
        _seen_ids.add(_el["id"])

# de-duplicate longtable header rows (LaTeX firsthead + continuation head)
for _t in soup.find_all("table"):
    _rows = _t.find_all("tr")
    while len(_rows) >= 2 and _rows[0].get_text("|", strip=True) and \
          _rows[0].get_text("|", strip=True) == _rows[1].get_text("|", strip=True):
        _rows[1].decompose()
        _rows = _t.find_all("tr")

# cover images (sources in covers/, copied to assets/img/covers)
def cover_html(img, alt, credit, cls="cover"):
    return ('<figure class="%s"><img src="assets/img/covers/%s" alt="%s"><figcaption>%s</figcaption></figure>'
            % (cls, img, html.escape(alt), credit))
HUB_COVERS = {
    "part-02-picnic-at-hanging-rock.html": ("picnic-newspaper.jpg",
        "A magnifying glass over a newspaper headline: College mystery deepens, four still missing",
        "<i>Picnic at Hanging Rock</i> (dir. Peter Weir, 1975)"),
    "part-03-the-lottery-and-other-stories.html": ("lottery-hyman.jpg",
        "Illustration: a raised hand holds up a paper slip marked with a black spot above a crowd of villagers",
        "Miles Hyman, <i>Shirley Jackson&rsquo;s &lsquo;The Lottery&rsquo;: The Authorized Graphic Adaptation</i> (2016)"),
}

SAML_HTML = """<div class="saml">
<div class="saml-item"><span class="saml-badge">Th</span><div class="saml-body"><b>Thematic-based topic sentence</b>
<p>Your topic sentence needs to be based upon a theme in the text, not a character.</p>
<div class="saml-ex"><span class="saml-no">&#10007;</span> &lsquo;Tessie Hutchinson is stoned to death by the villagers.&rsquo;<br>
<span class="saml-yes">&#10003;</span> &lsquo;Jackson suggests that blind loyalty to tradition allows ordinary people to commit extraordinary cruelty.&rsquo;</div></div></div>
<div class="saml-item"><span class="saml-badge">E</span><div class="saml-body"><b>Evidence</b>
<p>Quotes and scenes from the text that support the theme.</p></div></div>
<div class="saml-item"><span class="saml-badge">S</span><div class="saml-body"><b>Symbols</b>
<p>Symbols that relate to this theme &mdash; including historical and social context, and setting.</p></div></div>
<div class="saml-item"><span class="saml-badge">A</span><div class="saml-body"><b>Authorial intention</b>
<p>What was the author intending?</p></div></div>
<div class="saml-item"><span class="saml-badge">M</span><div class="saml-body"><b>Metalanguage</b>
<p>Discuss the metalanguage the author uses around this theme.</p></div></div>
<div class="saml-item"><span class="saml-badge">L</span><div class="saml-body"><b>Linking sentence</b>
<p>Link back to your contention.</p></div></div>
<p class="saml-note">Only the <b>Th</b> and <b>L</b> elements need to appear in this order &mdash; the middle elements can be woven through the paragraph.</p>
</div>"""

exp_pat = re.compile(r"ZZEXP\s+(.+?)\s+ZZEXPEND")
_TOPIC = ("<p class=\"saml-topic\"><b>Topic:</b> &lsquo;The desire for social acceptance shapes the behaviour of many of "
          "Jackson&rsquo;s characters.&rsquo; Do you agree?</p>")
_STEPS = ('<div class="saml-item"><span class="saml-badge">1</span><div class="saml-body"><b>Text, author and form</b>'
          '<p>Name the text, its author (or director) and its form: novel, film, play, short story collection.</p></div></div>'
          '<div class="saml-item"><span class="saml-badge">2</span><div class="saml-body"><b>Contention</b>'
          '<p>%s</p></div></div>'
          '<div class="saml-item"><span class="saml-badge">3</span><div class="saml-body"><b>Three arguments</b>'
          '<p>%s</p></div></div>')
INTRO_HTML = ('<div class="saml">' + _STEPS % (
    "Your answer to the topic, in one clear sentence.",
    "Outline the argument of each body paragraph, in the order they will appear.") +
    _TOPIC + '<div class="saml-model"><p class="saml-model-label">Model introduction</p><p>'
    '<span class="mv">1</span>In her 1949 short story collection <i>The Lottery and Other Stories</i>, Shirley Jackson exposes the quiet pressures that sit beneath ordinary American life. '
    '<span class="mv">2</span>Jackson suggests that the desire for social acceptance shapes much of her characters&rsquo; behaviour, although it is often the fear of exclusion, rather than a wish to belong, that drives them. '
    '<span class="mv">3</span>Her characters conform to avoid the judgement of their communities, construct false versions of themselves in order to appear successful, and, at their worst, take part in cruelty so that they are not the ones left outside.'
    '</p></div></div>')
CONC_HTML = ('<div class="saml">' + _STEPS % (
    "Restate your contention, in fresh words.",
    "Sum up what each body paragraph proved, in the same order.") +
    '<div class="saml-model"><p class="saml-model-label">Model conclusion</p><p>'
    '<span class="mv">1</span>Across <i>The Lottery and Other Stories</i>, Shirley Jackson presents a world in which belonging is never guaranteed. '
    '<span class="mv">2</span>The need to be accepted is one of the most powerful forces in her characters&rsquo; lives, and fear of exclusion, more than a wish to belong, is what drives them. '
    '<span class="mv">3</span>They conform to escape judgement, invent more impressive versions of themselves, and join in cruelty rather than become its target, revealing how fragile, and how dangerous, the desire for acceptance can be.'
    '</p></div></div>')
_MARKERS = {"ZZSAML": SAML_HTML, "ZZINTRO": INTRO_HTML, "ZZCONC": CONC_HTML}
for _p in soup.find_all("p"):
    _k = _p.get_text().strip()
    if _k in _MARKERS:
        _p.replace_with(BeautifulSoup(_MARKERS[_k], "html.parser"))

exemplars = []
for _p in soup.find_all("p"):
    _m = exp_pat.search(_p.get_text())
    if _m:
        _s = _p.find_parent("section")
        exemplars.append({"title": _m.group(1).strip(), "id": _s.get("id") if _s else None})
        _p.decompose()

# ---------------- structure: parts -> chapters ----------------
def slugify(t):
    return re.sub(r"[^a-z0-9]+", "-", t.lower()).strip("-") or "section"

parts = [s for s in soup.find_all("section", class_="level1") if s.find_parent("section") is None]

HOWTO = open(os.path.join(BUILD, "snippets/howto.html"), encoding="utf-8").read()
R2025 = open(os.path.join(BUILD, "snippets/report2025.html"), encoding="utf-8").read()

nav_items = []   # {num,title,file,chapters:[{title,file}],pages:[page dicts in order]}
all_pages = []   # linear order for prev/next: {file,title,content_fn,nav_key,chapter_file_or_None}
id_to_page = {}

part_meta = []
for i, sec in enumerate(parts, 1):
    h1 = sec.find("h1")
    title = h1.get_text(" ", strip=True) if h1 else "Part %d" % i
    part_meta.append({"idx": i, "title": title, "slug": slugify(title),
                      "file": "part-%02d-%s.html" % (i, slugify(title)), "sec": sec})

# chapters left out of the site (none now: all worked examples use the 2027 texts)
DROP_CHAPTERS = set()

display_num = 0
for pm in part_meta:
    display_num += 1
    sec = pm["sec"]; hub = pm["file"]
    if pm["idx"] == 1:
        nav_items.append({"num": display_num, "title": "How to Use This Site", "file": hub, "chapters": []})
        all_pages.append({"file": hub, "title": "How to Use This Site", "html": HOWTO, "nav": hub})
        id_to_page[sec.get("id", "preface")] = hub
        continue
    children = sec.find_all("section", recursive=False)
    chapters = []
    used_cf = set()
    if len(children) >= 2:
        for j, ch in enumerate(children, 1):
            hh = ch.find(["h2", "h3", "h4"])
            ct = hh.get_text(" ", strip=True) if hh else "Section %d" % j
            cf = "p%02d-%s.html" % (pm["idx"], slugify(ct)[:60])
            if cf in used_cf:
                k = 2
                while "p%02d-%s-%d.html" % (pm["idx"], slugify(ct)[:60], k) in used_cf: k += 1
                cf = "p%02d-%s-%d.html" % (pm["idx"], slugify(ct)[:60], k)
            used_cf.add(cf)
            if cf in DROP_CHAPTERS: continue
            chapters.append({"title": ct, "file": cf, "sec": ch})
            for el in ch.find_all(id=True): id_to_page[el["id"]] = cf
            if ch.get("id"): id_to_page[ch["id"]] = cf
        for el in sec.find_all(id=True):
            if el["id"] not in id_to_page: id_to_page[el["id"]] = hub
        if sec.get("id"): id_to_page[sec["id"]] = hub
    else:
        for el in sec.find_all(id=True): id_to_page[el["id"]] = hub
        if sec.get("id"): id_to_page[sec["id"]] = hub
    nav_items.append({"num": display_num, "title": pm["title"], "file": hub,
                      "chapters": [{"title": c["title"], "file": c["file"]} for c in chapters]})
    all_pages.append({"file": hub, "title": pm["title"], "part": pm, "chapters": chapters, "nav": hub})
    for _ci, c in enumerate(chapters, 1):
        all_pages.append({"file": c["file"], "title": c["title"], "chapter": c,
                          "part": pm, "nav": hub, "chidx": _ci, "chtotal": len(chapters)})
    if pm["title"].startswith("Key Takeaways from the 2024"):
        display_num += 1
        f25 = "part-13-key-takeaways-from-the-2025-assessment-report.html"
        chs25 = [("General Exam Advice", "r25-general"),
                 ("Section A: Analytical Response to a Text", "r25-section-a"),
                 ("Section B: Creating a Text", "r25-section-b"),
                 ("Section C: Analysis of Argument and Language", "r25-section-c"),
                 ("Priority Checklist for 2027", "r25-checklist")]
        ch_pages = [{"title": t, "file": sn + ".html",
                     "html": open(os.path.join(BUILD, "snippets", sn + ".html"), encoding="utf-8").read()}
                    for t, sn in chs25]
        hub_html = open(os.path.join(BUILD, "snippets", "r25-hub.html"), encoding="utf-8").read()
        hub_html += '<h2 class="in-part-head">In this part</h2><div class="ch-list">%s</div>' % "".join(
            '<a class="ch-card" href="%s"><span class="ch-num">%d</span><span>%s</span></a>'
            % (c["file"], j + 1, html.escape(c["title"])) for j, c in enumerate(ch_pages))
        nav_items.append({"num": display_num, "title": "Key Takeaways from the 2025 Assessment Report",
                          "file": f25, "chapters": [{"title": c["title"], "file": c["file"]} for c in ch_pages]})
        all_pages.append({"file": f25, "title": "Key Takeaways from the 2025 Assessment Report",
                          "html": hub_html, "nav": f25})
        for c in ch_pages:
            all_pages.append({"file": c["file"], "title": c["title"], "html": c["html"], "nav": f25})

REV_HTML = open(os.path.join(BUILD, "snippets", "revision-program.html"), encoding="utf-8").read()
for _pf, _cf, _ct, _ch in [
    ("part-12-effectively-studying-for-exams.html", "revision-program.html", "Week-by-Week Revision Program", REV_HTML)]:
    for _it in nav_items:
        if _it["file"] == _pf:
            _it["chapters"].append({"title": _ct, "file": _cf})
    for _pg in all_pages:
        if _pg["file"] == _pf and "chapters" in _pg:
            _pg["chapters"].append({"title": _ct, "file": _cf})
    _li = max(i for i, p in enumerate(all_pages) if p.get("nav") == _pf)
    all_pages.insert(_li + 1, {"file": _cf, "title": _ct, "html": _ch, "nav": _pf})

VOCAB_HTML = open(os.path.join(BUILD, "snippets", "vocab.html"), encoding="utf-8").read()
P06 = "part-06-analysing-argument.html"
for _it in nav_items:
    if _it["file"] == P06:
        _it["chapters"].append({"title": "High-Scoring Vocabulary Bank", "file": "vocabulary.html"})
for _pg in all_pages:
    if _pg["file"] == P06 and "chapters" in _pg:
        _pg["chapters"].append({"title": "High-Scoring Vocabulary Bank", "file": "vocabulary.html"})
_last6 = max(i for i, p in enumerate(all_pages) if p.get("nav") == P06)
all_pages.insert(_last6 + 1, {"file": "vocabulary.html", "title": "High-Scoring Vocabulary Bank",
                              "html": VOCAB_HTML, "nav": P06})

SST_HTML = open(os.path.join(BUILD, "snippets", "sentence-starters.html"), encoding="utf-8").read()
for _it in nav_items:
    if _it["file"] == P06:
        _it["chapters"].append({"title": "Sentence Starters for Analytical Writing", "file": "sentence-starters.html"})
for _pg in all_pages:
    if _pg["file"] == P06 and "chapters" in _pg:
        _pg["chapters"].append({"title": "Sentence Starters for Analytical Writing", "file": "sentence-starters.html"})
_last6b = max(i for i, p in enumerate(all_pages) if p.get("nav") == P06)
all_pages.insert(_last6b + 1, {"file": "sentence-starters.html", "title": "Sentence Starters for Analytical Writing",
                              "html": SST_HTML, "nav": P06})

for e in exemplars:
    e["url"] = (id_to_page.get(e["id"], "index.html") + "#" + e["id"]) if e["id"] else "index.html"


# ================= study tools =================
def _clean(t): return re.sub(r"\s+", " ", t).strip()

def _heading_chain(el, stop):
    chain = []
    sec = el.find_parent("section")
    while sec is not None and sec is not stop.parent:
        hh = sec.find(["h1","h2","h3","h4","h5"], recursive=False) or sec.find(["h2","h3","h4","h5"])
        if hh: chain.append(_clean(hh.get_text()))
        if sec is stop: break
        sec = sec.find_parent("section")
    return list(reversed(chain))

flashcards = []
for pg in all_pages:
    if "chapter" not in pg or "quote-bank" not in pg["file"]: continue
    text_name = pg["part"]["title"]
    root = pg["chapter"]["sec"]
    for li in root.find_all("li"):
        q = _clean(li.get_text(" "))
        if len(q) < 20 or li.find("ul"): continue
        chain = _heading_chain(li, root)
        cat = " \u00b7 ".join(c for c in chain[1:] if c) or chain[0] if chain else pg["title"]
        flashcards.append({"q": q, "cat": (chain[0] + " \u00b7 " + cat) if len(chain) > 1 else pg["title"],
                           "text": text_name})

topics_data = {}
for pg in all_pages:
    if "chapter" not in pg or "practice-analytical-text-response-topics" not in pg["file"]: continue
    tname = pg["part"]["title"]
    lines = [ _clean(x) for x in pg["chapter"]["sec"].get_text("\n").split("\n") ]
    out, cur = [], None
    for ln in lines:
        m = re.match(r"^(\d+)\.(?:\s+(.*))?$", ln)
        if m:
            if cur: out.append(_clean(cur))
            cur = m.group(2) or ""
        elif cur is not None and ln and not ln.lower().startswith(("topics from", "practice analytical")):
            if len(ln) < 120: cur += " " + ln
            else:
                out.append(_clean(cur)); cur = None
    if cur: out.append(_clean(cur))
    topics_data.setdefault(tname, [])
    topics_data[tname] += [re.sub(r"\s+([?,.!:;])", r"\1", t) for t in out if len(t) > 25]

glossary = []
for pg in all_pages:
    if "chapter" not in pg: continue
    if pg["file"] == "p02-film-techniques.html": srcname = "Film technique"
    elif pg["file"] == "p06-analysing-written-language.html": srcname = "Persuasive technique"
    else: continue
    tbl = pg["chapter"]["sec"].find("table")
    if not tbl: continue
    for tr in tbl.find_all("tr")[1:]:
        cells = [_clean(c.get_text(" ")) for c in tr.find_all(["td","th"])]
        if len(cells) >= 2 and cells[0] and len(cells[0]) < 60:
            d = cells[1] + ((" \u2014 " + cells[2]) if len(cells) > 2 and cells[2] else "")
            glossary.append({"term": cells[0], "def": d, "src": srcname})
EXTRA_GLOSSARY = [
 ("Allusion", "An indirect reference to another text, event or figure that imports its associations into the work."),
 ("Characterisation", "The methods an author uses to construct a character: dialogue, actions, appearance, others' reactions."),
 ("Connotation", "The emotional or cultural associations a word carries beyond its literal meaning."),
 ("Contention", "The central argument a writer or speaker advances; in your essay, the position your paragraphs prove."),
 ("Dramatic irony", "When the audience knows something a character does not, creating tension or poignancy."),
 ("Emotive language", "Word choices designed to provoke an emotional response and position the audience."),
 ("Flashback", "A scene set earlier than the main narrative, used to reveal context or motive."),
 ("Foreshadowing", "Hints or clues that prepare the audience for later events."),
 ("Framing device", "A narrative structure that encloses the main story, shaping how it is read."),
 ("Hyperbole", "Deliberate exaggeration for emphasis or effect."),
 ("Imagery", "Language appealing to the senses to create vivid impressions."),
 ("Inclusive language", "Pronouns like 'we' and 'our' that position the audience as sharing the writer's view."),
 ("Juxtaposition", "Placing contrasting elements side by side so each sharpens the other."),
 ("Metaphor", "A direct comparison describing one thing as another to transfer its qualities."),
 ("Motif", "A recurring image, phrase or idea that accumulates meaning across a text."),
 ("Narrative voice", "The perspective and personality through which a story is told."),
 ("Pathos", "An appeal to the audience's emotions."),
 ("Personification", "Giving human qualities to non-human things."),
 ("Rebuttal", "Directly addressing and dismantling an opposing argument."),
 ("Rhetorical question", "A question posed for effect, leading the audience toward an implied answer."),
 ("Satire", "Humour, irony or exaggeration used to criticise people, institutions or ideas."),
 ("Simile", "A comparison using 'like' or 'as'."),
 ("Stage directions", "A playwright's instructions for action, delivery and staging \u2014 key evidence when analysing drama."),
 ("Symbolism", "Objects, settings or images that carry meaning beyond their literal presence."),
 ("Tone", "The attitude a writer or speaker conveys toward their subject or audience."),
 ("Vernacular", "Everyday or regional language that grounds characters in place, class or community."),
 ("Ad hominem", "Attacking the person making an argument rather than the argument itself."),
 ("Allegory", "A narrative whose characters and events stand for a parallel moral, political or historical meaning."),
 ("Anaphora", "Deliberate repetition of a word or phrase at the start of successive clauses to build rhythm and force."),
 ("Antithesis", "Setting opposing ideas in balanced phrasing to sharpen the contrast between them."),
 ("Appeal to authority", "Citing experts, credentials or institutions so the audience defers to the position."),
 ("Appeal to fear", "Raising threatening consequences so the audience feels the risk of not agreeing."),
 ("Appeal to hip-pocket", "Framing an issue around cost and personal finances to engage self-interest."),
 ("Appeal to patriotism", "Invoking national identity and pride so agreement feels loyal and dissent disloyal."),
 ("Archetype", "A character type or pattern recurring across literature that carries instant associations."),
 ("Aside", "A short remark delivered to the audience that other characters do not hear."),
 ("Bandwagon", "Suggesting most people already agree, pressuring the audience to join the majority."),
 ("Call to action", "A direct instruction telling the audience what to do next."),
 ("Chiaroscuro", "Strong contrast of light and shadow in a frame, often signalling moral ambiguity or noir style."),
 ("Clich\u00e9", "A worn expression whose overuse signals lazy or manipulative reasoning \u2014 or is deployed knowingly."),
 ("Colloquial language", "Informal, conversational wording that builds rapport and an ordinary, relatable persona."),
 ("Cumulative listing", "Piling up examples or details so the sheer accumulation feels like proof."),
 ("Diegetic sound", "Sound that belongs to the world of the film, heard by its characters."),
 ("Epigraph", "A quotation placed at the start of a text that frames how it should be read."),
 ("Euphemism", "A softened expression that makes something unpleasant more palatable \u2014 or hides it."),
 ("Expert opinion", "Quoting a specialist to lend borrowed credibility to a claim."),
 ("Generalisation", "A sweeping claim about a whole group from limited cases; persuasive but vulnerable to rebuttal."),
 ("Intertextuality", "Meaning created through a text's references to or echoes of other texts."),
 ("Irony", "A gap between what is said and what is meant, or between expectation and outcome."),
 ("Jargon", "Specialised technical vocabulary that can build authority or exclude an audience."),
 ("Loaded language", "Words carrying strong connotations that smuggle judgement into apparent description."),
 ("Montage", "A sequence of shots compressed together to convey time passing or accumulating meaning."),
 ("Non-diegetic sound", "Sound outside the film's world \u2014 score, narration \u2014 shaping audience response directly."),
 ("Oxymoron", "Two contradictory terms fused together to provoke thought."),
 ("Paradox", "A statement that seems self-contradictory yet reveals an underlying truth."),
 ("Pun", "Wordplay exploiting double meanings, often to disarm or mock."),
 ("Repetition", "Repeating words or structures so an idea lodges in the audience's memory."),
 ("Sarcasm", "Bitter, mocking irony directed at a target."),
 ("Soliloquy", "A speech delivered alone on stage, giving direct access to a character's inner thoughts."),
 ("Statistics", "Numerical evidence that lends an argument an air of objectivity and precision."),
 ("Straw man", "Misrepresenting an opposing view in a weakened form so it is easier to knock down."),
 ("Tone shift", "A deliberate change in tone mid-text that redirects the audience's response."),
 ("Tricolon", "A three-part list whose rhythm makes a point feel complete and memorable."),
 ("Understatement", "Deliberately downplaying something so its true scale lands harder."),
]
_existing = set(g["term"].lower() for g in glossary)
for _t, _d in EXTRA_GLOSSARY:
    if _t.lower() not in _existing:
        glossary.append({"term": _t, "def": _d, "src": "Metalanguage"})
glossary.sort(key=lambda g: g["term"].lower())

TOOL_LABEL = '<div class="part-label">Study Tools</div>'
fc_page = TOOL_LABEL + """<h1>Quote Flashcards</h1>
<p class="lede">Test yourself on the quote banks. Read the quote, recall who says it and which theme it serves, then flip.</p>
<div class="tool-bar">
  <select aria-label="Which text" id="fc-text"><option value="">Both texts</option></select>
  <button id="fc-shuffle">Shuffle</button>
  <span class="tool-count" id="fc-count"></span>
</div>
<div class="fc-card" id="fc-card" tabindex="0">
  <div class="fc-inner">
    <div class="fc-face"><div class="fc-front" id="fc-front"></div><div class="fc-hint">Select the card, or press Space, to flip it</div></div>
    <div class="fc-face fc-back-face"><div class="fc-back" id="fc-back"></div></div>
  </div>
</div>
<div class="tool-bar">
  <button id="fc-prev">&#8592; Previous</button>
  <button id="fc-flip">Flip</button>
  <button id="fc-next">Next &#8594;</button>
</div>
<div class="tool-bar fc-judge">
  <button id="fc-again">Again</button>
  <button id="fc-know" class="fc-know">Got it</button>
  <span class="tool-count" id="fc-known"></span>
  <button id="fc-reset" class="fc-reset">Reset progress</button>
</div>
<p class="fc-help">Cards you mark &ldquo;Got it&rdquo; move to the back of the deck, so the ones you still need come up first. Your progress is saved in this browser.</p>
<script>window.FLASHCARDS = %s;</script>
<script>
(function(){
  var all = window.FLASHCARDS, deck = [], i = 0, flipped = false;
  var texts = {}; all.forEach(function(c){ texts[c.text] = 1; });
  var sel = document.getElementById('fc-text');
  Object.keys(texts).forEach(function(t){ var o = document.createElement('option'); o.value = t; o.textContent = t; sel.appendChild(o); });
  function shuffle(a){ for (var j = a.length - 1; j > 0; j--){ var k = Math.floor(Math.random() * (j + 1)); var tmp = a[j]; a[j] = a[k]; a[k] = tmp; } }
  var known = {}; try { known = JSON.parse(localStorage.getItem('fcKnown') || '{}'); } catch (e) {}
  function key(c){ var h = 0, s = c.q; for (var j = 0; j < s.length; j++){ h = (h * 31 + s.charCodeAt(j)) | 0; } return 'k' + h; }
  function save(){ try { localStorage.setItem('fcKnown', JSON.stringify(known)); } catch (e) {} }
  function rebuild(){
    var pool = all.filter(function(c){ return !sel.value || c.text === sel.value; });
    var todo = pool.filter(function(c){ return !known[key(c)]; }), done = pool.filter(function(c){ return known[key(c)]; });
    shuffle(todo); shuffle(done); deck = todo.concat(done); i = 0; show();
  }
  function tally(){
    var pool = all.filter(function(c){ return !sel.value || c.text === sel.value; });
    var k = pool.filter(function(c){ return known[key(c)]; }).length;
    document.getElementById('fc-known').textContent = 'You know ' + k + ' of ' + pool.length;
  }
  function show(){
    if (!deck.length) return;
    flipped = false;
    document.getElementById('fc-card').classList.remove('flipped');
    document.getElementById('fc-front').textContent = deck[i].q;
    document.getElementById('fc-back').textContent = deck[i].text + ' \u2014 ' + deck[i].cat;
    document.getElementById('fc-count').textContent = 'Card ' + (i + 1) + ' of ' + deck.length;
    var kn = !!known[key(deck[i])];
    document.getElementById('fc-know').setAttribute('aria-pressed', String(kn));
    tally();
  }
  function flip(){ flipped = !flipped; document.getElementById('fc-card').classList.toggle('flipped', flipped); }
  document.getElementById('fc-card').addEventListener('click', flip);
  document.getElementById('fc-card').addEventListener('keydown', function(e){ if (e.key === ' ' || e.key === 'Enter') { e.preventDefault(); flip(); } });
  document.getElementById('fc-flip').addEventListener('click', flip);
  document.getElementById('fc-next').addEventListener('click', function(){ i = (i + 1) %% deck.length; show(); });
  document.getElementById('fc-prev').addEventListener('click', function(){ i = (i - 1 + deck.length) %% deck.length; show(); });
  document.getElementById('fc-shuffle').addEventListener('click', rebuild);
  document.getElementById('fc-know').addEventListener('click', function(){ known[key(deck[i])] = 1; save(); i = (i + 1) %% deck.length; show(); });
  document.getElementById('fc-again').addEventListener('click', function(){ delete known[key(deck[i])]; save(); i = (i + 1) %% deck.length; show(); });
  document.getElementById('fc-reset').addEventListener('click', function(){ if (confirm('Clear the cards you have marked as known?')) { known = {}; save(); rebuild(); } });
  sel.addEventListener('change', rebuild);
  rebuild();
})();
</script>""" % json.dumps(flashcards, ensure_ascii=False)

tp_page = TOOL_LABEL + """<h1>Practice Topics &amp; Essay Timer</h1>
<p class="lede">Draw a random analytical topic and write against the clock, exam-style.</p>
<div class="tool-bar">
  <select aria-label="Which text" id="tp-text"></select>
  <button id="tp-draw">Draw a topic</button>
</div>
<div class="tp-topic" id="tp-topic">Press &ldquo;Draw a topic&rdquo; to begin.</div>
<div class="timer-wrap">
  <div class="timer" id="timer">60:00</div>
  <div class="tool-bar">
    <select aria-label="Timer length" id="t-mins"><option value="60">60 min (exam section)</option><option value="45">45 min</option><option value="30">30 min</option><option value="20">20 min (plan only)</option></select>
    <button id="t-start">Start</button>
    <button id="t-pause" disabled>Pause</button>
    <button id="t-reset">Reset</button>
  </div>
</div>
<script>window.TOPICS = %s;</script>
<script>
(function(){
  var T = window.TOPICS, sel = document.getElementById('tp-text');
  var names = Object.keys(T);
  var o0 = document.createElement('option'); o0.value = ''; o0.textContent = 'Either text'; sel.appendChild(o0);
  names.forEach(function(n){ var o = document.createElement('option'); o.value = n; o.textContent = n + ' (' + T[n].length + ' topics)'; sel.appendChild(o); });
  document.getElementById('tp-draw').addEventListener('click', function(){
    var pool = [];
    names.forEach(function(n){ if (!sel.value || sel.value === n) T[n].forEach(function(t){ pool.push({n: n, t: t}); }); });
    var pick = pool[Math.floor(Math.random() * pool.length)];
    document.getElementById('tp-topic').textContent = '[' + pick.n + '] ' + pick.t;
  });
  var total = 3600, left = 3600, iv = null;
  var disp = document.getElementById('timer'), start = document.getElementById('t-start'),
      pause = document.getElementById('t-pause'), reset = document.getElementById('t-reset'),
      mins = document.getElementById('t-mins');
  function fmt(s){ var m = Math.floor(s / 60), x = s %% 60; return m + ':' + (x < 10 ? '0' : '') + x; }
  function draw(){ disp.textContent = fmt(left); disp.classList.toggle('t-low', left <= 300 && left > 0); }
  function done(){ clearInterval(iv); iv = null; disp.textContent = "Time's up!"; disp.classList.add('t-done'); start.disabled = false; pause.disabled = true; }
  start.addEventListener('click', function(){
    if (iv) return;
    if (left <= 0){ left = total; }
    disp.classList.remove('t-done');
    iv = setInterval(function(){ left--; if (left <= 0){ done(); return; } draw(); }, 1000);
    start.disabled = true; pause.disabled = false;
  });
  pause.addEventListener('click', function(){ clearInterval(iv); iv = null; start.disabled = false; pause.disabled = true; });
  reset.addEventListener('click', function(){ clearInterval(iv); iv = null; total = left = parseInt(mins.value, 10) * 60; disp.classList.remove('t-done'); draw(); start.disabled = false; pause.disabled = true; });
  mins.addEventListener('change', function(){ if (!iv){ total = left = parseInt(mins.value, 10) * 60; draw(); } });
  draw();
})();
</script>""" % json.dumps(topics_data, ensure_ascii=False)

gl_items = "".join('<div class="gl-item" data-term="%s"><b>%s</b> <span class="gl-src">%s</span><p>%s</p></div>'
                   % (html.escape(g["term"].lower()), html.escape(g["term"]), html.escape(g["src"]), html.escape(g["def"]))
                   for g in glossary)
gl_page = TOOL_LABEL + """<h1>Glossary of Techniques</h1>
<p class="lede">Every film and persuasive technique from the guide in one alphabetical reference.</p>
<div class="tool-bar"><input aria-label="Filter terms" id="gl-filter" type="search" placeholder="Filter terms&hellip;" style="flex:1;max-width:340px"></div>
<div class="gl-list" id="gl-list">%s</div>
<script>
(function(){
  var inp = document.getElementById('gl-filter'), items = document.querySelectorAll('.gl-item');
  inp.addEventListener('input', function(){
    var q = inp.value.trim().toLowerCase();
    items.forEach(function(it){ it.style.display = !q || it.textContent.toLowerCase().indexOf(q) > -1 ? '' : 'none'; });
  });
})();
</script>""" % gl_items

qz_page = TOOL_LABEL + """<h1>Technique Quiz</h1>
<p class="lede">A definition appears &mdash; pick the technique it describes. Ten questions per round, drawn from the glossary.</p>
<div class="tool-bar">
  <span class="tool-count" id="qz-progress" style="margin-left:0"></span>
  <span class="tool-count" id="qz-score"></span>
</div>
<div class="qz-box">
  <div class="qz-def" id="qz-def"></div>
  <div class="qz-opts" id="qz-opts"></div>
  <div class="qz-feedback" id="qz-feedback"></div>
</div>
<div class="tool-bar">
  <button id="qz-next" style="display:none">Next question &#8594;</button>
  <button id="qz-restart" style="display:none">New round</button>
</div>
<script>window.QUIZ = %s;</script>
<script>
(function(){
  var all = window.QUIZ, round = [], qi = 0, score = 0, answered = false;
  function shuffle(a){ for (var j = a.length - 1; j > 0; j--){ var k = Math.floor(Math.random() * (j + 1)); var t = a[j]; a[j] = a[k]; a[k] = t; } return a; }
  function start(){
    round = shuffle(all.slice()).slice(0, 10); qi = 0; score = 0;
    document.getElementById('qz-restart').style.display = 'none';
    ask();
  }
  function ask(){
    answered = false;
    var q = round[qi];
    var pool = shuffle(all.filter(function(g){ return g.term !== q.term; })).slice(0, 3);
    var opts = shuffle(pool.concat([q]));
    document.getElementById('qz-progress').textContent = 'Question ' + (qi + 1) + ' of ' + round.length;
    document.getElementById('qz-score').textContent = 'Score: ' + score;
    document.getElementById('qz-def').textContent = q.def;
    document.getElementById('qz-feedback').textContent = '';
    document.getElementById('qz-next').style.display = 'none';
    var box = document.getElementById('qz-opts'); box.innerHTML = '';
    opts.forEach(function(o){
      var b = document.createElement('button'); b.className = 'qz-opt'; b.textContent = o.term;
      b.addEventListener('click', function(){ pick(b, o, q); });
      box.appendChild(b);
    });
  }
  function pick(btn, o, q){
    if (answered) return;
    answered = true;
    var btns = document.querySelectorAll('.qz-opt');
    btns.forEach(function(b){ b.disabled = true; if (b.textContent === q.term) b.classList.add('qz-right'); });
    if (o.term === q.term){ score++; document.getElementById('qz-feedback').textContent = 'Correct.'; }
    else { btn.classList.add('qz-wrong'); document.getElementById('qz-feedback').textContent = 'Not quite \u2014 this one is \u201c' + q.term + '\u201d.'; }
    document.getElementById('qz-score').textContent = 'Score: ' + score;
    if (qi < round.length - 1){ document.getElementById('qz-next').style.display = ''; }
    else {
      document.getElementById('qz-feedback').textContent += ' Round over: ' + score + ' / ' + round.length + '.';
      document.getElementById('qz-restart').style.display = '';
    }
  }
  document.getElementById('qz-next').addEventListener('click', function(){ qi++; ask(); });
  document.getElementById('qz-restart').addEventListener('click', start);
  start();
})();
</script>""" % json.dumps([{"term": g["term"], "def": g["def"]} for g in glossary], ensure_ascii=False)

EXAMGEN = json.load(open(os.path.join(BUILD, "examgen", "examgen.json"), encoding="utf-8"))
# template slots: sb = text 2 (Picnic at Hanging Rock), re = text 1 (The Lottery and Other Stories)
EXAMGEN["sb"] = topics_data.get("Picnic at Hanging Rock", EXAMGEN["sb"])
EXAMGEN["re"] = topics_data.get("The Lottery and Other Stories", EXAMGEN["re"])
SLOTCFG = json.load(open(os.path.join(BUILD, "examgen", "slots.json"), encoding="utf-8"))
eg_page = TOOL_LABEL + """<h1>Exam Generator</h1>
<p class="lede">Generate a unique three-section practice examination on the spot &mdash; the complete task book as a Word document, identical in format to the real paper: cover page, instructions, Section A topics for both texts, a Creating Texts prompt with stimulus material, Section C source material and the assessment criteria.</p>
<div class="tool-bar">
  <button id="eg-go">Generate exam &#8595;</button>
  <span class="tool-count" id="eg-note"></span>
</div>
<p style="font-family:var(--sans);font-size:13.5px;color:var(--muted)">Every exam is assembled fresh from the question banks the moment you click. Print it and sit it under timed conditions &mdash; then mark it against the <a href="part-09-exam-assessment-criteria.html">assessment criteria</a>.</p>
<script src="assets/vendor/jszip.min.js"></script>
<script>window.EG_DATA = %s; window.EG_SLOTS = %s;</script>
<script>
(function(){
  var D = window.EG_DATA, S = window.EG_SLOTS, note = document.getElementById('eg-note');
  function pick(a){ return a[Math.floor(Math.random() * a.length)]; }
  function two(a){ var x = pick(a), y = pick(a), t = 0;
    while (y === x && a.length > 1 && t++ < 12) y = pick(a);
    return [x, y]; }
  function xesc(s){ return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function fill(s){ return s.split(String.fromCharCode(10)).map(xesc)
    .join('</w:t><w:br/><w:t xml:space="preserve">'); }
  function loadImg(url){ return new Promise(function(res, rej){
    var im = new Image(); im.onload = function(){ res(im); }; im.onerror = rej; im.src = url; }); }
  function slotPng(im, px){ var c = document.createElement('canvas');
    c.width = px[0]; c.height = px[1];
    var g = c.getContext('2d');
    g.fillStyle = '#ffffff'; g.fillRect(0, 0, c.width, c.height);
    if (im){ var r = Math.min(c.width / im.width, c.height / im.height);
      var w = im.width * r, h = im.height * r;
      g.drawImage(im, (c.width - w) / 2, (c.height - h) / 2, w, h); }
    return c.toDataURL('image/png').split(',')[1]; }
  document.getElementById('eg-go').addEventListener('click', function(){
    note.textContent = 'Assembling exam\u2026';
    fetch('assets/exam/web-template.docx').then(function(r){
      if (!r.ok) throw new Error('template fetch failed');
      return r.arrayBuffer();
    }).then(function(buf){ return JSZip.loadAsync(buf); }).then(function(zip){
      return zip.file('word/document.xml').async('string').then(function(xml){
        var sb = two(D.sb), re = two(D.re), b = pick(D.b),
            c = pick(D.c.filter(function(x){ return x.imgs.length; }));
        var repl = { '{A7}': sb[0], '{A8}': sb[1], '{A10}': re[0], '{A11}': re[1],
                     '{G9}': b.title || '', '{G11}': b.s1 || '', '{G15}': b.s3 || '' };
        Object.keys(repl).forEach(function(k){ xml = xml.split(k).join(fill(repl[k])); });
        zip.file('word/document.xml', xml);
        var jobs = [];
        function put(slot, url){
          jobs.push((url ? loadImg(url) : Promise.resolve(null)).then(function(im){
            zip.file(S.slots[slot], slotPng(im, S.px[slot]), { base64: true });
          }));
        }
        put('g13', b.img ? 'assets/exam/b/' + b.img : null);
        ['n13', 'n16', 'n17'].forEach(function(slot, k){
          put(slot, c.imgs[k] ? 'assets/exam/c/' + encodeURIComponent(c.imgs[k]) : null);
        });
        return Promise.all(jobs).then(function(){
          return zip.generateAsync({ type: 'blob',
            mimeType: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' });
        });
      });
    }).then(function(blob){
      var id = Math.random().toString(36).slice(2, 7).toUpperCase();
      var a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = 'Practice-Exam-' + id + '.docx';
      document.body.appendChild(a); a.click(); a.remove();
      note.textContent = 'Downloaded Practice-Exam-' + id + '.docx';
    }).catch(function(e){ note.textContent = 'Generation failed: ' + e; });
  });
})();
</script>""" % (json.dumps(EXAMGEN, ensure_ascii=False), json.dumps(SLOTCFG))

# ---------- outline builder (static page, no % formatting) ----------
ob_page = TOOL_LABEL + """<h1>Essay Outline Builder</h1>
<p class="lede">Plan body paragraphs with the right scaffold for the task: <b>Th.E.S.A.M.L.</b> for a Section A text response, <b>What &middot; How &middot; Why</b> for Section C analysing argument. (Section B pieces are not built from a formula &mdash; see <a href="part-05-creating-texts.html">Creating Texts</a>.) Everything autosaves on this device.</p>
<div class="tool-bar" id="ob-modes">
  <button type="button" class="ob-mode" data-m="a">Section A &mdash; Th.E.S.A.M.L.</button>
  <button type="button" class="ob-mode" data-m="c">Section C &mdash; What &middot; How &middot; Why</button>
</div>
<div class="ob-field"><label id="ob-cont-label">Contention (your essay&rsquo;s overall argument)</label><textarea aria-labelledby="ob-cont-label" id="ob-contention" rows="2" placeholder="e.g. Jackson suggests that blind loyalty to tradition allows ordinary people to commit extraordinary cruelty."></textarea></div>
<div id="ob-paras"></div>
<div class="tool-bar">
  <button id="ob-add">+ Add paragraph</button>
  <span style="flex:1"></span>
  <button id="ob-copy">Copy plan</button>
  <button id="ob-print">Print plan</button>
  <button id="ob-clear">Clear all</button>
</div>
<div id="ob-preview" class="ob-preview"></div>
<script>
(function(){
  var FIELDSETS = {
    a: [
      ['th', 'Th \u2014 Thematic topic sentence', 'A sentence based on a theme, not a character.'],
      ['e', 'E \u2014 Evidence', 'Quotes and scenes that support the theme.'],
      ['s', 'S \u2014 Symbols', 'Symbols, context and setting that relate to the theme.'],
      ['a', 'A \u2014 Authorial intention', 'What was the author intending?'],
      ['m', 'M \u2014 Metalanguage', 'The techniques you will name and analyse.'],
      ['l', 'L \u2014 Linking sentence', 'Link back to your contention.']
    ],
    c: [
      ['what', 'What \u2014 The argument', 'What is the author arguing at this point of the piece?'],
      ['how', 'How \u2014 Technique and evidence', 'Which persuasive technique or language choice, with a short embedded quote?'],
      ['why', 'Why \u2014 Effect on the audience', 'How does this position the specific target audience to think, feel or act?']
    ]
  };
  var CONT = {
    a: ['Contention (your essay\u2019s overall argument)', 'e.g. Jackson suggests that blind loyalty to tradition allows ordinary people to commit extraordinary cruelty.'],
    c: ['Opening overview \u2014 author, form, contention, tone, audience', 'e.g. In her opinion piece, [author] contends that\u2026 in a [tone] tone, targeting\u2026']
  };
  var FIELDS;
  var state = { mode: 'a', a: { contention: '', paras: [{}] }, c: { contention: '', paras: [{}] } };
  try {
    var sv = JSON.parse(localStorage.getItem('obState') || 'null');
    if (sv && sv.a && sv.c) state = sv;
    else if (sv && sv.paras) state.a = sv;
  } catch(e){}
  function cur(){ return state[state.mode]; }
  function setMode(m){
    state.mode = m;
    FIELDS = FIELDSETS[m];
    document.getElementById('ob-cont-label').textContent = CONT[m][0];
    document.getElementById('ob-contention').placeholder = CONT[m][1];
    var mb = document.querySelectorAll('.ob-mode');
    for (var i = 0; i < mb.length; i++){ mb[i].classList.toggle('ob-mode-on', mb[i].getAttribute('data-m') === m); }
    save(); render(); preview();
  }
  function save(){ try { localStorage.setItem('obState', JSON.stringify(state)); } catch(e){} }
  function render(){
    document.getElementById('ob-contention').value = cur().contention || '';
    var host = document.getElementById('ob-paras'); host.innerHTML = '';
    cur().paras.forEach(function(p, pi){
      var box = document.createElement('div'); box.className = 'ob-para';
      var head = document.createElement('div'); head.className = 'ob-para-head';
      head.innerHTML = '<b>Body paragraph ' + (pi + 1) + '</b>';
      if (cur().paras.length > 1){
        var rm = document.createElement('button'); rm.textContent = 'Remove'; rm.className = 'ob-rm';
        rm.addEventListener('click', function(){ cur().paras.splice(pi, 1); save(); render(); preview(); });
        head.appendChild(rm);
      }
      box.appendChild(head);
      FIELDS.forEach(function(f){
        var w = document.createElement('div'); w.className = 'ob-field';
        var lb = document.createElement('label'); lb.textContent = f[1]; w.appendChild(lb);
        var ta = document.createElement('textarea'); ta.rows = 2; ta.placeholder = f[2]; ta.value = p[f[0]] || '';
        ta.addEventListener('input', function(){ p[f[0]] = ta.value; save(); preview(); });
        w.appendChild(ta); box.appendChild(w);
      });
      host.appendChild(box);
    });
  }
  function planText(){
    var out = 'ESSAY PLAN (' + (state.mode === 'a' ? 'Section A - Th.E.S.A.M.L.' : 'Section C - What/How/Why') + ')' + String.fromCharCode(10) + (state.mode === 'a' ? 'Contention: ' : 'Overview: ') + (cur().contention || '') + String.fromCharCode(10);
    cur().paras.forEach(function(p, pi){
      out += String.fromCharCode(10) + 'BODY PARAGRAPH ' + (pi + 1) + String.fromCharCode(10);
      FIELDS.forEach(function(f){ if (p[f[0]]) out += '  ' + f[1] + ': ' + p[f[0]] + String.fromCharCode(10); });
    });
    return out;
  }
  function esc(s){ return s.replace(/[&<>]/g, function(c){ return { '&':'&amp;','<':'&lt;','>':'&gt;' }[c]; }); }
  function preview(){
    var h = '<h2>Your plan</h2>';
    if (cur().contention) h += '<p><b>' + (state.mode === 'a' ? 'Contention' : 'Overview') + ':</b> ' + esc(cur().contention) + '</p>';
    cur().paras.forEach(function(p, pi){
      var rows = FIELDS.filter(function(f){ return p[f[0]]; });
      if (!rows.length) return;
      h += '<h3>Body paragraph ' + (pi + 1) + '</h3><ul>';
      rows.forEach(function(f){ h += '<li><b>' + f[1].split(' \u2014 ')[0] + ':</b> ' + esc(p[f[0]]) + '</li>'; });
      h += '</ul>';
    });
    document.getElementById('ob-preview').innerHTML = h;
  }
  document.getElementById('ob-contention').addEventListener('input', function(e){ cur().contention = e.target.value; save(); preview(); });
  document.getElementById('ob-add').addEventListener('click', function(){ if (cur().paras.length < 5){ cur().paras.push({}); save(); render(); } });
  document.getElementById('ob-copy').addEventListener('click', function(){ navigator.clipboard.writeText(planText()).then(function(){ document.getElementById('ob-copy').textContent = 'Copied \u2713'; setTimeout(function(){ document.getElementById('ob-copy').textContent = 'Copy plan'; }, 1500); }); });
  document.getElementById('ob-print').addEventListener('click', function(){ window.print(); });
  document.getElementById('ob-clear').addEventListener('click', function(){ if (confirm('Clear this plan?')){ state[state.mode] = { contention: '', paras: [{}] }; save(); render(); preview(); } });
  var mbs = document.querySelectorAll('.ob-mode');
  for (var mi = 0; mi < mbs.length; mi++){
    (function(b){ b.addEventListener('click', function(){ setMode(b.getAttribute('data-m')); }); })(mbs[mi]);
  }
  setMode(state.mode || 'a');
})();
</script>"""

# ---------- vocabulary upgrader ----------
VOCAB_SWAPS = {
  "shows": ["demonstrates", "illustrates", "reveals", "highlights", "conveys", "depicts", "exposes", "emphasises", "underscores"],
  "show": ["demonstrate", "illustrate", "reveal", "highlight", "convey", "depict", "expose", "emphasise"],
  "showed": ["demonstrated", "illustrated", "revealed", "highlighted", "conveyed", "depicted"],
  "shown": ["demonstrated", "illustrated", "revealed", "conveyed"],
  "says": ["asserts", "contends", "argues", "maintains", "suggests", "posits", "claims", "declares", "implies"],
  "say": ["assert", "contend", "argue", "maintain", "suggest", "claim"],
  "said": ["asserted", "contended", "argued", "maintained", "suggested", "claimed"],
  "does": ["constructs", "orchestrates", "positions", "cultivates", "reinforces", "subverts", "foregrounds", "amplifies"],
  "did": ["constructed", "orchestrated", "positioned", "reinforced", "subverted"],
  "likes": ["favours", "endorses", "embraces", "advocates for"],
  "liked": ["favoured", "endorsed", "embraced"],
  "doesn't like": ["rejects", "condemns", "critiques", "denounces", "repudiates"],
  "good": ["effective", "compelling", "powerful", "persuasive"],
  "bad": ["destructive", "corrosive", "damaging", "flawed"],
  "gets": ["compels", "positions", "prompts", "invites"],
  "thing": ["element", "idea", "notion", "concern"],
  "things": ["elements", "ideas", "notions", "concerns"],
  "a lot": ["considerably", "extensively", "markedly"],
  "very": ["profoundly", "distinctly", "markedly"],
}
vu_page = TOOL_LABEL + """<h1>Vocabulary Upgrader</h1>
<p class="lede">Paste a paragraph and it flags the words that flatten analytical writing &mdash; <em>shows, says, does, very, thing</em> and friends &mdash; with stronger swaps from the vocabulary bank. Pick a suggestion to replace it.</p>
<textarea aria-label="Your paragraph" id="vu-text" rows="8" style="width:100%%;font-family:var(--serif);font-size:16.5px;line-height:1.6;padding:16px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink)" placeholder="Paste your paragraph here&hellip;"></textarea>
<div class="tool-bar">
  <button id="vu-check">Check my writing</button>
  <span class="tool-count" id="vu-count"></span>
</div>
<div id="vu-out" class="vu-out"></div>
<p style="font-family:var(--sans);font-size:13.5px;color:var(--muted)">See the full <a href="vocabulary.html">Vocabulary Bank</a> for the complete lists.</p>
<script>window.VU = %s;</script>
<script>
(function(){
  var SW = window.VU, out = document.getElementById('vu-out'), ta = document.getElementById('vu-text');
  var keys = Object.keys(SW).sort(function(a, b){ return b.length - a.length; });
  function esc(s){ return s.replace(/[&<>]/g, function(c){ return { '&':'&amp;','<':'&lt;','>':'&gt;' }[c]; }); }
  function check(){
    var text = ta.value;
    if (!text.trim()){ out.innerHTML = ''; document.getElementById('vu-count').textContent = ''; return; }
    var pattern = new RegExp('\\\\b(' + keys.map(function(k){ return k.replace(/[.*+?^${}()|[\\]\\\\]/g, '\\\\$&'); }).join('|') + ')\\\\b', 'gi');
    var n = 0, html = '';
    var last = 0, m;
    while ((m = pattern.exec(text)) !== null){
      html += esc(text.slice(last, m.index));
      var word = m[0], sugg = SW[word.toLowerCase()] || [];
      n++;
      html += '<span class="vu-flag" tabindex="0">' + esc(word) + '<span class="vu-pop">' +
        sugg.map(function(s){ return '<button class="vu-sw" data-i="' + m.index + '" data-len="' + word.length + '">' + esc(s) + '</button>'; }).join('') +
        '</span></span>';
      last = m.index + word.length;
    }
    html += esc(text.slice(last));
    out.innerHTML = '<div class="vu-render">' + html.replace(/\\n/g, '<br>') + '</div>';
    document.getElementById('vu-count').textContent = n ? n + ' word' + (n > 1 ? 's' : '') + ' to strengthen' : 'Nothing flagged \u2014 strong vocabulary throughout.';
    out.querySelectorAll('.vu-sw').forEach(function(b){
      b.addEventListener('click', function(){
        var i = parseInt(b.dataset.i, 10), len = parseInt(b.dataset.len, 10);
        ta.value = ta.value.slice(0, i) + b.textContent + ta.value.slice(i + len);
        check();
      });
    });
  }
  document.getElementById('vu-check').addEventListener('click', check);
})();
</script>""" % json.dumps(VOCAB_SWAPS, ensure_ascii=False)

# ---------- timed micro-drills ----------
dr_page = TOOL_LABEL + """<h1>Micro-Drills</h1>
<p class="lede">Five-minute bursts that build one skill at a time. Draw a drill, write against the clock.</p>
<div class="tool-bar">
  <select aria-label="Drill type" id="dr-type">
    <option value="topics">Three topic sentences (5 min)</option>
    <option value="plan">Plan an essay \u2014 no prose (5 min)</option>
    <option value="contention">Contention in one sentence (2 min)</option>
    <option value="link">Linking sentence back to contention (2 min)</option>
  </select>
  <button id="dr-go">Draw a drill</button>
  <span class="tool-count timer" id="dr-timer" style="font-size:28px"></span>
</div>
<div class="tp-topic" id="dr-topic" style="display:none"></div>
<textarea aria-label="Your drill answer" id="dr-pad" style="display:none;width:100%%;min-height:200px;font-family:var(--serif);font-size:16.5px;line-height:1.6;padding:16px;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--ink);margin-top:10px" placeholder="Write here&hellip;"></textarea>
<div class="tool-bar"><span class="tool-count" id="dr-wc" style="margin-left:0"></span></div>
<script>window.DRT = %s;</script>
<script>
(function(){
  var T = window.DRT, iv = null;
  var TASKS = {
    topics: ['Write THREE different thematic topic sentences for this topic:', 300],
    plan: ['Plan a full essay for this topic \u2014 contention plus three Th.E.S.A.M.L. skeletons. Dot points only:', 300],
    contention: ['Write your contention for this topic in ONE sentence:', 120],
    link: ['Write a linking sentence that ends a body paragraph and returns to your contention for this topic:', 120]
  };
  function pick(){ var names = Object.keys(T), n = names[Math.floor(Math.random() * names.length)];
    return '[' + n + '] ' + T[n][Math.floor(Math.random() * T[n].length)]; }
  function fmt(s){ return Math.floor(s / 60) + ':' + (s %% 60 < 10 ? '0' : '') + (s %% 60); }
  document.getElementById('dr-go').addEventListener('click', function(){
    var t = TASKS[document.getElementById('dr-type').value];
    document.getElementById('dr-topic').style.display = '';
    document.getElementById('dr-topic').innerHTML = '<b>' + t[0] + '</b><br><br>' + pick();
    var pad = document.getElementById('dr-pad'); pad.style.display = ''; pad.value = ''; pad.focus();
    var left = t[1], el = document.getElementById('dr-timer');
    clearInterval(iv); el.classList.remove('t-done'); el.textContent = fmt(left);
    iv = setInterval(function(){ left--;
      if (left <= 0){ clearInterval(iv); el.textContent = "Time!"; el.classList.add('t-done'); return; }
      el.textContent = fmt(left); el.classList.toggle('t-low', left <= 30);
    }, 1000);
  });
  document.getElementById('dr-pad').addEventListener('input', function(e){
    var w = e.target.value.trim() ? e.target.value.trim().split(/\\s+/).length : 0;
    document.getElementById('dr-wc').textContent = w + ' words';
  });
})();
</script>""" % json.dumps(topics_data, ensure_ascii=False)

hub_tools = TOOL_LABEL + """<h1>Study Tools</h1>
<p class="lede">Interactive revision tools built from the guide&rsquo;s own content.</p>
<h2 class="in-part-head">Tools</h2>
<div class="ch-list">
  <a class="ch-card" href="flashcards.html"><span>Quote Flashcards</span></a>
  <a class="ch-card" href="practice-topics.html"><span>Practice Topics &amp; Essay Timer</span></a>
  <a class="ch-card" href="glossary.html"><span>Glossary of Techniques</span></a>
  <a class="ch-card" href="technique-quiz.html"><span>Technique Quiz</span></a>
  <a class="ch-card" href="exam-generator.html"><span>Exam Generator</span></a>
  <a class="ch-card" href="outline-builder.html"><span>Essay Outline Builder</span></a>
  <a class="ch-card" href="vocab-upgrader.html"><span>Vocabulary Upgrader</span></a>
  <a class="ch-card" href="micro-drills.html"><span>Micro-Drills</span></a>
</div>"""

display_num += 1
tools_num = display_num
nav_items.append({"num": tools_num, "title": "Study Tools", "file": "study-tools.html",
                  "chapters": [{"title": "Quote Flashcards", "file": "flashcards.html"},
                               {"title": "Practice Topics & Essay Timer", "file": "practice-topics.html"},
                               {"title": "Glossary of Techniques", "file": "glossary.html"},
                               {"title": "Technique Quiz", "file": "technique-quiz.html"},
                               {"title": "Exam Generator", "file": "exam-generator.html"},
                               {"title": "Essay Outline Builder", "file": "outline-builder.html"},
                               {"title": "Vocabulary Upgrader", "file": "vocab-upgrader.html"},
                               {"title": "Micro-Drills", "file": "micro-drills.html"}]})
all_pages.append({"file": "study-tools.html", "title": "Study Tools", "html": hub_tools, "nav": "study-tools.html"})
all_pages.append({"file": "flashcards.html", "title": "Quote Flashcards", "html": fc_page, "nav": "study-tools.html"})
all_pages.append({"file": "practice-topics.html", "title": "Practice Topics & Essay Timer", "html": tp_page, "nav": "study-tools.html"})
all_pages.append({"file": "glossary.html", "title": "Glossary of Techniques", "html": gl_page, "nav": "study-tools.html"})
all_pages.append({"file": "technique-quiz.html", "title": "Technique Quiz", "html": qz_page, "nav": "study-tools.html"})
all_pages.append({"file": "exam-generator.html", "title": "Exam Generator", "html": eg_page, "nav": "study-tools.html"})
all_pages.append({"file": "outline-builder.html", "title": "Essay Outline Builder", "html": ob_page, "nav": "study-tools.html"})
all_pages.append({"file": "vocab-upgrader.html", "title": "Vocabulary Upgrader", "html": vu_page, "nav": "study-tools.html"})
all_pages.append({"file": "micro-drills.html", "title": "Micro-Drills", "html": dr_page, "nav": "study-tools.html"})
_ed = os.path.join(PUBLIC, "assets", "exam")
for _sub in ("b", "c"):
    os.makedirs(os.path.join(_ed, _sub), exist_ok=True)
    for _f in os.listdir(os.path.join(BUILD, "examgen", _sub)):
        copy_if_changed(os.path.join(BUILD, "examgen", _sub, _f), os.path.join(_ed, _sub, _f))
_fi = os.path.join(PUBLIC, "assets", "img", "pdffrag")
os.makedirs(_fi, exist_ok=True)
for _f in os.listdir(os.path.join(BUILD, "pdffrag", "img")):
    copy_if_changed(os.path.join(BUILD, "pdffrag", "img", _f), os.path.join(_fi, _f))
# Picnic character stills (sources in picnic/), resized for the Character Quote Bank
CHAR_PHOTOS = {"Miranda": "miranda.jpg", "Marion": "marion.jpg", "Irma": "Irma.jpg", "Edith": "edith.jpg",
               "Mrs Appleyard": "mrsappleyard.jpg", "Sara Waybourne": "sarawaybourne.jpg",
               "Miss McCraw": "missmcraw.jpg", "Mademoiselle de Poitiers": "mademoiselle.jpg",
               "Miss Lumley": "miss lumley.jpg", "Michael Fitzhubert": "michaelfithubert.jpg",
               "Albert Crundall": "albertcrundall.jpg"}
_pd = os.path.join(PUBLIC, "assets", "img", "picnic")
os.makedirs(_pd, exist_ok=True)
from PIL import Image
for _k, _f in list(CHAR_PHOTOS.items()):
    _out = slugify(_k) + ".jpg"
    _src, _dst = os.path.join(BUILD, "picnic", _f), os.path.join(_pd, _out)
    if not os.path.exists(_dst) or os.path.getmtime(_dst) < os.path.getmtime(_src):
        _im = Image.open(_src).convert("RGB"); _im.thumbnail((900, 900)); _im.save(_dst, quality=82)
    CHAR_PHOTOS[_k] = _out
os.makedirs(os.path.join(PUBLIC, "assets", "pdf"), exist_ok=True)
_cv = os.path.join(PUBLIC, "assets", "img", "covers")
os.makedirs(_cv, exist_ok=True)
for _f in os.listdir(os.path.join(BUILD, "covers")):
    shutil.copy(os.path.join(BUILD, "covers", _f), os.path.join(_cv, _f))
_sc = os.path.join(PUBLIC, "assets", "img", "sectionc")
os.makedirs(_sc, exist_ok=True)
for _f in os.listdir(os.path.join(BUILD, "sectionc")):
    if _f.endswith((".svg", ".png")):
        shutil.copy(os.path.join(BUILD, "sectionc", _f), os.path.join(_sc, _f))
copy_if_changed(os.path.join(BUILD, "localpdf", "persuasive-techniques-reference.pdf"),
                os.path.join(PUBLIC, "assets", "pdf", "persuasive-techniques-reference.pdf"))
copy_if_changed(os.path.join(BUILD, "examgen", "web-template.docx"), os.path.join(_ed, "web-template.docx"))
print("TOOLS: flashcards=%d topics=%s glossary=%d" % (len(flashcards), {k: len(v) for k, v in topics_data.items()}, len(glossary)))

def rewrite_anchors(scope, current):
    for a in scope.find_all("a", href=True):
        if a["href"].startswith("#"):
            pg = id_to_page.get(a["href"][1:])
            if pg and pg != current: a["href"] = pg + a["href"]

# ---------------- nav / shell ----------------
NAV_SHORT = {"Key Takeaways from the 2024 Assessment Report": "2024 Assessment Report",
             "Key Takeaways from the 2025 Assessment Report": "2025 Assessment Report"}
def nav_html(active_nav, active_file):
    out = []
    for it in nav_items:
        num = "%d" % it["num"]
        if it["chapters"]:
            is_open = " open" if it["file"] == active_nav else ""
            cls = ' class="active"' if active_file == it["file"] else ""
            subs = "".join('<li%s><a href="%s">%s</a></li>' %
                           (' class="active"' if c["file"] == active_file else "", c["file"], html.escape(c["title"]))
                           for c in it["chapters"])
            out.append('<li class="grp"><details%s><summary><a%s href="%s"><span class="num">%s</span>%s</a></summary>'
                       '<ul class="subnav">%s</ul></details></li>'
                       % (is_open, cls, it["file"], num, html.escape(NAV_SHORT.get(it["title"], it["title"])), subs))
        else:
            cls = ' class="active"' if it["file"] == active_file else ""
            out.append('<li%s><a href="%s"><span class="num">%s</span>%s</a></li>'
                       % (cls, it["file"], num, html.escape(NAV_SHORT.get(it["title"], it["title"]))))
    return "\n".join(out)

ANNOTATIONS = json.load(open(os.path.join(BUILD, "annotations.json"), encoding="utf-8"))
def apply_annotations(page_file, body):
    notes = ANNOTATIONS.get(page_file)
    if not notes:
        return body, 0
    CAT_LABEL = {"ideas": "Ideas &amp; interpretation", "structure": "Structure &amp; evidence",
                 "language": "Language &amp; technique", "audience": "Audience positioning",
                 "voice": "Voice &amp; craft"}
    hit = 0
    used = []
    for a in notes:
        q, n, c = a["q"], a["n"], a.get("c", "ideas")
        if q in body:
            body = body.replace(q, '<mark class="anno anno-%s" tabindex="0">%s<span class="anno-tip"><b class="anno-cat">%s</b>%s</span></mark>'
                                % (c, q, CAT_LABEL.get(c, ""), n), 1)
            hit += 1
            if c not in used: used.append(c)
    if hit:
        legend = "".join('<button class="lg lg-%s" data-cat="%s">%s</button>' % (c, c, CAT_LABEL[c]) for c in used)
        body = ('<div class="anno-hint">Select a highlighted passage to see what earns marks in that moment. '
                'Use the buttons to show one category at a time.<div class="anno-legend">%s</div></div>' % legend) + body
    return body, hit


def shift_headings(sec):
    """Sub-headings start at h2 under the page h1; keep their original look via an hl<n> class."""
    import re as _re
    hs = [h for h in sec.find_all(_re.compile("^h[2-6]$"))]
    if not hs:
        return
    delta = min(int(h.name[1]) for h in hs) - 2
    if delta <= 0:
        return
    for h in hs:
        n = int(h.name[1])
        h["class"] = h.get("class", []) + ["hl%d" % n]
        h.name = "h%d" % (n - delta)

IMG_ALT = {
    "Screenshot 2025-07-24 105659.png": "Proofreading checklist: varied vocabulary, varied sentences, formal style, no first person, linking words, textual evidence, links to the topic, a clear conclusion, and correct spelling, grammar and punctuation",
    "aud.png": "Mind map: young adults branching to working (pay, roster) and studying at uni (student politics, grades), each with further sub-topics",
    "image.png": "Mind map: young adults branching to working (pay, roster) and studying at uni (student politics, grades), each with further sub-topics",
    "Screenshot 2025-07-24 105411.png": "Table of text types and what each is good for, from blog post (reflecting on a topic) to feature article (exploring a topic in detail)",
    "2024ExamSectionB.png": "2024 exam Framework 3, Writing about personal journeys: the title Finding My Way and three stimuli, including a photo of feet standing among painted arrows",
    "aud2.png": "Scale from formal to standard to casual language, matched to how well the author knows the audience",
    "Screenshot 2025-07-24 105039.png": "Annotated cartoon of a tank at a petrol station, with five numbered notes on colour, speech bubbles, placement, contrast and metaphor",
    "Screenshot 2025-07-23 161319.png": "Long Live Lollies poster: a cartoon chocolate bar and heart arm in arm under the words Focus on the good",
    "Screenshot 2025-07-25 085732.png": "Cartoon: a woman throws bread to ducks by a park bench while a duck asks, How about going easy on the carbs?",
    "Screenshot 2025-07-25 085941.png": "Hands holding up musical items against a white wall: a guitar, a cymbal, maracas, a vinyl record and drumsticks",
    "Screenshot 2025-07-25 090126.png": "A heron in shallow wetland water pecking at floating plastic rubbish",
}

_IMG_SIZE = {}
def polish_images(body):
    """Alt text for known images, lazy loading below the first image, WebP for large PNGs."""
    from urllib.parse import unquote as _uq
    soup_ = BeautifulSoup(body, "html.parser")
    for i, img in enumerate(soup_.find_all("img")):
        src = img.get("src", "")
        name = _uq(src.split("/")[-1])
        if img.get("alt") is None:
            img["alt"] = IMG_ALT.get(name, "")
        if i > 0 and not img.get("loading"):
            img["loading"] = "lazy"
        img["decoding"] = "async"
        if src.startswith("assets/img/") and name.lower().endswith(".png"):
            path = os.path.join(PUBLIC, *_uq(src).split("/"))
            if os.path.exists(path) and os.path.getsize(path) > 120000:
                webp = path[:-4] + ".webp"
                if not os.path.exists(webp) or os.path.getmtime(webp) < os.path.getmtime(path):
                    from PIL import Image as _Im
                    _Im.open(path).save(webp, "WEBP", quality=82, method=6)
                img["src"] = src[:-4] + ".webp"
        if src.startswith("assets/") and not (img.get("width") and img.get("height")):
            fp = os.path.join(PUBLIC, *_uq(img["src"]).split("/"))
            if os.path.exists(fp):
                if fp not in _IMG_SIZE:
                    _IMG_SIZE[fp] = None
                    if fp.lower().endswith(".svg"):
                        _vb = re.search(r'viewBox="[\d.\-]+ [\d.\-]+ ([\d.]+) ([\d.]+)"', open(fp, encoding="utf-8").read())
                        if _vb:
                            _IMG_SIZE[fp] = (round(float(_vb.group(1))), round(float(_vb.group(2))))
                    else:
                        from PIL import Image as _Im
                        with _Im.open(fp) as _x:
                            _IMG_SIZE[fp] = _x.size
                if _IMG_SIZE[fp]:
                    img["width"], img["height"] = (str(v) for v in _IMG_SIZE[fp])
    # no heading-level jumps: a heading never sits more than one level below the one before it
    import re as _re
    prev = 0
    for h in soup_.find_all(_re.compile("^h[1-6]$")):
        n = int(h.name[1])
        if prev and n > prev + 1:
            if not h.get("class") and h.parent is not None and h.parent.name == "section":
                h["class"] = ["hl%d" % n]
            h.name = "h%d" % (prev + 1)
            n = prev + 1
        prev = n
    return str(soup_)

QUOTE_FIX = re.compile(r"(^|[\s\(\[\u2014\u2013>])\u2019(?=\S)")
def fix_quotes(html_str):
    return QUOTE_FIX.sub("\\1\u2018", html_str)

def shell(title, active_nav, active_file, main_html, prevnext=""):
    return """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>%s &middot; %s</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;0,8..60,700;1,8..60,400&family=Source+Sans+3:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<meta property="og:site_name" content="VCE English Exam Preparation Guide">
<meta property="og:title" content="%s">
<meta property="og:description" content="South Oakleigh College Units 3/4 English exam preparation guide - texts, essays, practice exams and study tools.">
<meta property="og:image" content="https://nmo-soc.github.io/VCE-English-Guide/assets/img/soc-logo.png">
<script>try{var _t=localStorage.getItem('siteTheme');if(_t==='dark'||(!_t&&window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches))document.documentElement.setAttribute('data-theme','dark');}catch(e){}</script>
<link rel="stylesheet" href="assets/style.css?v=72">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
<button id="menu-toggle" aria-label="Open menu">&#9776;</button>
<button id="search-toggle" type="button" aria-label="Search the guide"><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/></svg></button>
<div class="layout">
  <aside class="sidebar" id="sidebar">
    <a class="brand" href="index.html">
      <img class="brand-logo" src="assets/img/soc-logo.png" alt="South Oakleigh College">
      <span class="brand-title">VCE English</span>
      <span class="brand-sub">Exam Prep Guide</span>
    </a>
    <div class="search-wrap">
      <label for="search" class="vh">Search the guide</label><input id="search" type="search" placeholder="Search the guide&hellip;" autocomplete="off" aria-controls="search-results" aria-autocomplete="list">
      <div id="search-results"></div>
    </div>
    <nav class="toc"><ol>%s</ol></nav>
    <div class="side-foot">South Oakleigh College, 2027</div>
  </aside>
  <main class="content" id="main">
    %s
    %s
  </main>
</div>
%s
<script src="assets/site.js?v=50"></script>
<script data-goatcounter="https://nmo.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
</body>
</html>""" % (html.escape(title), SITE_TITLE, html.escape(title), nav_html(active_nav, active_file), fix_quotes(main_html), fix_quotes(prevnext),
       '')

def page_toc(scope):
    lis = []
    for h in scope.find_all(["h2", "h3", "h4", "h5"]):
        anc = h.find_parent("section")
        if anc is not scope and anc and anc.get("id"):  # skip the page's own title heading
            lis.append('<li class="lvl%s"><a href="#%s">%s</a></li>'
                       % (h.name[1], anc["id"], html.escape(h.get_text(" ", strip=True))))
    return ('<details class="page-toc" open><summary>On this page</summary><ul>%s</ul></details>' % "".join(lis)) if lis else ""

# ---------------- search index ----------------
search = []
for pg in all_pages:
    if pg.get("nosearch"): continue
    if "chapter" in pg:
        scope, part_title = pg["chapter"]["sec"], pg["part"]["title"]
    elif "part" in pg:
        scope, part_title = pg["part"]["sec"], pg["part"]["title"]
    else:
        _txt = re.sub(r"\s+", " ", BeautifulSoup(pg["html"], "html.parser").get_text(" "))[:1500]
        search.append({"t": pg["title"], "p": pg["title"], "u": pg["file"], "b": _txt.strip()})
        continue
    if "chapters" in pg and pg["chapters"]:
        search.append({"t": pg["title"], "p": pg["title"], "u": pg["file"]})
        continue
    for h in scope.find_all(["h1", "h2", "h3", "h4", "h5"]):
        anc = h.find_parent("section")
        hid = anc.get("id") if anc else None
        body = ""
        if anc:
            import copy as _copy
            _cl = _copy.copy(anc)
            for _sub in _cl.find_all("section"): _sub.decompose()
            body = re.sub(r"\s+", " ", _cl.get_text(" "))[:1500].strip()
        _t = h.get_text(" ", strip=True)
        _par = anc.find_parent("section") if anc else None
        if _par is not None:
            _ph = _par.find(["h1", "h2", "h3", "h4", "h5"])
            _pt = _ph.get_text(" ", strip=True) if _ph else ""
            if _pt and _pt != _t and _pt != pg["title"] and _pt != part_title and len(_pt) < 60:
                _t = _pt + " - " + _t
        search.append({"t": _t, "p": part_title,
                       "u": pg["file"] + ("#" + hid if hid else ""), "b": body})
json.dump(search, open(os.path.join(PUBLIC, "assets", "search.json"), "w", encoding="utf-8"), ensure_ascii=False)

# ---------------- write pages ----------------
PRACTICE_LINKS = """
<p>Official past VCE English examinations and examiner reports are published by the VCAA:</p>
<p><a class="btn-inline" href="https://www.vcaa.vic.edu.au/assessment/vce/examination-specifications-past-examinations-and-examination-reports/english" target="_blank" rel="noopener">Past VCE English examinations (VCAA)</a></p>
<h2>Practice exams</h2>
<p>The following practice exams are hosted externally (a free account may be required to view them). They open in a new tab.</p>
<ul class="exp-list exam-links">
<li><a href="https://www.studocu.com/en-au/document/hillcrest-christian-college/english/vce-english-section-c-exam-practice-2024-insight-publications/144053159" target="_blank" rel="noopener">Practice Exam I</a></li>
<li><a href="https://www.studocu.com/en-au/document/kew-high-school/vce-english/vce-english-practice-exam-analyzing-boxing-risks-vs-ama-credibility/127292037" target="_blank" rel="noopener">Practice Exam II</a></li>
<li><a href="https://www.studocu.com/en-au/document/john-monash-science-school/chemistry-unit-4/vce-english-year-12-trial-exam-paper-2024-comprehensive-task-book/163993956" target="_blank" rel="noopener">Practice Exam III</a></li>
<li><a href="https://www.studocu.com/en-au/document/melbourne-high-school/english/2025-tssm-vce-english-trial-exam-question-answer-book/142530772" target="_blank" rel="noopener">Practice Exam IV</a></li>
<li><a href="https://www.studocu.com/en-au/document/melbourne-high-school/english/2025-vce-english-year-12-trial-exam-task-book/143045324" target="_blank" rel="noopener">Practice Exam V</a></li>
<li><a href="https://www.studocu.com/en-au/document/loreto-mandeville-hall-toorak/english/2025-vce-english-year-12-trial-exam-task-book/141298123" target="_blank" rel="noopener">Practice Exam VI</a></li>
<li><a href="https://www.studocu.com/en-au/document/loreto-mandeville-hall-toorak/english/2025-vce-english-trial-examination-comprehensive-study-guide/141298120" target="_blank" rel="noopener">Practice Exam VII</a></li>
</ul>
<h2>School-purchased trial exams</h2>
<p>The following trial exams were purchased by South Oakleigh College under licence for the exclusive use of its students. They are available only through the school&rsquo;s SharePoint &mdash; sign in with your school account to view them. Please do not share, repost or distribute them outside the school.</p>
<ul class="exp-list exam-links">
<li><a href="https://eduvic.sharepoint.com/:b:/r/sites/EDUVIC_SOC_26_EN34A_NMO/Shared%20Documents/General/Practice%20Exams/Practice%20Exam%20VIII%20with%20Model%20Section%20C.pdf?csf=1&web=1&e=icqicL" target="_blank" rel="noopener">Practice Exam VIII with Model Section C</a></li>
<li><a href="https://eduvic.sharepoint.com/:b:/r/sites/EDUVIC_SOC_26_EN34A_NMO/Shared%20Documents/General/Practice%20Exams/practice-exam-ix.pdf?csf=1&web=1&e=mycdzw" target="_blank" rel="noopener">Practice Exam IX</a></li>
</ul>
"""

for k, pg in enumerate(all_pages):
    prev_a = ('<a class="pn prev" href="%s"><span>&#8592; Previous</span><b>%s</b></a>'
              % (all_pages[k-1]["file"], html.escape(all_pages[k-1]["title"]))) if k else "<span></span>"
    next_a = ('<a class="pn next" href="%s"><span>Next &#8594;</span><b>%s</b></a>'
              % (all_pages[k+1]["file"], html.escape(all_pages[k+1]["title"]))) if k < len(all_pages)-1 else "<span></span>"
    pn = '<nav class="prevnext">%s%s</nav>' % (prev_a, next_a)
    num = next(it["num"] for it in nav_items if it["file"] == pg["nav"])

    if "html" in pg:
        body = pg["html"]
        body = re.sub(r'<div class="part-label">Part \d+</div>', '<div class="part-label">Part %d</div>' % num, body)
    elif "chapters" in pg and pg["chapters"]:
        sec = pg["part"]["sec"]
        for c in pg["chapters"]:
            if "sec" in c: c["sec"].extract()
        rewrite_anchors(sec, pg["file"])
        h1 = sec.find("h1")
        if h1: h1.insert_before(BeautifulSoup('<div class="part-label">Part %d</div>' % num, "html.parser"))
        _cover = HUB_COVERS.get(pg["file"])
        if h1 and _cover:
            _after = h1.find_next_sibling()
            (_after if _after is not None and _after.name == "p" else h1).insert_after(BeautifulSoup(cover_html(*_cover), "html.parser"))
        cards = "".join('<a class="ch-card" href="%s"><span class="ch-num">%d</span><span>%s</span></a>'
                        % (c["file"], j+1, html.escape(c["title"])) for j, c in enumerate(pg["chapters"]))
        body = sec.decode() + '<h2 class="in-part-head">In this part</h2><div class="ch-list">%s</div>' % cards
    elif pg["file"] == "p08-english-exam-generator.html":
        crumb = ('<div class="part-label"><a href="%s">Part %d: %s</a>'
                 '<span class="ch-pos">Chapter %d of %d</span></div>'
                 % (pg["part"]["file"], num, html.escape(pg["part"]["title"]),
                    pg.get("chidx", 8), pg.get("chtotal", 8)))
        body = crumb + """<h1>English Exam Generator</h1>
<p>The exam generator now runs directly on this site &mdash; no download needed. It assembles a full three-section practice paper from the question banks: a random analytical topic for your text, a Creating Texts prompt with stimulus material, and an Analysing Argument source. Each generated paper downloads as a Word document identical in format to the real exam task book.</p>
<p><a class="btn" style="background:var(--accent);color:#fff" href="exam-generator.html">Open the Exam Generator &#8594;</a></p>
<p style="font-family:var(--sans);font-size:13.5px;color:var(--muted)">The original desktop version (Windows) is still available:
<a class="file-dl" href="assets/files/ExamGenerator.exe" download>ExamGenerator.exe</a></p>"""
    elif "chapter" in pg:
        sec = pg["chapter"]["sec"]
        if "quote-bank" in pg["file"]:
            sec["class"] = sec.get("class", []) + ["quotes-page"]
            # site.js adds a Theme / Story-or-Character toggle to these pages
            _sortable = {"p03-quote-banks.html": "story", "p02-thematic-quote-bank.html": "character"}
            if pg["file"] in _sortable:
                sec["data-sortable"] = _sortable[pg["file"]]
        if "exemplar" in pg["file"] or "sample-" in pg["file"]:
            sec["class"] = sec.get("class", []) + ["exemplar-page"]
        if pg["file"] == "p02-character-quote-bank.html":
            for _h in sec.find_all("h4"):
                _img = CHAR_PHOTOS.get(_clean(_h.get_text()))
                if _img:
                    _h.insert_after(BeautifulSoup('<figure class="char-photo"><img src="assets/img/picnic/%s" alt="%s" loading="lazy"></figure>'
                                                  % (_img, html.escape(_clean(_h.get_text()))), "html.parser"))
        if pg["file"] in ("p03-story-and-theme-grid.html", "p02-sequence-and-theme-grid.html"):
            for _tb in sec.find_all("table"):
                _tb["class"] = _tb.get("class", []) + ["theme-grid"]
        if pg["file"] == "p06-section-c-from-previous-exams.html":
            # lay every past task out like the exam paper (same look as the practice tasks)
            _instr = ('<p class="sc-label">Section C &ndash; Analysis of argument and language</p>'
                      '<p class="sc-label">Instructions</p><ul>'
                      '<li>In this section, you are required to analyse the use of argument(s) and language to persuade an intended audience to share the point of view expressed in a persuasive text.</li>'
                      '<li>Read the background information below and the material that follows, and write an analytical response to the task.</li>'
                      '<li>For the purposes of this task, the term &lsquo;language&rsquo; refers to written and spoken language, and &lsquo;visuals&rsquo; refers to images and graphics.</li>'
                      '<li>Your response will be assessed according to the Section C assessment criteria.</li></ul>'
                      '<p class="sc-label">Task</p><p>Write an analysis of the ways in which arguments, written and spoken language, and visuals are used in the material below to try to persuade the intended audience to share the point of view presented.</p>'
                      '<p class="sc-label">Background information</p>')
            _years = {"our-local-gym": "2024 VCAA exam", "strapleton-community-voice": "2024 VCAA sample exam", "an-open-letter": "2023 VCAA exam", "hapsey-happenings": "2022 VCAA exam"}
            # 2025 is rebuilt from the VCAA paper itself (the booklet copy had merged paragraphs)
            # 2024 and 2025 are rebuilt from the VCAA papers, with the exam's own images
            for _pre, _frag in (("lighting-the-way", "vcaa-2025.html"), ("our-local-gym", "vcaa-2024.html")):
                _old = sec.find("section", id=lambda x, _pre=_pre: x and x.startswith(_pre))
                if _old:
                    _old.replace_with(BeautifulSoup(open(os.path.join(BUILD, "sectionc", _frag),
                                                         encoding="utf-8").read(), "html.parser"))
            _secs = sec.find_all("section", class_="level4", recursive=False)
            for _s in _secs:
                _h = _s.find("h4")
                _label = next((p for p in _s.find_all("p", recursive=False)
                               if p.get_text(strip=True) == "Background information"), None)
                if not (_h and _label):
                    continue
                _bg = _label.find_next_sibling("p")
                _yr = next((y for k, y in _years.items() if _s.get("id", "").startswith(k)), "")
                if _yr:
                    _h.string = "%s: %s" % (_yr, _h.get_text())
                _ins = BeautifulSoup('<div class="sc-paper sc-instructions">%s</div>' % _instr, "html.parser").div
                # the background ends at the sentence introducing "the following" piece; anything after it
                # in the same source paragraph is the start of the article
                _segs, _cur = [], []
                for _c in list(_bg.contents):
                    if getattr(_c, "name", None) == "span" and "pbr" in (_c.get("class") or []):
                        _segs.append(_cur); _cur = []
                    else:
                        _cur.append(_c)
                _segs.append(_cur)
                _txt = lambda seg: "".join(x.get_text() if hasattr(x, "get_text") else str(x) for x in seg)
                _cut = next((i for i, sg in enumerate(_segs) if "following" in _txt(sg)), len(_segs) - 1)
                _rest = [sg for sg in _segs[_cut + 1:] if _txt(sg).strip()]
                _bg_new = BeautifulSoup("<p></p>", "html.parser").p
                for _i, sg in enumerate(_segs[:_cut + 1]):
                    if _i: _bg_new.append(BeautifulSoup('<span class="pbr"></span>', "html.parser").span)
                    for x in sg: _bg_new.append(x.extract() if hasattr(x, "extract") else x)
                _lead = None
                if _rest:
                    _lead = BeautifulSoup("<p></p>", "html.parser").p
                    for _i, sg in enumerate(_rest):
                        if _i: _lead.append(BeautifulSoup('<span class="pbr"></span>', "html.parser").span)
                        for x in sg: _lead.append(x.extract() if hasattr(x, "extract") else x)
                _bg.replace_with(_lead) if _lead else _bg.extract()
                _ins.append(_bg_new)
                _label.decompose()
                _art = BeautifulSoup('<div class="sc-paper sc-article"></div>', "html.parser").div
                for _ch in [c for c in _s.contents if c is not _h]:
                    _art.append(_ch.extract())
                _s["class"] = _s.get("class", []) + ["sc-scenario"]
                _s.append(_ins)
                _s.append(_art)
                _src = {"2024 VCAA exam": "VCAA 2024 VCE English examination", "2024 VCAA sample exam": "VCAA 2024 VCE English sample examination", "2023 VCAA exam": "VCAA 2023 VCE English examination", "2022 VCAA exam": "VCAA 2022 VCE English examination"}.get(_yr, "VCAA VCE English examination")
                _s.append(BeautifulSoup('<p class="sc-credit">Source: %s, Section C &copy; Victorian Curriculum and Assessment Authority.</p>' % _src, "html.parser"))
            # newest first: 2026, 2025, 2024, then the earlier tasks
            _rank = lambda s: 0 if s.get("id", "").startswith("vcaa-2025") else 1 if s.get("id", "").startswith("vcaa-2024") else 2 if s.get("id", "").startswith("strapleton") else 3
            _order = sorted(_secs, key=_rank)
            for _s in _order:
                sec.append(_s.extract())
            _first = _order[0] if _order else None
            _new = BeautifulSoup(open(os.path.join(BUILD, "sectionc", "vcaa-2026.html"), encoding="utf-8").read(), "html.parser")
            _intro = BeautifulSoup('<p class="sc-intro">Section C tasks from past VCAA English exams, laid out as they appear on the exam paper, newest first. '
                                   'Allow about an hour for each. The full papers are available on the VCAA website.</p>', "html.parser")
            if _first:
                _first.insert_before(_new)
                _new_sec = sec.find(id="vcaa-2026-frozen-swirl")
                _new_sec.insert_before(_intro)
        if pg["file"] == "p06-practice-articles-for-analysis.html":
            # original Section C practice tasks live in sectionc/ (web only)
            for _p in sec.find_all("p"):
                if "Resources upcoming" in _p.get_text():
                    _p.decompose()
            sec.append(BeautifulSoup(open(os.path.join(BUILD, "sectionc", "practice-articles.html"),
                                          encoding="utf-8").read(), "html.parser"))
        if pg["file"] == "p02-written-exemplars.html":
            # Section A low/medium/high sample essays on Picnic (web only, from sectionc/)
            sec.append(BeautifulSoup(open(os.path.join(BUILD, "sectionc", "picnic-section-a-essays.html"),
                                          encoding="utf-8").read(), "html.parser"))
        if pg["file"] == "p03-written-exemplars.html":
            # Section A low/medium/high sample essays on The Lottery (web only, from sectionc/)
            sec.append(BeautifulSoup(open(os.path.join(BUILD, "sectionc", "lottery-section-a-essays.html"),
                                          encoding="utf-8").read(), "html.parser"))
        if pg["file"] == "p05-personal-journeys.html":
            # one more Personal Journeys sample piece (web only, from sectionc/)
            sec.append(BeautifulSoup(open(os.path.join(BUILD, "sectionc", "personal-journeys-sample.html"),
                                          encoding="utf-8").read(), "html.parser"))
        if pg["file"] == "p04-what-is-needed-in-an-essay.html":
            # mark bands for Section A, quoted from the Section A descriptors (web only, from sectionc/)
            sec.append(BeautifulSoup(open(os.path.join(BUILD, "sectionc", "mark-bands-section-a.html"),
                                          encoding="utf-8").read(), "html.parser"))
        if pg["file"] == "p06-sample-analysing-argument-essays.html":
            # show Scenario 3 (task + letter) from the Section C practice tasks above the sample essays
            _sc3 = BeautifulSoup(open(os.path.join(BUILD, "sectionc", "practice-articles.html"),
                                      encoding="utf-8").read(), "html.parser").find(id="scenario-3-regional-trains")
            _h = sec.find(lambda tag: tag.name in ("h3", "h4") and tag.get_text(strip=True) == "The Task and Letter")
            if _sc3 and _h:
                _p = _h.find_next_sibling("p")
                for _div in reversed(_sc3.find_all("div", recursive=False)):
                    (_p or _h).insert_after(_div)
        if pg["file"] == "p02-symbols.html":
            _ul = sec.find("ul")
            if _ul:
                _rows = []
                for _li in _ul.find_all("li", recursive=False):
                    _sub = _li.find("ul")
                    _name = _li.get_text("\n").split("\n")[0].strip()
                    _pts = [x.get_text(" ", strip=True) for x in (_sub.find_all("li") if _sub else [])]
                    _cell = "<br>".join("&ndash; " + html.escape(p) for p in _pts)
                    _rows.append("<tr><td><b>%s</b></td><td>%s</td></tr>" % (html.escape(_name), _cell))
                _tbl = BeautifulSoup('<table class="qt-table"><thead><tr><th>Symbol</th>'
                                     '<th>Meaning and significance</th></tr></thead><tbody>%s</tbody></table>'
                                     % "".join(_rows), "html.parser")
                _ul.replace_with(_tbl)
        rewrite_anchors(sec, pg["file"])
        hh = sec.find(["h2", "h3", "h4"])
        if hh: hh.name = "h1"
        pos = ('<span class="ch-pos">Chapter %d of %d</span>' % (pg["chidx"], pg["chtotal"])) if pg.get("chidx") else ""
        crumb = ('<div class="part-label"><a href="%s">Part %d: %s</a>%s</div>'
                 % (pg["part"]["file"], num, html.escape(pg["part"]["title"]), pos))
        shift_headings(sec)
        _toc = page_toc(sec)
        _h1 = sec.find("h1")
        if _h1 and _toc:
            _h1.insert_after(BeautifulSoup(_toc, "html.parser"))
            body = crumb + sec.decode()
        else:
            body = crumb + _toc + sec.decode()
    else:
        sec = pg["part"]["sec"]
        rewrite_anchors(sec, pg["file"])
        h1 = sec.find("h1")
        if h1: h1.insert_before(BeautifulSoup('<div class="part-label">Part %d</div>' % num, "html.parser"))
        shift_headings(sec)
        body = page_toc(sec) + sec.decode()

    if pg["file"] == "p06-analysing-written-language.html":
        body += """<h2>Persuasive Techniques Reference (printable)</h2>
<p>The full reference table &mdash; techniques, definitions, examples and intended effects &mdash; as a document you can view or print.</p>
<div class="pdf-embed">
  <div class="pdf-embed-bar"><span class="pdf-name">Analysing Argument: Persuasive Techniques</span>
  <a class="pdf-open" href="assets/pdf/persuasive-techniques-reference.pdf" target="_blank" rel="noopener">Open in new tab &#8599;</a>
  <a class="pdf-dl" href="assets/pdf/persuasive-techniques-reference.pdf" download>Download &#8595;</a></div>
  <iframe class="pdf-frame" src="assets/pdf/persuasive-techniques-reference.pdf#view=FitH" loading="lazy" title="Persuasive Techniques Reference"></iframe>
</div>"""
    body = polish_images(fix_quotes(body))
    body, _ah = apply_annotations(pg["file"], body)
    if pg["file"] == "part-08-practice-exams.html":
        _g = re.search(r'(<section[^>]*id="english-exam-generator".*?</section>)', body, re.S)
        if _g:
            body = body.replace(_g.group(1), "", 1) + PRACTICE_LINKS + _g.group(1)
        else:
            body += PRACTICE_LINKS
    _html = shell(pg["title"], pg["nav"], pg["file"], body, pn)
    # colour each exam section's pages with that section's colour (see style.css body.sec-a/b/c)
    _cls = section_class(pg["file"])
    if _cls:
        _html = _html.replace("<body>", '<body class="%s">' % _cls, 1)
    open(os.path.join(PUBLIC, pg["file"]), "w", encoding="utf-8").write(_html)

# ---------------- landing ----------------
def exemplar_groups_html(exemplars):
    GROUPS = [("Section A: Picnic at Hanging Rock", "p02-"),
              ("Section A: The Lottery and Other Stories", "p03-"),
              ("Section B: Creating Texts", "p05-"),
              ("Section C: Analysing Argument", "p06-")]
    out = []
    used = set()
    for label, prefix in GROUPS:
        items = [e for e in exemplars if e["url"].startswith(prefix)]
        if not items: continue
        used.update(id(e) for e in items)
        out.append('<div class="group-head">%s</div><ul class="exp-list">%s</ul>'
                   % (label, "".join('<li><a href="%s">%s</a></li>' % (e["url"], html.escape(e["title"])) for e in items)))
    rest = [e for e in exemplars if id(e) not in used]
    if rest:
        out.append('<div class="group-head">Other</div><ul class="exp-list">%s</ul>'
                   % "".join('<li><a href="%s">%s</a></li>' % (e["url"], html.escape(e["title"])) for e in rest))
    return "".join(out)

ICONS = {
 "How to Use This Site": '<circle cx="12" cy="12" r="9"/><path d="M12 8l3 7-7-3z"/>',
 "Picnic at Hanging Rock": '<rect x="3" y="8" width="18" height="12" rx="2"/><path d="M3 8l3-4 4 3 4-3 4 3 3-2v3"/>',
 "The Lottery and Other Stories": '<path d="M4 17a8 8 0 0 1 16 0"/><path d="M8 17a4 4 0 0 1 8 0"/>',
 "Analytical Text Response Essays": '<path d="M14 3l7 7-11 11H3v-7z"/><path d="M12 5l7 7"/>',
 "Creating Texts": '<path d="M4 20l1-5L16 4l4 4L9 19z"/><path d="M14 6l4 4"/>',
 "Analysing Argument": '<path d="M21 12a8 7 0 0 1-8 7 9 9 0 0 1-4-1l-5 2 2-4a7 7 0 0 1-1-4 8 7 0 0 1 8-7 8 7 0 0 1 8 7z"/>',
 "The Exam": '<circle cx="12" cy="13" r="8"/><path d="M12 9v4l3 2M9 2h6"/>',
 "Practice Exams": '<rect x="7" y="3" width="13" height="16" rx="2"/><path d="M4 7v12a2 2 0 0 0 2 2h10"/>',
 "Exam Assessment Criteria": '<rect x="4" y="3" width="16" height="18" rx="2"/><path d="M8 9l2 2 4-4M8 16h8"/>',
 "Exam Checklists": '<rect x="3" y="3" width="18" height="18" rx="3"/><path d="M8 12l3 3 5-6"/>',
 "Key Takeaways from the 2024 Assessment Report": '<path d="M4 20V10M10 20V4M16 20v-8M21 20H3"/>',
 "Key Takeaways from the 2025 Assessment Report": '<path d="M3 17l6-6 4 4 8-8"/><path d="M15 7h6v6"/>',
 "Effectively Studying For Exams": '<path d="M12 5c-2-2-6-2-8 0v13c2-2 6-2 8 0 2-2 6-2 8 0V5c-2-2-6-2-8 0z"/><path d="M12 5v13"/>',
 "Study Tools": '<path d="M13 2L4 14h6l-1 8 9-12h-6z"/>',
}
def icon_svg(title):
    body = ICONS.get(title, '<circle cx="12" cy="12" r="9"/>')
    return ('<span class="card-ico"><svg width="26" height="26" viewBox="0 0 24 24" fill="none" '
            'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round">%s</svg></span>' % body)

BLURB = {
 "How to Use This Site": "Quick orientation: search, sections, practice exams and suggested study routes.",
 "Picnic at Hanging Rock": "Peter Weir's film — scenes, characters, symbols, film techniques and quote banks.",
 "The Lottery and Other Stories": "Shirley Jackson's twelve set stories — summaries, themes, quote banks and a theme grid.",
 "Analytical Text Response Essays": "Planning, structure, and proofreading a text-response essay.",
 "Creating Texts": "Audience, purpose, personal journeys and practice stimuli.",
 "Analysing Argument": "Language analysis — written & visual, sample articles and essays.",
 "The Exam": "Format and strategies for addressing the requirements.",
 "Practice Exams": "Full practice papers and past exams.",
 "Exam Assessment Criteria": "How Sections A, B and C are marked.",
 "Exam Checklists": "Ready-reference checklists for exam day.",
 "Key Takeaways from the 2024 Assessment Report": "What VCAA assessors flagged in 2024, section by section.",
 "Key Takeaways from the 2025 Assessment Report": "What VCAA assessors flagged in 2025 — topic verbs, Framework choices and the interplay discriminator.",
 "Effectively Studying For Exams": "Study habits, schedules, recall and wellbeing.",
}
contents = "".join('<li><a href="%s"><span class="cl-num">%d</span>%s</a></li>'
                   % (it["file"], it["num"], html.escape(it["title"])) for it in nav_items)

def _sec(letter, name, asks, links):
    lis = "".join('<li><a href="%s">%s</a></li>' % (f, t) for f, t in links)
    return ('<section class="exam-sec es-%s" aria-labelledby="sec-%s">'
            '<h2 id="sec-%s"><span class="es-sec">Section %s</span>%s</h2><p class="es-asks">%s</p><ul>%s</ul></section>'
            % (letter.lower(), letter.lower(), letter.lower(), letter, name, asks, lis))

exam_band = "".join([
    _sec("A", "Analytical response to a text",
         "An essay on one of your two texts.",
         [("part-02-picnic-at-hanging-rock.html", "<i>Picnic at Hanging Rock</i>"),
          ("part-03-the-lottery-and-other-stories.html", "<i>The Lottery and Other Stories</i>"),
          ("p02-sequence-and-theme-grid.html", "Picnic sequence and theme grid"),
          ("p03-story-and-theme-grid.html", "Lottery story and theme grid"),
          ("practice-topics.html", "Practice topics and essay timer"),
          ("part-04-analytical-text-response-essays.html", "Writing a text response")]),
    _sec("B", "Creating a text",
         "A piece of your own, built from stimulus material and the Framework of Ideas.",
         [("p05-personal-journeys.html", "Personal journeys"),
          ("p05-practice-stimuli.html", "Practice stimuli"),
          ("p05-section-b-under-exam-conditions.html", "Writing under exam conditions"),
          ("p05-sample-creating-texts-piece-19-20.html", "Sample pieces"),
          ("p05-audience.html", "Audience and purpose")]),
    _sec("C", "Analysis of argument and language",
         "An analysis of an unseen persuasive text and its visuals.",
         [("p06-practice-articles-for-analysis.html", "Practice articles"),
          ("p06-sample-analysing-argument-essays.html", "Sample essays, low to high"),
          ("p06-section-c-from-previous-exams.html", "Section C from previous exams"),
          ("p06-essay-structure.html", "Essay structure"),
          ("p06-analysing-written-language.html", "Analysing written language"),
          ("p06-analysing-visual-language.html", "Analysing visual language")]),
])

before_links = "".join('<li><a href="%s">%s</a></li>' % (f, t) for f, t in [
    ("part-07-the-exam.html", "Exam format and timing"),
    ("part-09-exam-assessment-criteria.html", "How it&rsquo;s marked"),
    ("part-10-exam-checklists.html", "Checklists"),
    ("part-13-key-takeaways-from-the-2025-assessment-report.html", "2025 assessors&rsquo; report"),
    ("part-11-key-takeaways-from-the-2024-assessment-report.html", "2024 assessors&rsquo; report"),
    ("part-08-practice-exams.html", "Practice exams"),
    ("revision-program.html", "Week-by-week revision"),
    ("study-tools.html", "Study tools")])

landing = """
<section class="home-hero">
  <div class="hero-media">
    <img src="assets/img/covers/home-hanging-rock.jpg" width="1280" height="720" alt="Hanging Rock rising above Michael Fitzhubert in a still from the film">
    <header class="home-box">
      <h1 class="home-title">VCE English Exam Preparation Guide</h1>
      <p class="home-meta">For students sitting the English exam in 2027. Three sections, three hours of writing: start with the one you&rsquo;re working on.</p>
      <span id="resume-slot"></span>
    </header>
  </div>
  <p class="hero-credit"><i>Picnic at Hanging Rock</i> (dir. Peter Weir, 1975)</p>
</section>
<div class="exam-band">%s</div>
<section class="before-exam" aria-labelledby="before-h"><h2 id="before-h">Before the exam</h2><ul>%s</ul></section>
<section class="all-parts" aria-labelledby="parts-h"><h2 id="parts-h">All parts of the guide</h2><ol class="parts-list">%s</ol></section>
<div class="site-foot">
  <div class="sf-motto">Sapere aude</div>
  <div class="sf-sub">South Oakleigh College. Compiled by Mr Morlin, version Incipit 9.0.1. This site is provided free and as-is for study purposes, without warranty of any kind. Content is offered in good faith but may contain errors &mdash; check anything high-stakes with your teacher. External links lead to sites not controlled by the author, and no liability is accepted for their content or for any loss arising from use of this site.</div>
</div>
""" % (exam_band, before_links, contents)
open(os.path.join(PUBLIC, "index.html"), "w", encoding="utf-8").write(shell("Home", "", "index.html", landing))

nf = """
<div class="nf-wrap">
  <div class="nf-code">404</div>
  <h1>Page not found</h1>
  <p>That page doesn&rsquo;t exist &mdash; it may have moved when the site was reorganised.</p>
  <p><a class="btn" style="background:var(--accent);color:#fff" href="index.html">Back to the guide</a></p>
  <p style="font-family:var(--sans);font-size:14px;color:var(--muted)">Or use the search box in the sidebar &mdash; it covers every page.</p>
</div>
"""
open(os.path.join(PUBLIC, "404.html"), "w", encoding="utf-8").write(shell("Page not found", "", "404.html", nf))

print("PAGES:", len(all_pages) + 1, "| PARTS:", len(nav_items), "| IMGS:", n_imgs, "| PDFS:", len(copied_pdfs),
      "| SEARCH:", len(search), "| EXEMPLARS:", len(exemplars))
for it in nav_items:
    print(" %02d %-46s %d chapters" % (it["num"], it["title"][:46], len(it["chapters"])))
