# =========================================================
# BankSight - Optimized Streamlit Application
# =========================================================

import streamlit as st
import pandas as pd
import logging
from db_connection import get_connection, create_tables
from analytics_queries import QUERIES

# ---------------------------------------------------------
# LOGGING CONFIGURATION
# ---------------------------------------------------------
logging.basicConfig(
    filename="banksight.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# ---------------------------------------------------------
# INITIAL SETUP
# ---------------------------------------------------------
st.set_page_config(
    page_title="BankSight Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

create_tables()

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
# DATABASE HELPERS
# ---------------------------------------------------------
def fetch_df(query, params=None):
    conn = get_connection()
    df = pd.read_sql(query, conn, params=params)
    conn.close()
    return df

def execute_query(query, params=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(query, params or ())
    conn.commit()
    conn.close()

# ---------------------------------------------------------
# SIDEBAR NAVIGATION
# ---------------------------------------------------------
st.sidebar.title("🏦 BankSight")
page = st.sidebar.radio(
    "Navigation",
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
    **BankSight** is a banking analytics and admin dashboard built using  
    **Python, SQL, Pandas, and Streamlit**.

    ### Key Capabilities
    - Customer, Account & Transaction Management
    - CRUD Operations on all entities
    - Credit / Debit Simulation
    - Analytical SQL Insights
    - Logging & Error Handling
    """)

# ---------------------------------------------------------
# VIEW TABLES
# ---------------------------------------------------------
elif page == "View Tables":
    st.header("📄 View Database Tables")

    table = st.selectbox("Select Table", TABLES)
    df = fetch_df(f"SELECT * FROM {table}")
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# FILTER DATA
# ---------------------------------------------------------
elif page == "Filter Data":
    st.header("🔍 Filter Data")

    table = st.selectbox("Select Table", TABLES)
    df = fetch_df(f"SELECT * FROM {table}")

    column = st.selectbox("Select Column", df.columns)
    value = st.text_input("Enter filter value")

    if value:
        filtered = df[df[column].astype(str).str.contains(value, case=False)]
        st.dataframe(filtered, use_container_width=True)
    else:
        st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# CRUD OPERATIONS
# ---------------------------------------------------------
elif page == "CRUD Operations":
    st.header("🛠 CRUD Operations")

    table = st.selectbox("Select Table", TABLES)
    action = st.radio("Action", ["View", "Insert", "Update", "Delete"])

    df = fetch_df(f"SELECT * FROM {table}")
    pk_col = df.columns[0]

    if action == "View":
        st.dataframe(df, use_container_width=True)

    elif action == "Insert":
        st.subheader("➕ Insert Record")
        record = {}

        for col in df.columns:
            record[col] = st.text_input(col)

        if st.button("Insert"):
            try:
                cols = ",".join(record.keys())
                placeholders = ",".join(["?"] * len(record))
                execute_query(
                    f"INSERT INTO {table} ({cols}) VALUES ({placeholders})",
                    tuple(record.values())
                )
                logging.info(f"Inserted record into {table}")
                st.success("Record inserted successfully")
            except Exception as e:
                logging.error(str(e))
                st.error("Insertion failed")

    elif action == "Update":
        st.subheader("✏️ Update Record")

        record_id = st.selectbox(f"Select {pk_col}", df[pk_col])
        column = st.selectbox("Column to update", df.columns)
        new_value = st.text_input("New value")

        if st.button("Update"):
            execute_query(
                f"UPDATE {table} SET {column}=? WHERE {pk_col}=?",
                (new_value, record_id)
            )
            logging.info(f"Updated {table} {pk_col}={record_id}")
            st.success("Record updated")

    elif action == "Delete":
        st.subheader("🗑 Delete Record")

        record_id = st.selectbox(f"Select {pk_col}", df[pk_col])
        if st.button("Delete"):
            execute_query(
                f"DELETE FROM {table} WHERE {pk_col}=?",
                (record_id,)
            )
            logging.warning(f"Deleted from {table} {pk_col}={record_id}")
            st.success("Record deleted")

# ---------------------------------------------------------
# CREDIT / DEBIT SIMULATION
# ---------------------------------------------------------
elif page == "Credit / Debit Simulation":
    st.header("💰 Credit / Debit Simulation")

    customer_id = st.text_input("Enter Customer ID (e.g., C0001)")
    amount = st.number_input("Amount (₹)", min_value=0.0, step=100.0)

    action = st.radio("Select Action", ["Check Balance", "Deposit", "Withdraw"])

    if st.button("Submit"):
        try:
            df = fetch_df("""
                SELECT a.customer_id, a.account_balance
                FROM customers c
                JOIN accounts a ON c.customer_id = a.customer_id
                WHERE c.customer_id = ?
            """, (customer_id,))

            if df.empty:
                st.error("No account found for this customer")
            else:
                account_id = df.iloc[0]["customer_id"]
                balance = df.iloc[0]["account_balance"]

                if action == "Check Balance":
                    st.success(f"Current Balance: ₹{balance:,.2f}")

                elif action == "Deposit":
                    new_balance = balance + amount
                    execute_query(
                        "UPDATE accounts SET account_balance=?, last_updated=CURRENT_TIMESTAMP WHERE customer_id=?",
                        (new_balance, account_id)
                    )
                    logging.info(f"Deposit ₹{amount} to account {account_id}")
                    st.success(f"Deposited ₹{amount:,.2f}")
                    st.info(f"Updated Balance: ₹{new_balance:,.2f}")

                elif action == "Withdraw":
                    if amount > balance:
                        st.error("Insufficient balance")
                    else:
                        new_balance = balance - amount
                        execute_query(
                            "UPDATE accounts SET account_balance=?, last_updated=CURRENT_TIMESTAMP WHERE customer_id=?",
                            (new_balance, account_id)
                        )
                        logging.info(f"Withdraw ₹{amount} from account {account_id}")
                        st.success(f"Withdrawn ₹{amount:,.2f}")
                        st.info(f"Updated Balance: ₹{new_balance:,.2f}")

        except Exception as e:
            logging.error(str(e))
            st.error("Transaction failed")

# ---------------------------------------------------------
# ANALYTICAL INSIGHTS
# ---------------------------------------------------------
elif page == "Analytical Insights":
    st.header("📊 Analytical Insights")

    query_name = st.selectbox("Select Question", list(QUERIES.keys()))
    st.code(QUERIES[query_name], language="sql")

    df = fetch_df(QUERIES[query_name])
    st.dataframe(df, use_container_width=True)

# ---------------------------------------------------------
# ABOUT
# ---------------------------------------------------------
elif page == "About":
    st.header("ℹ️ About BankSight")
    st.markdown("""
    **Developer:** Nathiya  
    **Project Type:** Banking Analytics Dashboard  
    **Tech Stack:** Python, SQL, Pandas, Streamlit  
    **Domain:** Banking & Finance
    """)

