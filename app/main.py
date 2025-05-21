from api import auth, todos, metrics
from db import database, models
from fastapi import FastAPI
from prometheus_client import Counter, Histogram
from elasticapm.contrib.starlette import make_apm_client, ElasticAPM
import elasticapm

elasticapm.instrument()

# Инициализация базы данных
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(debug=True)

apm = make_apm_client(
    {
        "SERVICE_NAME": "todos-app",
        "SERVER_URL": "	https://9ef4f0c366104414ae851b8dca472c54.apm.us-central1.gcp.cloud.es.io:443",
        "SECRET_TOKEN": "exeEUZZ0koQo75fCQh",
        "ENVIRONMENT": "development",
        "LOG_LEVEL": "DEBUG",
    }
)
app.add_middleware(ElasticAPM, client=apm)

# -----------------

HTTP_REQUESTS = Counter(
    "http_requests_total", "Total HTTP requests", ["method", "endpoint", "http_status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP request latency", ["method", "endpoint"]
)


# @app.middleware("http")
# async def metrics_middleware(request, call_next):
#     method = request.method
#     path = request.url.path
#     with REQUEST_LATENCY.labels(method, path).time():
#         response = await call_next(request)
#     HTTP_REQUESTS.labels(method, path, response.status_code).inc()
#     return response


# Подключение маршрутов
app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(metrics.router)
