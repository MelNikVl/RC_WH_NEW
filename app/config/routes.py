from fastapi import APIRouter
from controllers.materials import MaterialsController
from controllers.geolocation import GeoLocationController
from controllers.front import FrontMainController

from app.controllers.accessories import AccessoriesController
from app.controllers.auth import AuthController
from app.controllers.logs import LogsController

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

for_admins = APIRouter(prefix='/for_admins',
                       tags=['for_admins'])

accessories = APIRouter(prefix='/accessories',
                        tags=['accessories'])


# здесь указываем эндпоинты
router.get("")(FrontMainController.index)
router.get("/auth")(FrontMainController.user_auth)
router.get("/ping")(FrontMainController.ping)
router.get("/instructions")(FrontMainController.instructions)
router.get("/admins_page")(FrontMainController.admins_page)
router.get("/repairs_page")(FrontMainController.repairs_page)

router.get("/trash_page")(FrontMainController.trash_page)
router.get("/{material_id}")(FrontMainController.only_one_card)

materials.post("/invoice")(FrontMainController.generate_invoice)
materials.post("/create")(MaterialsController.create)
materials.post("/get")(MaterialsController.get)
materials.put("/update-description")(MaterialsController.update_description)
materials.get("/list")(MaterialsController.list_of_materials)
materials.delete("/delete")(MaterialsController.delete_material)
materials.get("/get_last_update")(MaterialsController.get_last_update)
materials.post("/upload_photo")(MaterialsController.upload_photo)
materials.post("/update_title")(MaterialsController.update_title)

geolocation.post("/create")(GeoLocationController.create)
geolocation.post("/get-by-id")(GeoLocationController.get_by_id)
geolocation.post('/add_to_trash')(GeoLocationController.add_to_trash)
geolocation.post("/send_to_trash_finally")(GeoLocationController.send_to_trash_finally)
geolocation.get("/archive_trash_page")(GeoLocationController.archive_trash_page)
geolocation.post("/move_to_repair")(GeoLocationController.move_to_repair)
geolocation.post("/move_from_repair")(GeoLocationController.move_from_repair)
geolocation.post("/add_details_to_repair")(GeoLocationController.add_details_to_repair)
geolocation.post("/short_repair")(GeoLocationController.short_repair)

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
accessories.put("/add_accessories")(AccessoriesController.add_accessories)
accessories.get("")(AccessoriesController.accessories_page)

