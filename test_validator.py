from validator import validate_invoice


def make_invoice(**overrides):
    """Builds a clean, mathematically correct invoice. Tests tweak one thing at a time."""
    invoice = {
        "vendor_name": "Test Vendor",
        "invoice_number": "INV-001",
        "invoice_date": "2026-01-15",
        "currency": "SAR",
        "line_items": [
            {"description": "Item A", "quantity": 2, "unit_price": 50.0, "total": 100.0},
        ],
        "subtotal": 100.0,
        "discount": 0.0,
        "vat_amount": 15.0,
        "grand_total": 115.0,
    }
    invoice.update(overrides)
    return invoice


def test_clean_invoice_passes():
    assert validate_invoice(make_invoice()) == []


def test_missing_invoice_number_is_flagged():
    issues = validate_invoice(make_invoice(invoice_number=None))
    assert any("MISSING FIELD: invoice_number" in i for i in issues)


def test_line_item_math_error_is_flagged():
    bad_items = [{"description": "Item A", "quantity": 2, "unit_price": 50.0, "total": 130.0}]
    issues = validate_invoice(make_invoice(
        line_items=bad_items, subtotal=130.0, vat_amount=0.0, grand_total=130.0))
    assert any("MATH ERROR" in i for i in issues)


def test_vat_inclusive_line_totals_pass():
    # Sephora-style: unit price pre-tax, line total includes 15% VAT
    inv = make_invoice(
        line_items=[{"description": "Item A", "quantity": 1, "unit_price": 100.0, "total": 115.0}],
        subtotal=100.0, vat_amount=15.0, grand_total=115.0)
    assert validate_invoice(inv) == []


def test_subtotal_mismatch_is_flagged():
    issues = validate_invoice(make_invoice(subtotal=80.0, vat_amount=0.0, grand_total=80.0))
    assert any("SUBTOTAL MISMATCH" in i for i in issues)


def test_grand_total_mismatch_is_flagged():
    issues = validate_invoice(make_invoice(grand_total=999.0))
    assert any("TOTAL MISMATCH" in i for i in issues)