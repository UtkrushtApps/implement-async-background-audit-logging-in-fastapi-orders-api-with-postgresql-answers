# database.py
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

# Example DSN: postgresql+asyncpg://user:password@localhost/mydatabase
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost/ecoorder")

engine = create_async_engine(DATABASE_URL, echo=False, future=True)

AsyncSessionLocal = sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

def get_session():
    # Dependency
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        session.close()
