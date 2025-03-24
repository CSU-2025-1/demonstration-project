from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

SHARD1_DB_URL = os.getenv("SHARD1_DB_URL")
SHARD2_DB_URL = os.getenv("SHARD2_DB_URL")

engine_shard1 = create_engine(SHARD1_DB_URL)
engine_shard2 = create_engine(SHARD2_DB_URL)

SessionShard1 = sessionmaker(bind=engine_shard1)
SessionShard2 = sessionmaker(bind=engine_shard2)


def get_db_shard(todo_id: str):
    # Пример: по первому символу UUID
    if todo_id[0] in "01234567":
        db = SessionShard1()
    else:
        db = SessionShard2()
    try:
        yield db
    finally:
        db.close()


def get_all_dbs():
    db1 = SessionShard1()
    db2 = SessionShard2()
    try:
        yield db1, db2
    finally:
        db1.close()
        db2.close()
