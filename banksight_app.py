# =========================================================
# BankSight - Streamlit Application
# =========================================================

import streamlit as st
import pandas as pd
from db_connection import get_connection, create_tables
from analytics_queries import QUERIES

# ---------------------------------------------------------
# INITIAL SETUP
# ---------------------------------------------------------
st.set_page_config(page_title="BankSight Dashboard", layout="wide")

create_tables()  # SAFE: uses CREATE TABLE IF NOT EXISTS
conn = get_connection()
cur = conn.cursor()

TABLES = [
    "customers",
    "accounts",
    "transactions",
    "loans",
    "credit_cards",
    "support_tickets",
    "branches"
]

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("🏦 BankSight Navigation")
page = st.sidebar.radio(
    "Go to",
    [
        "Introduction",
        "View Tables",
        "Filter Data",
        "CRUD Operations",
        "Credit / Debit Simulation",
        "Analytical Insights",
        "About"
    ]
)

# ---------------------------------------------------------
# INTRODUCTION
# ---------------------------------------------------------
if page == "Introduction":
    st.title("🏦 BankSight: Transaction Intelligence Dashboard")
    st.markdown("""
    **BankSight** is a financial analytics dashboard built using  
    **Python, SQL, Pandas, and Streamlit**.

    **Key Features**
    - Customer & Account Analysis
    - Transaction Monitoring
    - Loan & Credit Insights
    - CRUD Operations
    - Credit / Debit Simulation
    - Analytical SQL Insights
    """)

# ---------------------------------------------------------
# VIEW TABLES (ALL 7 TABLES)
# ---------------------------------------------------------
elif page == "View Tables":
    st.header("📄 View Database Tables")
    table = st.selectbox("Select Table", TABLES)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df)

# ---------------------------------------------------------
# FILTER DATA (ALL 7 TABLES – GENERIC)
# ---------------------------------------------------------
elif page == "Filter Data":
    st.header("🔍 Filter Data")

    table = st.selectbox("Select Table", TABLES)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    column = st.selectbox("Select Column", df.columns)
    value = st.text_input("Enter value to filter")

    if value:
        filtered_df = df[df[column].astype(str).str.contains(value, case=False)]
        st.dataframe(filtered_df)
    else:
        st.dataframe(df)

# ---------------------------------------------------------
# CRUD OPERATIONS (ALL 7 TABLES – GENERIC)
# ---------------------------------------------------------
elif page == "CRUD Operations":
    st.header("🛠 CRUD Operations")

    operation = st.radio("Select Operation", ["View", "Insert", "Update", "Delete"])
    table = st.selectbox("Select Table", TABLES)
    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    # ---------- VIEW ----------
    if operation == "View":
        st.dataframe(df)

    # ---------- INSERT ----------
    elif operation == "Insert":
        st.subheader(f"➕ Insert into {table}")
        new_data = {}

        for col in df.columns:
            new_data[col] = st.text_input(f"{col}")

        if st.button("Insert Record"):
            cols = ",".join(new_data.keys())
            placeholders = ",".join(["?"] * len(new_data))
            values = tuple(new_data.values())

            cur.execute(
                f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                values
            )
            conn.commit()
            st.success("Record inserted successfully")

    # ---------- UPDATE ----------
    elif operation == "Update":
        st.subheader(f"✏️ Update {table}")

        pk_col = df.columns[0]
        pk_value = st.selectbox(f"Select {pk_col}", df[pk_col])

        column = st.selectbox("Column to update", df.columns)
        new_value = st.text_input("New value")

        if st.button("Update Record"):
            cur.execute(
                f"UPDATE {table} SET {column}=? WHERE {pk_col}=?",
                (new_value, pk_value)
            )
            conn.commit()
            st.success("Record updated successfully")

    # ---------- DELETE ----------
    elif operation == "Delete":
        st.subheader(f"🗑 Delete from {table}")

        pk_col = df.columns[0]
        pk_value = st.selectbox(f"Select {pk_col} to delete", df[pk_col])

        if st.button("Delete Record"):
            cur.execute(
                f"DELETE FROM {table} WHERE {pk_col}=?",
                (pk_value,)
            )
            conn.commit()
            st.success("Record deleted successfully")

# ---------------------------------------------------------
# CREDIT / DEBIT SIMULATION (ACCOUNTS ONLY – JOIN BASED)
# ---------------------------------------------------------
elif page == "Credit / Debit Simulation":
    st.header("💰 Deposit / Withdraw Money")

    customer_id = st.text_input("Enter Customer ID (e.g., C0001)")
    amount = st.number_input("Enter Amount (₹)", min_value=0.0, step=100.0)

    action = st.radio(
        "Select Action",
        ["Check Balance", "Deposit", "Withdraw"]
    )

    if st.button("Submit"):
        cur.execute("""
            SELECT a.customer_id, a.account_balance
            FROM customers c
            JOIN accounts a
                ON c.customer_id = a.customer_id
            WHERE c.customer_id = ?
        """, (customer_id,))

        row = cur.fetchone()

        if not row:
            st.error("No account found for this customer")
        else:
            account_id, balance = row

            if action == "Check Balance":
                st.success(f"💳 Current Balance: ₹{balance:,.2f}")

            elif action == "Deposit":
                new_balance = balance + amount
                cur.execute(
                    "UPDATE accounts SET account_balance=? WHERE customer_id=?",
                    (new_balance, account_id)
                )
                conn.commit()
                st.success(f"Deposited ₹{amount:,.2f}")
                st.info(f"Updated Balance: ₹{new_balance:,.2f}")

            elif action == "Withdraw":
                if amount > balance:
                    st.error("Insufficient balance")
                else:
                    new_balance = balance - amount
                    cur.execute(
                        "UPDATE accounts SET account_balance=? WHERE customer_id=?",
                        (new_balance, account_id)
                    )
                    conn.commit()
                    st.success(f"Withdrawn ₹{amount:,.2f}")
                    st.info(f"Updated Balance: ₹{new_balance:,.2f}")

# ---------------------------------------------------------
# ANALYTICAL INSIGHTS (ALL 15 QUERIES PLACEHOLDER)
# ---------------------------------------------------------
elif page=="Analytical Insights":
    st.header("📊 Analytical Insights")
    q = st.selectbox("Select Question", list(QUERIES.keys()))
    st.code(QUERIES[q], language="sql")
    df = pd.read_sql(QUERIES[q], conn)
    st.dataframe(df)

# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------
elif page == "About":
    st.header("👤 About the Creator")
    st.markdown("""
    **Name:** Nathiya  
    **Role:** Data Science / Analytics Trainee  
    **Skills:** Python, SQL, Pandas, Streamlit  
    **Project:** BankSight – Transaction Intelligence Dashboard
    """)

# ---------------------------------------------------------
conn.close()
