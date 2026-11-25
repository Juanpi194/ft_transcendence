from fastapi import FastAPI

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.core.constants import API_NAME
from app.services.follows import follow_user
from app.services.exceptions import SocialError

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


# TODO: Move to a router folder
@app.post("/users/{followed_id}/follow")
def follow_user_main(follower_id: int, followed_id: int,
                     db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        follow = follow_user(db, follower_id, followed_id)
    except SocialError as e:
        raise HTTPException(status_code=409, detail=str(e))
    return {"status": follow.status}
