import sys
from typing import List

from sqlalchemy import desc, distinct

sys.path.append("..")
import datetime

from fastapi import HTTPException
from pydantic import parse_obj_as
from models.models import Material, GeoLocation, Trash, Repair
from payload.response import GeoLocationUploadResponse
from fastapi.encoders import jsonable_encoder

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
    async def get_materials_for_trash(db) -> List[Material]:
        all_materials_for_trash = db.query(GeoLocation).filter(GeoLocation.status == "на списание").all()
        materials_for_trash = []
        for i in all_materials_for_trash:
            flag = False
            if db.query(Material).filter(Material.id == i.material_id).first():
                for j in materials_for_trash:
                    if (j.id == i.material_id):
                        flag = True
                        break
                if not flag:
                    materials_for_trash.append(db.query(Material).filter(Material.id == i.material_id).first())
        return materials_for_trash

    @staticmethod
    async def get_materials_in_work(db) -> List[Material]:
        all_materials_in_work = db.query(GeoLocation).filter(GeoLocation.status == "Выдан").all()
        materials_in_work = []
        for i in all_materials_in_work:
            flag = False
            if db.query(Material).filter(Material.id == i.material_id).first():
                for j in materials_in_work:
                    if (j.id == i.material_id):
                        flag = True
                        break
                if not flag:
                    materials_in_work.append(db.query(Material).filter(Material.id == i.material_id).first())
        return materials_in_work

    @staticmethod
    async def get_materials_at_warehouses(db) -> List[Material]:
        all_materials_at_warehouses = db.query(GeoLocation).filter(GeoLocation.status == "хранение").all()
        materials_at_warehouses = []
        for i in all_materials_at_warehouses:
            flag = False
            if db.query(Material).filter(Material.id == i.material_id).first():
                for j in materials_at_warehouses:
                    if (j.id == i.material_id):
                        flag = True
                        break
                if not flag:
                    materials_at_warehouses.append(db.query(Material).filter(Material.id == i.material_id).first())
        return materials_at_warehouses


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


    @staticmethod
    def list_of_repair(material_id, db):
        all_rep_unique_id = db.query(distinct(Repair.repair_unique_id)).filter(Repair.material_id == material_id).all()
        unique_ids = [item[0] for item in all_rep_unique_id]
        # uniq_id_val = {}
        uniq_id_val = []
        for i in unique_ids:
            # rt = 1
            last = []
            for ie in db.query(Repair).filter(Repair.repair_unique_id == i).all():
                rrrr = jsonable_encoder(ie)
                print(ie)
                last.append(rrrr)
            uniq_id_val.append(last)
            # uniq_id_val[rt] = last
            # rt += 1
        print(uniq_id_val)
        return uniq_id_val
