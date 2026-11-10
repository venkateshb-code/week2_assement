from app.database import SessionLocal
from app.models import Customer, Product
from app.operations import place_order, get_stock
from app.mongo_events import store_five_order_events


def seed_demo_data():
    with SessionLocal() as session:
        try:
            customer = session.get(Customer, 1)
            if customer is None:
                session.add(Customer(
                    id=1, name="Arun", email="arun@example.com",
                    phone="9876543210"
                ))

            product = session.get(Product, 1)
            if product is None:
                session.add(Product(
                    id=1, name="Laptop", price=50000, stock=10
                ))
            session.commit()
        except Exception:
            session.rollback()
            raise


def reset_demo_stock():
    # Resets the demo product so the successful and rollback examples
    # both start with exactly 10 units. Use only in this demo database.
    with SessionLocal() as session:
        try:
            product = session.get(Product, 1)
            product.stock = 10
            session.commit()
        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_demo_data()
    reset_demo_stock()

    place_order(customer_id=1, product_id=1, qty=2)

    # Reset only to make the rollback proof independently start at stock 10.
    reset_demo_stock()
    before = get_stock(1)

    try:
        place_order(customer_id=1, product_id=1, qty=2, force_error=True)
    except RuntimeError as exc:
        print(f"Forced failure: rolled back ({exc})")

    after = get_stock(1)
    print(f"Stock before failure: {before}")
    print(f"Stock after failure: {after}")

    store_five_order_events()
