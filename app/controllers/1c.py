import requests
from requests.auth import HTTPBasicAuth

url = "https://dc-fs-erp/rc_upp/ws/IT.1cws?wsdl"
basic = HTTPBasicAuth('rc-spb\\bpsupport', 'Bp2684')

def get_material():
    resp = requests.get(url, auth=basic, verify=False)
    print(resp.text)