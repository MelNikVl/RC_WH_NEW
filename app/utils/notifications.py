import datetime
import secrets
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from os.path import basename

from sqlalchemy.orm import Session

from db.db import get_db
from models.models import Notifications

gmail_login = "testpython20231@gmail.com"
gmail_pass = "seprtpqgzfwgcsvs"


# addresses = ["shumerrr@yandex.ru", "dklsgj@gmail.com"]


class SUBJECT(Enum):
    UTILIZATION = "Списание активов"
    RELOCATION = "Перемещение активов"
    REPAIR = "Ремонт активов"


@staticmethod
def notify(db: Session, subject, addresses: list, invoice=None, materials: list[dict[int, str]] = None):
    unique = secrets.token_hex(8)
    addresses_to = ", ".join(addresses)
    new_notify = Notifications(category=subject.value, user=addresses_to,
                               unique_code=unique, date_time=datetime.datetime.now())
    db.add(new_notify)
    db.commit()
    message = MIMEMultipart("")
    message["Subject"] = subject.value
    message["From"] = gmail_login
    message['To'] = addresses_to
    html = ""
    match subject:
        case SUBJECT.UTILIZATION:
            with open(invoice, "rb") as file:
                part = MIMEApplication(file.read(), Name=basename(invoice))
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(invoice)
                message.attach(part)
            html = """\
                <html>
                  <body>
                    <p>Накладная по списанию: </p>
                    <a href="http://abc.ru/notification_read?unique=123">Уведомлён</a>
                  </body>
                </html>
                """
        case SUBJECT.REPAIR:
            html = f"""\
                <html>
                    <body>
                        <p>Уведомляем Вас о том, что следующий актив был отправлен в ремонт:</p>
                        <p>id: {materials[0]} &nbsp; Номер: {materials[1]}</p>
                        <a href="">Уведомлён</a>
                    </body>
                </html>                        
                """
    part2 = MIMEText(html, "html")
    message.attach(part2)

    serv = smtplib.SMTP("smtp.gmail.com", 587)
    # smtp_server.ehlo()
    serv.starttls()
    serv.login(gmail_login, gmail_pass)
    serv.sendmail(gmail_login, addresses, message.as_string())
