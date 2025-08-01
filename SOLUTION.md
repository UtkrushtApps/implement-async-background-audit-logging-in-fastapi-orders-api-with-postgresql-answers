# Solution Steps

1. Design the database schema: add a new 'order_audit_logs' table with a foreign key to 'orders', storing order_id, old_status, new_status, timestamp, and reason. Enforce constraints to ensure old_status != new_status and reference order_id.

2. Implement the SQLAlchemy models in 'models.py' for Order (if not present already) and OrderAuditLog, adding relationships between them for ORM usability.

3. Set up asynchronous database configuration in 'database.py', using SQLAlchemy's create_async_engine, with a factory for AsyncSession objects.

4. Implement asynchronous audit logging logic in 'audit.py'. Define a function to insert an OrderAuditLog entry using an async DB session. Add error handling for reliability.

5. In 'main.py', modify the order status update endpoint to: (a) select and update the Order's status; (b) schedule the async audit logging function in a FastAPI BackgroundTask, passing order_id, old_status, new_status, and optional reason.

6. Optionally, provide an endpoint to query audit logs by order, for testing and demonstration.

7. On app startup, ensure tables are created by running 'Base.metadata.create_all'.

8. Test to ensure that changing an order status creates an audit log asynchronously: (1) update a status, (2) query logs, and (3) see that API response is fast and logs are accurate.

