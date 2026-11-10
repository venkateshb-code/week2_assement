import os
import psycopg2


def get_connection():
    return psycopg2.connect(
        host=os.getenv("PGHOST", "localhost"),
        port=os.getenv("PGPORT", "5432"),
        dbname=os.getenv("PGDATABASE", "venkatesh"),
        user=os.getenv("PGUSER", "postgres"),
        password=os.getenv("PGPASSWORD", ""),
    )


def get_orders(customer_id):
    """Fetch orders; the customer_id value is bound separately from SQL."""
    query = """
        SELECT id, customer_id, amount, created_at
        FROM performance_orders
        WHERE customer_id::text = %s
        ORDER BY id;
    """
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(query, (str(customer_id),))
            return cur.fetchall()
    finally:
        conn.close()


if __name__ == "__main__":
    normal_rows = get_orders(1)
    print("Input 1 ->", len(normal_rows), "row(s)")
    for row in normal_rows[:5]:
        print(row)

    attack_rows = get_orders("1 OR 1=1")
    print("Input '1 OR 1=1' ->", len(attack_rows), "row(s)")
    print("Expected: 0 rows")
