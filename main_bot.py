
import telebot
from telebot import types

token = '5329245219:AAFk9jZCoshDSu08SkACDgp2xC8m8_s7X1I'

with open('status.txt', 'r') as f:
    conversation = f.read()

bot = telebot.TeleBot(token)
start_buttons = ['begin calculate expenses', 'add expense', 'calculate expenses']


categories = ["Кар`єра", "Сім'я", "Оточення", "Творчість і хоббі",
              "Відпочинок та подорожі", "Розвиток (освіта)", "Здоров'я, спорт"]

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']


@bot.message_handler(commands=['start'])
def start_bot(message):
    start_markup = types.ReplyKeyboardMarkup()
    for i in start_buttons:
        start_markup.add(types.KeyboardButton(i.title()))
    bot.send_message(message.chat.id, 'Hello, User!', reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def begin_calculate_expenses(message):
    global conversation, categories
    if message.text.lower() not in start_buttons:
        bot.reply_to(message, 'Unknown option!')
        return
    if conversation == "True":
        if message.text.lower() == start_buttons[0]:
            bot.reply_to(message, 'You have already started your week!')
            return
        elif message.text.lower() == start_buttons[1]:
            categories_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for i in categories:
                categories_markup.add(types.KeyboardButton(i))
            msg = bot.send_message(message.chat.id, "Choose your category: ", reply_markup=categories_markup)
            bot.register_next_step_handler(msg, choose_category)
        else:
            bot.reply_to(message, 'Calculating expanses!')
            conversation = "False"
            with open('status.txt', 'w') as saver:
                saver.write(conversation)
            return
    if message.text.lower() == start_buttons[1]:
        if conversation == "False":
            bot.reply_to(message, 'You have not started your week yet!')
            return
    elif message.text.lower() == start_buttons[0]:
        conversation = "True"
        with open("status.txt", 'w') as saver:
            saver.write(conversation)
        categories_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in categories:
            categories_markup.add(types.KeyboardButton(i))
        msg = bot.send_message(message.chat.id, "Choose your category: ", reply_markup=categories_markup)
        bot.register_next_step_handler(msg, choose_category)
    elif message.text.lower() == start_buttons[-1]:
        bot.reply_to(message, 'There is nothing to calculate!')


def choose_category(message):
    global categories, days
    if message.text not in categories:
        bot.send_message(message.chat.id, "There is no category!")
    dates = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for date in days:
        dates.add(types.KeyboardButton(date))
    msg = bot.send_message(message.chat.id, "Enter date when transaction has been done:", reply_markup=dates)
    bot.register_next_step_handler(msg, enter_date)


def enter_date(message):
    global days
    if message.text not in days:
        bot.reply_to(message, "Invalid day!")
        return
    msg = bot.send_message(message.chat.id, "Enter amount of money has been spent: ")
    bot.register_next_step_handler(msg, get_amount_of_money)


def get_amount_of_money(message):
    if not message.text.isdigit():
        bot.reply_to(message, 'Enter in digits!')
        return
    bot.send_message(message.chat.id, 'Cool, i wrote it!')


bot.infinity_polling()
