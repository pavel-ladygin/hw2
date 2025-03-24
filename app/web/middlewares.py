import base64
import json
import typing

from aiohttp.web_exceptions import HTTPUnprocessableEntity
from aiohttp.web_middlewares import middleware
from aiohttp.web_response import json_response
from aiohttp_apispec import validation_middleware
from aiohttp_session import setup, session_middleware, get_session
from aiohttp_session.cookie_storage import EncryptedCookieStorage
from cryptography import fernet
from marshmallow import missing
from yaml import KeyToken

from app.web.utils import error_json_response

if typing.TYPE_CHECKING:
    from app.web.app import Application, Request

HTTP_ERROR_CODES = {
    400: "bad_request",
    401: "unauthorized",
    403: "forbidden",
    404: "not_found",
    405: "not_implemented",
    409: "conflict",
    500: "internal_server_error",
}

# Генерация ключа для шифрования сессий
fernet_key = fernet.Fernet.generate_key()
secret_key = base64.urlsafe_b64decode(fernet_key)

# Настройка middleware для сессий
class InvalidDataError(Exception):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class AuthorizeError(Exception):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
class ThemeTitleError(Exception):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
class QestionError (Exception):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
class NoValueError(Exception):
    def __init__(self, message: str, details: dict = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}
@middleware
async def error_handling_middleware(request: "Request", handler):
    try:
        response = await handler(request)

    # Обработка неверных полей запроса
    except KeyError as e:
        missing_field = str(e)[1:-1] # Чтобы не было повторяющихся ковычек
        return json_response(status=400, data={
            "status": "bad_request",
            "message": "Unprocessable Entity",
            "data": {
                "json":
                    {missing_field: ["Missing data for required field."]
                     }
            }
        })
    # Обработка невалидных данных запроса
    except InvalidDataError as e:
        # Обработка ошибок валидации
        return json_response(status=403, data={
            "status": "forbidden",
            "message": e.message,
            "data": e.details
        })
    # Обработка неавторизованного пользователя
    except AuthorizeError as e:
        return json_response(status=401, data={
            "status" : "unauthorized",
            "message" : e.message,
            "data" : e.details
        })
    # Обработка совпадения названия темы
    except ThemeTitleError as e:
        return json_response(status=409, data={
            "status" : "conflict",
            "message" : e.message,
            "data" : e.details
        })
    except QestionError as e:
        return json_response(status=400, data={
            "status": "bad_request",
            "message": e.message,
            "data": e.details
        })
    except NoValueError as e:
        return json_response(status=404, data={
            "status": "not_found",
            "message": e.message,
            "data": e.details
        })

    except HTTPUnprocessableEntity as e:
        return error_json_response(
            http_status=400,
            status=HTTP_ERROR_CODES[400],
            message=e.reason,
            data=json.loads(e.text),
        )

    return response
    # TODO: обработать все исключения-наследники HTTPException и отдельно Exception, как server error
    #  использовать текст из HTTP_ERROR_CODES

@middleware
async def validation_middleware(request: "Request", handler):
    # Исключение для запроса авторизации
    if request.path == "/admin.login":
        return await handler(request)
    session_ = await get_session(request)
    if "admin_email" not in session_:
        return json_response(status=401, data={
            "status" : "unauthorized",
            "message" : "You don't authorized user",
            "data" : ""
        })
    return await handler(request)



def setup_middlewares(app: "Application"):
    app.middlewares.append(error_handling_middleware)
    app.middlewares.append(validation_middleware)
