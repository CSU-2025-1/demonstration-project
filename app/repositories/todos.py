from db.models import TodoItem
from repositories.base import BaseRepository
from schemas.todos import TodoCreate
from sqlalchemy.orm import Session


class TodosRepository(BaseRepository[TodoItem, TodoCreate]):
    def __init__(self, db: Session):
        super().__init__(db, TodoItem)

    def get_all(self, user_id: int | None = None) -> list[TodoItem]:
        query = self.db.query(self.model)
        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        return query.all()

    def get_by_id(self, id: int, user_id: int | None = None) -> TodoItem | None:
        query = self.db.query(self.model).filter(self.model.id == id)
        if user_id is not None:
            query = query.filter(self.model.user_id == user_id)
        return query.first()

    def create(self, obj_in: TodoCreate, user_id: int) -> TodoItem:
        db_obj = self.model(**obj_in.dict(), user_id=user_id)
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj
