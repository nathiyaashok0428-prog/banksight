# analytics_queries.py

QUERIES = {
    "Q1 Customers & Avg Balance by City": """
    SELECT c.city,
           COUNT(DISTINCT c.customer_id) AS total_customers,
           ROUND(AVG(a.account_balance),2) AS avg_balance
    FROM customers c
    JOIN accounts a ON c.customer_id = a.customer_id
    GROUP BY c.city
    """,

    "Q2 Highest Balance Account Type": """
    SELECT account_type, SUM(account_balance) total_balance
    FROM customers c JOIN accounts a
    ON c.customer_id=a.customer_id
    GROUP BY account_type
    ORDER BY total_balance DESC
    LIMIT 1
    """,

    "Q3 Top 10 Customers by Balance": """
    SELECT c.customer_id, c.name, SUM(a.account_balance) total_balance
    FROM customers c JOIN accounts a
    ON c.customer_id=a.customer_id
    GROUP BY c.customer_id
    ORDER BY total_balance DESC
    LIMIT 10
    """,

    "Q4 2023 Customers with Balance > 1L": """
    SELECT c.customer_id, c.name, a.account_balance
    FROM customers c JOIN accounts a
    ON c.customer_id=a.customer_id
    WHERE strftime('%Y', join_date)='2023'
    AND a.account_balance > 100000
    """,

    "Q5 Transaction Volume by Type": """
    SELECT txn_type, SUM(amount) total_amount
    FROM transactions
    GROUP BY txn_type
    """,

    "Q6 Failed Transactions by Type": """
    SELECT txn_type, COUNT(*) failed_count
    FROM transactions
    WHERE status='failed'
    GROUP BY txn_type
    """,

    "Q7 Transaction Count by Type": """
    SELECT txn_type, COUNT(*) txn_count
    FROM transactions
    GROUP BY txn_type
    """,

    "Q8 High Value Accounts": """
    SELECT customer_id, COUNT(*) high_txns
    FROM transactions
    WHERE amount > 20000
    GROUP BY customer_id
    HAVING high_txns >=5
    """,

    "Q9 Avg Loan Amount by Type": """
    SELECT loan_type,
           AVG(loan_amount) avg_amount,
           AVG(interest_rate) avg_interest
    FROM loans
    GROUP BY loan_type
    """,

    "Q10 Customers with Multiple Active Loans": """
    SELECT customer_id, COUNT(*) loan_count
    FROM loans
    WHERE loan_status IN ('Active','Approved')
    GROUP BY customer_id
    HAVING loan_count >1
    """,

    "Q11 Top 5 Outstanding Loans": """
    SELECT customer_id, SUM(loan_amount) total_loan
    FROM loans
    WHERE loan_status!='Closed'
    GROUP BY customer_id
    ORDER BY total_loan DESC
    LIMIT 5
    """,

    "Q12 Avg Loan Amount per Branch": """
    SELECT branch, AVG(loan_amount) avg_loan
    FROM loans
    GROUP BY branch
    """,

    "Q13 Age Group Distribution": """
    SELECT
    CASE
      WHEN age BETWEEN 18 AND 25 THEN '18-25'
      WHEN age BETWEEN 26 AND 35 THEN '26-35'
      WHEN age BETWEEN 36 AND 50 THEN '36-50'
      ELSE '50+'
    END age_group,
    COUNT(*) count
    FROM customers
    GROUP BY age_group
    """,

    "Q14 Longest Resolution Time": """
    SELECT issue_category,
           AVG(julianday(date_closed)-julianday(date_opened)) avg_days
    FROM support_tickets
    WHERE date_closed IS NOT NULL
    GROUP BY issue_category
    ORDER BY avg_days DESC
    """,

    "Q15 Top Support Agents": """
    SELECT support_agent, COUNT(*) resolved
    FROM support_tickets
    WHERE priority='Critical' AND customer_rating>=4
    GROUP BY support_agent
    ORDER BY resolved DESC
    """
}
