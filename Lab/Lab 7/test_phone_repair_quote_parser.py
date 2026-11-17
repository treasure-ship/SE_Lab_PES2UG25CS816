from hypothesis import given, strategies as st
from phone_repair_quote_parser import mask_imei, parse_parts_order, parse_model


@given(st.text() | st.none())
def test_mask_imei_no_crash(s):
    try:
        result = mask_imei(s)
    except Exception as e:
        assert False, f"mask_imei crashed with: {e!r} for input {s!r}"
    # Output must be a string and never longer than the cleaned input
    assert isinstance(result, str)
    if isinstance(s, str):
        cleaned = s.replace('-', '').replace(' ', '')
        assert len(result) <= len(cleaned)


@given(st.text() | st.none())
def test_parse_parts_order_no_crash(s):
    try:
        result = parse_parts_order(s)
    except Exception as e:
        assert False, f"parse_parts_order crashed with: {e!r} for input {s!r}"
    # Output must be a {str: int} dictionary with positive quantities
    assert isinstance(result, dict)
    for part, qty in result.items():
        assert isinstance(part, str) and part != ""
        assert isinstance(qty, int) and qty > 0


@given(st.text() | st.none())
def test_parse_model_no_crash(s):
    try:
        result = parse_model(s)
    except Exception as e:
        assert False, f"parse_model crashed with: {e!r} for input {s!r}"
    # Output must always be a (brand, model) tuple of strings
    assert isinstance(result, tuple) and len(result) == 2
    assert all(isinstance(x, str) for x in result)