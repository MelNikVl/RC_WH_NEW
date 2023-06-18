import datetime
import json
from typing import Dict

from fastapi import Depends, Request
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from crud.geolocation import GeoLocationCRUD
from payload.request import GeoLocationCreateRequest, GeoLocationGetByIdRequest
from starlette.responses import FileResponse
from utils.utils import response

from app.controllers.front import templates
from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import User, LogItem, GeoLocation, Material, Trash

"""
контроллер 
то класс который принимает в себя параметры из эндпоинта, котоыре передаются ему по опредленному юрл
который указан в роутс
"""


class GeoLocationController:
    @staticmethod
    async def create(body: GeoLocationCreateRequest,
                     db: Session = Depends(get_db),
                     user: User = Depends(AuthUtil.decode_jwt)):
        geolocation = await GeoLocationCRUD.create(material_id=body.material_id,
                                                   place=body.place,
                                                   client_mail=body.client_mail,
                                                   status=body.status,
                                                   db=db)

        # логируем
        create_geo_event = LogItem(kind_table="Расположение активов",
                                   user_id=user["username"],
                                   passive_id=body.material_id,
                                   modified_cols="новое расположение",
                                   values_of_change=f'новое место: {body.place},'
                                                    f' новый статус: {body.status},'
                                                    f' новый ответственный: {body.client_mail}',
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   )
        db.add(create_geo_event)
        db.commit()

        return response(data=geolocation)

    @staticmethod
    async def get_by_id(body: GeoLocationGetByIdRequest, db: Session = Depends(get_db),
                        user: User = Depends(AuthUtil.decode_jwt)):
        geolocation = await GeoLocationCRUD.get_by_id(material_id=body.material_id, db=db)
        return response(data=geolocation)

    @staticmethod
    async def add_to_trash(material_id,
                           user: User = Depends(AuthUtil.decode_jwt),
                           db: Session = Depends(get_db)):
        add_to_trash = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).all()[-1]
        add_to_trash.status = "на списание"
        db.commit()

        # логируем
        create_geo_event = LogItem(kind_table="Расположение активов",
                                   user_id=user["username"],
                                   passive_id=material_id,
                                   modified_cols="status",
                                   values_of_change="актив добавлен к списанию",
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   )
        db.add(create_geo_event)
        db.commit()

        return response(data=f'актив {material_id} добавлен в список на списание')

    @staticmethod
    async def download_file_for_trash():
        # Укажите путь и имя файла, который нужно скачать
        file_path = "llll.xlsx"

        # Верните объект FileResponse для скачивания файла
        return FileResponse(file_path, filename="имя_файла_при_скачивании")

    @staticmethod
    async def trash_page(db: Session = Depends(get_db),
                         request: Request = None,
                         t: str = None  # jwt токен
                         ):

        out: Dict = {}

        get_materials_for_trash = db.query(GeoLocation).filter(GeoLocation.status == "на списание").all()
        materials_for_trash = []
        count_for_trash = 0
        for i in get_materials_for_trash:
            flag = False
            if db.query(Material).filter(Material.id == i.material_id).first():
                for j in materials_for_trash:
                    if (j.id == i.material_id):
                        flag = True
                        break
                if not flag:
                    materials_for_trash.append(db.query(Material).filter(Material.id == i.material_id).first())
                    count_for_trash += 1

        out[0] = materials_for_trash
        out["token"] = t
        out["count_for_trash"] = count_for_trash

        return templates.TemplateResponse("trash_page.html", {"request": request, "data": out})

    @staticmethod
    async def send_to_trash_finally(db: Session = Depends(get_db),
                                    user: User = Depends(AuthUtil.decode_jwt)):
        get_materials_for_trash = db.query(GeoLocation).filter(GeoLocation.status == "на списание").all()
        materials_for_trash = []
        for i in get_materials_for_trash:
            flag = False
            if db.query(Material).filter(Material.id == i.material_id).first():
                for j in materials_for_trash:
                    if (j.id == i.material_id):
                        flag = True
                        break
                if not flag:
                    materials_for_trash.append(db.query(Material).filter(Material.id == i.material_id).first())

        for y in materials_for_trash:
            moving = []

            material_moving = db.query(GeoLocation).filter(GeoLocation.material_id == y.id).all()
            for m in material_moving:
                # moving.append(f'--- место: {m.place}, ответственный: {m.client_mail}, дата перемещения: {m.date_time}')
                moving.append({"место": m.place, "ответственный": m.client_mail, "дата перемещения": m.date_time})

            create_new_trash_archive = Trash(user_id=user.get("username"),
                                             material_id=y.id,
                                             category=y.category,
                                             title=y.title,
                                             description=y.description,
                                             # moving=json.dumps(moving, ensure_ascii=False),
                                             moving=str(jsonable_encoder(moving)),
                                             date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            )
            db.add(create_new_trash_archive)

            material_for_delete = db.query(Material).filter(Material.id == y.id).first()
            db.delete(material_for_delete)

            geo_for_delete = db.query(GeoLocation).filter(GeoLocation.material_id == y.id).first()
            db.delete(geo_for_delete)

            db.commit()

            return response(data=f'активы {materials_for_trash} списаны')
