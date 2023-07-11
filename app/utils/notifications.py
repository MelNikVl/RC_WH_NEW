import datetime
import secrets
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from os.path import basename
from sqlalchemy.orm import Session
from models.models import Notifications
from static_data import host

gmail_login = "testpython20231@gmail.com"
gmail_pass = "seprtpqgzfwgcsvs"


# addresses = ["shumerrr@yandex.ru", "dklsgj@gmail.com"]


class SUBJECT(Enum):
    UTILIZATION = "Списание активов"
    RELOCATION = "Перемещение актива"
    REPAIR = "Ремонт актива"


@staticmethod
def notify(db: Session, subject, addresses: list, invoice=None, materials: list[dict] = None):
    unique = secrets.token_hex(8)
    print(unique)
    addresses_to = ", ".join(addresses)

    message = MIMEMultipart("")
    message["Subject"] = subject.value
    message["From"] = gmail_login
    message['To'] = addresses_to
    html = ""
    match subject:
        case SUBJECT.UTILIZATION:

            new_notify = Notifications(category=subject.value,
                                       user=addresses_to,
                                       unique_code=unique,
                                       date_time=datetime.datetime.now()
                                       )
            db.add(new_notify)
            db.commit()

            with open(invoice, "rb") as file:
                part = MIMEApplication(file.read(), Name=basename(invoice))
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(invoice)
                message.attach(part)
            html = f"""\
                <html>
                  <body>
                    <p>Накладная по списанию в приложении</p>
                    <a href="">Фото утилизации (ссылка)</a>
                    <a href="">Вся документация по списанию от ____ </a>
                  </body>
                </html>
                """
        case SUBJECT.REPAIR:
            html = f"""\
                <html>
                    <body>
                        <p>Уведомляем Вас о том, что следующий актив был взят в ремонт:</p>
                        <p>id: {materials[0]} &nbsp; Номер: {materials[1]} --- {materials[2]}</p>
                        <a href="">Уведомлён</a>
                        <p>Если у вас возникли вопросы - напишите пожалуйста нам на общую почту +RCSPBADMINS</p>
                    </body>
                </html>                        
                """
        case SUBJECT.RELOCATION:
            new_notify = Notifications(category=f'{subject.value} {materials[0]}',
                                       user=addresses_to,
                                       unique_code=unique,
                                       date_time=datetime.datetime.now()
                                       )
            db.add(new_notify)
            db.commit()
            html = f"""\
                        <html>
                            <body>
                                <p>Уведомляем Вас о том, что следующий актив был перемещен на Ваше имя:</p>
                                <p>id: {materials[0]} &nbsp; Номер: {materials[1]}</p>
                                <p>Характеристики: {materials[2]}</p>
                                <p>Инициатор перемещения: {materials[4]}.</p>
                                <p>Планируемый статус после перемещения: {materials[3]}</p>
                                <a href="{host}/app/notification_answer?unique_code={unique}&material_id={materials[0]}">Уведомлен</a>
                                <p>Если у вас возникли вопросы - напишите пожалуйста нам на общую почту +RCSPBADMINS</p>
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


