import asyncio
from asyncio import Task

from app.store import Store
from app.store.bot.manager import BotManager


class Poller:
    def __init__(self, store: Store) -> None:
        self.session = None
        self.store = store
        self.is_running = False
        self._poll_task: Task | None = None
        self._stop_event = asyncio.Event()


    async def start(self) -> None:
        # TODO: добавить asyncio Task на запуск poll
        """Запускает поллинг в фоновом режиме"""
        if self.is_running:
            return
        self.is_running = True
        self._poll_task = asyncio.create_task(self._poll_loop())

    async def _poll_loop(self):
        """Основной цикл опроса"""
        while self.is_running:
            updates = await VkApiAccessor.poll(self=VkApiAccessor)
            if updates:
                await BotManager.handle_updates(updates, self=BotManager)

    async def stop(self) -> None:
        # TODO: gracefully завершить Poller
        if not self.is_running:
            return

        self.is_running = False
        if self._poll_task:
            await self._poll_task

    async def poll(self) -> None:
        updates = await VkApiAccessor.poll(self=VkApiAccessor)
        if updates:
            await BotManager.handle_updates(updates, self=BotManager)