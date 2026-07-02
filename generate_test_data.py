import json
import os
import random
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

random.seed(42)  # same "random" data every run - reproducible tests

OUT_DIR = "test_data"

VENDORS = ["Al Noor Trading Co", "Riyadh Tech Supplies", "Jeddah Office World",
           "Gulf Star Logistics", "Dar Alsalam Foods"]
ITEMS = ["Printer Paper A4", "USB-C Cable", "Office Chair", "Coffee Beans 1kg",
         "LED Desk Lamp", "Notebook Pack", "Wireless Mouse"]


def make_data(idx):
    """Create one mathematically correct invoice as a dictionary."""
    line_items = []
    for _ in range(random.randint(1, 4)):
        qty = random.randint(1, 5)
        price = round(random.uniform(5, 500), 2)
        line_items.append({"description": random.choice(ITEMS), "quantity": qty,
                           "unit_price": price, "total": round(qty * price, 2)})
    subtotal = round(sum(i["total"] for i in line_items), 2)
    vat = round(subtotal * 0.15, 2)
    return {
        "vendor_name": random.choice(VENDORS),
        "invoice_number": f"TST-{1000 + idx}",
        "invoice_date": f"2026-0{random.randint(1, 6)}-{random.randint(10, 28)}",
        "currency": "SAR",
        "line_items": line_items,
        "subtotal": subtotal,
        "discount": 0.0,
        "vat_amount": vat,
        "grand_total": round(subtotal + vat, 2),
    }


def draw_pdf(data, path):
    """Render the invoice dictionary as a simple PDF."""
    c = canvas.Canvas(path, pagesize=A4)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, 800, data["vendor_name"])
    c.setFont("Helvetica", 11)
    c.drawString(50, 770, "TAX INVOICE")
    c.drawString(50, 750, f"Invoice No: {data['invoice_number'] or ''}")
    c.drawString(50, 735, f"Date: {data['invoice_date']}")
    c.drawString(50, 720, f"Currency: {data['currency']}")

    y = 680
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Description")
    c.drawString(280, y, "Qty")
    c.drawString(340, y, "Unit Price")
    c.drawString(450, y, "Total")
    c.setFont("Helvetica", 10)
    for item in data["line_items"]:
        y -= 18
        c.drawString(50, y, item["description"])
        c.drawString(280, y, str(item["quantity"]))
        c.drawString(340, y, f"{item['unit_price']:.2f}")
        c.drawString(450, y, f"{item['total']:.2f}")

    y -= 30
    c.drawString(340, y, "Subtotal:")
    c.drawString(450, y, f"{data['subtotal']:.2f}")
    y -= 15
    c.drawString(340, y, "VAT 15%:")
    c.drawString(450, y, f"{data['vat_amount']:.2f}")
    y -= 15
    c.setFont("Helvetica-Bold", 11)
    c.drawString(340, y, "Grand Total:")
    c.drawString(450, y, f"{data['grand_total']:.2f}")
    c.save()


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    manifest = []

    for idx in range(1, 11):  # 10 invoices
        data = make_data(idx)
        expected_issues = []

        if idx == 7:   # planted error: broken line-item math
            data["line_items"][0]["total"] = round(data["line_items"][0]["total"] + 50, 2)
            expected_issues.append("MATH ERROR")
        if idx == 8:   # planted error: missing invoice number
            data["invoice_number"] = None
            expected_issues.append("MISSING FIELD")
        if idx == 9:   # planted error: wrong grand total
            data["grand_total"] = round(data["grand_total"] + 100, 2)
            expected_issues.append("TOTAL MISMATCH")
        if idx == 10:  # duplicate of invoice 1 (same vendor + number)
            data["vendor_name"] = manifest[0]["data"]["vendor_name"]
            data["invoice_number"] = manifest[0]["data"]["invoice_number"]
            expected_issues.append("DUPLICATE")

        pdf_path = os.path.join(OUT_DIR, f"invoice_{idx:02d}.pdf")
        draw_pdf(data, pdf_path)
        manifest.append({"file": pdf_path, "data": data, "expected_issues": expected_issues})

    with open(os.path.join(OUT_DIR, "ground_truth.json"), "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    print(f"Generated {len(manifest)} invoices in {OUT_DIR}/ (7 clean, 3 corrupted + 1 duplicate)")


if __name__ == "__main__":
    main()