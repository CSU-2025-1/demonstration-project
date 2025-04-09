from typing import Generic, Type, TypeVar, List
from sqlalchemy.orm import Session
from pydantic import BaseModel

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType]):
    def __init__(self, db: Session, model: Type[ModelType]):
        self.db = db
        self.model = model

    def get_all(self) -> List[ModelType]:
        return self.db.query(self.model).all()

    def get_by_id(self, id: int) -> ModelType:
        return self.db.query(self.model).filter(self.model.id == id).first()

    def create(self, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.dict())
        self.db.add(db_obj)
        self.db.commit()
        self.db.refresh(db_obj)
        return db_obj

    def update(self, db_obj: ModelType, obj_in: CreateSchemaType) -> ModelType:
        for field, value in obj_in.dict().items():
            setattr(db_obj, field, value)
        self.db.commit()
        return db_obj

    def delete(self, db_obj: ModelType) -> ModelType:
        self.db.delete(db_obj)
        self.db.commit()
        return db_obj
