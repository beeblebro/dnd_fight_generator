import telebot
import logging
from telebot import types
from generate_fight import generate_fight


with open("config/.token") as fp:
    token = fp.read()

bot = telebot.TeleBot(token)
default_error_message = "Что-то пошло не так"
telebot.logger.setLevel(logging.DEBUG)


class RandomFight:
    def __init__(self, n_heroes):
        self.n_heroes = n_heroes
        self.experience = None
        self.insignificance_threshold = None
        self.n_strong = None
        self.n_weak = None
        

def is_digit(message, function, error_message="Нужно ввести целое число"):
    if not message.text.isdigit():
        msg = bot.reply_to(message, error_message)
        bot.register_next_step_handler(msg, function)


@bot.message_handler(commands=['help'])
def help(message):
    with open("config/help_message") as fp:
        help_message = fp.read()
    bot.send_message(message.chat.id, help_message)


@bot.message_handler(commands=['generate_random_fight'])
def begin(message):
    try:
        answer = bot.reply_to(message, "Число героев:")
        bot.register_next_step_handler(answer, n_heroes)
    except Exception as e:
        bot.reply_to(message, default_error_message)

        
def n_heroes(message):
    try:
        is_digit(message, n_heroes)
        fight = RandomFight(int(message.text))
        answer = bot.reply_to(message, "Суммарный опыт:")
        bot.register_next_step_handler(answer, lambda x: experience(x, fight))
    except Exception as e:
        bot.reply_to(message, default_error_message)

        
def experience(message, fight):
    try:
        is_digit(message, lambda x: experience(x, fight))
        fight.experience = int(message.text)
        answer = bot.reply_to(message, "Порог незначительности (%):")
        bot.register_next_step_handler(answer, lambda x: insignificance_threshold(x, fight))
    except Exception as e:
        bot.reply_to(message, default_error_message)


def insignificance_threshold(message, fight):
    try:
        is_digit(message, insignificance_threshold)
        fight.insignificance_threshold = float(message.text) / 100
        answer = bot.reply_to(message, "Число сильных чудовищ:")
        bot.register_next_step_handler(answer, lambda x: n_strong(x, fight))
    except Exception as e:
        bot.reply_to(message, default_error_message)
    
    
def n_strong(message, fight):
    try:
        is_digit(message, n_strong)
        fight.n_strong = int(message.text)
        answer = bot.reply_to(message, "Число слабых чудовищ:")
        bot.register_next_step_handler(answer, lambda x: n_weak(x, fight))
    except Exception as e:
        bot.reply_to(message, default_error_message)

    
def n_weak(message, fight):
    try:
        is_digit(message, n_weak)
        fight.n_weak = int(message.text)
        res_message, table = generate_fight(
            fight.experience,
            fight.n_strong,
            fight.n_weak,
            fight.n_heroes,
            fight.insignificance_threshold
        )
        bot.send_message(message.chat.id, res_message)
        bot.send_message(message.chat.id, table)
    except Exception as e:
        bot.reply_to(message, default_error_message)


if __name__ == '__main__':
#     bot.enable_save_next_step_handlers(delay=2)
#     bot.load_next_step_handlers()
#     bot.polling(none_stop=True)
    bot.infinity_polling(True)
