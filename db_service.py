from datetime import datetime
from typing import Any

from pydantic import BaseModel, Json
from sqlalchemy.orm import Session

from model import Cache


class CacheRes(BaseModel):
    id: str = None
    response: Json[Any] = None
    created_at: datetime = None
    updated_at: datetime = None

    class ConfigDict:
        from_attributes = True


def select(db: Session, id: str):
    return db.query(Cache).filter(Cache.id == id).first()


def insert_minfo(db: Session, minfo: CacheRes):
    db_item = Cache(**minfo.model_dump())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def create_new_log(db: Session, schema: CacheRes):
    return insert_minfo(db=db, minfo=schema)


def fetch_one_log(db: Session, model_id: str):
    db_item = select(db, id=model_id)
    return db_item
