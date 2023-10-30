import requests
from requests import Session
from requests.auth import HTTPBasicAuth
from zeep import Client, Transport
from zeep.wsse import UsernameToken
import inspect

url = "https://dc-fs-erp/rc_upp/ws/IT.1cws?wsdl"
username = "rc-spb\\bpsupport"
password = "Bp2684"
basic = HTTPBasicAuth('rc-spb\\bpsupport', 'Bp2684')
basic_id = "000355389"


def get_material(id: str):
    session = Session()
    session.verify = False
    session.auth = basic
    transport = Transport(session=session)
    client = Client(
        url,
        transport=transport)

    # print(client.service.GetEquipment())
    response = client.service.GetEquipmentInfo(EquipmentID=id)
    from zeep import helpers
    _json = helpers.serialize_object(response, dict)
    # print(_json)
    return _json