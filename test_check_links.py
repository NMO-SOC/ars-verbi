"""Self-check for check_links.py. Run: python test_check_links.py"""
import http.server, os, tempfile, threading
import check_links as cl

class H(http.server.BaseHTTPRequestHandler):
    def do_HEAD(self):
        code = {"/ok": 200, "/gone": 404, "/nohead": 405, "/blocked": 403}.get(self.path, 404)
        self.send_response(code); self.end_headers()
    def do_GET(self):
        self.send_response(200 if self.path == "/nohead" else {"/ok": 200, "/blocked": 403}.get(self.path, 404)); self.end_headers()
    def log_message(self, *a): pass

srv = http.server.HTTPServer(("127.0.0.1", 0), H); threading.Thread(target=srv.serve_forever, daemon=True).start()
base = "http://127.0.0.1:%d" % srv.server_port
assert cl.check_external(base + "/ok")[0] == "ok"
assert cl.check_external(base + "/gone") == ("broken", "HTTP 404")
assert cl.check_external(base + "/nohead")[0] == "ok"          # HEAD refused, GET works
assert cl.check_external(base + "/blocked")[0] == "blocked"
assert cl.check_external("http://127.0.0.1:1/x")[0] in ("broken", "unreachable")   # nothing listening

with tempfile.TemporaryDirectory() as d:
    w = lambda n, s: open(os.path.join(d, n), "w", encoding="utf-8").write(s)
    w("a.html", '<h2 id="top">T</h2><a href="b.html">ok</a><a href="b.html#sec">ok</a><a href="b.html#nope">bad anchor</a>'
                '<a href="missing.html">bad file</a><a href="#top">self ok</a><a href="#ghost">self bad</a>'
                '<a href="mailto:x@y.z">m</a><a href="https://example.com/x">ext</a>')
    w("b.html", '<h2 id="sec">S</h2>')
    got = {(p, h) for p, h, _ in cl.check_internal(d, cl.read_site(d))}
    assert got == {("a.html", "b.html#nope"), ("a.html", "missing.html"), ("a.html", "#ghost")}, got
    assert cl.main(d, offline=True) == 1
    w("a.html", '<a href="b.html#sec">ok</a>'); assert cl.main(d, offline=True) == 0
print("check_links ok")
