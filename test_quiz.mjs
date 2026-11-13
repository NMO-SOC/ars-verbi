// Self-check for the Technique Quiz: runs the real page script against a fake page, simulating many refreshes.
// Run after build.py:  node test_quiz.mjs
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert';

const html = fs.readFileSync('public/technique-quiz.html', 'utf8');
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]).filter(s => s.includes('QUIZ_TERMS'));
assert.equal(scripts.length, 2, 'data script + quiz script');

function makeEl() {
  const el = { style: {}, textContent: '', handlers: {}, attrs: {}, children: [], classes: new Set(),
    classList: { add: c => el.classes.add(c) },
    addEventListener: (t, f) => { el.handlers[t] = f; },
    setAttribute: (k, v) => { el.attrs[k] = v; }, getAttribute: k => el.attrs[k] || null,
    appendChild: c => { el.children.push(c); }, disabled: false };
  Object.defineProperty(el, 'innerHTML', { set: () => { el.children = []; }, get: () => '' });
  return el;
}
const store = {};   // shared localStorage: survives "refreshes" like the real one

function openPage() {   // one page load
  const els = {};
  const document = {
    getElementById: id => els[id] || (els[id] = makeEl()),
    createElement: () => makeEl(),
    querySelectorAll: () => document.getElementById('qz-opts').children,
  };
  const ctx = { window: {}, document, Math, JSON, Array, localStorage: { getItem: k => (k in store ? store[k] : null), setItem: (k, v) => { store[k] = v; } } };
  vm.createContext(ctx);
  scripts.forEach(s => vm.runInContext(s.replace(/^\s*window\.QUIZ_TERMS/, 'window.QUIZ_TERMS'), ctx));
  return { els, terms: ctx.window.QUIZ_TERMS };
}

// play one round to the end, checking every question; returns the card ids the round used
function playRound(page, expectIds) {
  const { els, terms } = page;
  const seenBefore = JSON.parse(store.quizSeen || '[]').length;
  const ids = JSON.parse(store.quizSeen).slice(-10);
  const termsInRound = new Set();
  for (let q = 0; q < 10; q++) {
    const opts = els['qz-opts'].children;
    const texts = opts.map(b => b.textContent);
    assert.equal(opts.length, 4, 'four options');
    assert.equal(new Set(texts).size, 4, 'options are all different: ' + texts);
    const right = opts.filter(b => b.getAttribute('data-right'));
    assert.equal(right.length, 1, 'exactly one right answer');
    const prompt = els['qz-def'].textContent, kind = els['qz-kind'].textContent;
    const id = ids[q] || '';
    const term = terms.find(t => id.endsWith('|' + t.term));
    // prompts that ask for a technique must not contain its name
    if (/^Which technique/.test(kind)) {
      assert.ok(!prompt.toLowerCase().includes(right[0].textContent.toLowerCase()), 'prompt gives the answer away: ' + prompt + ' -> ' + right[0].textContent);
    }
    assert.ok(prompt.length > 3 && kind.length > 3);
    termsInRound.add(right[0].textContent);
    opts[Math.floor(Math.random() * 4)].handlers.click();     // answer something
    assert.ok(els['qz-more'].textContent.length > 5, 'shows the full explanation after answering');
    if (q < 9) els['qz-next'].handlers.click();
  }
  assert.equal(els['qz-restart'].style.display, '', 'restart offered at the end');
  return ids;
}

// 1. several refreshes: never the same card twice in a row of refreshes
const used = new Set(); let poolText = '';
for (let refresh = 1; refresh <= 12; refresh++) {
  const page = openPage();
  poolText = page.els['qz-pool'].textContent;
  const ids = playRound(page);
  assert.equal(new Set(ids.map(i => i.split('|')[1])).size, 10, 'ten different techniques in a round');
  ids.forEach(id => { assert.ok(!used.has(id), 'card repeated on refresh ' + refresh + ': ' + id); used.add(id); });
}
const total = Number(poolText.match(/^(\d+) cards/)[1]);
assert.ok(total >= 250, 'large pool: ' + total);

// 2. play on until the pool runs out: it must keep working and start a new cycle
let rounds = 12, resets = 0, last = JSON.parse(store.quizSeen).length;
for (; rounds < 80 && resets < 2; rounds++) {
  const page = openPage(); playRound(page);
  const now = JSON.parse(store.quizSeen).length;
  if (now <= last) resets++;
  last = now;
}
assert.ok(resets >= 1, 'a new cycle starts once the pool is used up');
assert.ok(rounds > 20, 'at least 20 rounds before the first repeat (got ' + rounds + ')');

// 3. no storage available (private window): still works
store.quizSeen = '{bad json';
const p = openPage(); playRound(p);
console.log('quiz ok: ' + total + ' cards, 12 refreshes with no repeat, ' + rounds + ' rounds played, new cycle starts when the pool is used up');
