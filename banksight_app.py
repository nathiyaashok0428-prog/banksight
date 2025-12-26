# =========================================================
# BankSight Streamlit App
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from db_connection import get_connection, create_tables
from analytics_queries import QUERIES

st.set_page_config("BankSight Dashboard", layout="wide")

create_tables()
conn = get_connection()

# ---------------- SIDEBAR ----------------
st.sidebar.title("🏦 BankSight Navigation")
page = st.sidebar.radio("Go to", [
    "Introduction",
    "View Tables",
    "Filter Data",
    "CRUD Operations",
    "Credit / Debit",
    "Analytical Insights",
    "About Creator"
])

# ---------------- INTRO ----------------
if page == "Introduction":
    st.title("🏦 BankSight: Transaction Intelligence Dashboard")
    st.markdown("""
    - Customer & account analytics  
    - Transaction behavior  
    - Loan insights  
    - Support performance  
    """)

# ---------------- VIEW TABLES ----------------
elif page == "View Tables":
    table = st.selectbox("Select table", [
        "customers","accounts","transactions",
        "branches","loans","credit_cards","support_tickets"
    ])
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df, use_container_width=True)

# ---------------- FILTER ----------------
elif page == "Filter Data":
    table = st.selectbox("Table", ["customers","transactions","loans"])
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    col = st.selectbox("Column", df.columns)
    val = st.text_input("Value")
    if val:
        df = df[df[col].astype(str).str.contains(val, case=False)]
    st.dataframe(df)

# ---------------- CRUD ----------------
elif page == "CRUD Operations":
    st.subheader("Add Customer")
    with st.form("add"):
        cid = st.text_input("Customer ID")
        name = st.text_input("Name")
        city = st.text_input("City")
        submit = st.form_submit_button("Insert")
        if submit:
            conn.execute(
                "INSERT OR IGNORE INTO customers VALUES (?,?,?,?,?,?,?)",
                (cid, name, "M", 30, city, "Savings", datetime.now())
            )
            conn.commit()
            st.success("Inserted")

# ---------------- CREDIT / DEBIT ----------------
elif page == "Credit / Debit":
    acc = st.number_input("Account ID", min_value=1)
    amt = st.number_input("Amount", min_value=0.0)
    action = st.radio("Action", ["Deposit","Withdraw"])

    if st.button("Apply"):
        bal = pd.read_sql(
            "SELECT account_balance FROM accounts WHERE account_id=?",
            conn, params=(acc,)
        )
        if bal.empty:
            st.error("Invalid account")
        else:
            balance = bal.iloc[0,0]
            if action == "Deposit":
                balance += amt
            else:
                if amt > balance:
                    st.error("Insufficient funds")
                    st.stop()
                balance -= amt

            conn.execute(
                "UPDATE accounts SET account_balance=?, last_updated=? WHERE account_id=?",
                (balance, datetime.now(), acc)
            )
            conn.commit()
            st.success(f"New Balance: ₹{balance}")

# ---------------- ANALYTICS ----------------
elif page == "Analytical Insights":
    qname = st.selectbox("Select Query", list(QUERIES.keys()))
    df = pd.read_sql(QUERIES[qname], conn)
    st.dataframe(df)

# ---------------- ABOUT ----------------
elif page == "About Creator":
    st.markdown("""
    **Name:** Nathiya Ashok  
    **Course:** GUVI – AI/ML  
    **Project:** BankSight  
    **Skills:** Python, SQL, Streamlit, Data Analytics  
    """)
