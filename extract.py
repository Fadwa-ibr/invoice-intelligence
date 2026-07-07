from google import genai
import json
import os
from validator import validate_invoice
from database import save_invoice

PROMPT = """You are an invoice data extraction system.
Extract the following from this invoice as clean JSON only:
vendor_name, invoice_number, invoice_date, currency,
line_items (description, quantity, unit_price, total),
subtotal, discount, vat_amount, grand_total.
The invoice may contain Arabic and English - extract English values where available.
If a field is missing, use null."""

def get_api_key():
    """Use the cloud's secret if available, otherwise the local key file."""
    key = os.environ.get("GEMINI_API_KEY")
    if key:
        return key
    return open("apikey.txt").read().strip()


def extract_invoice(pdf_path):
    """Extraction only - no validation, no saving. Used by the evaluator."""
    client = genai.Client(api_key=get_api_key())
    invoice = client.files.upload(file=pdf_path)
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[invoice, PROMPT],
        config={"response_mime_type": "application/json"},
    )
    return json.loads(response.text)


def process_invoice(pdf_path):
    """Full pipeline: extract -> validate -> store."""
    data = extract_invoice(pdf_path)
    issues = validate_invoice(data)
    status = save_invoice(data, issues)
    return data, issues, status


if __name__ == "__main__":
    data, issues, status = process_invoice("invoice.pdf")
    print(json.dumps(data, indent=2, ensure_ascii=False))
    print("Issues:", issues or "none")
    print("Save result:", status.upper())