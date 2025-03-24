import typing

from app.store.admin.accessor import AdminAccessor

if typing.TYPE_CHECKING:
    from app.web.app import Application


def setup_accessor(app: "Application"):
    adm_accesor = AdminAccessor(app)
    app.on_startup.append(adm_accesor.connect)