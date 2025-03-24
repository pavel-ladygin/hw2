import asyncio
from asyncio import Task
from typing import Optional

from app.store import Store
from app.store.bot.manager import BotManager


class Poller:
    def __init__(self, store: Store):
        self.store = store
        self.is_running = False
        self.poll_task: Optional[Task] = None


    async def start(self):
        self.is_running = True
        self.poll_task = asyncio.create_task(self.poll())

    async def stop(self):
        self.is_running = False
        if self.poll_task:
            await self.poll_task

        self.is_running = False
        if self._poll_task:
            await self._poll_task

    async def poll(self):
        while self.is_running:
            try:
                updates = await self.store.vk_api.poll()
                if updates:
                    await self.store.bots_manager.handle_updates(updates)
            except Exception as e:
                print(f"Poll error: {e}")
                await sleep(1)