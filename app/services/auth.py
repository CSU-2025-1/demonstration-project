from datetime import timedelta

from core.auth import create_access_token, get_password_hash, verify_password
from fastapi import HTTPException
from repositories.users import UsersRepository
from schemas.users import UserCreate
from sqlalchemy.orm import Session


class AuthService:
    def __init__(self, db: Session):
        self._db = db
        self._users_repo = UsersRepository(db)

    def authenticate_user(self, username: str, password: str) -> dict:
        user = self._users_repo.get_by_username(username)
        if not user or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=400, detail="Invalid credentials")

        token = create_access_token(
            data={"sub": str(user.id)},
            expires_delta=timedelta(minutes=30),
        )

        return {
            "access_token": token,
            "token_type": "bearer",
        }

    def register_user(self, user_in: UserCreate) -> dict:
        existing = self._users_repo.get_by_username(user_in.username)
        if existing:
            raise HTTPException(status_code=400, detail="Username already taken")

        hashed_pw = get_password_hash(user_in.password)
        user = self._users_repo.create_user(
            username=user_in.username,
            hashed_password=hashed_pw,
        )

        token = create_access_token(data={"sub": str(user.id)})
        return {"access_token": token, "token_type": "bearer"}
