import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { OstiumClient } from '@ostium/builder-sdk';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), '..');
const outDir = path.join(repoRoot, 'data', 'raw', 'activity_windows');
fs.mkdirSync(outDir, { recursive: true });

const pairs = [
  { label: 'WTI', pairId: 7, symbol: 'WTI-USD' },
  { label: 'BRENT', pairId: 55, symbol: 'BRENT-USD' },
];
const windows = [
  { event: 'apr13_canonical', segment: 'pre7', start: '2026-04-06T00:00:00Z', end: '2026-04-13T00:00:00Z' },
  { event: 'apr13_canonical', segment: 'event', start: '2026-04-13T00:00:00Z', end: '2026-04-14T00:00:00Z' },
  { event: 'apr13_canonical', segment: 'post7', start: '2026-04-14T00:00:00Z', end: '2026-04-21T00:00:00Z' },
  { event: 'mar9_10_cluster', segment: 'pre7', start: '2026-03-02T00:00:00Z', end: '2026-03-09T00:00:00Z' },
  { event: 'mar9_10_cluster', segment: 'event', start: '2026-03-09T00:00:00Z', end: '2026-03-11T00:00:00Z' },
  { event: 'mar9_10_cluster', segment: 'post7', start: '2026-03-11T00:00:00Z', end: '2026-03-18T00:00:00Z' },
];

function ms(iso) { return new Date(iso).getTime(); }
function safeJson(value) { return JSON.stringify(value, (_, v) => typeof v === 'bigint' ? v.toString() : v, 2); }
function fileSlug(...parts) { return parts.join('_').replace(/[^a-zA-Z0-9_\-]/g, '_'); }
function summarize(fills) {
  let notional = 0;
  let openingFees = 0;
  let totalFees = 0;
  const actions = {};
  const sides = {};
  for (const f of fills) {
    notional += Math.abs(Number(f.px || 0) * Number(f.szi || 0));
    const fees = f.fees || {};
    openingFees += Number(fees.opening || 0);
    for (const v of Object.values(fees)) totalFees += Number(v || 0);
    actions[f.action || 'unknown'] = (actions[f.action || 'unknown'] || 0) + 1;
    sides[f.side || 'unknown'] = (sides[f.side || 'unknown'] || 0) + 1;
  }
  return { fillCount: fills.length, notionalUsd: notional, openingFeesUsd: openingFees, totalFeesUsd: totalFees, actions, sides };
}

const result = { generatedAt: new Date().toISOString(), ok: false, pairs, windows: [], errors: [] };
try {
  const client = await OstiumClient.createReadOnly();
  for (const pair of pairs) {
    for (const win of windows) {
      const slug = fileSlug(pair.label, pair.pairId, win.event, win.segment);
      try {
        const fills = await client.getFillsByTime({
          user: 'ALL',
          pairId: pair.pairId,
          startTime: ms(win.start),
          endTime: ms(win.end),
          limit: 50000,
        });
        const rawPath = path.join(outDir, `${slug}.json`);
        fs.writeFileSync(rawPath, safeJson(fills));
        result.windows.push({ ...win, ...pair, rawPath, ...summarize(fills) });
      } catch (err) {
        result.errors.push({ pair, window: win, message: err?.message, name: err?.name, cause: String(err?.cause || '') });
      }
    }
  }
  result.ok = result.errors.length === 0 && result.windows.some(w => w.fillCount > 0);
} catch (err) {
  result.errors.push({ step: 'createReadOnly', message: err?.message, name: err?.name, cause: String(err?.cause || '') });
}
const summaryPath = path.join(outDir, 'activity_windows_summary.json');
fs.writeFileSync(summaryPath, safeJson(result));
console.log(safeJson({ ok: result.ok, summaryPath, windowCount: result.windows.length, errors: result.errors, windows: result.windows.map(w => ({ event: w.event, segment: w.segment, label: w.label, fillCount: w.fillCount, notionalUsd: Math.round(w.notionalUsd), openingFeesUsd: Math.round(w.openingFeesUsd) })) }));
process.exit(result.ok ? 0 : 2);
