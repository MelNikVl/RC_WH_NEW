import os
from aiogram import Bot

# main_folder = r"C:\Users\admin\Documents\GitHub\RC_WH_NEW\app\it_warehouse_docs"
# main_folder = "\\\\fs-mo\\ADMINS\\"

current_dir = os.path.dirname(os.path.abspath(__file__))
main_folder = os.path.join(current_dir, "app", "it_warehouse_docs")

bot = Bot("6255903272:AAEYZgt6krIp723UY7mchIN4u-ydVZRLOC0")
# bot_for_admin = Bot("5858975680:AAFdDI-XOEYqFxNf9OAbx0p6JgpuW89DiqE")

host = "http://192.168.1.104:50131"

utilization_ntf_users = ["shumerrr@yandex.ru", "sergey.zagustin@rencons.com", "nikolai.melnik@rencons.com"]
repair_ntf_users = "shumerrr@yandex.ru, sergey.zagustin@rencons.com"

