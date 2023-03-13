import telebot

from config import TOKEN
from vendor import Vendor
from order import Order

bot = telebot.TeleBot(TOKEN)
vendors = {}


@bot.message_handler(commands=['start', 'new_day'])
def command(message):
    global vendors
    vendors[message.chat.id] = Vendor(message)
    new_day_message(message)


@bot.message_handler(commands=['new_order'])
def command(message):
    new_order_massage(message)


@bot.message_handler(commands=['total'])
def command(message):
    vendor: Vendor = vendors[message.chat.id]
    text = f'Общая сумма:\n*{vendor.total_cash}*'
    bot.send_message(message.chat.id, text, parse_mode='Markdown')


def new_day_message(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Новый заказ', callback_data='new order'))
    bot.send_message(message.chat.id, f'Добро пожаловать, {vendors[message.chat.id]}!', reply_markup=markup)


def new_order_massage(message):
    vendor = vendors[message.chat.id]
    order_id = len(vendor.orders) + 1
    new_message = bot.send_message(message.chat.id, f'Заказ № {order_id}')
    vendor.orders[new_message.message_id] = Order(order_id)
    if message.text.startswith('Добро пожаловать'):
        bot.edit_message_text(message.text, message.chat.id, message.message_id, reply_markup=None)
    create_menu_level(new_message)


def create_menu_level(message):
    order = vendors[message.chat.id].orders[message.message_id]
    level_menu = order.curr_menu
    markup = telebot.types.InlineKeyboardMarkup(row_width=2)
    buttons = []
    for menu_item in level_menu:
        buttons.append(telebot.types.InlineKeyboardButton(menu_item.text, callback_data=menu_item.item_id))
    if level_menu[0].parent_id == 0:  # если главное меню
        markup.add(*buttons[:4])
        if len(buttons) > 4:
            for button in buttons[4:]:
                markup.add(button)
        markup.add(telebot.types.InlineKeyboardButton('☑️ Готово', callback_data='ready'))
    else:  # все остальные подменю
        markup.add(*buttons)
        markup.add(telebot.types.InlineKeyboardButton('🔙 Назад', callback_data='back'))
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=order, reply_markup=markup, parse_mode='Markdown')


def order_ready(message):
    vendor: Vendor = vendors[message.chat.id]
    order = vendor.orders[message.message_id]
    markup = order.__ready_order_buttons__
    print(order)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=order, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: call.data in ['is_payed', 'is_issued'])
def process_menu_button(call):
    data = call.data
    chat_id = call.message.chat.id
    order: Order = vendors[chat_id].orders[call.message.message_id]
    vendor: Vendor = vendors[chat_id]
    if data == 'is_issued':
        markup = order.issued()
    else:
        markup = order.paid()
        vendor.total_cash += vendor.orders[call.message.message_id].total_price
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=order, reply_markup=markup, parse_mode='Markdown')


@bot.callback_query_handler(func=lambda call: True)
def process_menu_button(call):
    data = call.data
    chat_id = call.message.chat.id
    if data == 'new order':
        return new_order_massage(call.message)
    order: Order = vendors[chat_id].orders[call.message.message_id]
    if data == 'back':
        order.menu_back()
    elif data == 'ready':
        return order_ready(call.message)
    else:
        data = int(data)
        for menu_item in order.curr_menu:
            if menu_item.item_id == data:
                if menu_item.children is not None:
                    order.menu_next(menu_item.children)
                else:
                    order.add(menu_item)
                    order.menu_reset()
                break
    create_menu_level(call.message)


@bot.message_handler(content_types=['text'])
def text_answer(message):
    bot.send_message(message.chat.id, eval(message.text))


if __name__ == '__main__':
    bot.polling()
