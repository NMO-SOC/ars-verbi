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
// no Origin (direct visit, curl) or ALLOWED_ORIGINS unset: always refused
assert.equal((await worker.fetch(new Request('https://w.test/'), env, ctx)).status, 403);
assert.equal((await worker.fetch(new Request('https://w.test/'), { ...env, ALLOWED_ORIGINS: undefined }, ctx)).status, 403);
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

// first chat model retired: the next one answers
const realRun = env.AI.run;
env.AI.run = async (model, args) => {
  if (model.includes('llama-3.3')) throw new Error('model not found');
  return realRun(model, args);
};
const fb = await (await call('https://nmo-soc.github.io', 'POST',
  { messages: [{ role: 'user', content: 'STUDENT QUESTION: Again' }] })).json();
assert.equal(fb.choices[0].message.content, 'Answer to: Again');
// first model answers with nothing (as Gemma 4 did): the next one answers
env.AI.run = async (model) => model.includes('llama-3.3') ? { response: '' } : { response: 'Backup answer' };
const em = await (await call('https://nmo-soc.github.io', 'POST', { messages: [{ role: 'user', content: 'x' }] })).json();
assert.equal(em.choices[0].message.content, 'Backup answer');
// OpenAI-style reply with a reasoning block is unwrapped
env.AI.run = async () => ({ choices: [{ message: { content: '<think>hmm</think> Tidy answer' } }] });
const oa = await (await call('https://nmo-soc.github.io', 'POST', { messages: [{ role: 'user', content: 'x' }] })).json();
assert.equal(oa.choices[0].message.content, 'Tidy answer');
// every model failing (e.g. daily allowance spent): an error the page can show
env.AI.run = async () => { throw new Error('allowance spent'); };
const bad = await call('https://nmo-soc.github.io', 'POST', { messages: [{ role: 'user', content: 'x' }] });
assert.equal(bad.status, 502);
assert.equal((await bad.json()).error.message, 'allowance spent');
console.log('worker ok');
