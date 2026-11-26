
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )


def get_order_status(order_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT order_id, customer_id, status, shipped_date
            FROM orders
            WHERE order_id = %s
        """

        cursor.execute(query, (order_id,))
        result = cursor.fetchone()

        if result is None:
            return {"error": "Order not found"}

        return {
            "order_id": result[0],
            "customer_id": result[1],
            "status": result[2],
            "shipped_date": str(result[3]) if result[3] else None
        }

    finally:
        conn.close()


def get_customer_orders(customer_id):
    conn = get_connection()

    try:
        cursor = conn.cursor()

        query = """
            SELECT order_id, customer_id, order_date, status
            FROM orders
            WHERE customer_id = %s
            ORDER BY order_date
        """

        cursor.execute(query, (customer_id,))
        results = cursor.fetchall()

        return [
            {
                "order_id": row[0],
                "customer_id": row[1],
                "order_date": str(row[2]) if row[2] else None,
                "status": row[3]
            }
            for row in results
        ]

    finally:
        conn.close()
