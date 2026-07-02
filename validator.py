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
        qty = item.get("quantity") or 0
        price = item.get("unit_price") or 0
        total = item.get("total") or 0
        pre_tax_ok = abs(qty * price - total) <= 0.01
        vat_incl_ok = abs(qty * price * 1.15 - total) <= 0.02
        if not (pre_tax_ok or vat_incl_ok):
            issues.append(f"MATH ERROR in item {i}: {qty} x {price} != {total}")

    # Check 3: items must sum to subtotal (pre-tax) or subtotal + VAT (inclusive)
    items_sum = sum((item.get("total") or 0) for item in data.get("line_items") or [])
    subtotal = data.get("subtotal") or 0
    vat = data.get("vat_amount") or 0
    if abs(items_sum - subtotal) > 0.01 and abs(items_sum - (subtotal + vat)) > 0.02:
        issues.append(f"SUBTOTAL MISMATCH: items sum to {items_sum}, invoice says {subtotal}")

    # Check 4: subtotal - discount + VAT must equal the grand total
    expected = subtotal - (data.get("discount") or 0) + (data.get("vat_amount") or 0)
    grand_total = data.get("grand_total") or 0
    if abs(expected - grand_total) > 0.01:
        issues.append(f"TOTAL MISMATCH: expected {expected}, invoice says {grand_total}")

    return issues