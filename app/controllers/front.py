import datetime
from io import BytesIO
import os
from typing import List, Dict

import fastapi
from fastapi import Depends, FastAPI, Request, Response
from pydantic import parse_obj_as
from sqlalchemy import distinct, desc
from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from crud.geolocation import GeoLocationCRUD

from crud.materials import MaterialCRUD
from starlette import status
from app.utils.auth import AuthUtil, user_dependency, bcrypt_context
from utils.utils import response

from app.controllers.materials import user_dependency
from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import User, GeoLocation, Material, Repair, Accessories

from app.payload.request import InvoiceCreateRequest
from docx import Document
from fastapi.responses import FileResponse

"""
выдаем на фронт OUT 
Session = Depends(get_db) - единораазовые обращения к бд
"""

templates = Jinja2Templates(directory="templates")


class FrontMainController:

    # эндпоинт что бы отслеживать валидность токена
    @staticmethod
    async def ping(user: user_dependency):
        return Response("ok", media_type="text/plain")

    @staticmethod
    async def generate_invoice(
            materials: InvoiceCreateRequest) -> FileResponse:  # генерируем ворд файл из таблицы списания
        directory = "invoices"
        if not os.path.exists(directory):
            os.makedirs(directory)
        out_name = os.path.join(directory, datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S") + ".docx")

        document = Document()
        par = document.add_paragraph()
        par.add_run('Акт на списание Материальных средств ЗАО «РЕНЕЙССАНС КОНСТРАКШН»').bold = True
        par.alignment = 1

        par = document.add_paragraph()
        par.add_run('(компьютеры, оргтеника, периферийное оборудование)').bold = True
        par.alignment = 1

        par = document.add_paragraph()
        par.add_run('№______________ от ' + datetime.datetime.now().strftime("%Y.%m.%d")).bold = True
        par.alignment = 1

        table = document.add_table(1, 6)
        table.style = 'Table Grid'
        heading_cells = table.rows[0].cells
        heading_cells[0].text = '№'
        heading_cells[1].text = 'ID'
        heading_cells[2].text = 'Category'
        heading_cells[3].text = 'Title'
        heading_cells[4].text = 'Description'
        heading_cells[5].text = 'Date'

        for item in materials.data:
            row_cells = table.add_row().cells
            row_cells[0].text = item[0]
            row_cells[1].text = item[1]
            row_cells[2].text = item[2]
            row_cells[3].text = item[3]
            row_cells[4].text = item[4]
            row_cells[5].text = item[5]

        par = document.add_paragraph()
        par = document.add_paragraph()
        par = document.add_paragraph()
        par.add_run('Подпись руководителя IT отдела _______________________________').bold = True
        par.alignment = 1

        document.save(out_name)
        return FileResponse(out_name)

    @staticmethod
    async def index(db: Session = Depends(get_db), request: Request = None, t: str = None):

        out: Dict = {}
        materials = await MaterialCRUD.list_of_materials(db=db)
        out[0] = jsonable_encoder(materials)

        # подсчет активов
        out["count_warehouse"] = await GeoLocationCRUD.get_materials_at_warehouses(db=db)

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
        # popo = "123"
        # print(bcrypt_context.hash(popo))
        return templates.TemplateResponse("auth.html", {"request": request})

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

    @staticmethod
    async def instructions(db: Session = Depends(get_db),
                           request: Request = None,
                           t: str = None  # jwt токен
                           ):
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        out: Dict = {}
        out["token"] = t
        out["username"] = result["username"]
        out["role"] = result["role"]

        return templates.TemplateResponse("instructions.html", {"request": request, "data": out})

    @staticmethod
    async def only_one_card(material_id,
                            request: Request = None,
                            t: str = None,  # jwt токен
                            db: Session = Depends(get_db)):

        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        material_card = jsonable_encoder(db.query(Material).filter(Material.id == material_id).first())
        material_geo1 = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).order_by(desc(GeoLocation.date_time)).all()

        current_geo = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).order_by(
            desc(GeoLocation.date_time)).all()[0]

        for item in material_geo1:
            item.date_time = item.date_time.strftime("%Y-%m-%d")

        date_time = material_card['date_time']
        datetime_obj = datetime.datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S.%f")
        formatted_date_time = datetime_obj.strftime("%Y-%m-%d %H:%M")

        out: Dict = {}
        out["token"] = t
        out["one_material"] = material_card
        out["geo_material"] = material_geo1
        out["repairs"] = GeoLocationCRUD.list_of_repair(material_id, db)
        print(GeoLocationCRUD.list_of_repair(material_id, db))
        out["date_time_f"] = formatted_date_time
        out["current_place"] = current_geo.place
        out["current_user"] = current_geo.client_mail
        out["current_status"] = current_geo.status

        return templates.TemplateResponse("one_material.html", {"request": request, "data": out})

    @staticmethod
    async def repairs_page(request: Request = None,
                           t: str = None,  # jwt токен
                           db: Session = Depends(get_db)):

        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        products = db.query(Repair).filter(Repair.id.in_(GeoLocationCRUD.list_of_active_repair(db))).all()

        out: Dict = {}
        out["token"] = t
        out["actives_in_repair"] = products
        out["count_repair"] = len(products)

        return templates.TemplateResponse("repair_page.html", {"request": request, "data": out})

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

        for item in materials_for_trash:
            item.date_time = item.date_time.strftime("%Y-%m-%d")


        out[0] = materials_for_trash
        out["token"] = t
        out["count_for_trash"] = len(materials_for_trash)

        return templates.TemplateResponse("trash_page.html", {"request": request, "data": out})
