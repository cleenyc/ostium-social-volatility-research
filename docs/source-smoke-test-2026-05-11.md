# Ostium Activity Source Smoke Test — 2026-05-11

## Result

**Green:** free/read-only Ostium SDK activity access works from Railway/Hermes.

Evidence: `@ostium/builder-sdk` `OstiumClient.createReadOnly()` succeeded without private keys; `getPairs()`, `getFillsByTime({ user: "ALL", pairId, ... })`, and `getFills({ user: "ALL", pairId, limit })` returned data.

## Pair mapping

- CL_USD: pairId `7`, `WTI-USD`
- BRENT_USD: pairId `55`, `BRENT-USD`

- Total pairs returned by SDK: 71

## Smoke windows

- `CL_USD_7_mar9_10_cluster`
  - window: 2026-03-09T00:00:00Z → 2026-03-11T00:00:00Z
  - fills: 3798
  - px*szi notional: $388,733,337
  - opening fees: $287,460
  - actions: {'Liquidation': 340, 'StopLoss': 293, 'Open': 1749, 'Close': 1278, 'TakeProfit': 70, 'RemoveCollateral': 68}
  - sides: {'B': 3249, 'S': 549}
- `CL_USD_7_apr13_canonical`
  - window: 2026-04-13T00:00:00Z → 2026-04-14T00:00:00Z
  - fills: 365
  - px*szi notional: $6,555,474
  - opening fees: $5,176
  - actions: {'Open': 189, 'StopLoss': 19, 'Close': 117, 'RemoveCollateral': 27, 'Liquidation': 8, 'TakeProfit': 5}
  - sides: {'B': 280, 'S': 85}
- `BRENT_USD_55_mar9_10_cluster`
  - window: 2026-03-09T00:00:00Z → 2026-03-11T00:00:00Z
  - fills: 0
  - px*szi notional: $0
  - opening fees: $0
  - actions: {}
  - sides: {}
- `BRENT_USD_55_apr13_canonical`
  - window: 2026-04-13T00:00:00Z → 2026-04-14T00:00:00Z
  - fills: 51
  - px*szi notional: $131,568
  - opening fees: $80
  - actions: {'Open': 20, 'Close': 22, 'StopLoss': 3, 'TakeProfit': 2, 'Liquidation': 4}
  - sides: {'B': 34, 'S': 17}

## Raw artifacts

- `fills_BRENT_USD_55_apr13_canonical`: `data/raw/source_smoke/sdk_get_fills_by_time_BRENT_USD_55_apr13_canonical.json`
- `fills_BRENT_USD_55_mar9_10_cluster`: `data/raw/source_smoke/sdk_get_fills_by_time_BRENT_USD_55_mar9_10_cluster.json`
- `fills_BRENT_USD_55_recent`: `data/raw/source_smoke/sdk_get_fills_recent_BRENT_USD_55_recent.json`
- `fills_CL_USD_7_apr13_canonical`: `data/raw/source_smoke/sdk_get_fills_by_time_CL_USD_7_apr13_canonical.json`
- `fills_CL_USD_7_mar9_10_cluster`: `data/raw/source_smoke/sdk_get_fills_by_time_CL_USD_7_mar9_10_cluster.json`
- `fills_CL_USD_7_recent`: `data/raw/source_smoke/sdk_get_fills_recent_CL_USD_7_recent.json`
- `pairs`: `data/raw/source_smoke/sdk_get_pairs_raw.json`

## Notes / caveats

- This is read-only and uses no Dune.
- The smoke script installed/uses `@ostium/builder-sdk` and `viem` via npm.
- `px * szi` has since been validated against `@ostium/builder-sdk`: `Fill.px` is execution price and `Fill.szi` is base-asset size, so `abs(px * szi)` is USD execution notional for WTI/Brent fills.
- Mar 9–10 has large WTI activity but zero Brent fills in this exact smoke window; Apr 13 has both WTI and Brent fills.
- Raw fill samples include public transaction hashes and no secrets.
