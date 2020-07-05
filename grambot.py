from aiogram import Bot, Dispatcher, executor, types # Сам aiogram
from aiogram.types.message import ContentType

import config  # Файл конфигурации с константами
import logging   # Библиотека логгирования

from sqliter import Sqliter  # Объект для работы с базой данных
from game import GameProcess  # Объект - процесс игры
import re


"""Logging"""
logging.basicConfig(format='%(asctime)s - %(message)s', filename="Simple_logging.log",  level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Bot started working")

"""Setting up a bot"""
bot = Bot(token=config.API_TOKEN)
dp = Dispatcher(bot)

"""Creating database instance"""
database = Sqliter('database.db')

"""Some global variables"""
current_bet_amount = 0
first_throw_result = 0
winning_numbers = []


async def common_rules(chat_id):
    """
    Sends main message to new user to chat_id
    :param chat_id:
    :return:
    """
    await bot.send_message(chat_id, "Здесь мы катаем игральный кубик и выигрываем деньги)")
    await bot.send_dice(chat_id)
    await bot.send_message(chat_id, "Твой начальный банк: 100 рублей. Отправь мне команду /play и выбери сумму своей ставки")
    await bot.send_message(chat_id, "Попробуй бросить кубик! (его можно найти, если выбить 'dice' в поле ввода сообщения)")
    await bot.send_message(chat_id, "Или отправь команду '/rules', чтобы подробно прочитать правила")


async def connect_database(chat_id, user_id):
    """
    Checks if new user is already registered in a game
    :param chat_id:
    :param user_id:
    :return:
    """
    if database.user_exists(user_id):
        user_info = database.get_user_info(user_id)
        return user_info

    else:
        await bot.send_message(chat_id, "Вы ещё не зарегистрированы! Пожалуйста, введите /start")
        return None


@dp.message_handler(commands=['rules'])
async def send_rules(message):
    """
    handles /rules command.
    sends main rules to a user
    :param message:
    :return:
    """
    await message.answer("Правила очень просты: ты бросаешь кубик 2 раза")
    await message.answer("Первый бросок называется 'счастливым', а второй - 'выигрышным'")
    await message.answer("Смысл игры - первым броском выбросить максимальное число, а вторым - минимальное")
    await message.answer("Если первым броском выбросить 6, а вторым - 1, то твоя ставка увеличится в 4 раза! ")
    with open('rules_table.jpg', 'rb') as photo:
        await bot.send_photo(
            message.chat.id,
            photo,
            caption="Вот таблица со всеми значениями")
    await message.answer("Отправь /play, чтобы начать игру!")


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    """
    handles /start command.
    checks if user already exists
    if so, asks him to send /play command and gives him his current balance
    else adds all the user data to the database and sends him common welcome messages
    :param message:
    :return:
    """

    if database.user_exists(message.from_user.id):
        user_info = database.get_user_info(message.from_user.id)
        await message.answer(f"{user_info[0][2]}, ты уже зарегистрирован!")
        await message.answer(f"Сейчас твой баланс: {user_info[0][6]} руб. Хочешь сделать ставку? Отправь /play")

    else:
        database.add_user(message)
        await message.answer(f"Поздравляю, {message.from_user.first_name} ты успешно зарегистрировался как игрок!")
        await common_rules(message.chat.id)


@dp.message_handler(commands=['play'])
async def balance(message):
    """
    symply checks user balance in the database
    NEEDS IMPROVEMENT!!!
    :param message:
    :return:
    """
    user_data = await connect_database(message.chat.id, message.from_user.id)
    if user_data:
        print(user_data)
        await bot.send_message(user_data[0][7], f"{user_data[0][2]}, Ваш текущий баланс: {user_data[0][6]} руб.")
        await bot.send_message(user_data[0][7], f"Хотите сделать ставку? Просто отправьте мне сообщение вида: "
                                                f"'Ставка 50' с суммой желаемой ставки")

    else:
        print("No such data")


#@dp.message_handler(regexp='^Ставка\s\d\d')
@dp.message_handler(regexp='(?:^[Сс]тавка|^[Bb]et|)\s\d\d')
async def make_bet(message):
    """
    handles special command for bet making 'Ставка &amound'
    checks if user finished previous game already
    divides a string and gets it's first number, then checks the database for user's current balance
    if balance token value is big enough to make a bet confirms it to a user and adds all the info into a database
    :param message:
    :return:
    """
    global current_bet_amount
    if first_throw_result == 0:                                                     # Is it a first throw? if so:
        a = re.split(' ', message.text)                                             # divide a string
        user_data = await connect_database(message.chat.id, message.from_user.id)  #!!!FIX THiS!!! HAVE A SPECIAL FUNCTION FOR A BALANCE CHECK!
        user_balance = user_data[0][6]
        new_balance = user_balance - int(a[1])
        if new_balance >= 0:                                                        # Check if balance is big enough
            current_bet_amount = a[1]
            database.set_new_balance(message.from_user.id, new_balance)
            await message.answer(f"Отлично: твоя ставка: {a[1]} руб.")            # Confirm
            await message.answer(f"На счету осталось: {new_balance} руб.")
            await message.answer(f"Бросай кубик!")
    else:                                                                            # If not:
        print("Ты не закончил с текущей игрой, ставок пока нет")                     # Not allowing to make a new bet


@dp.message_handler(content_types=ContentType.DICE)
async def game(message):
    """
    Handles messages with dice
    gets amount given
    if all bets are off creates a new game and checks if this is a first throw or second
    calculates all the data and gives a result to a user
    connects to the database and makes all the changes required
    :param message:
    :return:
    """
    global first_throw_result
    global winning_numbers
    global current_bet_amount
    current_dice_side = int(message.dice['value'])

    if current_bet_amount == 0:
        await message.answer(f"Ты ещё не сделал ставку, дружок! Отправь мне /play")
    else:

        if first_throw_result == 0:
            print("Created new game")
            a = GameProcess(current_dice_side)
            winning_numbers = a.first_throw()
            await message.answer(f"Отлично! У тебя выпала цифра {current_dice_side}")
            await message.answer(f"Теперь для победы надо выбить {winning_numbers}")
            first_throw_result = current_dice_side

        else:
            print(f"Continuing the game, first throw value is {current_dice_side}")
            a = GameProcess(current_dice_side)
            b = a.second_throw(current_dice_side, winning_numbers, current_bet_amount)
            if b == 0:
                await message.answer("К сожалению, вы проиграли")
                await message.answer(f"Текущий баланс: {database.check_balance(message.from_user.id)}")

            else:
                await message.answer(f"Вам возвращено {round(b)} руб. на счет")
                database.add_money_won(message.from_user.id, b)

                await message.answer(f"Текущий баланс: {database.check_balance(message.from_user.id)}")

            first_throw_result = 0
            winning_numbers = 0

#    dice_type = message.dice['emoji']


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
