from sqlalchemy.orm import Session
from db.models import TodoItem
from schemas.todos import TodoCreate
from repositories.base import BaseRepository


class TodosRepository(BaseRepository[TodoItem, TodoCreate]):
    def __init__(self, db: Session):
        super().__init__(db, TodoItem)
