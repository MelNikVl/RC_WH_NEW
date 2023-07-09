import logging
import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from typing import Any

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


gmail_login = "testpython20231@gmail.com"
gmail_pass = "seprtpqgzfwgcsvs"
addresses = ["shumerrr@yandex.ru", "dklsgj@gmail.com", "raven10maxtgc@gmail.com"]

def send_email(invoice):
    message = MIMEMultipart("")
    message["Subject"] = "Списание акивов"
    message["From"] = gmail_login
    message['To'] = ", ".join(addresses)
    html = """\
    <html>
      <body>
        <p>Накладная по списанию: </p>
      </body>
    </html>
    """
    part2 = MIMEText(html, "html")
    message.attach(part2)

    with open(invoice, "rb") as file:
        part = MIMEApplication(file.read(), Name=basename(invoice))
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(invoice)
        message.attach(part)

    serv = smtplib.SMTP("smtp.gmail.com", 587)
    # smtp_server.ehlo()
    serv.starttls()
    serv.login(gmail_login, gmail_pass)
    serv.sendmail(gmail_login, addresses, message.as_string())


def get_first_photo(material_id):
    fold = main_folder + f"\\photos\\{material_id}"
    file_list = os.listdir(fold)
    photo_files = [f for f in file_list if f.endswith(('.jpg', '.png', '.jpeg'))]
    if len(photo_files) > 1:
        return photo_files[1]
    else:
        return photo_files[0]
