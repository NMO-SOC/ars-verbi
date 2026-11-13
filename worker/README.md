# Ask Appleyard: Cloudflare setup

The site is static, so the AI calls go through this Cloudflare Worker. It uses
Workers AI (Cloudflare's own models), so there is no API key to store. Ask
Appleyard stays hidden on the site until `AA_WORKER` is set in `build.py`.

Last year's Worker (`jolly-waterfall-d01a…workers.dev`) no longer exists
(it returns Cloudflare error 1042), so this is a fresh one.

## One-off setup

1. **Log in** (opens a browser): `npx wrangler login`
2. **Create the question log** (the chat page tells students questions are logged):
   `npx wrangler kv namespace create LOG`
   and paste the `id` it prints into `wrangler.toml` in place of `PASTE_KV_ID_HERE`.
3. **Deploy**, from this `worker/` folder: `npx wrangler deploy`
   It prints the Worker URL, e.g. `https://ask-appleyard.<subdomain>.workers.dev`.
4. **Check it** (should print a JSON `data` array):
   `curl -X POST <url> -H "Origin: http://localhost" -H "Content-Type: application/json" -d "{\"embed\":true,\"input\":[\"test\"]}"`

## Switch it on in the site

1. In `build.py`, set `AA_WORKER = "<url>/"`, and `AA_EXAM` to the 2027 exam
   start once VCAA publishes it (e.g. `"2027-10-26T09:00"`).
2. `python build.py`
3. `powershell -ExecutionPolicy Bypass -File make-embeddings.ps1 -Worker <url>/`
4. Test locally: `python -m http.server 8000 -d public`, open
   `http://localhost:8000/ask-appleyard.html` and ask a question.
5. Ship it (branch, PR, merge). GitHub Pages redeploys.

## After every content change

Re-run `build.py`, then `make-embeddings.ps1`, and bump `AA_V` in `build.py`
so browsers fetch the new index. Without the embeddings file the bot still
works on keyword search alone, just less well on paraphrased questions.

## Running it

- **Cost:** stay on the Workers Free plan. Its daily AI allowance is the hard
  ceiling: when a busy day spends it, the bot shows an error until 00:00 UTC
  (10am Melbourne, 11am in daylight saving). On a paid plan the same traffic is billed instead.
- **Logs:** `npx wrangler kv key list --binding LOG`, or the KV page in the
  Cloudflare dashboard. Entries expire after 180 days.
- **Model:** `CHAT_MODEL` in `worker.js`. Check the Workers AI model list if
  Cloudflare retires it.
- **New site address** (e.g. the school intranet): add its origin to
  `ALLOWED_ORIGINS` in `wrangler.toml` and redeploy. The school web filter
  must also allow `workers.dev`.
- **Self-check** after editing `worker.js`: `node worker/test.mjs`
