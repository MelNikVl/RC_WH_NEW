import logging
from typing import Any


# добавляет в ответ в свагере - status
def response(data: Any, status: bool = True):
    if data is None:
        data = {}
    return {"data": data, "status": status}
