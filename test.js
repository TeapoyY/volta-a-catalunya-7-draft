// Volta a Catalunya 7-0 Monte Carlo test
// Extract simulateRace + winProb + pointsForPos from output.html
const fs = require('fs');
const html = fs.readFileSync('/tmp/volta-catalunya-build/output.html', 'utf8');
const m = html.match(/<script>([\s\S]*?)<\/script>/);
if (!m) { console.error('No <script> tag found'); process.exit(1); }
const code = m[1];

// Mock browser environment
const noop = () => {};
const fakeCtx = new Proxy({}, { get: () => noop });
const fakeEl = {
  classList:{add:noop,remove:noop,toggle:noop},
  innerHTML:'', textContent:'', value:'',
  appendChild:noop, querySelectorAll:()=>[], querySelector:()=>null,
  scrollTop:0, scrollHeight:0, scrollIntoView:noop,
  style:{}, dataset:{}, children:[], parentNode:null,
  setAttribute:noop, getAttribute:()=>null, addEventListener:noop,
  removeEventListener:noop, dispatchEvent:noop,
  focus:noop, blur:noop, click:noop,
};
const fakeCanvas = {
  getContext: () => fakeCtx,
  width:480, height:360,
  addEventListener:noop, classList:fakeEl.classList,
};
const fakeDocument = {
  getElementById: (id) => id === 'canvas' ? fakeCanvas : fakeEl,
  querySelectorAll: () => [],
  querySelector: () => null,
  createElement: () => fakeEl,
  body: fakeEl,
  documentElement: fakeEl,
};

global.document = fakeDocument;
global.setTimeout = noop;
global.localStorage = { getItem:()=>null, setItem:noop, removeItem:noop };
global.window = { addEventListener:noop };

// Wrap code in Function and expose key API
const fn = new Function('document', 'window', 'setTimeout', 'localStorage',
  code + '; return { DRIVERS, SCHEDULE, simulateRace, pointsForPos, mulberry32, eraSynergy };');
const api = fn(fakeDocument, global.window, noop, global.localStorage);

console.log(`DRIVERS count: ${api.DRIVERS.length}`);
console.log(`SCHEDULE count: ${api.SCHEDULE.length}`);
console.log(`First 3 drivers:`, api.DRIVERS.slice(0,3).map(d => `${d.name} (era ${d.era}, ${d.pos}, OVR ${d.ovr})`));
console.log(`Schedule:`, api.SCHEDULE.map(s => `${s.stage}. ${s.name} [${s.type}]`));

// Monte Carlo: simulate full 7-stage season across OVR levels
function mulberry32(seed) {
  return function() {
    seed |= 0; seed = seed + 0x6D2B79F5 | 0;
    let t = Math.imul(seed ^ seed >>> 15, 1 | seed);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t;
    return ((t ^ t >>> 14) >>> 0) / 4294967296;
  };
}

console.log('\n=== Monte Carlo 200 seasons × 8 OVR levels ===');
console.log('OVR  | AvgWins/7 | Perfect 7-0 | Min | Max');
console.log('-----|-----------|-------------|-----|-----');

for (const ovr of [70, 75, 80, 85, 88, 90, 95, 99]) {
  let totalWins = 0;
  let perfect = 0;
  let minWins = 99;
  let maxWins = 0;

  for (let seed = 1; seed <= 200; seed++) {
    const r = mulberry32(seed * 1000 + ovr);
    let wins = 0;
    for (let i = 0; i < api.SCHEDULE.length; i++) {
      const race = api.SCHEDULE[i];
      const result = api.simulateRace(ovr, race.type, r);
      if (result.playerPos === 1) wins++;
    }
    totalWins += wins;
    if (wins === api.SCHEDULE.length) perfect++;
    if (wins < minWins) minWins = wins;
    if (wins > maxWins) maxWins = wins;
  }

  const avg = (totalWins / 200).toFixed(2);
  console.log(`OVR ${ovr.toString().padStart(3)} | ${avg.padStart(9)} | ${(perfect/2).toFixed(1).padStart(10)}% | ${minWins.toString().padStart(3)} | ${maxWins.toString().padStart(3)}`);
}

// Single-race win rate check (verify OVR ordering)
console.log('\n=== Single-race win rate check (50 races × OVR) ===');
for (const ovr of [70, 80, 90, 95, 99]) {
  let wins = 0;
  for (let seed = 1; seed <= 50; seed++) {
    const r = mulberry32(seed * 7 + ovr);
    const result = api.simulateRace(ovr, 'mountain', r);  // hardest stage
    if (result.playerPos === 1) wins++;
  }
  console.log(`OVR ${ovr} mountain win rate: ${wins}/50 (${(wins*2)}%)`);
}
