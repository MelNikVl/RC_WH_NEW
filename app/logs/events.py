import codecs
import datetime
import json

from fastapi import Depends
from fastapi.encoders import jsonable_encoder
from sqlalchemy import event, text
from sqlalchemy.orm.attributes import get_history


def bind_materials(Material):
    @event.listens_for(Material, 'after_update')
    def after_update(mapper, connection, target):
        old_name = get_history(target, 'description').deleted
        old_name_bool = get_history(target, 'description').has_changes()
        name_1 = get_history(target, 'description').sum()
        if len(name_1) == 1:
            connection.execute(
                text(
                    f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
                    f"VALUES ('Активы', '{target.user_id}', '{target.id}', 'изменение актива', "
                    f" '{target.description}',"
                    f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))
        else:
            new_val = name_1[1] + " -------- > " + name_1[0]
            connection.execute(
                text(
                    f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
                    f"VALUES ('Активы', '{target.user_id}', '{target.id}', 'изменение актива', "
                    f" '{new_val}',"
                    f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))

    @event.listens_for(Material, 'after_delete')
    def after_delete(mapper, connection, target):
        connection.execute(
            text(
                f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
                f"VALUES ('Активы', '{target.user_id}', '{target.id}', 'удаление актива',"
                f" '{target.description}',"
                f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))

    # @event.listens_for(Material, 'after_insert')
    # def after_insert(mapper, connection, target):
    #     connection.execute(
    #         text(
    #             f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
    #             f"VALUES ('Активы', '{target.user_id}', '{target.id}', 'создание актива',"
    #             f" '{target.description}',"
    #             f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))


def bind_users(User):
    @event.listens_for(User, 'after_insert')
    def after_insert_user(mapper, connection, target):
        print("создание нового пользователя")
        connection.execute(
            text(
                f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
                f"VALUES ('Пользователи', 'admin', '{target.id}', 'creating user',"
                f" 'id: {target.username}, chat_id: {target.chat_id}, admin_permission: {target.is_admin}', "
                f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))

    @event.listens_for(User, 'after_update')
    def after_update_user(mapper, connection, target):
        print("обновление прав пользователя")
        connection.execute(
            text(
                f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
                f"VALUES ('Пользователи', '{target.id}', '{target.id}', 'update permission',"
                f" 'id: {target.username}, chat_id: {target.chat_id}, admin_permission: {target.is_admin}', "
                f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))

    @event.listens_for(User, 'after_delete')
    def after_delete_user(mapper, connection, target):
        print("удаление пользователя")
        connection.execute(
            text(
                f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, date_time) "
                f"VALUES ('Пользователи', 'admin', '{target.id}', 'удаление пользователя',"
                f" 'id: {target.username}, chat_id: {target.chat_id}, admin_permission: {target.is_admin}', "
                f"'{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}');"))


# def bind_geo(GeoLocation):
#     @event.listens_for(GeoLocation, 'after_insert')
#     def after_insert_geo(mapper, connection, target):
#         print("создание нового местополложения актива")
#         connection.execute(
#             text(
#                 f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, source_web_or_tg, date_time) "
#                 f"VALUES ('Расположение товаров', 'uuu', '{target.material_id}', 'изменение местоположения актива',"
#                 f" 'new place: {target.place}, new client_mail: {target.client_mail}', 'WEB', "
#                 f"'{datetime.datetime.now()}');"))
#
#     @event.listens_for(GeoLocation, 'after_update')
#     def after_update_geo(mapper, connection, target):
#         print("обновление нового местополложения актива")
#         connection.execute(
#             text(
#                 f"INSERT INTO log (kind_table, user_id, passive_id, modified_cols, values_of_change, source_web_or_tg, date_time) "
#                 f"VALUES ('Расположение товаров', 'uuu', '{target.material_id}', 'обновление местоположения актива',"
#                 f" 'place: {target.place}, client_mail: {target.client_mail}', 'WEB', "
#                 f"'{datetime.datetime.now()}');"))
