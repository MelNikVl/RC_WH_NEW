import datetime

from fastapi import Depends
from sqlalchemy.orm import Session

from crud.geolocation import GeoLocationCRUD
from payload.request import GeoLocationCreateRequest, GeoLocationGetByIdRequest
from utils.utils import response

from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import User, LogItem, GeoLocation

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
                                   user_id=user["id"],
                                   passive_id=body.material_id,
                                   modified_cols="новое расположение",
                                   values_of_change=f'новое место: {body.place},'
                                                    f'новый статус: {body.status},'
                                                    f' новый ответственный: {body.client_mail}',
                                   date_time=datetime.datetime.now()
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
        add_to_trash = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).first()
        add_to_trash.status = "на списание"
        db.commit()
        return response(data=f'актив {material_id} добавлен в список на списание')
