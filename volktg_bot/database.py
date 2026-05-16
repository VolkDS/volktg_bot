import asyncio
import asyncpg
import os

from typing import Optional

from . import logger

log = logger.logger_get()


class Database:
    def __init__(self):
        self._connect = None  # type: Optional[asyncpg.Connection]
        self._connecting = False
        self._stopping = False
        self.connected_callback = None

    async def run(self):
        while True:
            if self._connected():
                await asyncio.sleep(1)
                continue

            try:
                self._connect = await asyncpg.connect(
                    host=os.getenv("DATABASE_HOST"),
                    port=os.getenv("DATABASE_PORT"),
                    user=os.getenv("DATABASE_USERNAME"),
                    password=os.getenv("DATABASE_PASSWORD"),
                    database=os.getenv("DATABASE_DBNAME"),
                    timeout=10,
                    statement_cache_size=0,
                    command_timeout=10
                )  # type: Optional[asyncpg.Connection]
                self._connect.add_termination_listener(self._on_disconnect)
                log.info(f'Connected to DB successful')
                if self._connected() and self.connected_callback:
                    self.connected_callback()

            except Exception as e:
                log.error(f'Connection to DB failed: {e}')
                await asyncio.sleep(1)

    def _connected(self):
        return self._connect is not None and not self._connect.is_closed()

    def _on_disconnect(self, connect):
        log.error(f'DB disconnected')
        self._connect = None

    async def get_rating_by_total_prize(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            with a as (
                select p."name", count(*) as total_games, sum(prize) as total_prize
                from game_player gp
                join player p on p.id = gp.player_id
                join game g on g.id = gp.game_id
                where g.game_type_id = 1
                group by p."name"
            )
            select a.name, a.total_games, a.total_prize
            from a
            --where a.total_games > 2
            order by 3 desc, 2
        ''')
        return records

    async def get_rating_by_average_prize(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select
                p.name,
                count(gp.game_id) as total_games,
                sum(gp.prize) as total_prize,
                round(avg(gp.prize), 2) as average
            from game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where g.game_type_id = 1
            group by p.name
            having count(gp.game_id) > 2
            order by average desc
        ''')
        return records

    async def get_rating_by_bank_prize(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            with a as (
                select p."name", count(*) as total_games, sum(gp.bank_start) as total_bank_start, sum(gp.prize) as total_prize
                from game_player gp
                join player p on p.id = gp.player_id
                join game g on g.id = gp.game_id
                where g.game_type_id = 1
                group by p."name"
            )
            select a.name, a.total_games, a.total_bank_start, a.total_prize, round(a.total_prize::numeric/a.total_bank_start::numeric, 3) as bank_prize
            from a
            -- where a.total_games > 2
            order by 5 desc
        ''')
        return records

    async def get_top_win(self, limit):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select 
                p."name",
                gp.bank_start, 
                gp.prize,
                g.created::date as game_date
            from poker_stat.game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where g.game_type_id = 1
            order by gp.prize desc, gp.bank_start desc
            limit $1
        ''', limit)
        return records

    async def get_top_lose(self, limit):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select p."name", gp.bank_start, gp.prize, g.created::date as game_date
            from poker_stat.game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where g.game_type_id = 1
            order by gp.prize, gp.bank_start
            limit $1
        ''', limit)
        return records

    async def get_top_roll(self, limit):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select 
                p.name,
                gp.bank_start,
                gp.prize,
                g.created::date as game_date
            from poker_stat.game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where gp.prize > 0
                and g.game_type_id = 1
            order by gp.bank_start desc, gp.prize desc
            limit $1
        ''', limit)
        return records

    async def get_top_table(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select 
                g.created::date as game_date,
                sum(gp.bank_start) as bank,
                count(gp.player_id) as players_count
            from game_player gp
            join game g on g.id = gp.game_id
            where g.game_type_id = 1
            group by gp.game_id, g.created
            order by 2 desc
            limit 1
        ''')
        return records

    async def get_personal_game_history(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select g.created::date as game_date, gp.bank_start, gp.bank_end, gp.prize
            from game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where g.game_type_id = 1
                and p."name" = $1
            order by 1
        ''', name)
        return records

    async def get_personal_total_prize(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            with a as (
                select p."name", count(*) as total_games, sum(prize) as total_prize
                from game_player gp
                join player p on p.id = gp.player_id
                join game g on g.id = gp.game_id
                where g.game_type_id = 1
                group by p."name"
            )
            select a.name, a.total_games, a.total_prize
            from a
            where a.name = $1
        ''', name)
        return records

    async def get_personal_average_prize(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            with a as (
                select p."name", count(*) as total_games, sum(prize) as total_prize
                from game_player gp
                join player p on p.id = gp.player_id
                join game g on g.id = gp.game_id
                where g.game_type_id = 1
                group by p."name"
            )
            select a.name, a.total_games, (a.total_prize / a.total_games) as average
            from a
            where a.name = $1
        ''', name)
        return records

    async def get_personal_top_win(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select p."name", gp.bank_start, gp.prize, g.created::date as game_date
            from poker_stat.game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where gp.prize > 0
                and g.game_type_id = 1
                and p."name" = $1
            order by gp.prize desc, gp.bank_start desc
            limit 1
        ''', name)
        return records

    async def get_personal_top_lose(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select p."name", gp.bank_start, gp.prize, g.created::date as game_date
            from poker_stat.game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where gp.prize < 0
                and g.game_type_id = 1
                and p."name" = $1
            order by gp.prize, gp.bank_start
            limit 1
        ''', name)
        return records

    async def get_personal_top_roll(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            select p."name", gp.bank_start, gp.bank_end, gp.prize, g.created::date as game_date
            from poker_stat.game_player gp
            join player p on p.id = gp.player_id
            join game g on g.id = gp.game_id
            where gp.prize > 0
                and g.game_type_id = 1
                and p."name" = $1
            order by gp.bank_start desc, gp.prize desc
            limit 1
        ''', name)
        return records

    async def get_cash_by_roi(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            SELECT p.name,
                SUM(gp.prize) AS total_profit,
                SUM(gp.bank_start) AS total_buyin,
                ROUND(SUM(gp.prize) * 100.0 / NULLIF(SUM(gp.bank_start), 0), 2) AS roi
            FROM player p
            JOIN game_player gp ON p.id = gp.player_id
            JOIN game g ON gp.game_id = g.id
            WHERE g.league_id = 1
                and g.game_type_id = 1
            GROUP BY p.name
            HAVING COUNT(*) > 2
            ORDER BY roi DESC
        ''')
        return records

    async def get_rating_by_games(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            SELECT 
                p.name,
                COUNT(*) AS games_played
            FROM player p
            JOIN game_player gp ON p.id = gp.player_id
            JOIN game g ON gp.game_id = g.id
            WHERE g.league_id = 1
                and g.game_type_id = 1
            GROUP BY p.name
            ORDER BY games_played DESC
        ''')
        return records

    async def get_rating_by_winrate(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            SELECT p.name,
                COUNT(*) AS total_games,
                SUM(CASE WHEN gp.prize > 0 THEN 1 ELSE 0 END) AS winning_games,
                ROUND(SUM(CASE WHEN gp.prize > 0 THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS win_rate
            FROM player p
            JOIN game_player gp ON p.id = gp.player_id
            JOIN game g ON gp.game_id = g.id
            WHERE g.league_id = 1
                and g.game_type_id = 1
            GROUP BY p.name
            HAVING COUNT(*) > 2
            ORDER BY win_rate DESC
        ''')
        return records

    async def get_personal_stat(self, name):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            WITH player_stats AS (
                SELECT
                    p.name,
                    COUNT(*) AS total_games,
                    SUM(gp.prize) AS total_profit,
                    SUM(gp.bank_start) AS total_buyin,
                    ROUND(AVG(gp.bank_start), 2) AS avg_buyin,
                    ROUND(STDDEV(gp.bank_start), 2) AS stddev_buyin,
                    ROUND(COALESCE(SUM(gp.prize) * 100.0 / NULLIF(SUM(gp.bank_start), 0), 0), 2) AS roi,
                    ROUND(AVG(gp.prize), 2) AS avg_profit,
                    ROUND(STDDEV(gp.prize), 2) as prize_stddev,
                    MAX(gp.prize) AS best_game,
                    MIN(gp.prize) AS worst_game,
                    SUM(CASE WHEN gp.prize > 0 THEN 1 ELSE 0 END) AS winning_games,
                    SUM(CASE WHEN gp.prize < 1 THEN 1 ELSE 0 END) AS losing_games
                FROM player p
                JOIN game_player gp ON p.id = gp.player_id
                JOIN game g ON gp.game_id = g.id
                WHERE p.name = $1 
                    AND g.league_id = 1
                    AND g.game_type_id = 1
                GROUP BY p.name
            ),
            league_games AS (
                SELECT COUNT(DISTINCT id) AS total_games_in_league
                FROM game
                WHERE league_id = 1
                    and game_type_id = 1
            )
            SELECT
                ps.*,
                lg.total_games_in_league,
                ROUND((ps.total_games * 100.0 / lg.total_games_in_league), 2) AS participation_percentage,
                ROUND((ps.winning_games * 100.0 / ps.total_games), 2) AS win_rate
            FROM player_stats ps
            CROSS JOIN league_games lg;
        ''', name)
        return records

    async def get_rating_by_stability(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            SELECT
                p.name,
                ROUND(STDDEV(gp.prize), 2) as prize_stddev,
                COUNT(*) as games,
                ROUND(AVG(gp.prize), 2) as avg_prize
            FROM game_player gp
            JOIN player p ON gp.player_id = p.id
            JOIN game g ON gp.game_id = g.id
            WHERE g.league_id = 1
                AND g.game_type_id = 1
            GROUP BY p.name
            HAVING COUNT(*) > 2
            ORDER BY prize_stddev ASC
        ''')
        return records

    async def get_rating_by_win_streak(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            WITH player_games AS (
                -- Шаг 1: Получаем все игры каждого игрока с отметкой о выигрыше
                SELECT
                    gp.player_id,
                    p.name as player_name,
                    g.id as game_id,
                    g.created,
                    CASE
                        WHEN gp.prize > 0 THEN 1  -- Выигрыш
                        ELSE 0                     -- Проигрыш
                    END as is_win
                FROM game_player gp
                JOIN game g ON g.id = gp.game_id
                JOIN player p ON p.id = gp.player_id
                WHERE g.game_type_id = 1
            ),
            streak_groups AS (
                -- Шаг 2: Определяем группы последовательных игр без проигрышей
                -- Ключевая идея: считаем количество проигрышей (is_win = 0) до текущей строки
                SELECT
                    player_id,
                    player_name,
                    game_id,
                    created,
                    is_win,
                    COUNT(CASE WHEN is_win = 0 THEN 1 END)
                        OVER (PARTITION BY player_id ORDER BY created) as loss_group
                FROM player_games
            ),
            streaks AS (
                -- Шаг 3: Считаем длину каждой серии без проигрышей
                SELECT
                    player_id,
                    player_name,
                    loss_group,
                    COUNT(*) as streak_length
                FROM streak_groups
                WHERE is_win = 1  -- Учитываем только выигрышные игры
                GROUP BY player_id, player_name, loss_group
            ),
            max_streaks AS (
                -- Шаг 4: Для каждого игрока находим максимальную серию
                SELECT
                    player_id,
                    player_name,
                    MAX(streak_length) as max_streak
                FROM streaks
                GROUP BY player_id, player_name
            )
            -- Шаг 5: Выводим результат, включая игроков без выигрышей
            SELECT
                p.name as player_name,
                COALESCE(ms.max_streak, 0) as max_streak_without_loss
            FROM player p
            LEFT JOIN max_streaks ms ON ms.player_id = p.id
            ORDER BY max_streak_without_loss DESC, player_name;
        ''')
        return records

    async def get_rating_by_loss_streak(self):
        if not self._connected():
            return []

        records = await self._connect.fetch('''
            WITH player_games AS (
                -- Шаг 1: Получаем все игры каждого игрока с отметкой о проигрыше
                SELECT
                    gp.player_id,
                    p.name as player_name,
                    g.id as game_id,
                    g.created,
                    CASE
                        WHEN gp.prize > 0 THEN 0  -- Выигрыш
                        ELSE 1                    -- Проигрыш
                    END as is_loss
                FROM game_player gp
                JOIN game g ON g.id = gp.game_id
                JOIN player p ON p.id = gp.player_id
                WHERE g.game_type_id = 1
            ),
            streak_groups AS (
                -- Шаг 2: Определяем группы последовательных игр без выигрышей
                -- Ключевая идея: считаем количество выигрышей (is_loss = 0) до текущей строки
                SELECT
                    player_id,
                    player_name,
                    game_id,
                    created,
                    is_loss,
                    COUNT(CASE WHEN is_loss = 0 THEN 1 END)
                        OVER (PARTITION BY player_id ORDER BY created) as win_group
                FROM player_games
            ),
            streaks AS (
                -- Шаг 3: Считаем длину каждой серии без выигрышей
                SELECT
                    player_id,
                    player_name,
                    win_group,
                    COUNT(*) as streak_length
                FROM streak_groups
                WHERE is_loss = 1  -- Учитываем только проигрышные игры
                GROUP BY player_id, player_name, win_group
            ),
            max_streaks AS (
                -- Шаг 4: Для каждого игрока находим максимальную серию
                SELECT
                    player_id,
                    player_name,
                    MAX(streak_length) as max_streak
                FROM streaks
                GROUP BY player_id, player_name
            )
            -- Шаг 5: Выводим результат, включая игроков без выигрышей
            SELECT
                p.name as player_name,
                COALESCE(ms.max_streak, 0) as max_streak_without_win
            FROM player p
            LEFT JOIN max_streaks ms ON ms.player_id = p.id
            ORDER BY max_streak_without_win DESC, player_name;
        ''')
        return records
