import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { OstiumClient } from '@ostium/builder-sdk';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), '..');
const outDir = path.join(repoRoot, 'data', 'raw', 'source_smoke');
fs.mkdirSync(outDir, { recursive: true });

const windows = {
  mar9_10_cluster: ['2026-03-09T00:00:00Z', '2026-03-11T00:00:00Z'],
  apr13_canonical: ['2026-04-13T00:00:00Z', '2026-04-14T00:00:00Z'],
};

function ms(iso) { return new Date(iso).getTime(); }
function safeJson(value) {
  return JSON.stringify(value, (_, v) => typeof v === 'bigint' ? v.toString() : v, 2);
}
function writeJson(name, value) {
  const p = path.join(outDir, name);
  fs.writeFileSync(p, safeJson(value));
  return p;
}
function summarizeFill(f) {
  return {
    pairId: f.pairId,
    pairFrom: f.pairFrom,
    pairTo: f.pairTo,
    side: f.side,
    action: f.action,
    type: f.type,
    px: f.px,
    szi: f.szi,
    collateralUsed: f.collateralUsed,
    fees: f.fees,
    time: f.time,
    hash: f.hash,
  };
}
function matchesPair(pair, symbols) {
  const text = JSON.stringify(pair).toUpperCase();
  return symbols.some(s => text.includes(s));
}

const result = {
  generatedAt: new Date().toISOString(),
  sdk: '@ostium/builder-sdk',
  ok: false,
  pairCandidates: {},
  windows: {},
  errors: [],
  rawFiles: {},
};

try {
  const client = await OstiumClient.createReadOnly();
  result.isReadOnly = client.isReadOnly();

  const pairsResponse = await client.getPairs();
  result.rawFiles.pairs = writeJson('sdk_get_pairs_raw.json', pairsResponse);
  const pairs = Array.isArray(pairsResponse) ? pairsResponse : (pairsResponse.pairs || pairsResponse.data || []);
  result.pairCount = pairs.length;
  result.pairCandidates.CL_USD = pairs.filter(p => matchesPair(p, ['CL-USD', 'CL/USD', 'CRUDE', 'WTI']));
  result.pairCandidates.BRENT_USD = pairs.filter(p => matchesPair(p, ['BRENT-USD', 'BRENT/USD', 'BRENT']));

  const selected = [
    ...result.pairCandidates.CL_USD.map(p => ({ label: 'CL_USD', pair: p })),
    ...result.pairCandidates.BRENT_USD.map(p => ({ label: 'BRENT_USD', pair: p })),
  ];
  result.selectedPairs = selected.map(({ label, pair }) => ({ label, pairId: pair.pairId ?? pair.id, pairFrom: pair.pairFrom, pairTo: pair.pairTo, raw: pair }));

  for (const { label, pair } of selected) {
    const pairId = pair.pairId ?? pair.id;
    for (const [windowName, [startIso, endIso]] of Object.entries(windows)) {
      const key = `${label}_${pairId}_${windowName}`;
      try {
        const fills = await client.getFillsByTime({ user: 'ALL', pairId, startTime: ms(startIso), endTime: ms(endIso), limit: 10000 });
        result.rawFiles[`fills_${key}`] = writeJson(`sdk_get_fills_by_time_${key}.json`, fills);
        const summarized = fills.map(summarizeFill);
        const notional = summarized.reduce((acc, f) => acc + Math.abs(Number(f.px || 0) * Number(f.szi || 0)), 0);
        const openingFees = summarized.reduce((acc, f) => acc + Number(f.fees?.opening || 0), 0);
        result.windows[key] = {
          label, pairId, startIso, endIso,
          fillCount: summarized.length,
          sample: summarized.slice(0, 5),
          pxTimesSizeNotional: notional,
          openingFees,
          actions: summarized.reduce((acc, f) => { acc[f.action || 'unknown'] = (acc[f.action || 'unknown'] || 0) + 1; return acc; }, {}),
          sides: summarized.reduce((acc, f) => { acc[f.side || 'unknown'] = (acc[f.side || 'unknown'] || 0) + 1; return acc; }, {}),
        };
      } catch (err) {
        result.errors.push({ step: 'getFillsByTime', key, message: err?.message, name: err?.name, cause: String(err?.cause || '') });
      }
    }
    try {
      const recent = await client.getFills({ user: 'ALL', pairId, limit: 10 });
      const key = `${label}_${pairId}_recent`;
      result.rawFiles[`fills_${key}`] = writeJson(`sdk_get_fills_recent_${key}.json`, recent);
      result.windows[key] = { fillCount: recent.length, sample: recent.slice(0, 5).map(summarizeFill) };
    } catch (err) {
      result.errors.push({ step: 'getFills', pairId, message: err?.message, name: err?.name, cause: String(err?.cause || '') });
    }
  }
  result.ok = selected.length > 0 && Object.values(result.windows).some(w => w.fillCount > 0);
} catch (err) {
  result.errors.push({ step: 'createReadOnly/getPairs', message: err?.message, name: err?.name, stack: err?.stack?.split('\n').slice(0, 5).join('\n'), cause: String(err?.cause || '') });
}

const summaryPath = writeJson('sdk_activity_smoke_summary.json', result);
console.log(safeJson({ ok: result.ok, pairCount: result.pairCount, selectedPairs: result.selectedPairs, windowKeys: Object.keys(result.windows), errors: result.errors, summaryPath }));
process.exit(result.errors.length && !result.ok ? 2 : 0);
