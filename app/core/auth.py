from datetime import datetime, timedelta

from db.database import get_db
from db.models import User
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from repositories.users import UsersRepository
from sqlalchemy.orm import Session
from elasticapm.traces import capture_span
from elasticapm import set_context

SECRET_KEY = "wk07h2sssdERBmu9RfyBFSr0lAFiyiJb"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

ROLE_PRIORITY = {
    "loh": 0,
    "user": 1,
    "admin": 2,
}


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def require_minimum_role(min_role: str):
    def checker(user: User = Depends(get_current_user)):
        with capture_span("auth:role-decoding", span_type="auth"):
            if ROLE_PRIORITY.get(user.role, 0) < ROLE_PRIORITY.get(min_role, 0):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Access denied. '{min_role}' role required.",
                )
            return user

    return checker


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        with capture_span("auth:decode-jwt", span_type="auth"):
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_id: int = payload.get("sub")
            if user_id is None:
                raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = UsersRepository(db).get_by_id(user_id)
    if user is None:
        raise credentials_exception

    return user
