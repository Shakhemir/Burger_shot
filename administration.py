from config import admin_id
import telebot
from telebot.types import Message
from main import bot
from staffing import staff
from vendor import Vendor


class AdminBot(telebot.TeleBot):
    pass


def request_for_validate_new_vendor(message: Message):
    text = 'Запрос на добавление нового сотрудника:\n' \
           f'Username: *{message.chat.username}*\n' \
           f'FIO: _{message.chat.first_name} {message.chat.last_name}_'
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Добавить', callback_data=f'adminka validate {message.chat.id}'))
    bot.send_message(admin_id, text, reply_markup=markup)


def process_menu_button(call):
    data = call.data.split()[1:]
    print(f'{data=}')
    if data[0] == 'validate':
        chat_id = int(data[1])
        if chat_id not in staff.get_staff:
            staff.add_staff(chat_id, Vendor.get_name(call.message), 'unknown')
            bot.send_message(chat_id, 'Вы добавлены!\nДля начала нажмите /new_day', parse_mode="HTML")
