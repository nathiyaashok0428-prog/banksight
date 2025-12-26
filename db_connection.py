# db_connection.py

import sqlite3
import os

DB_NAME = "banksight.db"

def get_connection():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        customer_id TEXT PRIMARY KEY,
        name TEXT,
        gender TEXT,
        age INTEGER,
        city TEXT,
        account_type TEXT,
        join_date DATE
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS accounts (
        account_id INTEGER PRIMARY KEY AUTOINCREMENT,
        customer_id TEXT,
        account_balance REAL,
        last_updated TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        txn_id TEXT PRIMARY KEY,
        customer_id TEXT,
        txn_type TEXT,
        amount REAL,
        txn_time TEXT,
        status TEXT
    )
    """)

    cur.execute("""
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
    )
    """)

    cur.execute("""
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
    )
    """)

    cur.execute("""
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
    )
    """)

    conn.commit()
    conn.close()
