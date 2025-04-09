from core.producer import send_rpc_event
from repositories.todos import TodosRepository
from schemas.todos import TodoCreate, TodoItem
from services.base import BaseService
from services.caching_service import CachingService

CACHE_TTL = 60  # Время жизни кэша в секундах


class TodosService(BaseService, CachingService):
    def __init__(self, repository: TodosRepository):
        self._repository = repository

    def create(self, obj_in: TodoCreate) -> TodoItem:
        new_todo = self._repository.create(obj_in)
        send_rpc_event("todo_created", {"id": new_todo.id, "title": new_todo.title})

        # Инвалидация кэша после создания новой задачи
        self.invalidate_cache("todos")
        self.invalidate_cache(f"todo:{new_todo.id}")
        return new_todo

    def get(self, id: int) -> TodoItem:
        @self.cache_result(f"todo:{id}", ttl=CACHE_TTL)
        def fetch_todo():
            todo = self._repository.get_by_id(id)
            if not todo:
                raise ValueError(f"Task with ID {id} not found")
            send_rpc_event("todo_requested", {"id": todo.id, "title": todo.title})
            return todo

        return fetch_todo()

    def get_all(self):
        @self.cache_result("todos", ttl=CACHE_TTL)
        def fetch_todos():
            todos = self._repository.get_all()
            return todos

        return fetch_todos()

    def update(self, id: int, obj_in: TodoCreate) -> TodoItem:
        updated = self._repository.update(id, obj_in)
        if not updated:
            raise ValueError(f"Task with ID {id} not found")

        send_rpc_event("todo_updated", {"id": updated.id, "title": updated.title})

        # Инвалидация кэша после обновления задачи
        self.invalidate_cache(f"todo:{id}")
        self.invalidate_cache("todos")
        return updated

    def delete(self, id: int) -> TodoItem:
        deleted = self._repository.delete(id)
        if not deleted:
            raise ValueError(f"Task with ID {id} not found")

        send_rpc_event("todo_deleted", {"id": deleted.id, "title": deleted.title})

        # Инвалидация кэша после удаления задачи
        self.invalidate_cache(f"todo:{id}")
        self.invalidate_cache("todos")
        return deleted
