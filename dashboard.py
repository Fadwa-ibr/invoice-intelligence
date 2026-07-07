import streamlit as st
import pandas as pd
import sqlite3
import tempfile
import os
from extract import process_invoice
from database import init_db

init_db()  # make sure the invoices table exists (fresh cloud servers start empty)

st.set_page_config(page_title="Invoice Intelligence", page_icon="🧾", layout="wide")

st.title("🧾 Invoice Intelligence Dashboard")

uploaded = st.file_uploader("Upload an invoice PDF", type="pdf")
if uploaded:
    with st.spinner("Processing invoice with AI..."):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(uploaded.getbuffer())
            tmp_path = tmp.name
        try:
            data, issues, status = process_invoice(tmp_path)
        finally:
            os.remove(tmp_path)

    if status == "duplicate":
        st.warning(f"⚠️ Duplicate: invoice {data.get('invoice_number')} from "
                   f"{data.get('vendor_name')} is already in the database.")
    elif issues:
        st.error(f"🚩 Invoice {data.get('invoice_number')} saved but FLAGGED:")
        for issue in issues:
            st.write("-", issue)
    else:
        st.success(f"✅ Invoice {data.get('invoice_number')} from {data.get('vendor_name')} "
                   f"processed and saved — all checks passed.")

con = sqlite3.connect("invoices.db")
df = pd.read_sql_query("SELECT * FROM invoices ORDER BY created_at DESC", con)
con.close()

col1, col2, col3 = st.columns(3)
col1.metric("Total Invoices", len(df))
col2.metric("Flagged", int((df["status"] == "flagged").sum()))
col3.metric("Total Amount", f"{df['grand_total'].sum():,.2f} SAR")

st.dataframe(df, width="stretch")