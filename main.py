# main.py
from fastapi import FastAPI, BackgroundTasks, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import NoResultFound
from models import Base, Order
from database import engine, get_session
from audit import create_order_audit_log
from typing import Optional
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# --- Pydantic Schemas ---
class OrderStatusUpdate(BaseModel):
    new_status: str
    reason: Optional[str] = None

class OrderResponse(BaseModel):
    id: int
    status: str

# --- Startup: create tables ---
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# --- API endpoint to change order status ---
@app.patch("/orders/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    update: OrderStatusUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
):
    # Get the order
    result = await session.execute(select(Order).where(Order.id == order_id))
    order = result.scalars().first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    old_status = order.status
    new_status = update.new_status
    if old_status == new_status:
        raise HTTPException(status_code=400, detail="Order is already in the requested status.")

    # Update status
    order.status = new_status
    await session.commit()
    await session.refresh(order)

    # Schedule audit log to be recorded in the background
    background_tasks.add_task(
        create_order_audit_log,
        order_id,
        old_status,
        new_status,
        update.reason
    )

    return OrderResponse(id=order.id, status=order.status)

# (Optional) Example endpoint to fetch audit log for an order for demonstration
def _order_audit_log_query(order_id: int):
    from models import OrderAuditLog
    from sqlalchemy import select
    return select(OrderAuditLog).where(OrderAuditLog.order_id == order_id).order_by(OrderAuditLog.timestamp.asc())

@app.get("/orders/{order_id}/audit_logs")
async def get_order_audit_logs(order_id: int, session: AsyncSession = Depends(get_session)):
    from models import OrderAuditLog
    result = await session.execute(_order_audit_log_query(order_id))
    logs = result.scalars().all()
    return [
        {
            "timestamp": log.timestamp,
            "old_status": log.old_status,
            "new_status": log.new_status,
            "reason": log.reason,
        } for log in logs
    ]

# (For manual testing)
if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
