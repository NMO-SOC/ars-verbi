// Ask Appleyard proxy. The site sends {embed: true, input: [...]} or {messages, max_tokens};
// this answers in the OpenAI-style shape ask-appleyard.html reads. Runs on Workers AI,
// so there is no API key anywhere.
// ponytail: no per-user rate limit; the Workers Free plan's daily AI allowance is the ceiling
// (it renews at 00:00 UTC). Add a Rate Limiting binding if one class burns it.
const CHAT_MODEL = '@cf/meta/llama-3.3-70b-instruct-fp8-fast';
const EMBED_MODEL = '@cf/baai/bge-base-en-v1.5'; // 768 dimensions, as make-embeddings.ps1 expects

export default {
  async fetch(req, env, ctx) {
    const origin = req.headers.get('Origin') || '';
    const allowed = (env.ALLOWED_ORIGINS || '').split(',').map(s => s.trim()).filter(Boolean);
    if (!allowed.includes(origin)) return new Response('Forbidden', { status: 403 });
    const cors = { 'Access-Control-Allow-Origin': origin, 'Access-Control-Allow-Methods': 'POST, OPTIONS',
                   'Access-Control-Allow-Headers': 'Content-Type', 'Vary': 'Origin' };
    const reply = (obj, status = 200) =>
      new Response(JSON.stringify(obj), { status, headers: { ...cors, 'Content-Type': 'application/json' } });
    if (req.method === 'OPTIONS') return new Response(null, { headers: cors });
    if (req.method !== 'POST') return reply({ error: { message: 'POST only' } }, 405);

    let body;
    try { body = await req.json(); } catch { return reply({ error: { message: 'Bad request' } }, 400); }

    try {
      if (body.embed) {
        const input = Array.isArray(body.input) ? body.input.slice(0, 100).map(t => String(t).slice(0, 2000)) : [];
        if (!input.length) return reply({ error: { message: 'Nothing to embed' } }, 400);
        const r = await env.AI.run(EMBED_MODEL, { text: input });
        return reply({ data: r.data.map(embedding => ({ embedding })) });
      }

      const content = String((body.messages && body.messages[0] && body.messages[0].content) || '').slice(0, 60000);
      if (!content) return reply({ error: { message: 'Empty question' } }, 400);
      if (env.LOG) {
        // the page discloses this: question + network address, kept 180 days
        const q = content.split('STUDENT QUESTION: ').pop().slice(0, 1000);
        const ip = req.headers.get('CF-Connecting-IP') || '';
        ctx.waitUntil(env.LOG.put(new Date().toISOString() + '-' + crypto.randomUUID().slice(0, 8),
          JSON.stringify({ ip, q }), { expirationTtl: 180 * 86400 }));
      }
      const r = await env.AI.run(CHAT_MODEL, {
        messages: [{ role: 'user', content }],
        max_tokens: Math.min(Number(body.max_tokens) || 700, 1000)
      });
      return reply({ choices: [{ message: { content: r.response || '' } }] });
    } catch (e) {
      return reply({ error: { message: String((e && e.message) || e).slice(0, 200) } }, 502);
    }
  }
};
