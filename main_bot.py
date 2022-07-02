import json

import telebot
from telebot import types
from save_data import save_data, clear_data


class Bot:
    with open('status.txt', 'r') as f:
        conversation = f.read()

    def __init__(self):
        self.token = '5329245219:AAFk9jZCoshDSu08SkACDgp2xC8m8_s7X1I'
        self.bot = telebot.TeleBot(self.token)
        self.start_buttons = ['begin calculate expenses', 'add expense', 'calculate expenses']
        self.results = {
            "Кар`єра 👩‍💻": 0,
            "Сім'я 👨‍👩‍👦‍👦": 0,
            "Оточення 🤳": 0,
            "Творчість і хоббі 🐱‍👤": 0,
            "Відпочинок та подорожі 📆": 0,
            "Розвиток (освіта) 👨‍🎓": 0,
            "Здоров'я, спорт 🏓": 0
        }
        self.days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.data = {}

        @self.bot.message_handler(commands=['start'])
        def start_bot(message):
            start_markup = types.ReplyKeyboardMarkup()
            for i in self.start_buttons:
                start_markup.add(types.KeyboardButton(i.title()))
            self.bot.send_message(message.chat.id, f"""
        Привіт, {message.chat.first_name}, я допоможу тобі порахувати \
        всі твої витрати та дізнатися, на які сфери життя тобі треба дивитися більше
        """, reply_markup=start_markup)

        @self.bot.message_handler(content_types=['text'])
        def begin_calculate_expenses(message):
            if message.text.lower() not in self.start_buttons:
                self.bot.reply_to(message, 'Невідома команда!')
                return
            if self.conversation == "True":
                if message.text.lower() == self.start_buttons[0]:
                    self.bot.reply_to(message, 'Ви вже почали вести підрахунок!')
                    return
                elif message.text.lower() == self.start_buttons[1]:
                    categories_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                    for i in self.results.keys():
                        categories_markup.add(types.KeyboardButton(i))
                    msg = self.bot.send_message(message.chat.id, "Оберіть категорію: ", reply_markup=categories_markup)
                    self.bot.register_next_step_handler(msg, choose_category)
                else:
                    self.bot.reply_to(message, 'Обраховую витрати...')
                    expenses = self.calculate_expenses()
                    reply = '\n'.join(f"{i} - {expenses[i]:.2f} %" for i in expenses.keys() if self.results[i] != 0)
                    self.bot.send_message(message.chat.id, reply)
                    most_expense = max(self.results, key=self.results.get)
                    least_expense = min(self.results, key=self.results.get)
                    self.bot.send_message(message.chat.id,
                                          f'Зверніть увагу на категорію "{most_expense}": сюди ідуть найбільше витрат!'
                                          )
                    self.bot.send_message(message.chat.id,
                                          f'Зверніть увагу на категорію "{least_expense}": сюди ідуть найменше витрат!'
                                          )
                    for value in self.results.keys():
                        self.results[value] = 0
                    clear_data()
                    self.conversation = "False"
                    with open('status.txt', 'w') as saver:
                        saver.write(self.conversation)
                    return
            if message.text.lower() == self.start_buttons[1]:
                if self.conversation == "False":
                    self.bot.reply_to(message, 'Ви ще не почали вести витрати!')
                    return
            elif message.text.lower() == self.start_buttons[0]:
                self.conversation = "True"
                with open("status.txt", 'w') as saver:
                    saver.write(self.conversation)
                categories_markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
                for i in self.results.keys():
                    categories_markup.add(types.KeyboardButton(i))
                msg = self.bot.send_message(message.chat.id, "Оберіть категорію: ", reply_markup=categories_markup)
                self.bot.register_next_step_handler(msg, choose_category)
            elif message.text.lower() == self.start_buttons[-1]:
                self.bot.reply_to(message, 'Поки що немає чого обраховувати!')

        def choose_category(message):
            user_category = message.text
            if user_category not in self.results:
                self.bot.send_message(message.chat.id, "Такої категорії немає!")
            self.data['Category'] = user_category
            dates = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for date in self.days:
                dates.add(types.KeyboardButton(date))
            msg = self.bot.send_message(message.chat.id, "Введіть день коли була зроблена витрата: ",
                                        reply_markup=dates)
            self.bot.register_next_step_handler(msg, enter_date)

        def enter_date(message):
            user_entered_days = message.text
            if user_entered_days not in self.days:
                self.bot.reply_to(message, "Некорректний день!")
                return
            msg = self.bot.send_message(message.chat.id, "Введіть сумму витрати: ")
            self.bot.register_next_step_handler(msg, get_amount_of_money)

        def get_amount_of_money(message):
            user_amount_of_expenses = message.text
            if not user_amount_of_expenses.isdigit():
                self.bot.reply_to(message, 'Сумма має бути числом!')
                return
            self.data['Total expenses'] = user_amount_of_expenses
            start_markup = types.ReplyKeyboardMarkup()
            for i in self.start_buttons:
                start_markup.add(types.KeyboardButton(i.title()))
            self.bot.send_message(message.chat.id, 'Добре, я записав це!', reply_markup=start_markup)
            self.save_expense()

    def calculate_expenses(self):
        with open('expenses.json', 'r', encoding='utf8') as j:
            expenses_data = json.loads(j.read())
        total_expense = 0
        for expense in expenses_data['expenses']:
            self.results[expense['Category']] += float(expense['Total expenses'])
            total_expense += float(expense['Total expenses'])
        for i in self.results.keys():
            self.results[i] = (self.results[i] / total_expense) * 100
        return self.results

    def save_expense(self):
        save_data(self.data)
        self.data.clear()

    def start_polling(self):
        self.bot.polling(non_stop=True)


if __name__ == '__main__':
    main_bot = Bot()
    main_bot.start_polling()
