# banksight_data_load.py
import pandas as pd
import json
from db_connection import get_connection, create_tables

FILES = {
    "customers": "data/customers.csv",
    "accounts": "data/accounts.csv",
    "transactions": "data/transactions.csv",
    "branches": "data/branches.csv",
    "loans": "data/loans.csv",
    "credit_cards": "data/credit_cards.json",
    "support_tickets": "data/support_tickets.csv"
}

def load_data():
    create_tables()
    conn = get_connection()

    for table, path in FILES.items():
        if path.endswith(".csv"):
            df = pd.read_csv(path)
        else:
            with open(path) as f:
                df = pd.DataFrame(json.load(f))

        df.columns = df.columns.str.lower().str.replace(" ", "_")

        if table == "accounts" and "account_id" in df.columns:
            df.drop(columns=["account_id"], inplace=True)

        df.to_sql(table, conn, if_exists="append", index=False)
        print(f"Loaded {table}")

    conn.close()

if __name__ == "__main__":
    load_data()
