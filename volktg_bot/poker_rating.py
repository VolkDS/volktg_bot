from .database import Database


class PokerRating:
    def __init__(self, database: Database):
        self._db = database

        self._by_total_prize = []
        self._by_average_prize = []

    async def get_by_total_prize(self):
        return await self._db.get_rating_by_total_prize()

    async def get_by_average_prize(self):
        return await self._db.get_rating_by_average_prize()

    async def get_rating_by_bank_prize(self):
        return await self._db.get_rating_by_bank_prize()

    async def get_top_win(self, limit):
        return await self._db.get_top_win(limit)

    async def get_top_lose(self, limit):
        return await self._db.get_top_lose(limit)

    async def get_top_roll(self, limit):
        return await self._db.get_top_roll(limit)

    async def get_top_table(self):
        return await self._db.get_top_table()

    async def get_personal_game_history(self, name):
        return await self._db.get_personal_game_history(name)

    async def get_personal_total_prize(self, name):
        return await self._db.get_personal_total_prize(name)

    async def get_personal_average_prize(self, name):
        return await self._db.get_personal_average_prize(name)

    async def get_personal_top_win(self, name):
        return await self._db.get_personal_top_win(name)

    async def get_personal_top_lose(self, name):
        return await self._db.get_personal_top_lose(name)

    async def get_personal_top_roll(self, name):
        return await self._db.get_personal_top_roll(name)

    async def get_cash_by_roi(self):
        return await self._db.get_cash_by_roi()

    async def get_rating_by_games(self):
        return await self._db.get_rating_by_games()

    async def get_rating_by_stability(self):
        return await self._db.get_rating_by_stability()

    async def get_rating_by_winrate(self):
        return await self._db.get_rating_by_winrate()

    async def get_personal_stat(self, name):
        return await self._db.get_personal_stat(name)

    async def get_rating_by_win_streak(self):
        return await self._db.get_rating_by_win_streak()

    async def get_rating_by_loss_streak(self):
        return await self._db.get_rating_by_loss_streak()
