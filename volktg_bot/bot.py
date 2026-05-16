from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandObject
from aiogram.types import Message, BotCommand
from datetime import datetime
from prettytable import PrettyTable


from . import logger
from . poker_rating import PokerRating


log = logger.logger_get()


class TGBot:
    def __init__(self, bot_token: str, poker_rating: PokerRating):
        self._bot = Bot(token=bot_token)
        self._dp = Dispatcher()
        self._pr = poker_rating

        self._dp.message.register(self._help_handler, Command("help"))
        self._dp.message.register(self._info_handler, Command("info"))
        self._dp.message.register(self._start_handler, Command("start"))
        self._dp.message.register(self._poker_personal_rating_handler, Command("rating_personal"))

        self._dp.message.register(self._poker_top_profit_handler, Command("top_profit"))
        self._dp.message.register(self._poker_top_roi_handler, Command("top_roi"))
        self._dp.message.register(self._poker_top_average_handler, Command("top_average"))
        self._dp.message.register(self._poker_top_games_handler, Command("top_games"))
        self._dp.message.register(self._poker_top_winrate_handler, Command("top_winrate"))
        self._dp.message.register(self._poker_top_bestgames_handler, Command("top_bestgames"))
        self._dp.message.register(self._poker_top_worstgames_handler, Command("top_worstgames"))
        self._dp.message.register(self._poker_top_bankroll_handler, Command("top_bankroll"))
        self._dp.message.register(self._poker_top_stability_handler, Command("top_stability"))
        self._dp.message.register(self._poker_top_winstreak_handler, Command("top_winstreak"))
        self._dp.message.register(self._poker_top_lossstreak_handler, Command("top_lossstreak"))
        self._dp.message.register(self._poker_top_best_handler, Command("top_best"))

        self._dp.message.register(self._message_handler)
        self._dp.edited_message.register(self._edited_message_handler)

    async def run(self):
        await self._bot_command_menu()
        await self._dp.start_polling(self._bot)

    @staticmethod
    def _log_prefix(message: Message):
        return f"[chat_id={message.chat.id}({message.chat.type}) message_id={message.message_id} user_id={message.from_user.id} name=[{message.from_user.full_name}]"

    async def _bot_command_menu(self):
        await self._bot.set_my_commands([
            BotCommand(command="start", description="Старт"),
            BotCommand(command="help", description="Что я умею"),
            BotCommand(command="info", description="Информация о тебе"),
            BotCommand(command="rating_personal", description="Персональный рейтинг"),
            BotCommand(command="top_profit", description="Топ по сумме выигрыша"),
            BotCommand(command="top_roi", description="Топ по ROI"),
            BotCommand(command="top_average", description="Топ по среднему выигрышу"),
            BotCommand(command="top_games", description="Топ по количеству сыгранных игр"),
            BotCommand(command="top_winrate", description="Топ по проценту прибыльных игр"),
            BotCommand(command="top_bestgames", description="Топ по крупнейшим выигрышам"),
            BotCommand(command="top_worstgames", description="Топ по крупнейшим проигрышам"),
            BotCommand(command="top_bankroll", description="Топ по открутке банка"),
            BotCommand(command="top_stability", description="Топ по стабильности"),
            BotCommand(command="top_winstreak", description="Топ по выигрышам подряд"),
            BotCommand(command="top_lossstreak", description="Топ по проигрышам подряд"),
            BotCommand(command="top_best", description="Топ самых самых")
        ])

    async def _help_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: HELP")
        await message.answer_sticker("CAACAgIAAxkBAAOBaXubovBrCT0ItL2A1eWI0P8lrtkAAlYcAAMaGUg72lu9-vO6sDgE") # Тиньков - ни-х-я
        await message.answer("Меню слева - всё что я умею")

    async def _start_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: START")
        await message.answer("Привет! Я бот. Мой создатель - Дмитрий Волков")

    async def _info_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: INFO")
        response = (
            f"Информация о тебе:\n\n"
            f"ID: {message.from_user.id}\n"
            f"Бот: {'Да' if message.from_user.is_bot else 'Нет'}\n"
            f"Имя: {message.from_user.first_name}\n"
            f"Фамилия: {message.from_user.last_name}\n"
            f"Имя пользователя: @{message.from_user.username}\n"
            f"Язык: {message.from_user.language_code}\n"
            f"Премиум: {'Нет' if message.from_user.is_premium is None else 'Да'}"
        )
        await message.answer(response)

    async def _message_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: send message text=[{message.text}]")
        log.debug(f"{self._log_prefix(message)}: {message}")

        if 'drop table' in message.text:
            await message.answer("Хорошая попытка, но нет")

    async def _edited_message_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: edit message text=[{message.text}]")

        edit_date = message.edit_date
        response = (
            f"📝 Сообщение отредактировано!\n"
            f"🕒 Время редактирования: {datetime.fromtimestamp(edit_date)}\n"
            f"📄 Новый текст: {message.text or '[Нет текста]'}\n"
            f"👤 Пользователь: {message.from_user.full_name}"
        )

        await message.answer(response)

    async def _poker_top_best_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP BEST")

        records_win = await self._pr.get_top_win(1)
        records_lose = await self._pr.get_top_lose(1)
        records_roll = await self._pr.get_top_roll(1)
        records_table = await self._pr.get_top_table()

        win = records_win[0]
        lose = records_lose[0]
        roll = records_roll[0]
        table = records_table[0]

        response = (
            f'🤑 Самый крупный выигрыш:\n{win["name"]} {win["prize"]} руб. ({win["game_date"]})\n\n'
            f'😱 Самый крупный проигрыш:\n{lose["name"]} {lose["prize"]} руб. ({lose["game_date"]})\n\n'
            f'🤡 Самая крупная открутка:\n{roll["name"]} Закуп: {roll["bank_start"]} руб. Выигрыш: {roll["prize"]} руб. ({roll["game_date"]})\n\n'
            f'💰 Самый дорогой стол:\n{table["bank"]} руб. ({table["game_date"]}, {table["players_count"]} игроков)\n\n'
        )
        await message.answer(response, parse_mode='Markdown')

    async def _poker_personal_rating_handler(self, message: Message, command: CommandObject):
        log.debug(f"{self._log_prefix(message)}: POKER PERSONAL RATING [{message.text}]")
        if not command.args:
            await message.answer("/rating_personal <name>")
            return

        #arguments = command.args.split()
        name = command.args

        records = await self._pr.get_personal_game_history(name)
        if len(records) == 0:
            await message.answer('Игрок не найден')
            return

        table = PrettyTable()
        table.field_names = ['Дата', 'Закуп', 'Выигрыш']
        table.align['Дата'] = "l"
        table.align['Закуп'] = "l"
        table.align['Выигрыш'] = "l"
        for rec in records:
            table.add_row([rec['game_date'], rec['bank_start'], rec['prize']])

        total = await self._pr.get_personal_stat(name)

        win = await self._pr.get_personal_top_win(name)
        lose = await self._pr.get_personal_top_lose(name)
        roll = await self._pr.get_personal_top_roll(name)

        win_line = '🤑 Самый крупный выигрыш:\nНет выигрышей\n'
        if len(win) > 0:
            win_line = f'🤑 Самый крупный выигрыш:\n{win[0]["prize"]} руб. ({win[0]["game_date"]})\n'

        lose_line = '😱 Самый крупный проигрыш:\nНет проигрышей\n'
        if len(lose) > 0:
            lose_line = f'😱 Самый крупный проигрыш:\n{lose[0]["prize"]} руб. ({lose[0]["game_date"]})\n'

        roll_line = '🤡 Самая крупная открутка:\nНет откруток\n'
        if len(roll) > 0:
            roll_line = f'🤡 Самая крупная открутка:\nЗакуп: {roll[0]["bank_start"]} руб. Выигрыш: {roll[0]["prize"]} руб. ({roll[0]["game_date"]})\n'

        total_games_in_league = total[0]['total_games_in_league']
        total_games = total[0]['total_games']
        total_profit = total[0]['total_profit']
        total_buyin = total[0]['total_buyin']
        avg_buyin = total[0]['avg_buyin']
        stddev_buyin = total[0]['stddev_buyin']
        roi = total[0]['roi']
        avg_profit = total[0]['avg_profit']
        prize_stddev = total[0]['prize_stddev']
        winning_games = total[0]['winning_games']
        losing_games = total[0]['losing_games']
        participation_percentage = total[0]['participation_percentage']
        win_rate = total[0]['win_rate']

        response = (
            f'Статистика игрока: *{name}*\n'
            f'Участие в играх: {total_games}/{total_games_in_league} ({participation_percentage}%)\n'
            f'  - выиграно: {winning_games}\n'
            f'  - проиграно: {losing_games}\n'
            f'Баланс: {total_profit} руб.\n'
            f'Закуп: {total_buyin} руб.\n'
            f'ROI: {roi}%\n'
            f'Средний выигрыш: {avg_profit} (±{prize_stddev}) руб.\n'
            f'Средний закуп: {avg_buyin} (±{stddev_buyin}) руб.\n'
            f'Процент побед: {win_rate}%\n'
            '\n'
            f'{win_line}'
            f'{lose_line}'
            f'{roll_line}'
            '\n'
            f'История игр:\n'
            f'```\n{table.get_string()}```'
        )
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_profit_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP PROFIT")

        records = await self._pr.get_by_total_prize()
        table = PrettyTable()
        table.field_names = ['Имя', 'Игры', 'Выигрыш']
        table.align['Имя'] = "l"
        table.align['Игры'] = "c"
        table.align['Выигрыш'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['total_games'], rec['total_prize']])

        response = '🏆 Топ игроков по общему выигрышу:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_roi_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP ROI")

        records = await self._pr.get_cash_by_roi()
        table = PrettyTable()
        table.field_names = ['Имя', 'Выигрыш', 'Закуп', 'ROI']
        table.align['Имя'] = "l"
        table.align['Выигрыш'] = "l"
        table.align['Закуп'] = "l"
        table.align['ROI'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['total_profit'], rec['total_buyin'], rec['roi']])

        response = '🏆 Топ игроков по ROI (Return on Investment):\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_average_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP AVERAGE")

        records = await self._pr.get_by_average_prize()
        table = PrettyTable()
        table.field_names = ['Имя', 'Игры', 'Среднее']
        table.align['Имя'] = "l"
        table.align['Игры'] = "c"
        table.align['Среднее'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['total_games'], rec['average']])

        response = '🏆 Топ игроков по среднему выигрышу:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_games_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP GAMES")

        records = await self._pr.get_rating_by_games()
        table = PrettyTable()
        table.field_names = ['Имя', 'Игры']
        table.align['Имя'] = "l"
        table.align['Игры'] = "c"
        for rec in records:
            table.add_row([rec['name'], rec['games_played']])

        response = '🏆 Топ игроков по количеству сыгранных игр:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_winrate_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP WINRATE")

        records = await self._pr.get_rating_by_winrate()
        table = PrettyTable()
        table.field_names = ['Имя', 'Игры', 'Выигрыши', 'Процент']
        table.align['Имя'] = "l"
        table.align['Игры'] = "c"
        table.align['Выигрыши'] = "c"
        table.align['Процент'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['total_games'], rec['winning_games'], rec['win_rate']])

        response = '🏆 Топ игроков по проценту прибыльных игр:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_bestgames_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP BESTGAMES")

        records = await self._pr.get_top_win(10)
        table = PrettyTable()
        table.field_names = ['Имя', 'Дата', 'Закуп', 'Выигрыш']
        table.align['Имя'] = "l"
        table.align['Дата'] = "l"
        table.align['Закуп'] = "l"
        table.align['Выигрыш'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['game_date'], rec['bank_start'], rec['prize']])

        response = '🏆 Топ игроков по крупнейшим выигрышам:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_worstgames_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP WORSTGAMES")

        records = await self._pr.get_top_lose(10)
        table = PrettyTable()
        table.field_names = ['Имя', 'Дата', 'Закуп', 'Выигрыш']
        table.align['Имя'] = "l"
        table.align['Дата'] = "l"
        table.align['Закуп'] = "l"
        table.align['Выигрыш'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['game_date'], rec['bank_start'], rec['prize']])

        response = '🏆 Топ игроков по крупнейшим проигрышам:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')


    async def _poker_top_bankroll_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP BANKROLL")

        records = await self._pr.get_top_roll(10)
        table = PrettyTable()
        table.field_names = ['Имя', 'Дата', 'Закуп', 'Выигрыш']
        table.align['Имя'] = "l"
        table.align['Дата'] = "l"
        table.align['Закуп'] = "l"
        table.align['Выигрыш'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['game_date'], rec['bank_start'], rec['prize']])

        response = '🏆 Топ игроков по открутке банка:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_stability_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP STABILITY")

        records = await self._pr.get_rating_by_stability()
        table = PrettyTable()
        table.field_names = ['Имя', 'Игры', 'Отклонение', 'Среднее']
        table.align['Имя'] = "l"
        table.align['Дата'] = "l"
        table.align['Отклонение'] = "l"
        table.align['Среднее'] = "l"
        for rec in records:
            table.add_row([rec['name'], rec['games'], rec['prize_stddev'], rec['avg_prize']])

        response = '🏆 Топ игроков с самым предсказуемым результатом:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_winstreak_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP WINSTREAK")

        records = await self._pr.get_rating_by_win_streak()
        table = PrettyTable()
        table.field_names = ['Имя', 'Win Streak']
        table.align['Имя'] = "l"
        table.align['Win Streak'] = "c"
        for rec in records:
            table.add_row([rec['player_name'], rec['max_streak_without_loss']])

        response = '🏆 Топ игроков по выигранным играм подряд:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')

    async def _poker_top_lossstreak_handler(self, message: Message):
        log.debug(f"{self._log_prefix(message)}: POKER TOP LOSSSTREAK")

        records = await self._pr.get_rating_by_loss_streak()
        table = PrettyTable()
        table.field_names = ['Имя', 'Loss Streak']
        table.align['Имя'] = "l"
        table.align['Loss Streak'] = "c"
        for rec in records:
            table.add_row([rec['player_name'], rec['max_streak_without_win']])

        response = '🏆 Топ игроков по проигранным играм подряд:\n```\n{}```'.format(table.get_string())
        await message.answer(response, parse_mode='Markdown')
