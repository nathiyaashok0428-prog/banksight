import streamlit as st
import pandas as pd
from db_connection import get_connection, create_tables
from analytics_queries import QUERIES

st.set_page_config(page_title="BankSight Dashboard", layout="wide")

create_tables()
conn = get_connection()

st.sidebar.title("🏦 BankSight")
menu = st.sidebar.radio("Menu", [
    "View Tables",
    "Filtered Data",
    "CRUD Operations",
    "Credit / Debit",
    "Analytical Insights"
])

TABLES = [
    "customers","accounts","transactions",
    "branches","loans","credit_cards","support_tickets"
]

# ---------------- VIEW TABLES ----------------
if menu == "View Tables":
    table = st.selectbox("Select Table", TABLES)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df)

# ---------------- FILTERED DATA ----------------
elif menu == "Filtered Data":
    table = st.selectbox("Table", TABLES)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    column = st.selectbox("Column", df.columns)
    value = st.text_input("Value")
    if value:
        st.dataframe(df[df[column].astype(str).str.contains(value)])

# ---------------- CRUD ----------------
elif menu == "CRUD Operations":
    st.info("Insert / Delete demo")
    table = st.selectbox("Table", TABLES)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df.head())

# ---------------- CREDIT / DEBIT ----------------
elif menu == "Credit / Debit":
    acc_id = st.number_input("Account ID", min_value=1)
    amount = st.number_input("Amount", min_value=0.0)
    action = st.radio("Action", ["Credit", "Debit"])

    if st.button("Apply"):
        if action == "Credit":
            conn.execute(
                "UPDATE accounts SET account_balance = account_balance + ? WHERE account_id=?",
                (amount, acc_id)
            )
        else:
            conn.execute(
                "UPDATE accounts SET account_balance = account_balance - ? WHERE account_id=?",
                (amount, acc_id)
            )
        conn.commit()
        st.success("Transaction Successful")

# ---------------- ANALYTICS ----------------
elif menu == "Analytical Insights":
    qname = st.selectbox("Select Query", list(QUERIES.keys()))
    df = pd.read_sql(QUERIES[qname], conn)
    st.dataframe(df)
