import datetime, os, smtplib, ssl, shutil, fastapi
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from typing import Dict, List, Optional

from fastapi import Depends, Request, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.crud.geolocation import GeoLocationCRUD
from app.crud.materials import MaterialCRUD
from app.payload.request import GeoLocationCreateRequest, GeoLocationGetByIdRequest, RepairCreateRequest, \
    RepairStopRequest, RepairDetailsRequest, AccessoriesRequest
from starlette import status
from app.utils.utils import response
from app.controllers.front import templates
from app.utils.auth import AuthUtil, user_dependency
from db.db import get_db
from models.models import User, LogItem, GeoLocation, Material, Trash, Repair, Accessories


class AccessoriesController:

    @staticmethod
    async def accessories_page(db: Session = Depends(get_db),
                               request: Request = None,
                               t: str = None  # jwt токен
                               ):
        # проверка токена на валидность и если он не вализный - переадресация на авторизацию
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        out: Dict = {}

        accessories = db.query(Accessories).all()
        for item in accessories:
            item.date_time = item.date_time.strftime("%Y-%m-%d %H:%M")

        out[0] = accessories
        out["token"] = t
        out["count_accessories"] = len(accessories)

        return templates.TemplateResponse("accessories_page.html", {"request": request, "data": out})

    @staticmethod
    async def create(body: AccessoriesRequest,
                     user: user_dependency,
                     db: Session = Depends(get_db),
                     ):

        accessories = Accessories(category=body.category,
                                  title=body.title,
                                  count=body.count,
                                  responsible=user.get("username"),
                                  place=body.place,
                                  date_time=datetime.datetime.now())

        new_acc_event = LogItem(kind_table="Комплектующие",
                                   user_id=user["username"],
                                   passive_id=body.title,
                                   modified_cols="добавление комплектующих",
                                   values_of_change=f'категория: {body.category},'
                                                    f' количество {body.count}',
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   )

        db.add(new_acc_event)
        db.add(accessories)
        db.commit()

        return response(data="комплектующие добавлены", status=True)

    @staticmethod
    async def change_count(title, count,
                           user: user_dependency,
                           db: Session = Depends(get_db),
                           ):
        repair = db.query(Accessories).filter(Accessories.title == title).first()
        if repair.count == 0:
            return response(data="этих комплектующих нет", status=False)
        else:
            repair.count = repair.count - int(count)

            new_acc_event = LogItem(kind_table="Комплектующие",
                                    user_id=user["username"],
                                    passive_id=title,
                                    modified_cols="изменения количества комплектующих",
                                    values_of_change=f'новое количество: {count}',
                                    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    )

            db.add(new_acc_event)
            db.commit()

            return response(data="комплектующие взяты", status=True)