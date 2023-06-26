import time
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from typing import Annotated
from sqlalchemy.orm import Session
from db.db import get_db
from models.models import User

SECRET_KEY = 'e5403b2e10d566848d1d8a3b6909348f'
ALGORITHM = 'HS256'
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


class AuthUtil:

    @staticmethod
    def create_access_token(username: str,
                            user_id: int,
                            user_role: bool):
        expire = time.time() + 36000 # если что это 10 часов действия токена )
        post_jwt = {'sub': username,
                    'role': user_role,
                    'id': user_id,
                    'exp': expire}
        return jwt.encode(post_jwt, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    async def decode_jwt(token: OAuth2PasswordBearer = Depends(oauth2_scheme)):
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username_after_decode: str = payload.get("sub")
        user_id_after_decode = payload.get("id")
        user_role_after_decode = payload.get("role")
        if username_after_decode is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        return {"username": username_after_decode,
                "id": user_id_after_decode,
                "role": user_role_after_decode}

    @staticmethod
    def check_user(username: str, password: str, db: Session = Depends(get_db)):
        user = db.query(User).filter(User.username == username).first()
        if not user:
            raise HTTPException(status_code=401, detail="пользователь не совпадает")
        if user.password != password:
            raise HTTPException(status_code=401, detail="пароль не совпадает")
        return user


user_dependency = Annotated[dict, Depends(AuthUtil.decode_jwt)]
