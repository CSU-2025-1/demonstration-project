from db.database import Base
from sqlalchemy import Boolean, Column, String
import uuid


class TodoItem(Base):
    __tablename__ = "todos"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, index=True)
    description = Column(String)
    completed = Column(Boolean, default=False)
