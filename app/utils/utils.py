import logging
import os
from typing import Any, Dict
from static_data import main_folder
import re
import json

logging.basicConfig(level=logging.INFO,
                    filename="log.log",
                    filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


# добавляет в ответ в свагере - status
def response(data: Any, status: bool = True):
    if data is None:
        data = {}
    return {"data": data, "status": status}


# фотки к каждому товару
def get_first_photo(material_id: str):
    fold = main_folder + "\\photos\\" + material_id
    file_list = os.listdir(fold)

    out: Dict = {}
    out["len_of_files"] = len(file_list)

    photo_files = [f for f in file_list if f.endswith(('.jpg', '.png', '.jpeg'))]
    if len(photo_files) > 1:
        out["picture"] = photo_files[1]
        return out
    else:
        out["picture"] = photo_files[0]
        return out


regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


def email_validate(email):
    if re.fullmatch(regex, email):
        return True
    return False


class EmailConfig:
    @staticmethod
    def write(value: [str]):
        data: dict = {"emails": value}
        with open('config.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.close()
    @staticmethod
    def get_emails():
        f = open('config.json')
        data = json.load(f)
        emails = data["emails"] or []
        return emails
