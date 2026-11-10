from sqlalchemy import select
from app.database import SessionLocal
from app.models import Customer, Product, Order


def place_order(customer_id: int, product_id: int, qty: int, force_error: bool = False):
    """Update stock and insert an order in one atomic transaction."""
    if qty <= 0:
        raise ValueError("Quantity must be greater than zero")

    with SessionLocal() as session:
        try:
            product = session.execute(
                select(Product)
                .where(Product.id == product_id)
                .with_for_update()
            ).scalar_one_or_none()

            if product is None:
                raise ValueError("Product not found")

            if session.get(Customer, customer_id) is None:
                raise ValueError("Customer not found")

            if product.stock < qty:
                raise ValueError("Insufficient stock")

            old_stock = product.stock
            product.stock -= qty
            session.add(Order(customer_id=customer_id, product_id=product_id, qty=qty))

            # Test-only failure, deliberately after the stock update.
            if force_error:
                session.flush()
                raise RuntimeError("Forced transaction failure")

            session.commit()
            print(f"Order placed: stock {old_stock} -> {product.stock}")
        except Exception:
            session.rollback()
            raise


def get_stock(product_id: int) -> int:
    with SessionLocal() as session:
        product = session.get(Product, product_id)
        if product is None:
            raise ValueError("Product not found")
        return product.stock
