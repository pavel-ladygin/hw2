import os
import typing
import bcrypt
import yaml

from app.admin.models import Admin
from app.base.base_accessor import BaseAccessor
from app.store.database import database
from app.web.middlewares import InvalidDataError
from tests.conftest import config
from app.web import config
if typing.TYPE_CHECKING:
    from app.web.app import Application


class AdminAccessor(BaseAccessor):
    async def connect(self, app: "Application") -> None:
        admin_accessor = AdminAccessor
        # TODO: создать админа по данным в config.yml здесь
        self.app = app
        # Извлечение данных из конфига и хеширование пароля
        config_path = os.path.abspath("path/to/config.yml")
        with open("/Users/ladyginpavel/PycharmProjects/hw2/tests/config.yml", "r") as f:
            config_ = yaml.safe_load(f)
        admin_email = config_["admin"]["email"]
        admin_password = config_["admin"]["password"].encode("utf-8")
        hash_passwd = bcrypt.hashpw(admin_password, bcrypt.gensalt())

        # Проверяем, что админ еще не создан и создаем
        cur_admin = await admin_accessor.get_by_email(email=admin_email, self=app)
        if not cur_admin:
            admin_ = Admin(id=1, email=admin_email, password=str(hash_passwd))
            database.Database.admins.append(admin_)
            print("Connect to database")

    async def get_by_email(self, email: str) -> Admin | None:
        data = database.Database.admins
        for admin_ in data:
            if admin_.email == email:
                return admin_
        return None
    async def create_admin(email: str, password: str) -> Admin:
        #Проверяем валидность данных
        if email==password:
            raise InvalidDataError("Invalid data")
        # Декодируем и хешируем пароль
        encoded_passwd = password.encode("utf-8")
        hash_passwd = bcrypt.hashpw(encoded_passwd, bcrypt.gensalt())

        admin = Admin(id=len(database.Database.admins), email=email, password=str(hash_passwd))
        database.Database.admins.append(admin)
        return admin
