import typing
from urllib.parse import urlencode, urljoin

import yaml
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        # TODO: добавить создание aiohttp ClientSession,
        #  получить данные о long poll сервере с помощью метода groups.getLongPollServer
        #  вызвать метод start у Poller
        self.session = ClientSession()
        await self._get_long_poll_server()

    async def disconnect(self, app: "Application"):
        # TODO: закрыть сессию и завершить поллер
        if self.session:
            await self.session.close()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        with open("/Users/ladyginpavel/PycharmProjects/hw2/tests/config.yml", "r") as f:
            config_ = yaml.safe_load(f)
        url = "https://api.vk.com/method/groups.getLongPollServer"
        params = {
            "access_token": config_["bot"]["token"],
            "group_id": config_["bot"]["group_id"],
        }
        async with self.session.get(url, params=params) as resp:
            data = await resp.json()
            if "response" in data:
                response = data["response"]
                self.server = response["server"]
                self.key = response["key"]
                self.ts = response["ts"]

    async def poll(self) -> list[Update]:
        if not all([self.server, self.key, self.ts]):
            await self._get_long_poll_server()

        params = {
            "act": "a_check",
            "key": self.key,
            "ts": self.ts,
            "wait": 25
        }

        updates = []
        try:
            async with self.session.get(self.server, params=params) as resp:
                data = await resp.json()

                if "failed" in data:
                    await self._get_long_poll_server()
                    return []

                self.ts = data["ts"]

                for event in data.get("updates", []):
                    if event["type"] == "message_new":
                        msg = event["object"]["message"]
                        # Убедимся, что все обязательные поля присутствуют
                        if "from_id" in msg and "text" in msg:
                            updates.append(Update(
                                type="message_new",
                                object={
                                    "message": {
                                        "from_id": msg["from_id"],
                                        "text": msg["text"]
                                    }
                                }
                            ))
        except Exception as e:
            print(f"Poll error: {e}")

        return updates


    async def send_message(self, message: Message) -> None:
        url = "https://api.vk.com/method/messages.send"
        params = {
            "user_id": message.user_id,
            "message": message.text,
            "random_id": 0,
            "access_token": self.token,
            "v": "5.131"
        }

        try:
            async with self.session.post(url, params=params) as resp:
                await resp.json()
        except Exception as e:
            print(f"Send message error: {e}")