from google import genai
import json
from validator import validate_invoice
from database import save_invoice


client = genai.Client(api_key=open("apikey.txt").read().strip())
invoice = client.files.upload(file="invoice.pdf")

prompt = """You are an invoice data extraction system.
Extract the following from this invoice as clean JSON only:
vendor_name, invoice_number, invoice_date, currency,
line_items (description, quantity, unit_price, total),
subtotal, discount, vat_amount, grand_total.
The invoice may contain Arabic and English - extract English values where available.
If a field is missing, use null."""

response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=[invoice, prompt],
    config={"response_mime_type": "application/json"},
)

data = json.loads(response.text)

#data["vat_amount"] = 5.0   # TEMP: fake error to test the validator


print(json.dumps(data, indent=2, ensure_ascii=False))
issues = validate_invoice(data)
if issues:
    print("\n⚠ PROBLEMS FOUND:")
    for issue in issues:
        print(" -", issue)
else:
    print("\n✅ Invoice passed all checks")

    status = save_invoice(data, issues)
print("\nSave result:", status.upper())