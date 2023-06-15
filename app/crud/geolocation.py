import sys
from typing import List

from sqlalchemy import desc

sys.path.append("..")
import datetime

from fastapi import HTTPException
from pydantic import parse_obj_as
from models.models import Material, GeoLocation
from payload.response import GeoLocationUploadResponse

# from app.payload.response import GeoLocationUploadResponse

'''
класс CRUD - create read update delete
это класс в котором хранятся методы, котоыре мы вызываем внутри контроллера, котоыре выполняют бизнес логику
'''


class GeoLocationCRUD:

    @staticmethod
    async def create(material_id: int, place: str, client_mail: str, status: str, db):
        material = db.query(Material).filter(Material.id == material_id).all()
        if len(material) == 0:
            raise HTTPException(status_code=404, detail="Карточки актива с таким айди не найдено")
        else:
            geolocation = GeoLocation(material_id=material_id, place=place, client_mail=client_mail,
                                      status=status, date_time=datetime.datetime.now())
            db.add(geolocation)
            db.commit()
            material[0].geolocation_id = geolocation.id
            db.commit()
            return parse_obj_as(GeoLocationUploadResponse, geolocation)

    @staticmethod
    async def get_by_id(material_id: int, db):
        material = db.query(Material).filter(Material.id == material_id).all()
        if len(material) == 0:
            raise HTTPException(status_code=404, detail="Карточки актива с таким айди не найдено")
        else:
            geolocation = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).all()
            return parse_obj_as(List[GeoLocationUploadResponse], geolocation)


    @staticmethod
    async def current_place(material_id: int, db):
        material = db.query(Material).filter(Material.id == material_id).all()
        if len(material) == 0:
            raise HTTPException(status_code=404, detail="Карточки актива с таким айди не найдено")
        else:
            geolocation = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).order_by(desc(GeoLocation.date_time)).all()
            if len(geolocation) == 0:
                return None
            else:
                return parse_obj_as(GeoLocationUploadResponse, geolocation[0])
