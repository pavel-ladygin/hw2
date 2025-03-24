import typing

from app.store.admin.accessor import AdminAccessor
from app.store.bot.manager import BotManager
from app.store.vk_api.accessor import VkApiAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_accessor(app: "Application"):
    adm_accesor = AdminAccessor(app)
    vk_acces = VkApiAccessor(app)
    app.on_startup.append(adm_accesor.connect)
    app.on_shutdown.append(vk_acces.disconnect)