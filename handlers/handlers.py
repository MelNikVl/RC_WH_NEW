import datetime

from db.db import session
from keyboards.keyboards import geolocation_keyboard
from models.models import User, Material, GeoLocation, LogItem


# добавление описания
async def add_description_handler(bot, message, state):
    # присваиваем переменной user значение из БД равное айди пользователя в чате
    user = session.query(User).filter(User.chat_id == message.chat.id).one()
    # присваиваем переменной material значения для записи в бд
    material = Material(id=state[message.chat.id]["technic_id"],
                        title=state[message.chat.id]["model"],
                        category=state[message.chat.id]["category"],
                        date_time=datetime.datetime.now(),
                        user_id=user.id,
                        description=message.text)
    # добавляем данные в бд
    session.add(material)
    # записываем данные в бд
    session.commit()
    await bot.send_message(message.chat.id, "Хотели бы вы указать расположение актива?",
                           reply_markup=geolocation_keyboard())


# получание местоположение по айди
async def get_by_id_handler(bot, message):
    material = session.query(Material).filter(Material.id == message.text).all()
    # если пользователь ничего не ввел
    if len(material) == 0:
        await bot.send_message(message.chat.id, 'техника не найдена')
    # если введен айди - то выдаем значения из базы данных
    else:
        await bot.send_message(message.chat.id,
                               f'категория: {material[0].category},\nномер: {material[0].title},'
                               f'\nописание {material[0].description},\nдата создания {material[0].date_time}')


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
                                  status="здесь надо добавить кнопки для выбора статуса",
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
async def add_geolocation_handler(bot, message, state):
    geolocation = GeoLocation(client_mail=message.text, place=state[message.chat.id]['place'],
                              status="добавить кнопки для выбора статуса",
                              material_id=state[message.chat.id]['technic_id'], date_time=datetime.datetime.now())
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
                           f'Фото лежат тут - "fs-mo\ADMINS\Photo_warehouse\photos\{state[message.chat.id]["technic_id"]}"\n'
                           f'Toвар распологается в {geolocation.place}, ответсвенный - {geolocation.client_mail}'
                           )
