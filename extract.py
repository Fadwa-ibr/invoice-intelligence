from google import genai
import json
from validator import validate_invoice
from database import save_invoice

PROMPT = """You are an invoice data extraction system.
Extract the following from this invoice as clean JSON only:
vendor_name, invoice_number, invoice_date, currency,
line_items (description, quantity, unit_price, total),
subtotal, discount, vat_amount, grand_total.
The invoice may contain Arabic and English - extract English values where available.
If a field is missing, use null."""


def process_invoice(pdf_path):
    """Full pipeline: extract -> validate -> store. Returns (data, issues, status)."""
    client = genai.Client(api_key=open("apikey.txt").read().strip())
    invoice = client.files.upload(file=pdf_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[invoice, PROMPT],
        config={"response_mime_type": "application/json"},
    )
    data = json.loads(response.text)
    issues = validate_invoice(data)
    status = save_invoice(data, issues)
    return data, issues, status


if __name__ == "__main__":
    data, issues, status = process_invoice("invoice.pdf")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("Issues:", issues or "none")
    print("Save result:", status.upper())