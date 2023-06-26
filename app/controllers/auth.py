import datetime
import logging

from fastapi import Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import update
from sqlalchemy.orm import Session
from app.payload.request import UserAuth
from db.db import get_db
from app.utils.auth import AuthUtil
from models.models import User, LogItem
from passlib.context import CryptContext

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class AuthController:

    @staticmethod
    async def token(form_data: OAuth2PasswordRequestForm = Depends(),
                    db: Session = Depends(get_db)):

        user_db = AuthUtil.check_user(form_data.username, form_data.password, db)
        if not user_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not valiable user')
        token = AuthUtil.create_access_token(user_db.username, user_db.id, user_db.is_admin)

        # логируем авторизацию
        autorisation_event = LogItem(kind_table="Авторизация",
                                     user_id=user_db.username,
                                     passive_id=user_db.id,
                                     modified_cols="успешная авторизация WEB",
                                     values_of_change=None,
                                     date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                     )
        db.add(autorisation_event)
        db.commit()

        return {'access_token': token, 'type_token': 'bearer'}

    @staticmethod
    async def create_new_user(body: UserAuth,
                              db: Session = Depends(get_db),
                              user: User = Depends(AuthUtil.decode_jwt)
                              ):
        logging.info(f"username: , data: {body}")
        if user.get("role"):
            # ph = bcrypt_context.hash(body.password)
            if db.query(User).filter(User.username == body.username).first():
                return "такой пользователь уже есть"
            else:
                user = User(chat_id=body.chat_id_from_tg, username=body.username,
                            password=body.password, is_admin=body.is_admin)
                db.add(user)
                db.commit()
                return {"success": "success",
                        "user_chat_tg_id": body.chat_id_from_tg,
                        "user_login": body.username,
                        "user_password": body.password}
        else:
            return "недостаточно прав для создания пользователей"

    @staticmethod
    async def make_admin(username: str,
                         user: User = Depends(AuthUtil.decode_jwt),
                         db: Session = Depends(get_db)):
        if user.get("role"):
            update_stmt = update(User).where(User.username == username).values(is_admin=True)
            db.execute(update_stmt)
            db.commit()
            return {"success": f'Пользователь {username} назначен админом'}
        else:
            return {"error": "у вас нет прав на это действие"}

    @staticmethod
    async def get_users(db: Session = Depends(get_db),
                        user: User = Depends(AuthUtil.decode_jwt)):
        if user.get("role"):
            users = db.query(User).all()
            return users
        else:
            return "у вас недостаточно прав для этого действия"

    @staticmethod
    async def delete_user(user_for_delete, db: Session = Depends(get_db), user: User = Depends(AuthUtil.decode_jwt)):
        if user.get("role"):
            value = db.query(User).filter(User.username == user_for_delete).first()
            db.delete(value)
            db.commit()
            return f"пользователь {user_for_delete} успешно удален"
        else:
            return f"У вас нет разрешения для этого действия"

    @staticmethod
    async def telegram_and_app_id(db: Session = Depends(get_db),
                                  user: User = Depends(AuthUtil.decode_jwt)):
        value = db.query(User).filter(User.id == user.get("id")).first()
        return f"Your telegramm ID - {value.chat_id}, " \
               f"ID in this system - {value.id}"

    @staticmethod
    async def get_admins(db: Session = Depends(get_db),
                         user: User = Depends(AuthUtil.decode_jwt)):
        if user.get("role"):
            value = db.query(User).filter(User.is_admin == 1).all()
            return value
        else:
            return f"У вас нет разрешения для этого действия"

    @staticmethod
    async def add_telegramm_id(user_for_tg,
                               chat_id,
                               db: Session = Depends(get_db),
                               user: User = Depends(AuthUtil.decode_jwt)):
        if user.get("role"):
            user_to_update = db.query(User).filter(User.username == user_for_tg).first()
            user_to_update.chat_id = chat_id
            db.commit()
            return f'вы внесли новый чат айди: {chat_id}' \
                   f' телеграмма для пользователя {user_for_tg}'
        else:
            return f"У вас нет разрешения для этого действия"
