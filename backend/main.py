from fastapi import FastAPI

from fastapi import Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import User
from src.core import API_NAME

app = FastAPI(title=API_NAME)


@app.get("/")
def read_root() -> dict[str, str]:
    return {"message": "¡Hola desde el backend de ft-transcendence!"}


@app.post("/register/")
def register_user(username: str, email: str,
                  db: Session = Depends(get_db)) -> dict[str, str]:
    new_user = User(username=username, email=email,
                    hashed_password="fake_password")

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": f"New user {new_user.username} was created!"}
