from app.store.vk_api.dataclasses import Message, Update


class BotManager:
    def __init__(self, app: "Application"):  # Принимаем app, а не vk_api напрямую
        self.app = app

    async def handle_updates(self, updates: list[Update]):
        for update in updates:
            if update.type == "message_new":
                # Доступ к vk_api через app.store
                await self.app.store.vk_api.send_message(
                    Message(
                        user_id=update.object.message.from_id,
                        text="Ваше сообщение получено: " + update.object.message.text
                    )
                )