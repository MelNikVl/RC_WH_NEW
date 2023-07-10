import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from typing import Any, Dict

from static_data import main_folder

logging.basicConfig(level=logging.INFO,
                    filename="log.log",
                    filemode="w",
                    format="%(asctime)s - %(levelname)s - %(message)s")


# добавляет в ответ в свагере - status
def response(data: Any, status: bool = True):
    if data is None:
        data = {}
    return {"data": data, "status": status}



def get_first_photo(material_id):
    fold = main_folder + f"\\photos\\{material_id}"
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
