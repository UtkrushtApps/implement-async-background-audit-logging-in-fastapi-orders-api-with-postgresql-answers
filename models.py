# models.py
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, CheckConstraint
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, nullable=False)
    status = Column(String(32), nullable=False, default="placed")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    # NB: Other fields as needed by your app

    audit_logs = relationship("OrderAuditLog", back_populates="order")

class OrderAuditLog(Base):
    __tablename__ = "order_audit_logs"
    id = Column(Integer, primary_key=True)
    order_id = Column(Integer, ForeignKey("orders.id", ondelete='CASCADE'), nullable=False, index=True)
    old_status = Column(String(32), nullable=False)
    new_status = Column(String(32), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)
    reason = Column(Text, nullable=True)

    order = relationship("Order", back_populates="audit_logs")
    __table_args__ = (
        CheckConstraint("old_status != new_status", name="check_status_change"),
    )
