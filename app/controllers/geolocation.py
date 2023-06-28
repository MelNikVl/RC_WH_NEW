import datetime, os, smtplib, ssl, shutil, fastapi
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename
from typing import Dict, List, Optional

from fastapi import Depends, Request, UploadFile, File
from fastapi.encoders import jsonable_encoder
from sqlalchemy import desc
from sqlalchemy.orm import Session
from app.crud.geolocation import GeoLocationCRUD
from app.crud.materials import MaterialCRUD
from app.payload.request import GeoLocationCreateRequest, GeoLocationGetByIdRequest, RepairCreateRequest, \
    RepairStopRequest, RepairDetailsRequest
from starlette import status
from app.utils.utils import response
from app.controllers.front import templates
from app.utils.auth import AuthUtil
from db.db import get_db
from models.models import User, LogItem, GeoLocation, Material, Trash, Repair

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


class GeoLocationController:
    @staticmethod
    async def create(body: GeoLocationCreateRequest,
                     db: Session = Depends(get_db),
                     user: User = Depends(AuthUtil.decode_jwt)):

        if db.query(Repair).filter(Repair.material_id == body.material_id).all()[-1].repair_status == False:
            geolocation = await GeoLocationCRUD.create(material_id=body.material_id,
                                                       place=body.place,
                                                       client_mail=body.client_mail,
                                                       status=body.status,
                                                       initiator=user.get("username"),
                                                       db=db)

            # логируем
            create_geo_event = LogItem(kind_table="Расположение активов",
                                       user_id=user["username"],
                                       passive_id=body.material_id,
                                       modified_cols="новое расположение",
                                       values_of_change=f'новое место: {body.place},'
                                                        f' новый статус: {body.status},'
                                                        f' новый ответственный: {body.client_mail}',
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )
            db.add(create_geo_event)
            db.commit()

            return response(data=geolocation, status=True)
        else:
            return response(data="актив в ремонте и не подлежит перемещению", status=False)

    @staticmethod
    async def get_by_id(body: GeoLocationGetByIdRequest, db: Session = Depends(get_db),
                        user: User = Depends(AuthUtil.decode_jwt)):
        geolocation = await GeoLocationCRUD.get_by_id(material_id=body.material_id, db=db)
        return response(data=geolocation, status=True)

    @staticmethod
    async def add_to_trash(material_id,
                           user: User = Depends(AuthUtil.decode_jwt),
                           db: Session = Depends(get_db)):

        if db.query(Repair).filter(Repair.material_id == material_id).all()[-1].repair_status == False:
            add_to_trash = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).order_by(
                desc(GeoLocation.date_time)).all()[0]

            send_to_trash_01 = GeoLocation(material_id=material_id,
                                           place=add_to_trash.place,
                                           client_mail=user.get("username"),
                                           status="списание",
                                           initiator=user.get("username"),
                                           date_time=datetime.datetime.now()
                                           )

            # логируем
            create_geo_event = LogItem(kind_table="Расположение активов",
                                       user_id=user["username"],
                                       passive_id=material_id,
                                       modified_cols="status",
                                       values_of_change="актив добавлен к списанию",
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )

            db.add(send_to_trash_01)
            db.add(create_geo_event)
            db.commit()

            return response(data=f'актив {material_id} добавлен в список на списание', status=True)
        else:
            add_to_trash = db.query(GeoLocation).filter(GeoLocation.material_id == material_id).order_by(
                desc(GeoLocation.date_time)).all()[0]
            find_repair = db.query(Repair).filter(Repair.material_id == material_id)
            rapair_count_last = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_number

            last_repair = Repair(material_id=material_id,
                                 responsible_it_dept_user=user.get("username"),
                                 problem_description="отправлен на списание из ремонта",
                                 user_whose_technique=user.get("username"),
                                 repair_number=rapair_count_last + 1,
                                 date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                 repair_status=False,
                                 repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                                 )

            send_to_trash_01 = GeoLocation(material_id=material_id,
                                           place=add_to_trash.place,
                                           client_mail=user.get("username"),
                                           status="списание",
                                           date_time=datetime.datetime.now()
                                           )

            # логируем
            create_geo_event = LogItem(kind_table="Расположение активов",
                                       user_id=user["username"],
                                       passive_id=material_id,
                                       modified_cols="status",
                                       values_of_change="актив добавлен к списанию из ремонта",
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )

            db.add(last_repair)
            db.add(send_to_trash_01)
            db.add(create_geo_event)
            db.commit()

            return response(data=f'актив {material_id} добавлен в список на списание из ремонта', status=True)

    @staticmethod
    async def send_to_trash_finally(photos: List[UploadFile],
                                    db: Session = Depends(get_db),
                                    invoice: UploadFile = File(...),
                                    user: User = Depends(AuthUtil.decode_jwt)):

        # получаем список товаров на списание
        materials_for_trash = await GeoLocationCRUD.get_materials_for_trash(db=db)

        # создаем имена для папок
        timestamp = str(
            datetime.datetime.now().strftime("%Y-%m-%d-%H-%M") + "_активов_" + str(len(materials_for_trash)))
        destination_folder = os.path.join("\\\\fs-mo\\ADMINS\\Photo_warehouse\\archive_after_utilization", timestamp)

        photo_folder = os.path.join(destination_folder, "trashing_photos")
        old_photo_folder = os.path.join(destination_folder, "material_old_photos")

        # создаем папки если их нет
        os.makedirs(destination_folder, exist_ok=True)
        print(f'соаздана папка нового архива техники - {destination_folder}')
        os.makedirs(photo_folder, exist_ok=True)
        print(f'в папке {destination_folder} создана папка photos -- для фотографий списания')
        os.makedirs(old_photo_folder, exist_ok=True)
        print(f'в папке {destination_folder} создана папка material_photos для копирования папок с фото техники')
        out_filename = os.path.join(destination_folder, invoice.filename)

        # кладем накладную в папку списания
        with open(out_filename, "wb") as buffer:
            buffer.write(await invoice.read())
            print("накладная скопирована")

        # кладем фотки списания в папку списания
        for photo in photos:
            out_photo_path = os.path.join(photo_folder, photo.filename)
            with open(out_photo_path, "wb") as buffer:
                buffer.write(await photo.read())
        print("фото списания добавлены")

        # id_for_logging - для записи в таблицу логов айдишников техники, которая списана
        id_for_logging = []

        # перемещаем папки с фото в архив
        for i in materials_for_trash:
            folder_to_move = os.path.join("\\\\fs-mo\\ADMINS\\Photo_warehouse\\photos", str(i.id))
            id_for_logging.append(i.id)  # добавим айдишник каждой техники к списку
            destination = os.path.join(old_photo_folder, str(i.id))
            os.makedirs(destination, exist_ok=True)
            shutil.copytree(folder_to_move, destination, dirs_exist_ok=True)
            shutil.rmtree(folder_to_move)

            print(f'папка фото актива {i.id} перемещена в архив после списания')

        # копируем перемещения и данные об активах в таблицу треша и потом удаляем все из таблиц где они были.
        for y in materials_for_trash:
            # созраняем перемещения
            moving = []
            material_moving = db.query(GeoLocation).filter(GeoLocation.material_id == y.id).all()
            for m in material_moving:
                moving.append({"место": m.place, "ответственный": m.client_mail, "дата перемещения": m.date_time})
                print(f'история перемещений актива {m.material_id} перемещена')

            print(f'история перемещений актива {tr.material_id} создана')

            # созраняем ремонты
            repairs = []
            repairs_moving = db.query(Repair).filter(Repair.material_id == y.id).all()
            for tr in repairs_moving:
                repairs.append({"ответственный": tr.responsible_it_dept_user,
                                "проблема или решение": tr.problem_description,
                                "чья была техника": tr.user_whose_technique,
                                "дата": tr.responsible_it_dept_user})
            print(f'история ремонта актива {tr.material_id} создана')

            create_new_trash_archive = Trash(user_id=user.get("username"),
                                             material_id=y.id,
                                             category=y.category,
                                             title=y.title,
                                             description=y.description,
                                             moving=str(jsonable_encoder(moving)),
                                             repairs=str(jsonable_encoder(repairs)),
                                             date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                             folder_name=timestamp
                                             )
            db.add(create_new_trash_archive)
            print(f'актив {y.id} скопирован в таблицу Trash')

            material_for_delete = db.query(Material).filter(Material.id == y.id).first()
            db.delete(material_for_delete)
            print(f'актив {y.id} удален из таблицы Material')

            db.query(GeoLocation).filter(GeoLocation.material_id == y.id).delete()
            print(f'история передвижений актива {y.id} удалена из таблицы Гео')

            db.query(Repair).filter(Repair.material_id == y.id).all()
            print(f'история ремонтов актива {y.id} удалена из таблицы ретомнтов')

            db.commit()
            print(f'данные актива {y.id} записаны в новые таблицы и подтверждены')

        # логируем
        create_geo_event = LogItem(kind_table="Списание",
                                   user_id=user["username"],
                                   passive_id=0,
                                   modified_cols="перемещение в архив списания",
                                   values_of_change=f'активы: {str(jsonable_encoder(id_for_logging))} были списаны, '
                                                    f'записи об их местоположении теперь находятся в таблице архива. '
                                                    f'Фото данной техники перемещены в '
                                                    f'папку - {destination_folder}',
                                   date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                   )
        db.add(create_geo_event)
        db.commit()

        send_email(out_filename)

        return response(data=f'активы списаны, фото списания '
                             f'и накладная загружены, папки с фото техники перемещены в архив,'
                             f' логирование произведено', status=True)

    @staticmethod
    async def archive_trash_page(db: Session = Depends(get_db),
                                 request: Request = None,
                                 t: str = None  # jwt токен
                                 ):
        # проверка токена на валидность и если он не вализный - переадресация на авторизацию
        try:
            result = await AuthUtil.decode_jwt(t)
        except Exception as e:
            return fastapi.responses.RedirectResponse('/app/auth', status_code=status.HTTP_301_MOVED_PERMANENTLY)

        out: Dict = {}
        materials_for_archive_trash = db.query(Trash).all()
        out[0] = materials_for_archive_trash
        out["token"] = t

        return templates.TemplateResponse("archive_trash_page.html", {"request": request, "data": out})

    @staticmethod
    async def move_to_repair(data: RepairCreateRequest,
                             db: Session = Depends(get_db),
                             user: User = Depends(AuthUtil.decode_jwt),
                             ):

        if db.query(Repair).filter(Repair.material_id == data.material_id).all()[-1].repair_status == False:
            new_location = GeoLocation(material_id=data.material_id,
                                       place="IT отдел",
                                       client_mail=data.customer,
                                       status="ремонт",
                                       initiator=user.get("username"),
                                       date_time=datetime.datetime.now()
                                       )

            find_repair = db.query(Repair).filter(Repair.material_id == data.material_id)
            rapair_count_last = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_number

            new_repair = Repair(material_id=data.material_id,
                                responsible_it_dept_user=user.get("username"),
                                problem_description=data.problem,
                                user_whose_technique=data.customer,
                                repair_number=rapair_count_last + 1,
                                date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                repair_status=True,
                                repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                                )

            new_repair_event = LogItem(kind_table="Ремонт",
                                       user_id=user["username"],
                                       passive_id=data.material_id,
                                       modified_cols="актив взят в ремонт",
                                       values_of_change=f'проблема: {data.problem},'
                                                        f' технику сдал {data.customer}',
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )
            db.add(new_repair)
            db.add(new_location)
            db.add(new_repair_event)
            db.commit()
            return response(data="взяли на ремонт", status=True)
        else:
            return response(data="актив уже в ремонте", status=False)

    @staticmethod
    async def move_from_repair(body: RepairStopRequest,
                               db: Session = Depends(get_db),
                               user: User = Depends(AuthUtil.decode_jwt),
                               ):

        if db.query(Repair).filter(Repair.material_id == body.material_id).all()[-1].repair_status == True:
            new_location = GeoLocation(material_id=body.material_id,
                                       place=body.dept,
                                       client_mail=body.customer,
                                       status=body.status,
                                       initiator=user.get("username"),
                                       date_time=datetime.datetime.now()
                                       )

            find_repair = db.query(Repair).filter(Repair.material_id == body.material_id)
            rapair_count_last = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_number
            un_number_of_repair = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_unique_id

            get_out_repair = Repair(material_id=body.material_id,
                                    responsible_it_dept_user=user.get("username"),
                                    problem_description=body.decision,
                                    user_whose_technique=body.customer,
                                    repair_number=rapair_count_last + 1,
                                    date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                    repair_status=False,
                                    repair_unique_id=un_number_of_repair
                                    )

            new_repair_event = LogItem(kind_table="Ремонт",
                                       user_id=user["username"],
                                       passive_id=body.material_id,
                                       modified_cols="актив выдан из ремонта",
                                       values_of_change=f'решение: {body.decision},'
                                                        f' технику забрал {body.customer}',
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )
            db.add(get_out_repair)
            db.add(new_location)
            db.add(new_repair_event)
            db.commit()

            return response(data="отдали с ремонта", status=True)
        else:
            return response(data="актив не в ремонте", status=False)

    @staticmethod
    async def add_details_to_repair(body: RepairDetailsRequest,
                                    # file: UploadFile = None,
                                    db: Session = Depends(get_db),
                                    user: User = Depends(AuthUtil.decode_jwt),
                                    ):

        if db.query(Repair).filter(Repair.material_id == body.material_id).all()[-1].repair_status == True:

            # загружаем файл
            # await GeoLocationCRUD.upload_file_to_repair(body.material_id, file)

            find_repair = db.query(Repair).filter(Repair.material_id == body.material_id)
            rapair_count_last = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_number
            un_number_of_repair = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_unique_id
            user_repair = find_repair.order_by(desc(Repair.repair_number)).all()[0].user_whose_technique

            add_repair = Repair(material_id=body.material_id,
                                responsible_it_dept_user=user.get("username"),
                                problem_description=body.details,
                                user_whose_technique=user_repair,
                                repair_number=rapair_count_last + 1,
                                date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                repair_status=True,
                                repair_unique_id=un_number_of_repair
                                )

            new_repair_event = LogItem(kind_table="Ремонт",
                                       user_id=user["username"],
                                       passive_id=body.material_id,
                                       modified_cols="добавление информации",
                                       values_of_change=f'что добавлено: {body.details}',
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )
            db.add(add_repair)
            db.add(new_repair_event)
            db.commit()

            return response(data="добавлена информация о ремонте", status=True)
        else:
            return response(data="Актив не в ремонте. К нему нельзя добавить данные", status=False)

    @staticmethod
    async def short_repair(body: RepairCreateRequest,
                           # file: Optional[UploadFile] = None,
                           db: Session = Depends(get_db),
                           user: User = Depends(AuthUtil.decode_jwt),
                           ):

        if db.query(Repair).filter(Repair.material_id == body.material_id).all()[-1].repair_status == False:

            print("fjsldkjf")

            # загружаем файл
            # await GeoLocationCRUD.upload_file_to_repair(body.material_id, file)

            find_repair = db.query(Repair).filter(Repair.material_id == body.material_id)
            rapair_count_last = find_repair.order_by(desc(Repair.repair_number)).all()[0].repair_number

            new_repair = Repair(material_id=body.material_id,
                                responsible_it_dept_user=user.get("username"),
                                problem_description=str("быстрый ремонт -- " + body.problem),
                                user_whose_technique=body.customer,
                                repair_number=rapair_count_last + 1,
                                date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                repair_status=False,
                                repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                                )

            new_repair_event = LogItem(kind_table="Ремонт",
                                       user_id=user["username"],
                                       passive_id=body.material_id,
                                       modified_cols="быстрый ремонт на месте",
                                       values_of_change=f'проблема: {body.problem},'
                                                        f' техника у {body.customer}',
                                       date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                       )
            db.add(new_repair)
            db.add(new_repair_event)
            db.commit()

            return response(data="быстрый ремонт произвден", status=True)
        else:
            return response(data="актив уже в ремонте", status=False)
