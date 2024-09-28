
"""
SELECT user_id, AVG(spend) as avg_spend
FROM transactions
WHERE date >= '2023-01-01'
GROUP BY user_id;
"""