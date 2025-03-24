from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

PRIMARY_DB_URL = os.getenv("PRIMARY_DB_URL")
REPLICA_DB_URL = os.getenv("REPLICA_DB_URL")

engine_primary = create_engine(PRIMARY_DB_URL)
engine_replica = create_engine(REPLICA_DB_URL)

SessionPrimary = sessionmaker(bind=engine_primary)
SessionReplica = sessionmaker(bind=engine_replica)

Base = declarative_base()


def get_db_write():
    db = SessionPrimary()
    try:
        yield db
    finally:
        db.close()


def get_db_read():
    db = SessionReplica()
    try:
        yield db
    finally:
        db.close()
