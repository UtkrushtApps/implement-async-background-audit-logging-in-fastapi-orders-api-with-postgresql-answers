# audit.py
from database import AsyncSessionLocal
from models import OrderAuditLog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger("order_audit")

async def create_order_audit_log(order_id: int, old_status: str, new_status: str, reason: str = None):
    async with AsyncSessionLocal() as session:
        await _insert_audit_log(session, order_id, old_status, new_status, reason)

async def _insert_audit_log(session: AsyncSession, order_id: int, old_status: str, new_status: str, reason: str = None):
    log = OrderAuditLog(
        order_id=order_id,
        old_status=old_status,
        new_status=new_status,
        reason=reason,
    )
    session.add(log)
    try:
        await session.commit()
    except SQLAlchemyError as e:
        await session.rollback()
        logger.error(f"Failed to save audit log for order_id={order_id}: {e}")
