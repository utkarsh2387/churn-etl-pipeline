import sqlite3

conn = sqlite3.connect('data/churn_warehouse.db')
result = conn.execute(
    "SELECT anomaly_flag, COUNT(*) FROM customers_clean GROUP BY anomaly_flag"
).fetchall()
print(result)
conn.close()