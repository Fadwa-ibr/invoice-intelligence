def to_num(x):
    """Safely convert AI output to a number. '78.30' -> 78.3, junk/None -> 0.0"""
    try:
        return float(x)
    except (TypeError, ValueError):
        return 0.0


def validate_invoice(data):
    """Checks an extracted invoice for problems. Returns a list of issues."""
    issues = []

    # Check 1: required fields must exist
    required = ["vendor_name", "invoice_number", "invoice_date", "grand_total"]
    for field in required:
        if not data.get(field):
            issues.append(f"MISSING FIELD: {field}")

    # Check 2: line item math - accept both pre-tax and VAT-inclusive totals
    for i, item in enumerate(data.get("line_items") or [], start=1):
        qty = to_num(item.get("quantity"))
        price = to_num(item.get("unit_price"))
        total = to_num(item.get("total"))
        pre_tax_ok = abs(qty * price - total) <= 0.01
        vat_incl_ok = abs(qty * price * 1.15 - total) <= 0.02
        if not (pre_tax_ok or vat_incl_ok):
            issues.append(f"MATH ERROR in item {i}: {qty} x {price} != {total}")

    # Check 3: items must sum to subtotal (pre-tax) or subtotal + VAT (inclusive)
    items_sum = sum(to_num(item.get("total")) for item in data.get("line_items") or [])
    subtotal = to_num(data.get("subtotal"))
    vat = to_num(data.get("vat_amount"))
    if abs(items_sum - subtotal) > 0.01 and abs(items_sum - (subtotal + vat)) > 0.02:
        issues.append(f"SUBTOTAL MISMATCH: items sum to {items_sum}, invoice says {subtotal}")

    # Check 4: subtotal - discount + VAT must equal the grand total
    expected = subtotal - to_num(data.get("discount")) + vat
    grand_total = to_num(data.get("grand_total"))
    if abs(expected - grand_total) > 0.01:
        issues.append(f"TOTAL MISMATCH: expected {expected}, invoice says {grand_total}")

    return issues