import datetime

from aiogram.types import Message
from aiogram.utils import markdown

from app.crud.materials import MaterialCRUD
from app.utils.soap import get_material
from db.db import session
from models.models import User, Material, GeoLocation, LogItem, Repair


# добавление описания
async def add_description_handler(bot, message, state):
    user = session.query(User).filter(User.chat_id == message.chat.id).one()
    material = Material(id=state[message.chat.id]["technic_id"],
                        title=state[message.chat.id]["model"],
                        category=state[message.chat.id]["category"],
                        date_time=datetime.datetime.now(),
                        user_id=user.id,
                        description=message.text)
    session.add(material)
    session.commit()
    state[message.chat.id]["state"] = "add_geolocation"
    await bot.send_message(message.chat.id, "Введите местоположение")


# получание местоположение по айди
async def get_by_id_handler(bot, message):
    global geo
    material = session.query(Material).filter(Material.id == message.text).first()
    geos = session.query(GeoLocation).filter(Material.id == message.text).all()
    if len(geos)>0:
        geo = geos[-1]
    # если пользователь ничего не ввел
    if not material:
        await bot.send_message(message.chat.id, 'техника не найдена')
    # если введен айди - то выдаем значения из базы данных
    else:
        await bot.send_message(message.chat.id,
                               f'категория: {material.category},\nномер: {material.title},'
                               f'\nописание {material.description},\nдата создания {material.date_time}'
                               f'\nстатус {geo.status}')


# перемещение товара
async def move_object_handler(bot, message):
    text = message.text.split(',')
    if len(text) != 3:
        await bot.send_message(message.chat.id, 'Вы ввели что то не так')
    object_id = text[0]
    client_mail = text[1]
    object_location = text[2]
    material = session.query(Material).filter(Material.id == object_id).all()
    if len(material) == 0:
        await bot.send_message(message.chat.id, 'техника не найдена')
    else:
        geolocation = GeoLocation(material_id=object_id, place=object_location, client_mail=client_mail,
                                  status="хранение",
                                  initiator=message.chat.id,
                                  date_time=datetime.datetime.now())
        session.add(geolocation)
        session.commit()

        # логируем1
        create_geo_event = LogItem(kind_table="АКТИВЫ",
                                   user_id=message.chat.id,
                                   passive_id=object_id,
                                   modified_cols="перемещение актива из бота",
                                   values_of_change=f'новое место: {object_location},'
                                                    f'ивент: "перемещение техники. запрос из бота",'
                                                    f' новый ответственный: {client_mail}',
                                   date_time=datetime.datetime.now()
                                   )
        session.add(create_geo_event)
        session.commit()

        await bot.send_message(message.chat.id, f'Запись о перемещении техники сделана.\n'
                                                f'ID актива: {object_id}\n'
                                                f'Новый ответственный: {client_mail}\n'
                                                f'Будет находиться: {object_location}')


# показать перемещения товара
async def show_object_moving_handler(bot, message):
    material = session.query(Material).filter(Material.id == message.text).all()
    if len(material) == 0:
        await bot.send_message(message.chat.id, 'техника не найдена')
    else:
        geolocations = session.query(GeoLocation).filter(GeoLocation.material_id == material[0].id).all()
        if len(geolocations) == 0:
            await bot.send_message(message.chat.id, "актив еще не был никуда отправлен")
        else:
            text_to_send = "Передвижение объекта: \n\n"
            for i in geolocations:
                text_to_send += f'ответственный: {i.client_mail}, местонахождение: {i.place}, дата отправки: {i.date_time}\n'
            await bot.send_message(message.chat.id, text_to_send)


# начало создания карточки товара
async def add_id_handler(bot, message, state):
    if message.text.isdigit():
        materials = session.query(Material).filter(Material.id == message.text).all()
        if len(materials) == 0:
            state[message.chat.id]['technic_id'] = message.text
            print(state)
            state[message.chat.id]["state"] = "send_first_photo"
            await bot.send_message(message.chat.id, "Пришлите фото наклейки (номер техники)")
        else:
            await bot.send_message(message.chat.id, "Карточка с таким ID уже существует")
    else:
        await bot.send_message(message.chat.id, "Вы ввели не число. Введите число")


