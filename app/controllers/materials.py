import datetime
import logging
import os, platform
import shutil
from typing import Annotated
import uuid
from fastapi import Depends, File, UploadFile, HTTPException
from pydantic import parse_obj_as
from sqlalchemy import update
from sqlalchemy.orm import Session

from crud.materials import MaterialCRUD
from utils.utils import response
from app.payload.response import MaterialUploadResponse
from app.utils.auth import AuthUtil, user_dependency
from db import db
from db.db import get_db
from payload.request import MaterialCreateRequest, MaterialGetRequest, MaterialUpdateDescriptionRequest, \
    MaterialDeleteRequest
from models.models import Material, GeoLocation, LogItem
from models.models import User, Material



logging.basicConfig(level=logging.INFO,
                    filename="log.log",
                    filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")



class MaterialsController:

    # создание карточки актива
    @staticmethod
    async def create(body: MaterialCreateRequest,
                     user: user_dependency,
                     db: Session = Depends(get_db)):

        logging.info(f"username: , data: {body}")

        # if body.place is not None and body.client_mail is None:
        #     raise HTTPException(status_code=403, detail="Вы ввели место, но не ввели почту нового ответственного")
        # if body.place is None and body.client_mail is not None:
        #     raise HTTPException(status_code=403, detail="Вы ввели почту, но не ввели место расположения актива")
        # if body.place is not None and body.client_mail is not None:
        #     material = Material(id=body.id, user_id=user.get("id"), category=body.category, title=body.title,
        #                         description=body.description, date_time=datetime.datetime.now())
        #     db.add(material)
        #     db.commit()
        #     geolocation = GeoLocation(material_id=material.id, place=body.place, client_mail=body.client_mail,
        #                               date_time=datetime.datetime.now())
        #     db.add(geolocation)
        #     db.commit()
        #     material.geolocation_id = geolocation.id
        #     db.commit()
        # else:
        #     material = Material(id=body.id, user_id=user.get("id"), category=body.category, title=body.title,
        #                         description=body.description, date_time=datetime.datetime.now())
        #     db.add(material)
        #     db.commit()

        material = Material(id=body.id, user_id=user.get("username"), category=body.category, title=body.title,
                            description=body.description, date_time=datetime.datetime.now())
        db.add(material)
        db.commit()
        geolocation = GeoLocation(material_id=material.id, place=body.place, client_mail=user.get("username"),
                                  status="хранение", date_time=datetime.datetime.now())
        db.add(geolocation)
        db.commit()
        material.geolocation_id = geolocation.id
        db.commit()

        return parse_obj_as(MaterialUploadResponse, material)



    # получение карточки по айди
    @staticmethod
    async def get(body: MaterialGetRequest,
                  db: Session = Depends(get_db),
                  user: User = Depends(AuthUtil.decode_jwt)):
        material = await MaterialCRUD.get(id=body.id, db=db)
        return response(data=material)

    # обновление описания карточки
    @staticmethod
    async def update_description(body: MaterialUpdateDescriptionRequest,
                                 db: Session = Depends(get_db),
                                 user: User = Depends(AuthUtil.decode_jwt)):
        logging.info(f"username: , data: {body}")
        material = await MaterialCRUD.update_description(id=body.id, description=body.description, db=db)
        return response(data=material)

    @staticmethod
    async def update_title(title: str,
                           id_of_material: int,
                           user: user_dependency,
                           db: Session = Depends(get_db),
                           ):

        if user.get("role"):
            try:
                stmt = update(Material).where(Material.id == id_of_material).values(title=title)
                db.execute(stmt)
                db.commit()
                return f'Актив {id_of_material} изменен. Новый тайтл - {title}'
            except:
                return "такого активана нет"
        else:
            return "Недостаточно прав"


    # выводим список активов
    @staticmethod
    async def list_of_materials(db: Session = Depends(get_db),
                                user: User = Depends(AuthUtil.decode_jwt)):
        materials = await MaterialCRUD.list_of_materials(db=db)
        return response(data=materials)

    # удаление актива
    @staticmethod
    async def delete_material(id_for_delete,
                              # body: MaterialDeleteRequest,
                              db: Session = Depends(get_db),
                              user: User = Depends(AuthUtil.decode_jwt)):
        if user.get("role"):
            try:
                material = db.query(Material).filter(Material.id == id_for_delete).first()
                db.delete(material)
                db.commit()

                try:
                    destination_folder = f'\\\\fs-mo\\ADMINS\\Photo_warehouse\\photos\\{id_for_delete}'
                    # Удаляем папку на сервере
                    shutil.rmtree(destination_folder)

                    # логируем
                    create_geo_event = LogItem(kind_table="АКТИВЫ",
                                               user_id=user["id"],
                                               passive_id=id_for_delete,
                                               modified_cols="удаление",
                                               values_of_change=f'папка с фото удалена с сервера',
                                               date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                               )
                    db.add(create_geo_event)
                    db.commit()

                except Exception as e:
                    # логируем
                    create_geo_event = LogItem(kind_table="Расположение активов",
                                               user_id=user["id"],
                                               passive_id=id_for_delete,
                                               modified_cols="удаление",
                                               values_of_change=f'при удалении папки с сервера возникла ошибка - {e}',
                                               date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                               )
                    db.add(create_geo_event)
                    db.commit()

                return response(data={"INFO": f'Актив с ID {id_for_delete} удален успешно'})
            except Exception as e:
                return f'актива с id = {id_for_delete} не найдено'
        else:
            return "Недостаточно прав"


    @staticmethod
    async def get_last_update(user: User = Depends(AuthUtil.decode_jwt)):
        if user.get("role"):
            log_file_path = os.path.join(os.path.dirname(__file__), "../log.log")  # Путь к файлу логов

            # Читаем содержимое файла логов
            with open(log_file_path, "r") as file:
                log_content = file.read()

            return log_content
        else:
            return "You don't have permission"


    @staticmethod
    async def upload_photo(material_id,
                           file: UploadFile = File(...),
                           db: Session = Depends(get_db),
                           user: User = Depends(AuthUtil.decode_jwt)):

        # Путь к папке назначения на сервере
        destination_folder = ""
        if (platform.system() == "Windows"):
            destination_folder = os.path.join("\\\\fs-mo\\ADMINS\\Photo_warehouse\\photos",str(material_id))
        else:
            destination_folder = os.path.join("photos",str(material_id))
        # Подставьте путь к папке назначения на сервере

        # Проверяем, существует ли папка назначения, и создаем ее при необходимости
        os.makedirs(destination_folder, exist_ok=True)

        # Генерируем уникальное имя файла
        unique_filename = str(uuid.uuid4()) + os.path.splitext(file.filename)[1]

        # Создаем путь для сохранения файла в папке назначения
        destination_path = os.path.join(destination_folder, unique_filename)

        # Загружаем файл в папку назначения
        with open(destination_path, "wb") as buffer:
            buffer.write(await file.read())

        # логируем авторизацию
        autorisation_event = LogItem(kind_table="Активы",
                                     user_id=user.get("username"),
                                     passive_id=material_id,
                                     modified_cols="добавление фото для актива из WEB",
                                     values_of_change=None,
                                     date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                     )
        db.add(autorisation_event)
        db.commit()

        return {"message": f'Photo successfully added'}

