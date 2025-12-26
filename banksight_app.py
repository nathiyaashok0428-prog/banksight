# =========================================================
# banksight_app.py
# BankSight – Streamlit Dashboard (FINAL MERGED VERSION)
# =========================================================

import streamlit as st
import pandas as pd
from sqlalchemy import text
from db_connection import get_mysql_engine, create_tables
from analytics_queries import QUERIES

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="BankSight – Transaction Intelligence Dashboard",
    layout="wide"
)

st.title("🏦 BankSight – Transaction Intelligence Dashboard")

# ---------------- DB INIT ----------------
engine = get_mysql_engine()
create_tables()

# ---------------- HELPERS ----------------
@st.cache_data
def load_table(table):
    return pd.read_sql(f"SELECT * FROM {table}", engine)


def get_tables():
    q = "SHOW TABLES"
    df = pd.read_sql(q, engine)
    return df.iloc[:, 0].tolist()


def get_primary_key(table):
    q = f"SHOW KEYS FROM {table} WHERE Key_name='PRIMARY'"
    df = pd.read_sql(q, engine)
    return df["Column_name"].iloc[0]


def filter_dataframe(df):
    st.subheader("🔍 Filter Data")

    col = st.selectbox("Select column", df.columns)

    if pd.api.types.is_numeric_dtype(df[col]):
        min_v, max_v = float(df[col].min()), float(df[col].max())
        val = st.slider("Range", min_v, max_v, (min_v, max_v))
        df = df[df[col].between(val[0], val[1])]

    elif pd.api.types.is_datetime64_any_dtype(df[col]):
        start, end = st.date_input("Date range", [df[col].min(), df[col].max()])
        df = df[df[col].between(pd.to_datetime(start), pd.to_datetime(end))]

    else:
        opts = st.multiselect("Values", df[col].dropna().unique())
        if opts:
            df = df[df[col].isin(opts)]

    return df


# ---------------- SIDEBAR ----------------
st.sidebar.header("📂 Navigation")

tables = get_tables()
selected_table = st.sidebar.selectbox("Select Table", tables)

section = st.sidebar.radio(
    "Select Feature",
    [
        "View / Filter Data",
        "CRUD Operations",
        "Credit / Debit",
        "Analytical Insights"
    ]
)

# =========================================================
# 1️⃣ VIEW + FILTER
# =========================================================
if section == "View / Filter Data":
    df = load_table(selected_table)
    df = filter_dataframe(df)
    st.dataframe(df, use_container_width=True)

# =========================================================
# 2️⃣ CRUD OPERATIONS
# =========================================================
elif section == "CRUD Operations":
    st.subheader(f"🛠 CRUD – {selected_table}")
    df = load_table(selected_table)
    pk = get_primary_key(selected_table)

    action = st.radio("Action", ["View", "Add", "Update", "Delete"])

    # ---- VIEW ----
    if action == "View":
        st.dataframe(df, use_container_width=True)

    # ---- ADD ----
    elif action == "Add":
        with st.form("add_form"):
            record = {}
            for col in df.columns:
                record[col] = st.text_input(col)
            submitted = st.form_submit_button("Insert")

        if submitted:
            pd.DataFrame([record]).to_sql(
                selected_table, engine, if_exists="append", index=False
            )
            st.success("✅ Record inserted")

    # ---- UPDATE ----
    elif action == "Update":
        key_val = st.text_input(f"Enter {pk}")

        if st.button("Load Record"):
            row = df[df[pk].astype(str) == key_val]
            if row.empty:
                st.error("Record not found")
            else:
                with st.form("update_form"):
                    updated = {}
                    for col in df.columns:
                        updated[col] = st.text_input(col, str(row.iloc[0][col]))
                    submit = st.form_submit_button("Update")

                if submit:
                    set_clause = ", ".join(
                        [f"{c}='{v}'" for c, v in updated.items()]
                    )
                    engine.execute(
                        text(f"UPDATE {selected_table} SET {set_clause} WHERE {pk}='{key_val}'")
                    )
                    st.success("✅ Updated")

    # ---- DELETE ----
    elif action == "Delete":
        key_val = st.text_input(f"Enter {pk} to delete")
        if st.button("Delete"):
            engine.execute(
                text(f"DELETE FROM {selected_table} WHERE {pk}='{key_val}'")
            )
            st.success("🗑 Deleted")

# =========================================================
# 3️⃣ CREDIT / DEBIT
# =========================================================
elif section == "Credit / Debit":
    st.subheader("💰 Credit / Debit Account")

    account_id = st.number_input("Account ID", step=1)
    amount = st.number_input("Amount", min_value=1.0)
    action = st.radio("Type", ["Credit", "Debit"])

    if st.button("Submit"):
        bal_df = pd.read_sql(
            f"SELECT account_balance FROM accounts WHERE account_id={account_id}",
            engine
        )

        if bal_df.empty:
            st.error("Account not found")
        else:
            balance = bal_df.iloc[0]["account_balance"]

            if action == "Debit" and balance < amount:
                st.error("❌ Insufficient balance")
            else:
                new_balance = balance + amount if action == "Credit" else balance - amount

                engine.execute(
                    text(
                        f"UPDATE accounts SET account_balance={new_balance} "
                        f"WHERE account_id={account_id}"
                    )
                )

                txn = pd.DataFrame([{
                    "txn_id": f"T{pd.Timestamp.now().value}",
                    "customer_id": None,
                    "txn_type": action.lower(),
                    "amount": amount,
                    "txn_time": pd.Timestamp.now(),
                    "status": "success"
                }])

                txn.to_sql("transactions", engine, if_exists="append", index=False)

                st.success(f"✅ {action} successful | New balance ₹{new_balance}")

# =========================================================
# 4️⃣ ANALYTICAL INSIGHTS
# =========================================================
elif section == "Analytical Insights":
    st.subheader("📊 Analytical Insights")

    q_name = st.selectbox("Select Question", list(QUERIES.keys()))
    result = pd.read_sql(QUERIES[q_name], engine)

    st.dataframe(result, use_container_width=True)
