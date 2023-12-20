import datetime
import secrets
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from enum import Enum
from os.path import basename
from sqlalchemy.orm import Session

from app.utils.utils import EmailConfig
from models.models import Notifications
from static_data import host

# gmail_login = "testpython20231@gmail.com"
# gmail_pass = "seprtpqgzfwgcsvs"

gmail_login = "it.wh@rencons.com"
gmail_pass = "tznppgeklmillvha"



class SUBJECT(Enum):
    UTILIZATION = "Списание активов"
    RELOCATION = "Перемещение актива"
    REPAIR = "Ремонт актива"


@staticmethod
async def notify(db: Session, subject, addresses: list, invoice=None, material: []=None):
    unique = secrets.token_hex(8)
    addresses_to = ", ".join(addresses)

    message = MIMEMultipart("")
    message["Subject"] = subject.value
    message["From"] = gmail_login
    message['To'] = addresses_to

    message2 = MIMEMultipart("")
    message2["Subject"] = subject.value
    message2["From"] = gmail_login

    html = ""
    html2 = None
    match subject:
        case SUBJECT.UTILIZATION:
            with open(invoice, "rb") as file:
                part = MIMEApplication(file.read(), Name=basename(invoice))
                part['Content-Disposition'] = 'attachment; filename="%s"' % basename(invoice)
                message.attach(part)
            html = f"""\
                <html>
                  <body>
                    <p>Накладная по списанию в приложении</p>
                    <a href="">Документация по списанию \it-wh\it_warehouse_docs</a>
                  </body>
                </html>
                """
        case SUBJECT.REPAIR:
            html = f"""\
                <html>
                    <body>
                        <p>Уведомляем Вас о том, что следующий актив был взят в ремонт:</p>
                        <p>id: {material[0]} &nbsp; Номер: {material[1]} --- {material[2]}</p>
                        <p>Если согласны с действием перемещения актива на Вас, 
                        нажмите пожалуйста кнопку ниже. Если нет - напишите пожалуйста нам на 
                        общую почту: +RCSPBADMINS</p>
                        <a href="{host}/app/notification_answer?unique_code={unique}&material_id={material[0]}">Уведомлен</a>
                        <p>Так же если у вас возникли вопросы, можете их задать по адресу: +RCSPBADMINS</p>
                    </body>
                </html>                        
                """
        case SUBJECT.RELOCATION:
            html = f"""\
                        <html>
                            <body>
                                <p>Уведомляем Вас о том, что следующий актив был перемещен на Ваше имя:</p>
                                <p>id: {material[0]} &nbsp; Номер: {material[1]}</p>
                                <p>Характеристики: {material[2]}</p>
                                <p>Инициатор перемещения: {material[4]}.</p>
                                <p>Планируемый статус после перемещения: {material[3]}</p>
                                <p>Если согласны с действием перемещения актива на Вас, 
                                нажмите пожалуйста кнопку ниже. Если нет - напишите пожалуйста нам на 
                                общую почту: +RCSPBADMINS</p>
                                <a href="{host}/app/notification_answer?unique_code={unique}&material_id={material[0]}">Уведомлен</a>
                                <p>Так же если у вас возникли вопросы, можете их задать по адресу: +RCSPBADMINS</p>
                            </body>
                        </html>                        
                        """
            html2 = f"""\
                    <html>
                            <body>
                                <p>Новая заявка на пермещение актива id: {material[0]} &nbsp; Номер: {material[1]}</p>
                                <p>Характеристики: {material[2]}</p>
                                <p>Инициатор перемещения: {material[4]}.</p>
                                <p>Планируемый статус после перемещения: {material[3]}</p>
                                <p>Просим переместить данный актив в 1с. Если у вас есть дополнительные вопросы - напишите пожалуйста нам на 
                                общую почту: +RCSPBADMINS</p>
                            </body>
                        </html> 
                    """
    part2 = MIMEText(html, "html")
    message.attach(part2)

    serv = smtplib.SMTP("smtp.gmail.com", 587)
    serv.starttls()
    serv.login(gmail_login, gmail_pass)
    serv.sendmail(gmail_login, addresses, message.as_string())
    new_notify = Notifications(category=f'{subject.value} {material[0]}',
                               user=addresses_to,
                               unique_code=unique,
                               material_id=material[0],
                               date_time=datetime.datetime.now()
                               )
    # эта проверка нужна если существует айди геолокации
    if 0 <= 5 < len(material):
        new_notify.geolocation_id = material[5]
    db.add(new_notify)
    db.commit()

    emails2 = EmailConfig.get_emails()
    if len(emails2) and html2:
        part = MIMEText(html, "html")
        message2.attach(part)
        message2['To'] = ", ".join(emails2)
        serv.sendmail(gmail_login, emails2, message2.as_string())
