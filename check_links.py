"""Find dead links in the built site (public/): outgoing links, internal pages, and #section anchors.

Usage: python check_links.py            (checks everything; exit code 1 if anything is broken)
       python check_links.py --offline  (internal links and anchors only, no network)
Run after build.py, before shipping. Standard library only.

Results: BROKEN (404/410/DNS failure/refused) and UNREACHABLE (timeout) need a look. BLOCKED (403/429/999)
means the site refuses automated checks (Studocu often does): open those once in a browser instead.
"""
import os, re, sys, threading, urllib.request, urllib.error
from html.parser import HTMLParser
from concurrent.futures import ThreadPoolExecutor
from urllib.parse import urldefrag, urljoin, urlparse, unquote

UA = "ars-verbi-link-check/1.0 (+https://github.com/NMO-SOC/ars-verbi)"
BLOCKED = {401, 403, 429, 999}

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.links, self.ids = [], set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"): self.ids.add(a["id"])
        if tag == "a" and a.get("name"): self.ids.add(a["name"])
        if tag == "a" and a.get("href"): self.links.append(a["href"].strip())

def read_site(public):
    pages = {}
    for name in sorted(os.listdir(public)):
        if name.endswith(".html") and not name.startswith("_"):
            p = Page(); p.feed(open(os.path.join(public, name), encoding="utf-8", errors="replace").read())
            pages[name] = p
    return pages

def check_internal(public, pages):
    """[(page, href, problem)] for relative links whose file or #anchor does not exist."""
    bad = []
    for name, pg in pages.items():
        for href in pg.links:
            if re.match(r"^(https?:|mailto:|tel:|javascript:|data:|//)", href, re.I): continue
            target, frag = urldefrag(href)
            path = unquote(urlparse(target).path) or name
            full = os.path.normpath(os.path.join(public, os.path.dirname(name), path)) if path != name else os.path.join(public, name)
            if not os.path.exists(full):
                bad.append((name, href, "file not found")); continue
            if frag and full.endswith(".html"):
                tgt = pages.get(os.path.relpath(full, public).replace(os.sep, "/"))
                if tgt is not None and unquote(frag) not in tgt.ids:
                    bad.append((name, href, "#%s not on that page" % frag))
    return bad

def check_external(url, timeout=15):
    """('ok'|'blocked'|'broken'|'unreachable', detail)"""
    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(url, method=method, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return "ok", str(r.status)
        except urllib.error.HTTPError as e:
            if method == "HEAD" and e.code in (400, 403, 404, 405, 501): continue   # some servers reject HEAD
            return ("blocked" if e.code in BLOCKED else "broken"), "HTTP %d" % e.code
        except urllib.error.URLError as e:
            return ("unreachable" if "timed out" in str(e.reason) else "broken"), str(e.reason)[:80]
        except Exception as e:
            return "unreachable", type(e).__name__
    return "broken", "HTTP error"

def main(public="public", offline=False):
    pages = read_site(public)
    problems = check_internal(public, pages)
    ext = {}
    for name, pg in pages.items():
        for href in pg.links:
            if re.match(r"^https?://", href, re.I): ext.setdefault(urldefrag(href)[0], set()).add(name)
    results = {}
    if not offline:
        with ThreadPoolExecutor(max_workers=12) as ex:
            for url, res in zip(ext, ex.map(check_external, ext)): results[url] = res
    print("%d pages, %d internal problems, %d outgoing links%s" % (len(pages), len(problems), len(ext), " (not checked)" if offline else ""))
    for name, href, why in problems: print("  INTERNAL  %s -> %s  (%s)" % (name, href, why))
    for kind in ("broken", "unreachable", "blocked"):
        rows = [(u, d) for u, (k, d) in results.items() if k == kind]
        if rows: print("\n%s (%d)" % (kind.upper(), len(rows)))
        for u, d in sorted(rows):
            where = sorted(ext[u]); print("  %s  [%s]\n      on: %s%s" % (u, d, ", ".join(where[:3]), " +%d more" % (len(where) - 3) if len(where) > 3 else ""))
    bad = len(problems) + sum(1 for k, _ in results.values() if k in ("broken", "unreachable"))
    if not bad: print("\nNo broken links found.")
    return 1 if bad else 0

if __name__ == "__main__":
    sys.exit(main(offline="--offline" in sys.argv))
