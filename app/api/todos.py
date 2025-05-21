from typing import List
import random
import asyncio
from core.auth import get_current_user, require_minimum_role
from db.database import get_db
from db.models import User
from fastapi import APIRouter, Depends
from repositories.todos import TodosRepository
from schemas.todos import TodoCreate, TodoItem
from services.todos import TodosService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/todos",
    tags=["todos"],
)


def get_todos_service(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> TodosService:
    repository = TodosRepository(db)
    return TodosService(repository, current_user)


@router.get("", response_model=List[TodoItem])
async def read_todos(
    service: TodosService = Depends(get_todos_service),
    _: User = Depends(require_minimum_role("user")),
):

    await asyncio.sleep(random.uniform(0.1, 1.0))
    return service.get_all()


@router.get("/{todo_id}", response_model=TodoItem)
def read_todo(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    _: User = Depends(require_minimum_role("user")),
):
    return service.get(todo_id)


@router.post("", response_model=TodoItem)
async def create_todo(
    todo: TodoCreate,
    service: TodosService = Depends(get_todos_service),
    _: User = Depends(require_minimum_role("user")),
):
    return service.create(todo)


@router.put("/{todo_id}", response_model=TodoItem)
def update_todo(
    todo_id: int,
    todo: TodoCreate,
    service: TodosService = Depends(get_todos_service),
    _: User = Depends(require_minimum_role("user")),
):
    return service.update(todo_id, todo)


@router.delete("/{todo_id}", response_model=TodoItem)
def delete_todo(
    todo_id: int,
    service: TodosService = Depends(get_todos_service),
    _: User = Depends(require_minimum_role("user")),
):
    return service.delete(todo_id)
