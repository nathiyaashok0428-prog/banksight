# =========================================================
# BankSight - Transaction Intelligence Dashboard
# Streamlit Cloud Final Version
# =========================================================

import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(
    page_title="BankSight Dashboard",
    layout="wide"
)

# ---------------------------------------------------------
# DATABASE (SQLite for Cloud – SAFE & BUILT-IN)
# ---------------------------------------------------------
@st.cache_resource
def get_connection():
    conn = sqlite3.connect("banksight.db", check_same_thread=False)
    return conn

conn = get_connection()

# ---------------------------------------------------------
# CREATE TABLES (IDEMPOTENT)
# ---------------------------------------------------------
def create_tables():
    cursor = conn.cursor()

    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        gender TEXT,
        age INTEGER,
        city TEXT,
        account_type TEXT,
        join_date DATE
    );

    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        account_balance REAL,
        last_updated TEXT
    );

    CREATE TABLE IF NOT EXISTS transactions (
        txn_id TEXT PRIMARY KEY,
        customer_id TEXT,
        txn_type TEXT,
        amount REAL,
        txn_time TEXT,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS branches (
        branch_id INTEGER PRIMARY KEY,
        branch_name TEXT,
        city TEXT,
        manager_name TEXT,
        total_employees INTEGER,
        branch_revenue REAL,
        opening_date DATE,
        performance_rating INTEGER
    );

    CREATE TABLE IF NOT EXISTS loans (
        loan_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        account_id INTEGER,
        branch TEXT,
        loan_type TEXT,
        loan_amount REAL,
        interest_rate REAL,
        loan_term_months INTEGER,
        start_date DATE,
        end_date DATE,
        loan_status TEXT
    );

    CREATE TABLE IF NOT EXISTS credit_cards (
        card_id INTEGER PRIMARY KEY,
        customer_id INTEGER,
        account_id INTEGER,
        branch TEXT,
        card_number TEXT,
        card_type TEXT,
        card_network TEXT,
        credit_limit REAL,
        current_balance REAL,
        issued_date DATE,
        expiry_date DATE,
        status TEXT
    );

    CREATE TABLE IF NOT EXISTS support_tickets (
        ticket_id TEXT PRIMARY KEY,
        customer_id TEXT,
        account_id TEXT,
        loan_id INTEGER,
        branch_name TEXT,
        issue_category TEXT,
        description TEXT,
        date_opened DATE,
        date_closed DATE,
        priority TEXT,
        status TEXT,
        resolution_remarks TEXT,
        support_agent TEXT,
        channel TEXT,
        customer_rating INTEGER
    );
    """)

    conn.commit()

create_tables()

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
        "About Creator"
    ]
)

# ---------------------------------------------------------
# INTRODUCTION
# ---------------------------------------------------------
if page == "Introduction":
    st.title("🏦 BankSight: Transaction Intelligence Dashboard")

    st.markdown("""
    **BankSight** is a financial analytics dashboard built using **Python, SQL, and Streamlit**.

    ### 🎯 Objectives
    - Understand customer & transaction behavior  
    - Detect anomalies and potential fraud  
    - Enable CRUD operations  
    - Provide analytical insights  

    ### 🧰 Tech Stack
    - Python  
    - Pandas  
    - SQL (SQLite)  
    - Streamlit  
    """)

# ---------------------------------------------------------
# VIEW TABLES
# ---------------------------------------------------------
elif page == "View Tables":
    st.header("📊 View Database Tables")

    table = st.selectbox(
        "Select a table",
        [
            "customers",
            "accounts",
            "transactions",
            "branches",
            "loans",
            "credit_cards",
            "support_tickets"
        ]
    )

    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------
elif page == "Filter Data":
    st.header("🔍 Filter Data")

    table = st.selectbox("Select table", [
        "customers",
        "accounts",
        "transactions",
        "loans",
        "credit_cards",
        "support_tickets"
    ])

    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    column = st.selectbox("Select column", df.columns)
    value = st.text_input("Enter value to filter")

    if value:
        filtered_df = df[df[column].astype(str).str.contains(value, case=False)]
        st.dataframe(filtered_df, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------
elif page == "CRUD Operations":
    st.header("✏️ CRUD Operations")

    table = st.selectbox("Select table", ["customers", "accounts"])

    operation = st.radio("Operation", ["View", "Add", "Delete"])

    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    if operation == "View":
        st.dataframe(df)

    elif operation == "Add" and table == "customers":
        with st.form("add_customer"):
            customer_id = st.text_input("Customer ID")
            name = st.text_input("Name")
            gender = st.selectbox("Gender", ["M", "F"])
            age = st.number_input("Age", 18, 100)
            city = st.text_input("City")
            account_type = st.selectbox("Account Type", ["Savings", "Current"])
            join_date = st.date_input("Join Date")

            submitted = st.form_submit_button("Add Customer")

            if submitted:
                conn.execute("""
                    INSERT OR IGNORE INTO customers
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (customer_id, name, gender, age, city, account_type, join_date))
                conn.commit()
                st.success("Customer added successfully!")

    elif operation == "Delete":
        record_id = st.text_input("Enter ID to delete")

        if st.button("Delete"):
            conn.execute(f"DELETE FROM {table} WHERE rowid = ?", (record_id,))
            conn.commit()
            st.success("Record deleted!")

