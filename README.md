# Invoice Intelligence 🧾

AI-powered invoice processing system that extracts, validates, and stores
invoice data from Arabic and English PDFs — turning minutes of manual data
entry into seconds of automated processing.

## The Problem

Accounting teams manually retype invoice data into their systems. It's slow,
expensive (studies estimate $10–15 per invoice), and error-prone: duplicate
payments, VAT miscalculations, and typos cost companies real money.

## What This System Does

- 📄 **Extracts** structured data from PDF invoices (bilingual Arabic/English)
  using Gemini with enforced JSON structured outputs
- 🔍 **Validates** every invoice with independent audit logic: line-item math,
  subtotal consistency, VAT/total verification — the AI is never blindly trusted
- 🗄️ **Stores** results in SQL with automatic duplicate detection, blocking
  the same invoice from being processed (or paid) twice

## Architecture

```
PDF Invoice → extract.py  (Gemini + Structured Outputs)
                 ↓
          validator.py  (math & consistency audit)
                 ↓
          database.py  (SQLite + duplicate protection)
```
## Tech Stack

| Layer | Technology |
|---|---|
| AI Extraction | Google Gemini API (structured JSON output) |
| Validation | Pure Python business logic |
| Storage | SQLite (SQL, unique constraints) |

## Getting Started

1. Clone the repo and install dependencies:

       pip install -r requirements.txt

2. Get a free Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
3. Save it in a file named `apikey.txt` (already gitignored)
4. Drop an invoice PDF in the folder as `invoice.pdf` and run:

       python extract.py

## Roadmap

- [x] AI extraction with structured outputs
- [x] Validation engine (math, VAT, required fields)
- [x] SQL storage with duplicate detection
- [x] Live dashboard (Streamlit)
- [x] Unit tests for validation engine (pytest)
- [ ] Automated folder watching (drop a PDF → processed automatically)
- [ ] Docker deployment
- [ ] Natural-language queries over invoice data (RAG)

---

Built by [Fadwa Abushanab](https://github.com/Fadwa-ibr) — AI Integration & Automation Engineering