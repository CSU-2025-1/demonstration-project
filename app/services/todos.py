from core.logger import logger
from core.producer import send_rpc_event
from db.models import User
from repositories.todos import TodosRepository
from schemas.todos import TodoCreate, TodoItem
from services.base import BaseService
from services.caching_service import CachingService

CACHE_TTL = 60  # Время жизни кэша в секундах


class TodosService(BaseService, CachingService):
    def __init__(self, repository: TodosRepository, current_user: User):
        self._repository = repository
        self._user = current_user

    def create(self, obj_in: TodoCreate) -> TodoItem:
        new_todo = self._repository.create(obj_in, user_id=self._user.id)
        send_rpc_event("todo_created", {"id": new_todo.id, "title": new_todo.title})

        # Инвалидация кэша после создания новой задачи
        self.invalidate_cache("todos")
        self.invalidate_cache(f"todo:{new_todo.id}")
        logger.info(
            "Todo created", extra={"todo_id": new_todo.id, "user_id": self._user.id}
        )
        return new_todo

    def get(self, id: int) -> TodoItem:
        @self.cache_result(f"todo:{id}", ttl=CACHE_TTL)
        def fetch_todo():
            if self._user.role == "admin":
                todo = self._repository.get_by_id(id)
            else:
                todo = self._repository.get_by_id(id, user_id=self._user.id)

            if not todo:
                raise ValueError(f"Task with ID {id} not found")

            send_rpc_event("todo_requested", {"id": todo.id, "title": todo.title})

            logger.info(
                "Todo retrieved",
                extra={"todo_id": todo.id, "user_id": self._user.id},
            )

            return todo

        return fetch_todo()

    def get_all(self):
        @self.cache_result("todos", ttl=CACHE_TTL)
        def fetch_todos():
            if self._user.role == "admin":
                return self._repository.get_all()
            return self._repository.get_all(user_id=self._user.id)

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
