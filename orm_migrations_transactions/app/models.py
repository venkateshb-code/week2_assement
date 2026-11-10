from sqlalchemy import (
    Column, Integer, String, Numeric, ForeignKey, CheckConstraint
)
from sqlalchemy.orm import relationship
from app.database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), nullable=False, unique=True)
    # Added in migration 0002; omit this column when generating migration 0001.
    phone = Column(String(20), nullable=True)

    orders = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan",
    )


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    stock = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("price > 0", name="check_product_price"),
        CheckConstraint("stock >= 0", name="check_product_stock"),
    )

    orders = relationship("Order", back_populates="product")


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    qty = Column(Integer, nullable=False)

    __table_args__ = (
        CheckConstraint("qty > 0", name="check_order_qty"),
    )

    customer = relationship("Customer", back_populates="orders")
    product = relationship("Product", back_populates="orders")
