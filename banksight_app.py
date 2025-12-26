# banksight_app.py

import streamlit as st
import pandas as pd
from db_connection import get_connection, create_tables
from analytics_queries import QUERIES

st.set_page_config("BankSight Dashboard", layout="wide")
create_tables()
conn = get_connection()

MENU = st.sidebar.radio(
    "BankSight Navigation",
    ["Introduction","View Tables","Filter Data",
     "CRUD Operations","Credit / Debit Simulation",
     "Analytical Insights","About"]
)

# ---------- INTRO ----------
if MENU=="Introduction":
    st.title("🏦 BankSight: Transaction Intelligence Dashboard")
    st.write("End-to-end banking analytics using Python, SQL & Streamlit")

# ---------- VIEW TABLES ----------
elif MENU=="View Tables":
    table = st.selectbox("Select Table", 
        ["customers","accounts","transactions","loans",
         "credit_cards","support_tickets"])
    df = pd.read_sql(f"SELECT * FROM {table}", conn)
    st.dataframe(df)

# ---------- FILTER DATA ----------
elif MENU=="Filter Data":
    table = st.selectbox("Filter Table",
        ["customers","transactions","loans","accounts"])
    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    col = st.selectbox("Select Column", df.columns)
    val = st.text_input("Filter Value")

    if val:
        df = df[df[col].astype(str).str.contains(val)]
    st.dataframe(df)

# ---------- CRUD ----------
elif MENU=="CRUD Operations":
    table = st.selectbox("Table", ["customers","accounts","transactions"])
    action = st.radio("Action", ["View","Add","Update","Delete"])

    df = pd.read_sql(f"SELECT * FROM {table}", conn)

    if action=="View":
        st.dataframe(df)

    elif action=="Add":
        data = {}
        for col in df.columns:
            data[col] = st.text_input(col)
        if st.button("Insert"):
            pd.DataFrame([data]).to_sql(table, conn, if_exists="append", index=False)
            st.success("Record Added")

    elif action=="Update":
        pk = df.columns[0]
        record = st.selectbox("Select ID", df[pk])
        col = st.selectbox("Column", df.columns)
        new = st.text_input("New Value")
        if st.button("Update"):
            conn.execute(f"UPDATE {table} SET {col}=? WHERE {pk}=?",(new,record))
            conn.commit()
            st.success("Updated")

    elif action=="Delete":
        pk = df.columns[0]
        record = st.selectbox("Select ID", df[pk])
        if st.button("Delete"):
            conn.execute(f"DELETE FROM {table} WHERE {pk}=?",(record,))
            conn.commit()
            st.success("Deleted")

# ---------- CREDIT / DEBIT ----------
elif MENU == "Credit / Debit Simulation":
    st.header("💰 Deposit / Withdraw Money")

    customer_id = st.text_input("Enter Customer ID (e.g., C0001)")
    amount = st.number_input("Enter Amount (₹)", min_value=0.0, step=100.0)

    action = st.radio(
        "Select Action",
        ["Check Balance", "Deposit", "Withdraw"]
    )

    if st.button("Submit"):
        if not customer_id:
            st.error("Please enter Customer ID")
        else:
            conn = get_connection()
            cur = conn.cursor()

            # Fetch account
            cur.execute(
                "SELECT account_id, account_balance FROM accounts WHERE customer_id = ?",
                (customer_id,)
            )
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
                        "UPDATE accounts SET account_balance = ? WHERE account_id = ?",
                        (new_balance, account_id)
                    )
                    conn.commit()
                    st.success(f"✅ Deposited ₹{amount:,.2f}")
                    st.info(f"💳 Updated Balance: ₹{new_balance:,.2f}")

                elif action == "Withdraw":
                    if amount > balance:
                        st.error("❌ Insufficient balance")
                    else:
                        new_balance = balance - amount
                        cur.execute(
                            "UPDATE accounts SET account_balance = ? WHERE account_id = ?",
                            (new_balance, account_id)
                        )
                        conn.commit()
                        st.success(f"✅ Withdrawn ₹{amount:,.2f}")
                        st.info(f"💳 Updated Balance: ₹{new_balance:,.2f}")

            conn.close()


# ---------- ANALYTICS ----------
elif MENU=="Analytical Insights":
    q = st.selectbox("Select Question", list(QUERIES.keys()))
    st.code(QUERIES[q], language="sql")
    df = pd.read_sql(QUERIES[q], conn)
    st.dataframe(df)


# ---------- ABOUT ----------
elif MENU == "About":
    st.markdown("""
    **Project:** BankSight  
    **Domain:** Banking & Finance  
    **Skills:** Python, SQL, Pandas, Streamlit  
    **Developer:** Nathiya Ashok  
    **Platform:** Streamlit Cloud  
    """)
