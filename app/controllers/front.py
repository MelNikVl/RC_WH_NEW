import datetime
from io import BytesIO
import os
from typing import List, Dict

import fastapi
from fastapi import Depends, FastAPI, Request, Response
from pydantic import parse_obj_as
from sqlalchemy import distinct
from sqlalchemy.orm import Session

from fastapi.templating import Jinja2Templates
from fastapi.encoders import jsonable_encoder
from crud.geolocation import GeoLocationCRUD

from crud.materials import MaterialCRUD
from starlette import status
from app.utils.auth import AuthUtil, user_dependency
from utils.utils import response

from app.controllers.materials import user_dependency
from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import User, GeoLocation, Material, Repair

from app.payload.request import InvoiceCreateRequest
from docx import Document
from fastapi.responses import FileResponse

"""
выдаем на фронт OUT 
Session = Depends(get_db) - единораазовые обращения к таблицам
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
        material_geo = jsonable_encoder(db.query(GeoLocation).filter(GeoLocation.material_id == material_id).all())

        list_for_geo = []
        for i in material_geo:
            list_for_geo.append(i)

        out: Dict = {}
        out["token"] = t
        out["one_material"] = material_card
        out["geo_material"] = material_geo
        out["repairs"] = GeoLocationCRUD.list_of_repair(material_id, db)

        return templates.TemplateResponse("one_material.html", {"request": request, "data": out})
