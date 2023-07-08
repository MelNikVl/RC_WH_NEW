import os
import sys
import datetime
from typing import List, Dict
from sqlalchemy import desc, distinct, func
from fastapi import HTTPException
from pydantic import parse_obj_as
from models.models import Material, GeoLocation, Repair, Trash
from app.payload.response import GeoLocationUploadResponse
from fastapi.encoders import jsonable_encoder
from static_data import main_folder

sys.path.append("..")

class GeoLocationCRUD:

    @staticmethod
    async def create(material_id: int, place: str, client_mail: str, status: str, initiator: str, db):
        material = db.query(Material).filter(Material.id == material_id).all()
        if len(material) == 0:
            raise HTTPException(status_code=404, detail="Карточки актива с таким айди не найдено")
        else:
            geolocation = GeoLocation(material_id=material_id, place=place, client_mail=client_mail,
                                      status=status, date_time=datetime.datetime.now(), initiator=initiator)
            db.add(geolocation)
            db.commit()
            material[0].geolocation_id = geolocation.id
            db.commit()
            return parse_obj_as(GeoLocationUploadResponse, geolocation)

    @staticmethod
    async def get_materials_for_trash(db) -> List[Material]:
        all_materials_for_trash = db.query(GeoLocation).filter(GeoLocation.status == "списание").all()
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
    async def get_materials_at_warehouses(db):

        # Запрос для нахождения последних перемещений каждого товара
        subquery = db.query(GeoLocation.material_id, func.max(GeoLocation.date_time).label('max_date_time')). \
            group_by(GeoLocation.material_id).subquery()
        query = db.query(GeoLocation).join(subquery, GeoLocation.material_id == subquery.c.material_id). \
            filter(GeoLocation.date_time == subquery.c.max_date_time)

        latest_movements = query.all()

        material_all = db.query(Material).count()

        out: Dict = {}
        warehouse_count = 0
        get_out_count = 0
        repair_count = 0
        trash_count = 0

        for i in latest_movements:
            if i.status == "хранение":
                warehouse_count += 1
            elif i.status == "выдан":
                get_out_count += 1
            elif i.status == "ремонт":
                repair_count += 1
            elif i.status == "списание":
                trash_count += 1

        out["all_count"] = material_all
        out["warehouse_count"] = warehouse_count
        out["get_out_count"] = get_out_count
        out["repair_count"] = repair_count
        out["trash_count"] = trash_count

        return out

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
            geolocation = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).order_by(
                desc(GeoLocation.date_time)).all()
            if len(geolocation) == 0:
                return None
            else:
                return parse_obj_as(GeoLocationUploadResponse, geolocation[0])

    @staticmethod
    def list_of_repair(material_id, db):
        # формируем список уникальных айди ремонтов 1 товара - сначала последние
        all_rep_unique_id = db.query(distinct(Repair.repair_unique_id)) \
            .filter(Repair.material_id == material_id) \
            .order_by(desc(Repair.date_time)) \
            .all()
        unique_ids = [item[0] for item in all_rep_unique_id]
        uniq_id_val = []
        for i in unique_ids:
            last = []
            for ie in db.query(Repair).filter(Repair.repair_unique_id == i).all():
                rrrr = jsonable_encoder(ie)
                last.append(rrrr)
            uniq_id_val.append(last)
        return uniq_id_val

    @staticmethod
    def list_of_arch_trash(db):
        # формируем список уникальных айди ремонтов 1 товара - сначала последние
        all_trash_unique_id = db.query(distinct(Trash.trash_unique_id)).order_by(desc(Trash.date_time)).all()
        uniq_id_val = []
        for i in all_trash_unique_id:
            List = []
            for i in db.query(Trash).filter(Trash.trash_unique_id == i[0]).all():
                List.append(i)
            uniq_id_val.append(List)

        return uniq_id_val

    @staticmethod
    def list_of_active_repair(db):
        # Получение последнего идентификатора обращения для каждого уникального material_id
        last_ids = db.query(Repair.material_id, func.max(Repair.id), Repair.repair_status).group_by(
            Repair.material_id).all()

        list_active_repairs = []

        # Вывод последнего идентификатора обращения для каждого material_id
        for material_id, last_id, repair_status in last_ids:
            if repair_status:
                list_active_repairs.append(last_id)

        return list_active_repairs

    @staticmethod
    async def upload_file_to_repair(material_id_to_repair, file):
        destination_folder = os.path.join(f"{main_folder}\\photos", str(material_id_to_repair))
        destination_folder1 = os.path.join(destination_folder, "Repairs")
        os.makedirs(destination_folder1, exist_ok=True)

        # Создаем путь для сохранения файла в папке назначения
        destination_path = os.path.join(destination_folder1, str(datetime.datetime.now()))

        # Загружаем файл в папку назначения
        with open(destination_path, "wb") as buffer:
            buffer.write(await file.read())
