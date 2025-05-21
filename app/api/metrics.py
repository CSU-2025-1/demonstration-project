from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi import Response
from fastapi import APIRouter

router = APIRouter(
    prefix="/metrics",
    tags=["metrics"],
)


@router.get("/")
def metrics():
    data = generate_latest()
    return Response(data, media_type=CONTENT_TYPE_LATEST)
