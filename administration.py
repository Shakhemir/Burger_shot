from config import admin_id
import telebot
from telebot.types import Message
from main import bot
from staffing import staff
from vendor import Vendor


def request_for_validate_new_vendor(message: Message):
    text = 'Запрос на добавление нового сотрудника:\n' \
           f'Username: *{message.chat.username}*\n' \
           f'FIO: _{message.chat.first_name} {message.chat.last_name}_'
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton(
        'Добавить', callback_data=f'adminka validate {message.chat.id} {Vendor.get_name(message)}'))
    bot.send_message(chat_id=admin_id, text=text, reply_markup=markup)


def process_menu_button(call):
    data = call.data.split()[1:]
    print(f'{data=}')
    if data[0] == 'validate':
        chat_id = int(data[1])
        name = ' '.join(data[2:])
        if chat_id not in staff.get_staff:
            staff.add_staff(chat_id, name, 'unknown')
            bot.send_message(chat_id=chat_id, text='Вы добавлены!\nДля начала нажмите /new_day', parse_mode="HTML")
            bot.edit_message_text(chat_id=admin_id, message_id=call.message.message_id,
                                  text=call.message.text, reply_markup=None)
