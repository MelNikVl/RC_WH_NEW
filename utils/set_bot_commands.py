from aiogram import types

# айдишники телеграма, тех кто может пользоваться
admin_list = [5750415545, 314758775, 106655730]

"""
5750415545 - тестовый аккаунт
314758775 - Николай Мельник
106655730 - Сергей Загустин
"""


# проверка на админа
def check_if_admin(chat_id):
    if chat_id in admin_list:
        return True
    else:
        return False
