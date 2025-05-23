from fastapi import APIRouter
from controllers.materials import MaterialsController
from controllers.geolocation import GeoLocationController
from controllers.front import FrontMainController

from app.controllers.accessories import AccessoriesController
from app.controllers.admin import AdminController
from app.controllers.auth import AuthController
from app.controllers.logs import LogsController
from app.controllers.testing import TestingController
from app.utils.soap import get_material

APIRouter.enter = lambda self: self
APIRouter.exit = lambda *args: ''

router = APIRouter(prefix='/app',
                   tags=['app'])

materials = APIRouter(prefix='/materials',
                      tags=['materials'])

geolocation = APIRouter(prefix='/geolocation',
                        tags=['geolocation'])

auth = APIRouter(prefix='/auth',
                 tags=['auth'])

logs = APIRouter(prefix='/logs',
                 tags=['logs'])

for_admins = APIRouter(prefix='/admin',
                       tags=['for_admins'])

accessories = APIRouter(prefix='/accessories',
                        tags=['accessories'])

testing = APIRouter(prefix='/testing',
                        tags=['testing'])

# здесь указываем эндпоинты
router.get("")(FrontMainController.index)
router.get("/auth")(FrontMainController.user_auth)
router.get("/ping")(FrontMainController.ping)
router.get("/instructions")(FrontMainController.instructions)
router.get("/admins_page")(FrontMainController.admins_page)
router.get("/repairs_page")(FrontMainController.repairs_page)
router.get("/notifications_page")(FrontMainController.notifications_page)
router.get("/notification_answer")(FrontMainController.notification_answer)
router.get("/test_page")(FrontMainController.test_page)

router.get("/only_1c")(FrontMainController.only_1c)
materials.get("/from_1c")(MaterialsController.get_from_1c)
materials.post("/add_from_1c")(MaterialsController.add_from_1c)
materials.get("/by_responsible")(MaterialsController.get_by_responsible)
materials.get("/responsible_list")(FrontMainController.responsible_list)
materials.get("/one_product_list")(FrontMainController.excel_1c_list)

router.get("/trash_page")(FrontMainController.trash_page)
router.get("/{material_id}")(FrontMainController.only_one_card)

materials.post("/generate_list")(FrontMainController.generate_list)
materials.post("/invoice")(FrontMainController.generate_invoice)
materials.post("/create")(MaterialsController.create)
materials.post("/get")(MaterialsController.get)
materials.put("/update-description")(MaterialsController.update_description)
materials.get("/list")(MaterialsController.list_of_materials)
materials.delete("/delete")(MaterialsController.delete_material)
materials.get("/get_last_update")(MaterialsController.get_last_update)
materials.post("/upload_photo")(MaterialsController.upload_photo)
materials.post("/update_title")(MaterialsController.update_title)
materials.post("/send_comment")(MaterialsController.send_comment)
materials.get("/last_x_days")(MaterialsController.last_x_days)

geolocation.post("/create")(GeoLocationController.create)
geolocation.post("/get-by-id")(GeoLocationController.get_by_id)
geolocation.post('/add_to_trash')(GeoLocationController.add_to_trash)
geolocation.post("/send_to_trash_finally")(GeoLocationController.send_to_trash_finally)
geolocation.get("/archive_trash_page")(GeoLocationController.archive_trash_page)
geolocation.post("/move_to_repair")(GeoLocationController.move_to_repair)
geolocation.post("/move_from_repair")(GeoLocationController.move_from_repair)
geolocation.post("/add_details_to_repair")(GeoLocationController.add_details_to_repair)
geolocation.post("/short_repair")(GeoLocationController.short_repair)
geolocation.put("/refresh_1c")(GeoLocationController.refresh_1c)

auth.post("/token")(AuthController.token)
auth.post("/create_new_user")(AuthController.create_new_user)
auth.put("/make-admin")(AuthController.make_admin)
auth.get("/get_users")(AuthController.get_users)
auth.delete("/delete_user")(AuthController.delete_user)
auth.get("/telegram_and_app_id")(AuthController.telegram_and_app_id)
auth.get("/get_admins")(AuthController.get_admins)
auth.post("/add_telegramm_id")(AuthController.add_telegramm_id)

logs.get("/get_all")(LogsController.logs)

accessories.post("/create")(AccessoriesController.create)
accessories.put("/change_count")(AccessoriesController.change_count)
accessories.put("/change_location_acc")(AccessoriesController.change_location_acc)
accessories.put("/add_accessories")(AccessoriesController.add_accessories)
accessories.get("")(AccessoriesController.accessories_page)

testing.post("/create_10_iterations")(TestingController.create_10_iterations)
testing.post("/delete_all")(TestingController.delete_all)
testing.delete("/delete_folder_contents")(TestingController.delete_folder_contents)

for_admins.delete("/delete_emails")(AdminController.remove_emails)
for_admins.post("/create_email")(AdminController.create_email)

