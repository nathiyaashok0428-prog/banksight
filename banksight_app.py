# =========================================================
# BankSight Streamlit App - FINAL FULL VERSION
# =========================================================

import streamlit as st
import pandas as pd
from datetime import datetime
from db_connection import get_connection, create_tables
from analytics_queries import QUERIES

# ---------------- CONFIG ----------------
st.set_page_config("BankSight Dashboard", layout="wide")
create_tables()
conn = get_connection()

# ---------------- UTILS ----------------
def get_tables():
    q = "SELECT name FROM sqlite_master WHERE type='table'"
    return pd.read_sql(q, conn)["name"].tolist()

def get_primary_key(table):
    info = pd.read_sql(f"PRAGMA table_info({table})", conn)
    return info[info["pk"] == 1]["name"].values[0]

# ---------------- SIDEBAR ----------------
st.sidebar.title("🏦 BankSight")
page = st.sidebar.radio(
    "Navigation",
    [
        "Introduction",
        "View Tables",
        "Filter Data",
        "CRUD Operations",
        "Credit / Debit",
        "Analytical Insights",
        "About"
    ]
)

# =========================================================
# INTRODUCTION
# =========================================================
if page == "Introduction":
    st.title("🏦 BankSight – Transaction Intelligence Dashboard")
    st.markdown("""
    **Features**
    - Full Database View
    - Dynamic Filtering
    - Complete CRUD Operations
    - Credit / Debit Transactions
    - Analytical Insights (15 SQL Queries)
    """)

# =========================================================
# VIEW TABLES
# =========================================================
elif page == "View Tables":
    table = st.selectbox("Select Table", get_tables())
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# FILTER DATA (ALL TABLES)
# =========================================================
elif page == "Filter Data":
    table = st.selectbox("Select Table", get_tables())
    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    col = st.selectbox("Select Column", df.columns)
    val = st.text_input("Enter Filter Value")

    if val:
        df = df[df[col].astype(str).str.contains(val, case=False, na=False)]

    st.dataframe(df, use_container_width=True)

# =========================================================
# CRUD OPERATIONS (FULL)
# =========================================================
elif page == "CRUD Operations":
    table = st.selectbox("Select Table", get_tables())
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    pk = get_primary_key(table)

    st.subheader("📄 Existing Records")
    st.dataframe(df, use_container_width=True)

    action = st.radio("Action", ["Insert", "Update", "Delete"])

    # ---------- INSERT ----------
    if action == "Insert":
        st.subheader("➕ Insert Record")
        with st.form("insert_form"):
            values = {}
            for col in df.columns:
                values[col] = st.text_input(col)

            if st.form_submit_button("Insert"):
                cols = ", ".join(values.keys())
                placeholders = ", ".join(["?"] * len(values))
                conn.execute(
                    f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                    tuple(values.values())
                )
                conn.commit()
                st.success("Record inserted successfully")

    # ---------- UPDATE ----------
    elif action == "Update":
        st.subheader("✏️ Update Record")
        record_id = st.text_input(f"Enter {pk} value")

        with st.form("update_form"):
            updates = {}
            for col in df.columns:
                if col != pk:
                    updates[col] = st.text_input(col)

            if st.form_submit_button("Update"):
                set_clause = ", ".join([f"{c}=?" for c in updates])
                conn.execute(
                    f"UPDATE {table} SET {set_clause} WHERE {pk}=?",
                    tuple(updates.values()) + (record_id,)
                )
                conn.commit()
                st.success("Record updated successfully")

    # ---------- DELETE ----------
    elif action == "Delete":
        st.subheader("🗑 Delete Record")
        record_id = st.text_input(f"Enter {pk} value to delete")

        if st.button("Delete"):
            conn.execute(
                f"DELETE FROM {table} WHERE {pk}=?",
                (record_id,)
            )
            conn.commit()
            st.success("Record deleted successfully")

# =========================================================
# CREDIT / DEBIT (BALANCE CHECK ADDED)
# =========================================================
elif page == "Credit / Debit":
    st.subheader("💳 Credit / Debit Account")

    acc_id = st.number_input("Account ID", min_value=1, step=1)
    amount = st.number_input("Amount", min_value=0.0)
    action = st.radio("Transaction Type", ["Credit", "Debit"])

    if st.button("Process"):
        df = pd.read_sql(
            "SELECT account_balance FROM accounts WHERE account_id=?",
            conn,
            params=(acc_id,)
        )

        if df.empty:
            st.error("Account not found")
        else:
            balance = df.iloc[0, 0]
            st.info(f"Current Balance: ₹{balance}")

            if action == "Debit" and amount > balance:
                st.error("Insufficient balance")
            else:
                new_balance = balance + amount if action == "Credit" else balance - amount

                conn.execute(
                    "UPDATE accounts SET account_balance=?, last_updated=? WHERE account_id=?",
                    (new_balance, datetime.now(), acc_id)
                )
                conn.commit()

                st.success(f"Transaction successful. New Balance: ₹{new_balance}")

# =========================================================
# ANALYTICS
# =========================================================
elif page == "Analytical Insights":
    query_name = st.selectbox("Select Query", list(QUERIES.keys()))
    df = pd.read_sql(QUERIES[query_name], conn)
    st.dataframe(df, use_container_width=True)

# =========================================================
# ABOUT
# =========================================================
elif page == "About":
    st.markdown("""
    **Project:** BankSight  
    **Domain:** Banking & Finance  
    **Skills:** Python, SQL, Pandas, Streamlit  
    **Developer:** Nathiya Ashok  
    **Platform:** Streamlit Cloud  
    """)
