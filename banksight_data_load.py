# banksight_data_load.py

import pandas as pd
import sqlite3
from db_connection import get_connection, create_tables
import json
import os

DATA_PATH = "data"

FILES = {
    "customers": "customers.csv",
    "accounts": "accounts.csv",
    "transactions": "transactions.csv",
    "loans": "loans.csv",
    "branches": "branches.csv",
    "support_tickets": "support_tickets.csv",
    "credit_cards": "credit_cards.json"
}

def load_data():
    create_tables()
    conn = get_connection()

    for table, file in FILES.items():
        path = os.path.join(DATA_PATH, file)
        if not os.path.exists(path):
            continue

        if file.endswith(".csv"):
            df = pd.read_csv(path)
        else:
            with open(path) as f:
                df = pd.DataFrame(json.load(f))

        df.columns = df.columns.str.lower().str.replace(" ", "_")

        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"{table} loaded")

    conn.close()

if __name__ == "__main__":
    load_data()
