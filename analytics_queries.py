QUERIES = {
    "Customers per city & avg balance": """
        SELECT c.city, COUNT(DISTINCT c.customer_id) customers,
               AVG(a.account_balance) avg_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY c.city;
    """,

    "Highest balance account type": """
        SELECT account_type, SUM(account_balance) total_balance
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY account_type
        ORDER BY total_balance DESC
        LIMIT 1;
    """,

    "Top 10 customers by balance": """
        SELECT c.name, SUM(a.account_balance) total
        FROM customers c
        JOIN accounts a ON c.customer_id = a.customer_id
        GROUP BY c.customer_id
        ORDER BY total DESC
        LIMIT 10;
    """,

    "Transaction volume by type": """
        SELECT txn_type, SUM(amount) total_amount
        FROM transactions
        GROUP BY txn_type;
    """,

    "Failed transactions by type": """
        SELECT txn_type, COUNT(*) failed
        FROM transactions
        WHERE status='failed'
        GROUP BY txn_type;
    """,

    "High value accounts (>20000)": """
        SELECT customer_id, COUNT(*) cnt
        FROM transactions
        WHERE amount > 20000
        GROUP BY customer_id
        HAVING cnt >= 5;
    """
}
