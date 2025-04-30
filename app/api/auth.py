from db.database import get_db
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from schemas.users import UserCreate
from services.auth import AuthService
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)


def get_auth_service(db: Session = Depends(get_db)) -> AuthService:
    return AuthService(db)


@router.post("/token")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(get_auth_service),
):
    return service.authenticate_user(form_data.username, form_data.password)


@router.post("/register")
def register(
    user_in: UserCreate,
    service: AuthService = Depends(get_auth_service),
):
    return service.register_user(user_in)
