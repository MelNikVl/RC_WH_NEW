import datetime
import json
import os
import shutil
from typing import Dict, List

import fastapi
from fastapi import Depends, Request, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session

from app.crud.geolocation import GeoLocationCRUD
from payload.request import GeoLocationCreateRequest, GeoLocationGetByIdRequest
from starlette import status
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

        # проверка токена на валидность и если он не вализный - переадресация на авторизацию
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)
        out: Dict = {}
        materials_for_trash = await GeoLocationCRUD.get_materials_for_trash(db=db)
        out[0] = materials_for_trash
        out["token"] = t
        out["count_for_trash"] = len(materials_for_trash)

        return templates.TemplateResponse("trash_page.html", {"request": request, "data": out})

    @staticmethod
    async def send_to_trash_finally(photos: List[UploadFile],
                                    db: Session = Depends(get_db),
                                    invoice: UploadFile = File(...),
                                    user: User = Depends(AuthUtil.decode_jwt)):
        # положить туда накладную подгруженную
        # создать там папку для фоток самой утилизации
        # создать папку для папок где хранятся фото списанной техники. (и копировать туда их)
        # отправить письмо на 2 адреса с накладной и ссылкой на папку списания
        # все это дело залогировать

        # считаем количество товаров + записываем их в materials_for_trash

        materials_for_trash = await GeoLocationCRUD.get_materials_for_trash(db=db)

        timestamp = str(datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "_активов_" + str(len(materials_for_trash)))
        destination_folder = os.path.join("\\\\fs-mo\\ADMINS\\Photo_warehouse\\archive_after_utilization", timestamp)
        photo_folder = os.path.join(destination_folder, "photos")
        old_photo_folder = os.path.join(destination_folder, "material_photos")
        os.makedirs(destination_folder, exist_ok=True)
        os.makedirs(photo_folder, exist_ok=True)
        os.makedirs(old_photo_folder, exist_ok=True)
        out_filename = os.path.join(destination_folder, invoice.filename)

        with open(out_filename, "wb") as buffer:
            buffer.write(await invoice.read())
        for photo in photos:
            out_photo_path = os.path.join(photo_folder, photo.filename)
            with open(out_photo_path, "wb") as buffer:
                buffer.write(await photo.read())

        for i in materials_for_trash:
            folder_to_move = os.path.join("\\\\fs-mo\\ADMINS\\Photo_warehouse\\photos", str(i.id))
            destination = os.path.join(old_photo_folder,str(i.id))
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(folder_to_move, destination, dirs_exist_ok=True)
            shutil.rmtree(folder_to_move)


        # копируем перемещения и данные об активах в таблицу треша и потом удаляем все из таблиц где они были.
        # так же перемещаем папки с фото в папку списания
        for y in materials_for_trash:
            moving = []
            id_for_logging = []
            material_moving = db.query(GeoLocation).filter(GeoLocation.material_id == y.id).all()
            for m in material_moving:
                moving.append({"место": m.place, "ответственный": m.client_mail, "дата перемещения": m.date_time})
                id_for_logging.append(m.material_id)

            create_new_trash_archive = Trash(user_id=user.get("username"),
                                             material_id=y.id,
                                             category=y.category,
                                             title=y.title,
                                             description=y.description,
                                             moving=str(jsonable_encoder(moving)),
                                             date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                            )
            db.add(create_new_trash_archive)

            material_for_delete = db.query(Material).filter(Material.id == y.id).first()
            db.delete(material_for_delete)

            geo_for_delete = db.query(GeoLocation).filter(GeoLocation.material_id == y.id).first()
            db.delete(geo_for_delete)

            db.commit()

        # логируем
        create_geo_event = LogItem(kind_table="Списание",
                                   user_id=user["username"],
                                   passive_id=0000000,
                                   modified_cols="перемещение в архив списания",
                                   values_of_change=f'активы: {str(jsonable_encoder(id_for_logging))} были списаны, '
                                                    f'записи об их местоположении теперь находятся в таблице архива. '
                                                    f'Фото данной техники перемещены в '
                                                    f'папку - {destination_folder}',
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   )
        db.add(create_geo_event)
        db.commit()

        return response(data=f'активы списаны')

    @staticmethod
    async def archive_trash_page(db: Session = Depends(get_db),
                                 request: Request = None,
                                 t: str = None  # jwt токен
                                 ):
        # проверка токена на валидность и если он не вализный - переадресация на авторизацию
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        out: Dict = {}
        materials_for_archive_trash = db.query(Trash).all()
        out[0] = materials_for_archive_trash
        out["token"] = t

        return templates.TemplateResponse("archive_trash_page.html", {"request": request, "data": out})
