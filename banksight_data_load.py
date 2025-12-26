# =========================================================
# data_loader.py
# Pandas-based data insertion
# =========================================================

import pandas as pd
import json
import os
from db_connection import get_connection, create_tables

DATA_FILES = {
    "customers": "data/customers.csv",
    "accounts": "data/accounts.csv",
    "transactions": "data/transactions.csv",
    "branches": "data/branches.csv",
    "loans": "data/loans.csv",
    "credit_cards": "data/credit_cards.json",
    "support_tickets": "data/support_tickets.csv"
}

def load_file(path):
    if path.endswith(".csv"):
        return pd.read_csv(path)
    elif path.endswith(".json"):
        with open(path, "r", encoding="utf-8") as f:
            return pd.DataFrame(json.load(f))
    else:
        raise ValueError("Unsupported file")

def clean_df(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    return df

def insert_data():
    create_tables()
    conn = get_connection()

    for table, path in DATA_FILES.items():
        if not os.path.exists(path):
            continue

        df = clean_df(load_file(path))
        if df.empty:
            continue

        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"✅ Loaded {table}")

    conn.close()

if __name__ == "__main__":
    insert_data()
