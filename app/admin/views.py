import uuid
from uuid import uuid4
from aiohttp.web_response import json_response
from aiohttp import request
from aiohttp_session import session_middleware, new_session, get_session

from app.admin.models import Admin
from app.web.app import View, Application
from app.store.admin.accessor import AdminAccessor
from app.store.database.database import Database
from app.web.middlewares import AuthorizeError


class AdminLoginView(View):
    admin_accessor = AdminAccessor
    async def post(self):
        data = await self.request.json()
        if "email" not in data or "password" not in data:
            raise KeyError("email")
        admin_ = await AdminAccessor.create_admin(email=data["email"], password=data["password"])
        session = await new_session(request=self.request)
        session["admin_email"] = admin_.email
        return json_response(data={
            "status" : "ok" ,
            "data" : {
                "id" : admin_.id , "email": str(admin_.email)
            }
        })

class AdminCurrentView(View):
    async def get(self):
        session_ = await get_session(self.request)
        if "admin_email" not in session_:
            raise AuthorizeError("User is not authorize")
        # Ищем админа по почте из сессии
        admin_email = session_["admin_email"]
        admin_ = await AdminAccessor.get_by_email(email=admin_email, self=self.request)
        return json_response(data={
            "status" : "ok",
            "data" : {
                "id" : admin_.id,
                "email" : str(admin_.email)
            }
        })


