import asyncio
import os

from .bot import TGBot
from .database import Database
from .poker_rating import PokerRating


class Manager:
    def __init__(self):
        self._database = Database()
        self._poker_rating = PokerRating(self._database)
        self._bot = TGBot(bot_token=os.getenv("BOT_TOKEN"),
                          poker_rating=self._poker_rating)

    async def run(self):
        asyncio.ensure_future(self._database.run())
        await self._bot.run()
