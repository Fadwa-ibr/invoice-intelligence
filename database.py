import sqlite3
import json
from datetime import datetime

DB_FILE = "invoices.db"

def init_db():
    con = sqlite3.connect(DB_FILE)
    con.execute("""
        CREATE TABLE IF NOT EXISTS invoices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vendor_name TEXT,
            invoice_number TEXT,
            invoice_date TEXT,
            currency TEXT,
            subtotal REAL,
            discount REAL,
            vat_amount REAL,
            grand_total REAL,
            status TEXT,
            issues TEXT,
            line_items TEXT,
            created_at TEXT,
            UNIQUE(vendor_name, invoice_number)
        )
    """)
    con.commit()
    con.close()

def save_invoice(data, issues):
    init_db()
    con = sqlite3.connect(DB_FILE)
    status = "flagged" if issues else "valid"
    try:
        con.execute(
            """INSERT INTO invoices
               (vendor_name, invoice_number, invoice_date, currency,
                subtotal, discount, vat_amount, grand_total,
                status, issues, line_items, created_at)
               VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data.get("vendor_name"), data.get("invoice_number"),
             data.get("invoice_date"), data.get("currency"),
             data.get("subtotal"), data.get("discount"),
             data.get("vat_amount"), data.get("grand_total"),
             status, json.dumps(issues, ensure_ascii=False),
             json.dumps(data.get("line_items"), ensure_ascii=False),
             datetime.now().isoformat())
        )
        con.commit()
        return status
    except sqlite3.IntegrityError:
        return "duplicate"
    finally:
        con.close()