import datetime

import requests
from fastapi import Depends
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport
from zeep.wsse import UsernameToken
import inspect

from app.utils.auth import AuthUtil
from models.models import User, LogItem, GeoLocation, Material, Trash, Repair

from db.db import get_db
from models.models import LogItem

url = "https://dc-fs-erp/rc_upp/ws/IT.1cws?wsdl"
username = "rc-spb\\bpsupport"
password = "Bp2684"
basic = HTTPBasicAuth('rc-spb\\bpsupport', 'Bp2684')
basic_id = "000355389"

# def last_x_days():
#     session = Session()
#     session.verify = False
#     session.auth = basic
#     transport = Transport(session=session)
#     client = Client(
#         url,
#         transport=transport)
#     print(client.service.GetEquipment(DepthDays=10))

def get_by_responsible():
    session = Session()
    session.verify = False
    session.auth = basic
    transport = Transport(session=session)
    client = Client(
        url,
        transport=transport)
    print(client.service.GetEquipmentOfResponsible(220032))

def get_material(id: str,
                 user: User = Depends(AuthUtil.decode_jwt),
                 db: Session = Depends(get_db)):
    # get_by_responsible(); return
    # last_x_days()
    # return
    session = Session()
    session.verify = False
    session.auth = basic
    transport = Transport(session=session)
    client = Client(
        url,
        transport=transport)

    # print(client.service.GetEquipment(10))
    response = client.service.GetEquipmentInfo(EquipmentID=id)

    # логируем авторизацию
    autorisation_event = LogItem(kind_table="Запрос в 1с",
                                 user_id=user["username"],
                                 passive_id=f'актив {id}',
                                 modified_cols=None,
                                 values_of_change=None,
                                 date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                 )
    db.add(autorisation_event)
    db.commit()

    print(response)
    from zeep import helpers
    _json = helpers.serialize_object(response, dict)
    _json["success"] = True
    # print(_json)
    return _json