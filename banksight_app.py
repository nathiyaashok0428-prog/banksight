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
elif MENU=="Credit / Debit Simulation":
    acc = st.number_input("Account ID", step=1)
    amount = st.number_input("Amount", min_value=0.0)
    action = st.radio("Action", ["Check Balance","Deposit","Withdraw"])

    cur = conn.cursor()
    cur.execute("SELECT account_balance FROM accounts WHERE account_id=?",(acc,))
    row = cur.fetchone()

    if row:
        balance = row[0]
        if action=="Check Balance":
            st.info(f"Current Balance: ₹{balance}")
        elif action=="Deposit" and st.button("Submit"):
            cur.execute("UPDATE accounts SET account_balance=account_balance+? WHERE account_id=?",(amount,acc))
            conn.commit()
            st.success("Deposit Successful")
        elif action=="Withdraw" and st.button("Submit"):
            if amount<=balance:
                cur.execute("UPDATE accounts SET account_balance=account_balance-? WHERE account_id=?",(amount,acc))
                conn.commit()
                st.success("Withdrawal Successful")
            else:
                st.error("Insufficient Balance")
    else:
        st.error("Account not found")

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