# добавление местоположения товара
async def add_geolocation_handler(bot, state, message=None, call_back=None):
    if message is not None:
        user = session.query(User).filter(User.chat_id == message.chat.id).one()
        geolocation = GeoLocation(client_mail=message.text,
                                  place=state[message.chat.id]['place'],
                                  status="выдан",
                                  material_id=state[message.chat.id]['technic_id'],
                                  initiator=user.username,
                                  date_time=datetime.datetime.now())

        new_repair = Repair(material_id=state[message.chat.id]['technic_id'],
                            responsible_it_dept_user=user.username,
                            problem_description="создание карточки актива",
                            repair_number=1,
                            date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            repair_status=False,
                            repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                            )

        session.add(new_repair)
        session.add(geolocation)
        session.commit()
        material = session.query(Material).filter(Material.id == state[message.chat.id]['technic_id']).one()
        material.geolocation_id = geolocation.id
        session.flush()
        session.commit()
        await bot.send_message(message.chat.id,
                               f'Карточка актива создана.\n'
                               f'ID: {state[message.chat.id]["technic_id"]}\n'
                               f'Категория: {state[message.chat.id]["category"]}\n'
                               f'Номер: {state[message.chat.id]["model"]}\n'
                               f'Статус: "выдан"\n'
                               f'Фото - "fs-mo\ADMINS\Photo_warehouse\photos\{state[message.chat.id]["technic_id"]}"\n'
                               f'Toвар распологается в {geolocation.place}, ответсвенный - {geolocation.client_mail}'
                               )
        create_material_from_bot = LogItem(kind_table="Активы",
                                           user_id=user.username,
                                           passive_id=state[message.chat.id]["technic_id"],
                                           modified_cols="создание актива из бота",
                                           values_of_change=f'Категория: {state[message.chat.id]["category"]}\n'
                                                            f'Номер: {state[message.chat.id]["model"]}\n'
                                                            f'Статус: "выдан"\n'
                                                            f'Toвар распологается в {geolocation.place},'
                                                            f' ответсвенный - {geolocation.client_mail}',
                                           date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                           )
        session.add(create_material_from_bot)
        session.commit()
    else:
        user = session.query(User).filter(User.chat_id == call_back.message.chat.id).one()
        geolocation = GeoLocation(client_mail="nomail",
                                  place=state[call_back.message.chat.id]['place'],
                                  status="хранение",
                                  material_id=state[call_back.message.chat.id]['technic_id'],
                                  initiator=user.username,
                                  date_time=datetime.datetime.now())

        new_repair = Repair(material_id=state[call_back.message.chat.id]['technic_id'],
                            responsible_it_dept_user=user.username,
                            problem_description="создание карточки актива",
                            repair_number=1,
                            date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            repair_status=False,
                            repair_unique_id=MaterialCRUD.generate_alphanum_random_string(20)
                            )

        session.add(new_repair)
        session.add(geolocation)
        session.commit()
        material = session.query(Material).filter(Material.id == state[call_back.message.chat.id]['technic_id']).one()
        material.geolocation_id = geolocation.id
        session.flush()
        session.commit()
        await bot.send_message(call_back.message.chat.id,
                               f'Карточка актива создана.\n'
                               f'ID: {state[call_back.message.chat.id]["technic_id"]}\n'
                               f'Категория: {state[call_back.message.chat.id]["category"]}\n'
                               f'Номер: {state[call_back.message.chat.id]["model"]}\n'
                               f'Статус: "хранение"\n'
                               f'Фото - "fs-mo\ADMINS\Photo_warehouse\photos\{state[call_back.message.chat.id]["technic_id"]}"\n'
                               )

        create_material_from_bot = LogItem(kind_table="Активы",
                                           user_id=user.username,
                                           passive_id=state[call_back.message.chat.id]["technic_id"],
                                           modified_cols="создание актива из бота",
                                           values_of_change=f'Категория: {state[call_back.message.chat.id]["category"]}\n'
                                                            f'Номер: {state[call_back.message.chat.id]["model"]}\n'
                                                            f'Статус: "хранение"\n',
                                           date_time=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                           )
        session.add(create_material_from_bot)
        session.commit()


async def search_1c(bot, message: Message):
    mat = get_material(message.text)['EquipmentData']
    koil = []
    for i in get_material(message.text)['EquipmentData']['MovementHistory']:
        koil.append(i)
    for u in koil:
        print(u)
    output = (f"*Данные по ID - * {mat['Code']}\n"
              f"Дата ввода: {mat['AcceptanceDate']}\n"
              f"*Описание:* {mat['NameRU']}\n"
              f"*Местонахождение:* {mat['CurrentDept']}\n"
              f"*Ответсвенный сейчас:* {mat['CurrentPerson']}\n"
              # f"*Ебаные перемещения* {koil}\n"
              )
    await bot.send_message(message.chat.id, output, parse_mode='Markdown')