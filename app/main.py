from api import todos
from db import database, models
from fastapi import FastAPI

# Инициализация базы данных
models.Base.metadata.create_all(bind=database.engine_shard1)
models.Base.metadata.create_all(bind=database.engine_shard2)

app = FastAPI()

# Подключение маршрутов
app.include_router(todos.router)
