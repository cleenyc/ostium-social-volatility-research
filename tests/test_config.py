from ostium_social_volatility.config import OIL_MARKETS, SMOKE_WINDOWS


def test_oil_markets():
    assert "CL-USD" in OIL_MARKETS
    assert "BRENT-USD" in OIL_MARKETS


def test_smoke_windows():
    assert "mar9_10_cluster" in SMOKE_WINDOWS
    assert "apr13_canonical" in SMOKE_WINDOWS
