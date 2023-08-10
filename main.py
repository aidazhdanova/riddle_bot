import os
import random
import telebot
from dotenv import load_dotenv
import re

load_dotenv()


class RiddleMasterBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.riddles = {
            "С виду — клин, а развернешь — блин": "Зонт",
            "Что принадлежит вам, однако другие этим пользуются чаще, чем вы сами?": "Имя",
            "Я такая хрупкая, что если ты произнесешь мое имя, ты сломаешь меня. Кто я?": "Тишина",
            "Я говорю без рта и слышу без ушей. У меня нет тела, но я парю вместе с ветром. Что я?": "Эхо",
            "Что следует вверх и вниз, но остается при этом на месте?": "Лестница",
            "Если он у вас есть, вы хотите поделиться. Если вы поделились, у вас его уже нет. Что это такое?": "Секрет",
            "Благодаря мне вы можете видеть сквозь стену. Что я?": "Окно",
            "Что идет без ног?": "Время",
            "Что проходит через леса, поля и города, но при этом никуда не движется?": "Дорога",
            "Идешь, идешь, а конца не найдешь": "Земной шар",
            "Какие 2 ноты обозначают съедобный продукт?": "Фа-соль",
            "Без рук, без ног, А рисовать умеет": "Мороз",
        }
        self.user_data = {}

        self.bot.message_handler(commands=['start'])(self.start)
        self.bot.message_handler(func=lambda message: message.text.lower() == "загадка")(self.send_riddle)
        self.bot.message_handler(func=lambda message: message.text.lower() == "еще")(self.send_riddle)
        self.bot.message_handler(content_types=['text'])(self.process_riddle)
        self.bot.callback_query_handler(func=lambda call: call.data == "start_riddle")(self.callback_start_riddle)

        # Создание случайного порядка загадок
        self.random_riddle_order = list(self.riddles.keys())
        random.shuffle(self.random_riddle_order)

    def start(self, message):
        """Обработчик команды /start."""
        self.user_data[message.chat.id] = {"current_riddle": None}
        markup = telebot.types.InlineKeyboardMarkup()
        start_button = telebot.types.InlineKeyboardButton("Хочу загадку", callback_data="start_riddle")
        markup.add(start_button)
        self.bot.send_message(
            message.chat.id,
            "Привет! Я бот-загадочник. Поиграем?",
            reply_markup=markup)

    def send_riddle(self, message):
        """Отправка пользователю загадки."""
        if not self.random_riddle_order:
            self.bot.send_message(
                message.chat.id,
                "Все загадки закончились. Можете попробовать еще раз позже.")
            return

        riddle = self.random_riddle_order.pop()
        self.user_data[message.chat.id]["current_riddle"] = riddle

        self.bot.send_message(message.chat.id, riddle)

    def process_riddle(self, message):
        """Обработка ответа пользователя на загадку."""
        if message.text.lower() == "загадка":
            self.send_riddle(message)
            return

        riddle = self.user_data[message.chat.id]["current_riddle"]
        expected_answer = self.riddles[riddle].lower()

        user_answer = re.sub(r'[^\w\s]', '', message.text.lower())
        # Удаляем все символы

        user_words = set(user_answer.split())
        expected_words = set(expected_answer.split())

        if user_words & expected_words:
            self.bot.send_message(message.chat.id, "Верно!")
            self.send_riddle(message)
        else:
            self.bot.send_message(message.chat.id,
                                  f"Неправильно. Правильный ответ: {expected_answer}")
            self.bot.send_message(
                message.chat.id,
                "Напишите 'Загадка', чтобы получить новую загадку.")

    def callback_start_riddle(self, call):
        """Обработчик коллбэка для начала новой загадки."""
        self.send_riddle(call.message)

    def start_polling(self):
        """Запуск бота в режиме ожидания новых сообщений."""
        self.bot.polling()


if __name__ == "__main__":
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    bot = RiddleMasterBot(token)
    bot.start_polling()