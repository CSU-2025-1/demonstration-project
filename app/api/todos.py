from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from services.todos import TodosService
from repositories.todos import TodosRepository
from schemas.todos import TodoCreate, TodoItem
from typing import List

router = APIRouter()


def get_todos_service(db: Session = Depends(get_db)) -> TodosService:
    repository = TodosRepository(db)
    return TodosService(repository)


@router.get("/todos", response_model=List[TodoItem])
def read_todos(service: TodosService = Depends(get_todos_service)):
    return service.get_all()


@router.get("/todos/{todo_id}", response_model=TodoItem)
def read_todo(todo_id: int, service: TodosService = Depends(get_todos_service)):
    return service.get(todo_id)


@router.post("/todos", response_model=TodoItem)
def create_todo(todo: TodoCreate, service: TodosService = Depends(get_todos_service)):
    return service.create(todo)


@router.put("/todos/{todo_id}", response_model=TodoItem)
def update_todo(
    todo_id: int, todo: TodoCreate, service: TodosService = Depends(get_todos_service)
):
    return service.update(todo_id, todo)


@router.delete("/todos/{todo_id}", response_model=TodoItem)
def delete_todo(todo_id: int, service: TodosService = Depends(get_todos_service)):
    return service.delete(todo_id)
