import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()


def store_five_order_events():
    client = MongoClient(os.getenv("MONGO_URI", "mongodb://localhost:27017/"))
    try:
        db = client[os.getenv("MONGO_DB", "order_management")]
        events = db["order_events"]
        events.delete_many({"demo_batch": "orm_migrations_demo"})

        rows = [
            {"customer_id": 1, "order_id": 101, "amount": 500},
            {"customer_id": 1, "order_id": 102, "amount": 300},
            {"customer_id": 1, "order_id": 103, "amount": 200},
            {"customer_id": 1, "order_id": 104, "amount": 150},
            {"customer_id": 1, "order_id": 105, "amount": 150},
        ]
        now = datetime.now(timezone.utc)
        for row in rows:
            row.update(event="order_created", created_at=now,
                       demo_batch="orm_migrations_demo")
        events.insert_many(rows)
        print("5 order events inserted successfully")

        pipeline = [
            {"$match": {"demo_batch": "orm_migrations_demo"}},
            {"$group": {
                "_id": "$customer_id",
                "total_amount": {"$sum": "$amount"},
                "total_orders": {"$sum": 1},
            }},
            {"$sort": {"_id": 1}},
        ]
        print("\nMongoDB Customer Totals:")
        for result in events.aggregate(pipeline):
            print(f"customer {result['_id']} -> {result['total_amount']}")
            print(f"  orders: {result['total_orders']}")
    finally:
        client.close()
