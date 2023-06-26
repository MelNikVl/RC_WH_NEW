import random
import string
import sys

sys.path.append("..")
from fastapi import HTTPException
from pydantic import parse_obj_as
from typing import List
from payload.response import MaterialUploadResponse
from models.models import Material


'''
класс CRUD - create read update delete
здесь бизнес логика для энпоинтов
'''

class MaterialCRUD:
    # Получение карточки по айди
    @staticmethod
    async def get(db, id: int):
        material = db.query(Material).filter(Material.id == id).all()
        if len(material) == 0:
            raise HTTPException(status_code=404, detail="Модели с таким айди не найдено")
        return parse_obj_as(MaterialUploadResponse, material[0])

    # ОБновление описания карточки
    @staticmethod
    async def update_description(db, id: int, description: str):
        material = db.query(Material).filter(Material.id == id).all()
        if len(material) == 0:
            raise HTTPException(status_code=404, detail="Модели с таким айди не найдено")
        else:
            material[0].description = description
            db.flush()
            db.commit()
            return parse_obj_as(MaterialUploadResponse, material[0])

    # Получения всего списка материалов
    @staticmethod
    async def list_of_materials(db):
        materials = db.query(Material).all()
        return parse_obj_as(List[MaterialUploadResponse], materials)  # засовывывает в шаблон данные

    @staticmethod
    def generate_alphanum_random_string(length):
        letters_and_digits = string.ascii_letters + string.digits
        rand_string = ''.join(random.sample(letters_and_digits, length))
        return rand_string


