from sqlalchemy import Column, String, JSON, DateTime, func

from database import Base


class Cache(Base):
    __tablename__ = "icp_cache"

    id = Column(String, primary_key=True, index=True)
    response = Column(JSON)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now())