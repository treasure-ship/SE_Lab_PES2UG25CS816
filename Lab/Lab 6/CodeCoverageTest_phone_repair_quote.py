import pytest
from phone_repair_quote import repair_quote, repair_days, trade_in_value


# ---------- Starter tests ----------
def test_budget_screen():
    assert repair_quote("screen", "budget", False, False) == 4600


def test_in_stock_quick():
    assert repair_days("battery", True, 2) == 1


# ---------- repair_quote ----------
def test_unknown_part():
    with pytest.raises(ValueError):
        repair_quote("speaker", "budget", False, False)


def test_unknown_brand_tier():
    with pytest.raises(ValueError):
        repair_quote("screen", "premium", False, False)


def test_flagship_battery_under_warranty_express():
    # cost 0 (warranty) + labour 300 + express 500
    assert repair_quote("battery", "flagship", True, True) == 800


# ---------- repair_days ----------
def test_no_technician_screen_out_of_stock():
    # 3 + 5
    assert repair_days("screen", False, 0) == 8


# ---------- trade_in_value ----------
def test_trade_in_invalid_input():
    with pytest.raises(ValueError):
        trade_in_value(0, 10, False)


def test_trade_in_too_old():
    assert trade_in_value(10000, 60, False) == 0


def test_trade_in_new_phone_cracked():
    # 60% of 10000 = 6000, halved = 3000
    assert trade_in_value(10000, 6, True) == 3000


def test_trade_in_one_to_two_years():
    assert trade_in_value(10000, 18, False) == 4000


def test_trade_in_older_phone():
    assert trade_in_value(10000, 36, False) == 2000