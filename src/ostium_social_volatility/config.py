from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
SOURCE_SMOKE_DIR = RAW_DIR / "source_smoke"
DOCS_DIR = REPO_ROOT / "docs"

OIL_MARKETS = ("CL-USD", "BRENT-USD")
SMOKE_WINDOWS = {
    "mar9_10_cluster": ("2026-03-09T00:00:00Z", "2026-03-11T00:00:00Z"),
    "apr13_canonical": ("2026-04-13T00:00:00Z", "2026-04-14T00:00:00Z"),
}
