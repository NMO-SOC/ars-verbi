"""Self-check for export_log.py's parsing (no Cloudflare needed). Run: python test_export_log.py"""
import json
import export_log as el

store = {   # an old entry (question only) and new ones, keyed like the Worker's keys
    "2026-11-13T01:07:34.893Z-ce355289": {"ip": "1.2.3.4", "q": "What does Hanging Rock symbolise?"},
    "2026-11-13T02:00:00.000Z-aaaaaaaa": {"ip": "1.2.3.5", "q": "Best AFL team?", "model": "llama-3.3-70b-instruct-fp8-fast",
                                          "a": "I'm afraid that's not a question about VCE English study."},
    "2026-11-13T03:00:00.000Z-bbbbbbbb": {"ip": "1.2.3.6", "q": "Who is Miranda?", "model": "llama-3.3-70b-instruct-fp8-fast",
                                          "a": "Miranda is the most admired of the girls."},
}
# wrangler prints a banner before values: parsing must cope
get = lambda k: " ⛅️ wrangler 4.x\n-------\n" + json.dumps(store[k])
r = el.rows(list(store), get)
assert [x[0] for x in r] == ["2026-11-13T03:00:00.000Z", "2026-11-13T02:00:00.000Z", "2026-11-13T01:07:34.893Z"]   # newest first
assert [x[4] for x in r] == ["", "declined / not covered", ""]
assert r[2][5] == "" and r[2][3] == ""                                    # old entry: no answer, no model
assert el.json_in("banner\n[1, 2]", "[") == [1, 2]
print("export_log ok")
