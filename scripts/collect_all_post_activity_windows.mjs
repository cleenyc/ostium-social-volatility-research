import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { OstiumClient } from '@ostium/builder-sdk';

const __filename = fileURLToPath(import.meta.url);
const repoRoot = path.resolve(path.dirname(__filename), '..');
const sourcePosts = path.join(repoRoot, 'data', 'raw', 'social', 'x_ostium_oil_90d.json');
const outDir = path.join(repoRoot, 'data', 'raw', 'all_post_activity_windows');
fs.mkdirSync(outDir, { recursive: true });

const pairs = [
  { label: 'WTI', pairId: 7, symbol: 'WTI-USD' },
  { label: 'BRENT', pairId: 55, symbol: 'BRENT-USD' },
];

function safeJson(value) { return JSON.stringify(value, (_, v) => typeof v === 'bigint' ? v.toString() : v, 2); }
function ms(d) { return new Date(`${d}T00:00:00Z`).getTime(); }
function isoDate(msValue) { return new Date(msValue).toISOString().slice(0, 10); }
function addDays(d, days) { return isoDate(ms(d) + days * 24 * 60 * 60 * 1000); }
function classifyPost(p) {
  const text = p.text || '';
  if (text.startsWith('RT @')) return 'retweet';
  if ((p.conversation_id && p.conversation_id !== p.id) || text.startsWith('@')) return 'reply';
  return 'original';
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
  return {
    fillCount: fills.length,
    notionalUsd,
    openingFeesUsd,
    totalFeesUsd,
    actions,
    sides,
    sample: fills.slice(0, 5).map(f => ({
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
    })),
  };
}

const postsRaw = JSON.parse(fs.readFileSync(sourcePosts, 'utf8')).data || [];
const posts = postsRaw.map(p => ({ id: p.id, created_at: p.created_at, date: p.created_at.slice(0, 10), text: p.text, conversation_id: p.conversation_id, post_type: classifyPost(p), public_metrics: p.public_metrics || {} }));
const dates = [...new Set(posts.map(p => p.date))].sort();
const generatedAt = new Date().toISOString();
const nowDate = generatedAt.slice(0, 10);
const result = { generatedAt, sourcePosts, pairs, postCount: posts.length, uniqueDates: dates, posts, windows: [], errors: [] };

const client = await OstiumClient.createReadOnly();
for (const date of dates) {
  const segments = [
    { segment: 'pre7', start: addDays(date, -7), end: date, days: 7 },
    { segment: 'event', start: date, end: addDays(date, 1), days: 1 },
    { segment: 'post7', start: addDays(date, 1), end: addDays(date, 8), days: 7 },
  ];
  for (const pair of pairs) {
    for (const seg of segments) {
      try {
        const fills = await client.getFillsByTime({ user: 'ALL', pairId: pair.pairId, startTime: ms(seg.start), endTime: ms(seg.end), limit: 50000 });
        const summary = summarize(fills);
        result.windows.push({
          date,
          segment: seg.segment,
          start: `${seg.start}T00:00:00Z`,
          end: `${seg.end}T00:00:00Z`,
          days: seg.days,
          isPartial: seg.end > nowDate,
          ...pair,
          ...summary,
        });
      } catch (err) {
        result.errors.push({ date, segment: seg.segment, pair, message: err?.message, name: err?.name, cause: String(err?.cause || '') });
      }
    }
  }
}
const outPath = path.join(outDir, 'all_post_activity_windows_summary.json');
fs.writeFileSync(outPath, safeJson(result));
console.log(safeJson({ ok: result.errors.length === 0, outPath, postCount: result.postCount, uniqueDateCount: dates.length, windowCount: result.windows.length, errors: result.errors.slice(0, 5) }));
process.exit(result.errors.length ? 2 : 0);
