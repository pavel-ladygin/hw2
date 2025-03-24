import base64
import os

from aiohttp.web import (
    Application as AiohttpApplication,
    Request as AiohttpRequest,
    View as AiohttpView,
)
from aiohttp_session import setup
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet

from app.admin.models import Admin
from app.store import Store, setup_store
from app.store.database.database import Database
from app.web.config import Config, setup_config
from app.web.logger import setup_logging
from app.web.middlewares import setup_middlewares
from app.web.routes import setup_routes


class Application(AiohttpApplication):
    config: Config | None = None
    store: Store | None = None
    database: Database = Database()


class Request(AiohttpRequest):
    admin: Admin | None = None

    @property
    def app(self) -> Application:
        return super().app()


class View(AiohttpView):
    @property
    def request(self) -> Request:
        return super().request

    @property
    def store(self) -> Store:
        return self.request.app.store

    @property
    def data(self) -> dict:
        return self.request.get("data", {})

app = Application()
KEY_FILE = "secret_key.txt"
# Генерация или загрузка ключа
if os.path.exists(KEY_FILE):
    with open(KEY_FILE, "rb") as f:
        secret_key = f.read()
else:
    secret_key = fernet.Fernet.generate_key()
    with open(KEY_FILE, "wb") as f:
        f.write(secret_key)
# Преобразование ключа в формат, подходящий для EncryptedCookieStorage
secret_key = base64.urlsafe_b64decode(secret_key)
# Настройка middleware для сессий
setup(app, EncryptedCookieStorage(secret_key))


def setup_app(config_path: str) -> Application:
    setup_logging(app)
    setup_config(app, config_path)
    setup_routes(app)
    setup_middlewares(app)
    setup_store(app)
    return app
