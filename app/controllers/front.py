from typing import List, Dict

import fastapi
from fastapi import Depends, FastAPI, Request, Response
from pydantic import parse_obj_as
from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from crud.geolocation import GeoLocationCRUD

from crud.materials import MaterialCRUD
from starlette import status
from app.utils.auth import AuthUtil, user_dependency
from utils.utils import response

from app.controllers.materials import user_dependency
from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import User

"""
выдаем на фронт OUT 
Session = Depends(get_db) - единораазовые обращения к таблицам
"""

templates = Jinja2Templates(directory="templates")


class FrontMainController:

    # эндпоинт что бы отслеживать валидность токена
    @staticmethod
    async def ping(user: user_dependency):
        return Response("ok", media_type="text/plain")

    @staticmethod
    async def index(db: Session = Depends(get_db), request: Request = None, t: str = None):
        materials = await MaterialCRUD.list_of_materials(db=db)
        out: Dict = {}
        out[0] = jsonable_encoder(materials)
        try:
            result = await AuthUtil.decode_jwt(t)
            out["username"] = result["username"]
            out["role"] = result["role"]
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        # апендим к основному json еще и местоположение актива из таблицы ГЕО
        for i in range(len(out[0])):
            geolocation_place = await GeoLocationCRUD.current_place(material_id=out[0][i]['id'], db=db)
            if geolocation_place is None:
                out[0][i].update({"geolocation_place": "место не указано"})
                out[0][i].update({"geolocation_status": "статуса нет"})
            else:
                out[0][i].update({"geolocation_place": geolocation_place.place})
                out[0][i].update({"geolocation_status": geolocation_place.status})
        out["token"] = t
        return templates.TemplateResponse("table.html", {"request": request, "data": out})

    @staticmethod
    async def user_auth(db: Session = Depends(get_db),
                        request: Request = None,
                        ):
        return templates.TemplateResponse("auth.html", {"request": request})

    # test 2345

    @staticmethod
    async def admins_page(db: Session = Depends(get_db),
                          request: Request = None,
                          t: str = None  # jwt токен
                          ):
        is_admin = 0
        try:
            result = await AuthUtil.decode_jwt(t)
            is_admin = int(result["role"])
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        if (is_admin):
            out: Dict = {}
            out["token"] = t
            out["users"] = jsonable_encoder(db.query(User).all())
            return templates.TemplateResponse("admins_page.html", {"request": request, "data": out})
        else:
            return fastapi.responses.RedirectResponse('/app', status_code=status.HTTP_301_MOVED_PERMANENTLY)
