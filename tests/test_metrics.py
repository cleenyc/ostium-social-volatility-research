from ostium_social_volatility.metrics import engagement_count, fill_notional, is_oil_text, oil_categories, pct_change, post_type, summarize_fills


def test_engagement_count():
    assert engagement_count({"retweet_count": 1, "reply_count": 2, "like_count": 3, "quote_count": 4, "bookmark_count": 5}) == 15


def test_is_oil_text():
    assert is_oil_text("Hormuz blockade and Brent oil shock")
    assert not is_oil_text("Gateway to global markets")


def test_post_type():
    assert post_type({"id": "1", "conversation_id": "1", "text": "BRENT OIL LIVE"}) == "original"
    assert post_type({"id": "2", "conversation_id": "1", "text": "@path_taha 66% fee reduction for oil"}) == "reply"
    assert post_type({"id": "3", "conversation_id": "3", "text": "RT @foo oil"}) == "retweet"


def test_oil_categories():
    assert oil_categories("Hormuz blockade live, trade Brent and WTI oil") == ["hormuz", "brent", "wti_cl", "oil"]


def test_fill_summary():
    fills = [
        {"px": "10", "szi": "2", "fees": {"opening": "1", "rollover": "0.5"}, "action": "Open", "side": "B"},
        {"px": "5", "szi": "-3", "fees": {"opening": "0", "builder": "2"}, "action": "Close", "side": "S"},
    ]
    s = summarize_fills(fills)
    assert fill_notional(fills[0]) == 20
    assert s["fill_count"] == 2
    assert s["notional_usd"] == 35
    assert s["opening_fees_usd"] == 1
    assert s["total_fees_usd"] == 3.5
    assert s["actions"] == {"Open": 1, "Close": 1}


def test_pct_change():
    assert pct_change(150, 100) == 50
    assert pct_change(1, 0) is None
