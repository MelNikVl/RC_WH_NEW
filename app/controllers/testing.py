import datetime
import os
import secrets

from fastapi import Depends, UploadFile, File
from sqlalchemy import delete
from sqlalchemy.orm import Session
import shutil
from app.crud.geolocation import GeoLocationCRUD
from app.crud.materials import MaterialCRUD
from app.utils.auth import user_dependency
from db.db import get_db
from models.models import Material, Repair, Accessories, LogItem, GeoLocation
from static_data import main_folder


class TestingController:
    @staticmethod
    async def create_10_iterations(user: user_dependency,
                                   file: UploadFile = File(...),
                                   db: Session = Depends(get_db)):

        for i in range(10):
            new_10_materials = Material(id=i,
                                        user_id=user.get("username"),
                                        category="компьютер",
                                        title=f"pc10{i}",
                                        description="i7 7700, ssd: 500gb, video: GeForce 1060",
                                        date_time=datetime.datetime.now()
                                        )
            # ФОТО
            destination_folder = os.path.join(f'{main_folder}\\photos', str(i))
            os.makedirs(destination_folder, exist_ok=True)
            unique_filename = str(secrets.token_hex(4)) + os.path.splitext(file.filename)[1]
            destination_path = os.path.join(destination_folder, unique_filename)
            with open(destination_path, "wb") as buffer:
                buffer.write(await file.read())

            new_10_geolocation = GeoLocation(material_id=i,
                                             place="тестирование. Склад 1 - полка 1",
                                             client_mail="testing@mail.ru",
                                             status="хранение",
                                             initiator=user.get("username"),
                                             date_time=datetime.datetime.now()
                                             )
            new_10_repair = Repair(material_id=i,
                                   responsible_it_dept_user=user.get("username"),
                                   problem_description="создание карточки актива",
                                   repair_number=1,
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                   repair_status=False,
                                   repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                                   )
            new_10_accessories = Accessories(category="переходник",
                                      title="vga - hdmi",
                                      count=10,
                                      responsible=user.get("username"),
                                      place="создано для теста. склад 1",
                                      date_time=datetime.datetime.now()
                                      )

            new_test_event = LogItem(kind_table="Тестирование",
                                    user_id=user["username"],
                                    passive_id=555555555555,
                                    modified_cols="разные колонки",
                                    values_of_change="добавлено 10 активов, 10 ремонтов, 10 комплектующих",
                                    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                    )

            db.add(new_10_materials)
            db.add(new_10_geolocation)
            db.add(new_10_repair)
            db.add(new_10_accessories)
            db.add(new_test_event)
            db.commit()

        return "все ок. добавлено"

    @staticmethod
    async def delete_all(user: user_dependency,
                         db: Session = Depends(get_db)):
        delete_materials = delete(Material)
        delete_geos = delete(GeoLocation)
        delete_repairs = delete(Repair)
        delete_logs = delete(LogItem)
        delete_asseccories = delete(Accessories)
        db.execute(delete_materials)
        db.execute(delete_geos)
        db.execute(delete_repairs)
        db.execute(delete_logs)
        db.execute(delete_asseccories)
        db.commit()

        return "все ок. все активы удалены"

    @staticmethod
    def delete_folder_contents():
        shutil.rmtree(f'{main_folder}\\photos')
        return "папка фото склада очищена"

