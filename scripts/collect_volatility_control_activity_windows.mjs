import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { OstiumClient } from '@ostium/builder-sdk';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), '..');

function argValue(name, fallback) {
  const idx = process.argv.indexOf(name);
  return idx >= 0 && process.argv[idx + 1] ? process.argv[idx + 1] : fallback;
}
function resolveRepoPath(value) { return path.isAbsolute(value) ? value : path.join(repoRoot, value); }
function stripQuotes(value) { return value.replace(/^['"]|['"]$/g, ''); }
function readStudyConfig(studyPath) {
  const text = fs.readFileSync(studyPath, 'utf8');
  const lines = text.split(/\r?\n/);
  const get = (key) => {
    const escaped = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const re = new RegExp(`^\\s*${escaped}:\\s*(.+?)\\s*(?:#.*)?$`);
    for (const line of lines) {
      const m = line.match(re);
      if (m) return stripQuotes(m[1].trim());
    }
    return null;
  };
  const markets = [];
  let cur = null;
  for (const raw of lines) {
    const line = raw.replace(/#.*$/, '');
    const label = line.match(/^\s*-\s+label:\s*(.+?)\s*$/);
    if (label) {
      cur = { label: stripQuotes(label[1].trim()) };
      markets.push(cur);
      continue;
    }
    if (!cur) continue;
    const symbol = line.match(/^\s+ostium_builder_symbol:\s*(.+?)\s*$/);
    if (symbol) cur.symbol = stripQuotes(symbol[1].trim());
    const pairId = line.match(/^\s+ostium_pair_id:\s*(\d+)\s*$/);
    if (pairId) cur.pairId = Number(pairId[1]);
  }
  return {
    outPath: resolveRepoPath(get('volatility_control_activity_windows') || 'data/raw/volatility_control_activity_windows/volatility_control_activity_windows_summary.json'),
    marketOhlcDir: resolveRepoPath(get('market_ohlc_dir') || 'data/raw/market_ohlc'),
    pairs: markets.filter(m => m.label && m.symbol && Number.isFinite(m.pairId)),
  };
}

const studyPath = resolveRepoPath(argValue('--study', 'configs/study.oil-hormuz.example.yaml'));
const config = readStudyConfig(studyPath);
const outPath = config.outPath;
const outDir = path.dirname(outPath);
fs.mkdirSync(outDir, { recursive: true });
const pairs = config.pairs.map(m => ({
  label: m.label,
  pairId: m.pairId,
  symbol: m.symbol,
  ohlc: path.join(config.marketOhlcDir, `${m.symbol}_daily_ohlc.csv`),
}));
if (!pairs.length) throw new Error(`No configured markets found in ${studyPath}`);

function safeJson(value) { return JSON.stringify(value, (_, v) => typeof v === 'bigint' ? v.toString() : v, 2); }
function ms(d) { return new Date(`${d}T00:00:00Z`).getTime(); }
function iso(msValue) { return new Date(msValue).toISOString(); }
function isoDate(msValue) { return new Date(msValue).toISOString().slice(0, 10); }
function addDays(d, days) { return isoDate(ms(d) + days * 24 * 60 * 60 * 1000); }
function readDates(csvPath) {
  const text = fs.readFileSync(csvPath, 'utf8').trim();
  const lines = text.split(/\r?\n/);
  const headers = lines[0].split(',');
  const dateIdx = headers.indexOf('date');
  return lines.slice(1).map(line => line.split(',')[dateIdx]).filter(Boolean).sort();
}
function summarize(fills) {
  let notionalUsd = 0;
  let openingFeesUsd = 0;
  let totalFeesUsd = 0;
  const actions = {};
  const sides = {};
  for (const f of fills) {
    notionalUsd += Math.abs(Number(f.px || 0) * Number(f.szi || 0));
    const fees = f.fees || {};
    openingFeesUsd += Number(fees.opening || 0);
    for (const v of Object.values(fees)) totalFeesUsd += Number(v || 0);
    actions[f.action || 'unknown'] = (actions[f.action || 'unknown'] || 0) + 1;
    sides[f.side || 'unknown'] = (sides[f.side || 'unknown'] || 0) + 1;
  }
  return { fillCount: fills.length, notionalUsd, openingFeesUsd, totalFeesUsd, actions, sides };
}

const generatedAt = new Date().toISOString();
const nowDate = generatedAt.slice(0, 10);
const result = {
  generatedAt,
  studyPath,
  methodology: {
    purpose: 'Volatility-day control windows for comparing high-volatility days with oil posts vs high-volatility days without oil posts.',
    baseline: '30 calendar days before market date, end-exclusive',
    eventWindow: 'market date through two calendar days after, start-inclusive/end-exclusive',
  },
  pairs: pairs.map(({ label, pairId, symbol }) => ({ label, pairId, symbol })),
  datesByMarket: {},
  windows: [],
  errors: [],
};

async function runLimited(items, limit, worker) {
  const executing = new Set();
  const results = [];
  for (const item of items) {
    const p = Promise.resolve().then(() => worker(item));
    results.push(p);
    executing.add(p);
    p.finally(() => executing.delete(p));
    if (executing.size >= limit) await Promise.race(executing);
  }
  return Promise.all(results);
}

const jobs = [];
for (const pair of pairs) {
  const dates = readDates(pair.ohlc);
  result.datesByMarket[pair.label] = dates;
  for (const date of dates) {
    const segments = [
      { segment: 'baseline30', start: addDays(date, -30), end: date, days: 30 },
      { segment: 'event0_2', start: date, end: addDays(date, 3), days: 3 },
    ];
    for (const seg of segments) jobs.push({ date, pair, seg });
  }
}

const client = await OstiumClient.createReadOnly();
await runLimited(jobs, 8, async ({ date, pair, seg }) => {
  try {
    const startTime = ms(seg.start);
    const endTime = ms(seg.end);
    const fills = await client.getFillsByTime({ user: 'ALL', pairId: pair.pairId, startTime, endTime, limit: 50000 });
    result.windows.push({
      date,
      segment: seg.segment,
      start: iso(startTime),
      end: iso(endTime),
      days: seg.days,
      isPartial: isoDate(endTime) > nowDate,
      label: pair.label,
      pairId: pair.pairId,
      symbol: pair.symbol,
      ...summarize(fills),
    });
  } catch (err) {
    result.errors.push({ date, segment: seg.segment, pair: { label: pair.label, pairId: pair.pairId }, message: err?.message, name: err?.name, cause: String(err?.cause || '') });
  }
});

result.windows.sort((a, b) => `${a.label}:${a.date}:${a.segment}`.localeCompare(`${b.label}:${b.date}:${b.segment}`));
fs.writeFileSync(outPath, safeJson(result));
console.log(safeJson({ ok: result.errors.length === 0, outPath, markets: Object.fromEntries(Object.entries(result.datesByMarket).map(([k, v]) => [k, v.length])), windowCount: result.windows.length, errors: result.errors.slice(0, 5) }));
process.exit(result.errors.length ? 2 : 0);