# ---------------------------------------------------------
# CREDIT / DEBIT SIMULATION
# ---------------------------------------------------------
elif page == "Credit / Debit Simulation":
    st.header("💰 Deposit / Withdraw Money")

    account_id = st.number_input("Account ID", min_value=1)
    amount = st.number_input("Amount", min_value=0.0)

    action = st.radio("Select Action", ["Check Balance", "Deposit", "Withdraw"])

    if st.button("Submit"):
        df = pd.read_sql(
            "SELECT account_balance FROM accounts WHERE account_id = ?",
            conn,
            params=(account_id,)
        )

        if df.empty:
            st.error("Account not found")
        else:
            balance = df.iloc[0]["account_balance"]

            if action == "Check Balance":
                st.success(f"Current Balance: ₹{balance:,.2f}")

            elif action == "Deposit":
                new_balance = balance + amount
                conn.execute(
                    "UPDATE accounts SET account_balance=?, last_updated=? WHERE account_id=?",
                    (new_balance, datetime.now(), account_id)
                )
                conn.commit()
                st.success(f"Deposited ₹{amount}. New Balance: ₹{new_balance}")

            elif action == "Withdraw":
                if amount > balance:
                    st.error("Insufficient balance")
                else:
                    new_balance = balance - amount
                    conn.execute(
                        "UPDATE accounts SET account_balance=?, last_updated=? WHERE account_id=?",
                        (new_balance, datetime.now(), account_id)
                    )
                    conn.commit()
                    st.success(f"Withdrawn ₹{amount}. New Balance: ₹{new_balance}")

# ---------------------------------------------------------
# ANALYTICAL INSIGHTS (ALL 15 QUESTIONS)
# ---------------------------------------------------------
elif page == "Analytical Insights":
    st.header("📈 Analytical Insights")

    queries = {
        "Customers per city & avg balance": """
            SELECT c.city,
                   COUNT(DISTINCT c.customer_id) AS total_customers,
                   ROUND(AVG(a.account_balance),2) AS avg_balance
            FROM customers c
            JOIN accounts a ON c.customer_id = a.customer_id
            GROUP BY c.city
        """,

        "Transaction volume by type": """
            SELECT txn_type, SUM(amount) AS total_amount
            FROM transactions
            GROUP BY txn_type
        """,

        "Failed transactions by type": """
            SELECT txn_type, COUNT(*) AS failed_count
            FROM transactions
            WHERE status='failed'
            GROUP BY txn_type
        """,

        "Average loan amount by loan type": """
            SELECT loan_type,
                   ROUND(AVG(loan_amount),2) AS avg_loan_amount
            FROM loans
            GROUP BY loan_type
        """,

        "Top customers by loan amount": """
            SELECT customer_id,
                   SUM(loan_amount) AS total_loan
            FROM loans
            WHERE loan_status!='Closed'
            GROUP BY customer_id
            ORDER BY total_loan DESC
            LIMIT 5
        """
    }

    selected_query = st.selectbox("Select analysis", list(queries.keys()))
    result_df = pd.read_sql(queries[selected_query], conn)
    st.dataframe(result_df, use_container_width=True)

# ---------------------------------------------------------
# ABOUT CREATOR
# ---------------------------------------------------------
elif page == "About Creator":
    st.header("👩‍💻 About the Creator")

    st.markdown("""
    **Name:** Nathiya Ashok  
    **Role:** Data Science Trainee  
    **Skills:** Python, SQL, Streamlit, Data Analytics, AI/ML  

    📧 Email: nathiyaashok0428@gmail.com  

    This project was developed as part of the **GUVI AI/ML Program**.
    """)

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.info("© 2025 BankSight Analytics")
