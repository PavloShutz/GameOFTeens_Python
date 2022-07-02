import json

import telebot
from telebot import types
from save_data import save_data, clear_data

token = 'token'

with open('status.txt', 'r') as f:
    conversation = f.read()

bot = telebot.TeleBot(token)
start_buttons = ['begin calculate expenses', 'add expense', 'calculate expenses']

categories = ["Кар`єра", "Сім'я", "Оточення", "Творчість і хоббі",
              "Відпочинок та подорожі", "Розвиток (освіта)", "Здоров'я, спорт"]

results = {
    "Кар`єра": 0,
    "Сім'я": 0,
    "Оточення": 0,
    "Творчість і хоббі": 0,
    "Відпочинок та подорожі": 0,
    "Розвиток (освіта)": 0,
    "Здоров'я, спорт": 0
}

days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
data = {}


def calculate_expenses():
    global results
    with open('expenses.json', 'r', encoding='utf8') as j:
        expenses_data = json.loads(j.read())
    total_expense = 0
    for expense in expenses_data['expenses']:
        results[expense['Category']] += float(expense['Total expenses'])
        total_expense += float(expense['Total expenses'])
    new_results = []
    for i in results.keys():
        new_results.append(f"{i} - {((results[i] / total_expense) * 100):.2f} %")
    return new_results


def save_expense():
    global data
    save_data(data)
    data.clear()


@bot.message_handler(commands=['start'])
def start_bot(message):
    start_markup = types.ReplyKeyboardMarkup()
    for i in start_buttons:
        start_markup.add(types.KeyboardButton(i.title()))
    bot.send_message(message.chat.id, f"""
Привіт, {message.chat.first_name}, я допоможу тобі порахувати \
всі твої витрати та дізнатися, на які сфери життя тобі треба дивитися більше
""", reply_markup=start_markup)


@bot.message_handler(content_types=['text'])
def begin_calculate_expenses(message):
    global conversation, categories, results
    if message.text.lower() not in start_buttons:
        bot.reply_to(message, 'Невідома команда!')
        return
    if conversation == "True":
        if message.text.lower() == start_buttons[0]:
            bot.reply_to(message, 'Ви вже почали вести підрахунок!')
            return
        elif message.text.lower() == start_buttons[1]:
            categories_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for i in categories:
                categories_markup.add(types.KeyboardButton(i))
            msg = bot.send_message(message.chat.id, "Оберіть категорію: ", reply_markup=categories_markup)
            bot.register_next_step_handler(msg, choose_category)
        else:
            bot.reply_to(message, 'Обраховую витрати...')
            expenses = calculate_expenses()
            for expense in expenses:
                bot.send_message(message.chat.id, expense)
            bot.send_message(message.chat.id,
                             f'Зверніть увагу на категорію {max(results, key=results.get)}: тут ідуть найбільші витрати!'
                             )
            bot.send_message(message.chat.id,
                             f'Зверніть увагу на категорію {min(results, key=results.get)}: тут ідуть найменші витрати!'
                             )
            for value in results.keys():
                results[value] = 0
            clear_data()
            conversation = "False"
            with open('status.txt', 'w') as saver:
                saver.write(conversation)
            return
    if message.text.lower() == start_buttons[1]:
        if conversation == "False":
            bot.reply_to(message, 'Ви ще не почали вести витрати!')
            return
    elif message.text.lower() == start_buttons[0]:
        conversation = "True"
        with open("status.txt", 'w') as saver:
            saver.write(conversation)
        categories_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
        for i in categories:
            categories_markup.add(types.KeyboardButton(i))
        msg = bot.send_message(message.chat.id, "Оберіть категорію: ", reply_markup=categories_markup)
        bot.register_next_step_handler(msg, choose_category)
    elif message.text.lower() == start_buttons[-1]:
        bot.reply_to(message, 'Поки що немає чого обраховувати!')


def choose_category(message):
    global categories, days, data
    user_category = message.text
    if user_category not in categories:
        bot.send_message(message.chat.id, "Такої категорії немає!")
    data['Category'] = user_category
    dates = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    for date in days:
        dates.add(types.KeyboardButton(date))
    msg = bot.send_message(message.chat.id, "Введіть день коли була зроблена витрата: ", reply_markup=dates)
    bot.register_next_step_handler(msg, enter_date)


def enter_date(message):
    global days
    user_entered_days = message.text
    if user_entered_days not in days:
        bot.reply_to(message, "Некорректний день!")
        return
    msg = bot.send_message(message.chat.id, "Введіть сумму витрати: ")
    bot.register_next_step_handler(msg, get_amount_of_money)


def get_amount_of_money(message):
    global data
    user_amount_of_expenses = message.text
    if not user_amount_of_expenses.isdigit():
        bot.reply_to(message, 'Сумма має бути числом!')
        return
    data['Total expenses'] = user_amount_of_expenses
    start_markup = types.ReplyKeyboardMarkup()
    for i in start_buttons:
        start_markup.add(types.KeyboardButton(i.title()))
    bot.send_message(message.chat.id, 'Добре, я записав це!', reply_markup=start_markup)
    save_expense()


bot.infinity_polling()
