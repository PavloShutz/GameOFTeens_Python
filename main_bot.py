"""Simple Telegram Bot 'Circle of Life',
built on pyTelegramBotApi.
"""

import json
import os
from typing import Optional

import telebot  # type: ignore
from telebot import types
from save_data import save_data, clear_data


class Bot:

    def __init__(self):
        """Circle of Life bot for Telegram."""
        self.token = os.environ.get('Circle_Of_Life_Token')
        self.bot = telebot.TeleBot(self.token)
        self.start_buttons = ['почати обраховувати витрати',
                              'додати витрату', 'обрахувати витрату(и)']
        self.results = {
            "Кар`єра 👩‍💻": 0,
            "Сім'я 👨‍👩‍👦‍👦": 0,
            "Оточення 🤳": 0,
            "Творчість і хоббі 🐱‍👤": 0,
            "Відпочинок та подорожі 📆": 0,
            "Розвиток (освіта) 👨‍🎓": 0,
            "Здоров'я, спорт 🏓": 0,
        }
        self.days = ['Понеділок', 'Вівторок', 'Середа',
                     'Четвер', "П'ятниця", 'Субота', 'Неділя']
        self.data = {}
        self.total_expense = 0
        self.start_markup = types.ReplyKeyboardMarkup()
        for i in self.start_buttons:
            self.start_markup.add(types.KeyboardButton(i.title()))
        with open('status.txt', 'r') as f:
            self.conversation = f.read()

        @self.bot.message_handler(commands=['start'])
        def start_bot(message) -> None:
            """Starting our bot."""
            self.bot.send_message(message.chat.id, f"""
                Привіт, {message.chat.first_name},
я допоможу тобі порахувати всі твої витрати 💵 та дізнатися,
на які сфери життя тобі треба дивитися більше 📜.
        """, reply_markup=self.start_markup)

        @self.bot.message_handler(content_types=['text'])
        def begin_calculate_expenses(message):
            """The main logic of bot."""
            if message.text.lower() not in self.start_buttons:
                self.bot.reply_to(message, 'Невідома команда!')
                return
            if self.conversation == "True":
                if message.text.lower() == self.start_buttons[0]:
                    self.bot.reply_to(message,
                                      'Ви вже почали вести підрахунок!')
                    return
                elif message.text.lower() == self.start_buttons[1]:
                    categories_markup = types.ReplyKeyboardMarkup(
                        one_time_keyboard=True,
                    )
                    for category in self.results.keys():
                        categories_markup.add(types.KeyboardButton(category))
                    msg = self.bot.send_message(message.chat.id,
                                                "Оберіть категорію: ",
                                                reply_markup=categories_markup,
                                                )
                    self.bot.register_next_step_handler(msg, choose_category)
                else:
                    try:
                        self.bot.reply_to(message, 'Обраховую витрати...')
                        expenses = self.calculate_expenses()
                        reply = '\n'.join(
                            f"{expense} - {expenses[expense]:.2f} %"
                            for expense in expenses.keys()
                            if self.results[expense] != 0)
                        self.bot.send_message(
                            message.chat.id, reply,
                        )
                        new_results = {}
                        for result in self.results.keys():
                            if self.results[result] != 0:
                                new_results[result] = self.results[result]
                        if len(new_results) == 1:
                            key = [k for k, v in new_results.items()
                                   if v == 100][0]
                            self.bot.send_message(
                                message.chat.id,
                                'Зверніть увагу '
                                'на категорію '
                                f'"{key}": '
                                'сюди ідуть <b><u>усі</u></b> витрати!',
                                reply_markup=self.start_markup,
                                parse_mode='html',
                            )
                            self.annul_results()
                            return
                        most_expense = max(new_results, key=new_results.get)
                        least_expense = min(new_results, key=new_results.get)
                        self.bot.send_message(
                            message.chat.id,
                            'Зверніть увагу на категорію '
                            f'"{most_expense}": '
                            'сюди ідуть <b><u>найбільше</u></b> витрат!',
                            parse_mode='html',
                        )
                        self.bot.send_message(
                            message.chat.id,
                            'Зверніть увагу на категорію '
                            f'"{least_expense}": '
                            'сюди ідуть <b><u>найменше</u></b> витрат!',
                            parse_mode='html',
                        )
                        self.annul_results()
                        return
                    except AttributeError:
                        self.bot.send_message(
                            message.chat.id,
                            'Поки що немає чого обраховувати!',
                            reply_markup=self.start_markup,
                        )
                        self.save_conversation_status("False")
                        clear_data()
                        return
            if message.text.lower() == self.start_buttons[1]:
                if self.conversation == "False":
                    self.bot.reply_to(message,
                                      'Ви ще не почали вести витрати!',
                                      )
                    return
            elif message.text.lower() == self.start_buttons[0]:
                self.save_conversation_status("True")
                categories_markup = types.ReplyKeyboardMarkup(
                    one_time_keyboard=True,
                )
                for category_name in self.results.keys():
                    categories_markup.add(types.KeyboardButton(category_name))
                msg = self.bot.send_message(message.chat.id,
                                            "Оберіть категорію: ",
                                            reply_markup=categories_markup,
                                            )
                self.bot.register_next_step_handler(msg, choose_category)
            elif message.text.lower() == self.start_buttons[-1]:
                self.bot.reply_to(message, 'Поки що немає чого обраховувати!')

        def choose_category(message) -> None:
            """Bot gets category from user and saves it, if input
            data is valid.
            """
            user_category = message.text
            if user_category not in self.results:
                self.bot.send_message(message.chat.id,
                                      "Такої категорії немає!",
                                      reply_markup=self.start_markup,
                                      )
                self.save_conversation_status("False")
                clear_data()
                return
            self.data['Category'] = user_category
            dates = types.ReplyKeyboardMarkup(one_time_keyboard=True)
            for date in self.days:
                dates.add(types.KeyboardButton(date))
            msg = self.bot.send_message(message.chat.id,
                                        "Введіть день коли була "
                                        "зроблена витрата: ",
                                        reply_markup=dates,
                                        )
            self.bot.register_next_step_handler(msg, enter_date)

        def enter_date(message) -> None:
            user_entered_days = message.text
            if user_entered_days not in self.days:
                self.bot.send_message(message.chat.id,
                                      "Некорректний день!",
                                      reply_markup=self.start_markup,
                                      )

                return
            msg = self.bot.send_message(message.chat.id,
                                        "Введіть сумму витрати: ",
                                        )
            self.bot.register_next_step_handler(msg, get_amount_of_money)

        def get_amount_of_money(message) -> None:
            """Getting amount of money in digits.
            Bot expects, that user knows in which currency
            he wants to count his expenses.
            """
            user_amount_of_expenses = message.text
            try:
                float(user_amount_of_expenses)
            except ValueError:
                self.bot.send_message(message.chat.id,
                                      'Сумма має бути числом!',
                                      reply_markup=self.start_markup,
                                      )
                return
            self.data['Total expenses'] = user_amount_of_expenses
            self.bot.send_message(message.chat.id,
                                  'Добре, я записав це!',
                                  reply_markup=self.start_markup,
                                  )
            self.save_expense()

    def calculate_expenses(self) -> Optional[dict]:
        """Calculate percents of expense for each category.
        Returns:
            dict with results of calculating
        """
        with open('expenses.json', 'r', encoding='utf8') as j:
            expenses_data = json.loads(j.read())
        try:
            for expense in expenses_data['expenses']:
                self.results[expense['Category']] += \
                    float(expense['Total expenses'])
                self.total_expense += float(expense['Total expenses'])
            for i in self.results.keys():
                self.results[i] = (self.results[i] / self.total_expense) * 100
            return self.results
        except (ZeroDivisionError, AttributeError):
            self.save_conversation_status("False")
            return None

    def annul_results(self):
        for value in self.results.keys():
            self.results[value] = 0
        clear_data()
        self.total_expense = 0
        self.save_conversation_status("False")

    def save_expense(self) -> None:
        """Saves data to json and clears old data"""
        save_data(self.data)
        self.data.clear()

    def save_conversation_status(self, status: str) -> None:
        """Saves conversation status in 'status.txt'
        Args:
            status (str): string representing of conversation status.
        """
        self.conversation = status
        with open("status.txt", 'w') as saver:
            saver.write(self.conversation)

    def start_polling(self) -> None:
        """Bot will be polling infinitive"""
        self.bot.polling(non_stop=True)


if __name__ == '__main__':
    main_bot = Bot()
    main_bot.start_polling()
