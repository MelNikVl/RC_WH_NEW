from fastapi import Depends
from sqlalchemy.orm import Session

from app.utils.auth import user_dependency
from app.utils.utils import response
from db.db import get_db
from models.models import Email


class AdminController:
    @staticmethod
    async def remove_emails(ids: list[int], user: user_dependency, db: Session = Depends(get_db)):
        for id in ids:
            db.query(Email).filter(Email.id == id).delete()
        db.commit()
        return response()

    @staticmethod
    async def create_email(addr:str, role: int, user: user_dependency, db: Session = Depends(get_db)):
        new_email = Email(addr=addr, description=role)
        db.add(new_email)
        db.commit()
        return response()