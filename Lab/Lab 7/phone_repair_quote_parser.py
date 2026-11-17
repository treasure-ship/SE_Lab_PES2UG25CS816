import re

# part name, then 'x' and a quantity (ASCII digits only, capped to avoid huge ints)
_ITEM_PATTERN = re.compile(r'^(.*\S)\s*x\s*([0-9]{1,9})$', re.IGNORECASE)


def mask_imei(imei):
    """
    Removes dashes and spaces, then hides all but the last four digits.
    Returns '' for None, non-string or empty input.
    If 4 or fewer characters remain, all of them are hidden.
    """
    if not isinstance(imei, str):
        return ''
    imei = imei.replace('-', '').replace(' ', '')
    if len(imei) <= 4:
        return '*' * len(imei)
    return '*' * (len(imei) - 4) + imei[-4:]


def parse_parts_order(text):
    """
    Parses 'screen x1; battery x2' into a {part: quantity} dictionary.
    Malformed items (missing part, missing/invalid quantity, zero quantity)
    are skipped. Repeated parts have their quantities added together.
    Returns {} for None, non-string or empty input.
    """
    order = {}
    if not isinstance(text, str):
        return order
    for item in text.split(';'):
        match = _ITEM_PATTERN.match(item.strip())
        if not match:
            continue
        part = match.group(1).strip()
        qty = int(match.group(2))
        if part and qty > 0:
            order[part] = order.get(part, 0) + qty
    return order


def parse_model(text):
    """
    Splits 'Brand Model name' into a (brand, model) tuple.
    A single word is treated as the brand with an empty model.
    Returns ('', '') for None, non-string or blank input.
    """
    if not isinstance(text, str):
        return ('', '')
    parts = text.strip().split(None, 1)
    if not parts:
        return ('', '')
    brand = parts[0].title()
    model = parts[1].strip() if len(parts) > 1 else ''
    return brand, model


def main():
    print("==== Running mask_imei ====")
    value = input("Enter an IMEI number (e.g. 35-209900-176148-1): ")
    print("Masked IMEI:", mask_imei(value))

    print("\n==== Running parse_parts_order ====")
    value = input("Enter parts and quantities as PART xQTY separated by ; (e.g. screen x1; battery x2): ")
    print("Parts order:", parse_parts_order(value))

    print("\n==== Running parse_model ====")
    value = input("Enter the phone brand and model (e.g. Samsung Galaxy S23): ")
    print("Brand and model:", parse_model(value))


if __name__ == "__main__":
    main()