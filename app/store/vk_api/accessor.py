import typing
from typing import Optional, List

from aiohttp.client import ClientSession
import aiohttp

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: Optional[ClientSession] = None
        self.key: Optional[str] = None
        self.server: Optional[str] = None
        self.poller: Optional[Poller] = None
        self.ts: Optional[int] = None

    async def connect(self, app: "Application"):
        self.session = aiohttp.ClientSession()
        await self._get_long_poll_server()
        self.poller = Poller(app.store)
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.poller:
            await self.poller.stop()
        if self.session:
            await self.session.close()

    async def _get_long_poll_server(self):
        url = self._build_query(
            "https://api.vk.com/",
            "groups.getLongPollServer",
            {
                "group_id": self.app.config.bot.group_id,
                "access_token": self.app.config.bot.token
            }
        )
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.server = data["response"]["server"]
            self.key = data["response"]["key"]
            self.ts = data["response"]["ts"]

    async def poll(self) -> List[Update]:
        url = f"{self.server}?act=a_check&key={self.key}&ts={self.ts}&wait=25"
        async with self.session.get(url) as resp:
            data = await resp.json()
            self.ts = data["ts"]
            return [
                Update(type=u["type"], object=UpdateObject.from_dict(u["object"]))
                for u in data.get("updates", [])
                if u["type"] == "message_new"
            ]

    async def send_message(self, message: Message) -> None:
        url = self._build_query(
            "https://api.vk.com/",
            "messages.send",
            {
                "user_id": message.user_id,
                "message": message.text,
                "access_token": self.app.config.bot.token,
                "random_id": 0
            }
        )
        async with self.session.get(url) as resp:
            await resp.json()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        url = host + method + "?"
        if "v" not in params:
            params["v"] = "5.131"
        url += "&".join([f"{k}={v}" for k, v in params.items()])
        return url