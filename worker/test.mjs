// Self-check for worker.js with a fake Workers AI binding. Run: node worker/test.mjs
import assert from 'node:assert';
import worker from './worker.js';

const logged = [];
const env = {
  ALLOWED_ORIGINS: 'https://nmo-soc.github.io, http://localhost',
  AI: { run: async (model, args) => model.includes('bge')
    ? { data: args.text.map(() => [0.1, 0.2]) }
    : { response: 'Answer to: ' + args.messages[0].content.slice(-5) } },
  LOG: { put: async (k, v) => logged.push(JSON.parse(v)) }
};
const ctx = { waitUntil: p => p };
const call = (origin, method, body) => worker.fetch(new Request('https://w.test/', {
  method, headers: { Origin: origin, 'Content-Type': 'application/json', 'CF-Connecting-IP': '1.2.3.4' },
  body: body && JSON.stringify(body) }), env, ctx);

assert.equal((await call('https://evil.example', 'POST', { embed: true, input: ['x'] })).status, 403);
const pre = await call('https://nmo-soc.github.io', 'OPTIONS');
assert.equal(pre.headers.get('Access-Control-Allow-Origin'), 'https://nmo-soc.github.io');

const emb = await (await call('http://localhost', 'POST', { embed: true, input: ['a', 'b'] })).json();
assert.equal(emb.data.length, 2);
assert.deepEqual(emb.data[0].embedding, [0.1, 0.2]);

const chat = await (await call('https://nmo-soc.github.io', 'POST',
  { messages: [{ role: 'user', content: 'rules... STUDENT QUESTION: Hello' }], max_tokens: 700 })).json();
assert.equal(chat.choices[0].message.content, 'Answer to: Hello');
assert.deepEqual(logged, [{ ip: '1.2.3.4', q: 'Hello' }]);

assert.equal((await call('http://localhost', 'POST', { messages: [] })).status, 400);
console.log('worker ok');
