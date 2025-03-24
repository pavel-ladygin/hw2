import typing

from app.store.vk_api.dataclasses import Update, Message
if typing.TYPE_CHECKING:
    from app.web.app import Application
    from app.store.vk_api.accessor import VkApiAccessor


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app


    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            await self.vk_api.send_message(Message(
                user_id=update.user_id,
                text="Ваш фиксированный ответ"
            ))