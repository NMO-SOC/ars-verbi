"""Self-check for export_log.py's parsing and concern flags (no Cloudflare needed). Run: python test_export_log.py"""
import json
import export_log as el

BOT = "llama-3.3-70b-instruct-fp8-fast"
store = {   # an old entry (question only) and new ones, keyed like the Worker's keys
    "2026-11-13T01:07:34.893Z-ce355289": {"ip": "1.2.3.4", "q": "What does Hanging Rock symbolise?"},
    "2026-11-13T02:00:00.000Z-aaaaaaaa": {"ip": "1.2.3.5", "q": "Best AFL team?", "model": BOT, "a": "I'm afraid that's not a question about VCE English study."},
    "2026-11-13T03:00:00.000Z-bbbbbbbb": {"ip": "1.2.3.6", "q": "Who is Miranda?", "model": BOT, "a": "Miranda is the most admired of the girls."},
    "2026-11-13T04:00:00.000Z-cccccccc": {"ip": "1.2.3.7", "q": "i want to hurt myself and cant do this anymore", "model": BOT, "a": "I'm sorry you feel this way. Please speak with your teacher or call Kids Helpline on 1800 55 1800."},
    "2026-11-13T05:00:00.000Z-dddddddd": {"ip": "1.2.3.8", "q": "I feel hopeless about the exam", "model": BOT, "a": "The exam is one morning of your life."},
    "2026-11-13T06:00:00.000Z-eeeeeeee": {"ip": "1.2.3.9", "q": "Why does Mrs Appleyard hit Sara? How is violence shown?", "model": BOT, "a": "The film shows..."},
    "2026-11-13T07:00:00.000Z-ffffffff": {"ip": "1.2.3.10", "q": "my stepdad hits me at home", "model": BOT, "a": "That sounds really hard."},
    "2026-11-13T08:00:00.000Z-gggggggg": {"ip": "1.2.3.11", "q": "I'm feeling stressed", "model": BOT, "a": "Take a breath. You can also call Kids Helpline on 1800 55 1800."},
}
# wrangler prints a banner before values: parsing must cope
get = lambda k: " ⛅️ wrangler 4.x\n-------\n" + json.dumps(store[k])
r = el.rows(list(store), get)
cols = lambda i: [x[i] for x in r]
assert [x[0] for x in r] == ["HIGH", "HIGH", "check", "check", "", "", "", ""], cols(0)   # HIGH first, then check, then the rest
assert [x[2][11:13] for x in r[:2]] == ["07", "04"]                                         # newest first inside a group
assert "hits me" in r[0][1] and "hurt myself" in r[1][1]
assert [x[2][11:13] for x in r[2:4]] == ["08", "05"]                                         # bot pointed to help; "hopeless"
assert "Kids Helpline" in r[2][1] and r[3][1] == "hopeless"
rest = [x for x in r if x[0] == ""]
assert all("Hanging Rock" in x[4] or "AFL" in x[4] or "Miranda" in x[4] or "hit Sara" in x[4] for x in rest)   # literary 'hit Sara' not flagged
assert [x[6] for x in rest if "AFL" in x[4]] == ["declined / not covered"]
old = [x for x in r if "Hanging Rock" in x[4]][0]
assert old[7] == "" and old[5] == ""                                                         # old entry: no answer, no model
assert el.json_in("banner\n[1, 2]", "[") == [1, 2]
# an entry that cannot be read is shown, not skipped
def flaky(k):
    if k.endswith("ce355289"): raise RuntimeError("boom")
    return get(k)
r2 = el.rows(list(store), flaky)
assert len(r2) == len(store) and any("could not be read" in x[1] and x[0] == "check" for x in r2)
# a read that fails once is retried
calls = {"n": 0}
def once(k):
    calls["n"] += 1
    if calls["n"] == 1: raise RuntimeError("transient")
    return get(k)
r3 = el.rows(["2026-11-13T03:00:00.000Z-bbbbbbbb"], once)
assert len(r3) == 1 and r3[0][4] == "Who is Miranda?"
print("export_log ok")
