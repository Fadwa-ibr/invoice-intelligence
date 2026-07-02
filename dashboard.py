import streamlit as st
import pandas as pd
import sqlite3

st.set_page_config(page_title="Invoice Intelligence", page_icon="🧾", layout="wide")

st.title("🧾 Invoice Intelligence Dashboard")

con = sqlite3.connect("invoices.db")
df = pd.read_sql_query("SELECT * FROM invoices ORDER BY created_at DESC", con)
con.close()

col1, col2, col3 = st.columns(3)
col1.metric("Total Invoices", len(df))
col2.metric("Flagged", int((df["status"] == "flagged").sum()))
col3.metric("Total Amount", f"{df['grand_total'].sum():,.2f} SAR")

st.dataframe(df, width="stretch") 
