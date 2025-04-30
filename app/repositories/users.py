from db.models import User
from repositories.base import BaseRepository
from schemas.users import UserCreate
from sqlalchemy.orm import Session


class UsersRepository(BaseRepository[User, UserCreate]):
    def __init__(self, db: Session):
        super().__init__(db, User)

    def get_by_username(self, username: str) -> User | None:
        return self.db.query(User).filter(User.username == username).first()

    def get_by_id(self, user_id: int) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user
