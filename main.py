import telebot
import myTelebot
import administration as adminka
from vendors_list import vendors
from order import OrderMessage
import os

__import__('dotenv').load_dotenv()  # загрузка данных из .env

# bot = telebot.TeleBot(TOKEN, parse_mode='Markdown')
bot = myTelebot.AdminBot(os.getenv('TOKEN'), parse_mode='Markdown')


@bot.message_handler(commands=['start', 'new_day'])
def command(message):
    if vendors.add(message):
        new_day_message(message)
    else:
        adminka.request_for_validate_new_vendor(message)


@bot.message_handler(commands=['new_order'])
def command(message):
    new_order_message(message)


@bot.message_handler(commands=['show_menu'])
def command(message):
    from form_menu import form_food_menu
    bot.send_message(chat_id=message.chat.id, text=form_food_menu())


@bot.message_handler(commands=['total'])
def command(message):
    vendor = vendors.get_vendor(message)
    text = f'Общая сумма за {vendor.date}:\n*{vendor.total_cash}* ₽'
    bot.send_message(chat_id=message.chat.id, text=text)


def new_day_message(message):
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton('Новый заказ', callback_data='new order'))
    bot.send_message(chat_id=message.chat.id, text=f'Добро пожаловать, {vendors.get_vendor(message)}!',
                     reply_markup=markup)


def new_order_message(message):
    vendor = vendors.get_vendor(message)
    order_id = len(vendor.orders) + 1
    new_message = bot.send_message(chat_id=message.chat.id, text=f'Заказ № {order_id}')
    vendor.orders[new_message.message_id] = OrderMessage(order_id)
    if message.text.startswith('Добро пожаловать'):
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=message.text, reply_markup=None)
    create_menu_level(new_message)


def create_menu_level(message):
    order = vendors.get_vendor(message).orders[message.message_id]
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
        if order.items:
            markup.add(telebot.types.InlineKeyboardButton('➖ Удалить', callback_data='delete'),
                       telebot.types.InlineKeyboardButton('☑️ Готово', callback_data='ready'))
    else:  # все остальные подменю
        markup.add(*buttons)
        markup.add(telebot.types.InlineKeyboardButton('🔙 Назад', callback_data='back'))
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=order, reply_markup=markup)


def order_ready(message):
    vendor = vendors.get_vendor(message)
    order = vendor.orders[message.message_id]
    markup = order.__ready_order_buttons__
    print(order)
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=order, reply_markup=markup)


def delete_order_items(message):
    vendor = vendors.get_vendor(message)
    order = vendor.orders[message.message_id]
    text = 'Выберите позиции для удаления:'
    markup = order.items_for_delete_buttons
    markup.add(telebot.types.InlineKeyboardButton('☑️ Готово', callback_data='del ready'))
    bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                          text=text, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('del '))
def process_menu_button(call):
    data = call.data[4:]
    order: OrderMessage = vendors.get_vendor(call.message).orders[call.message.message_id]
    if data == 'ready':
        create_menu_level(call.message)
    else:
        order.remove(int(data))
        delete_order_items(call.message)


@bot.callback_query_handler(func=lambda call: call.data in ['is_payed', 'is_issued'])
def process_menu_button(call):
    data = call.data
    chat_id = call.message.chat.id
    order: OrderMessage = vendors.get_vendor(call.message).orders[call.message.message_id]
    vendor = vendors.get_vendor(call.message)
    if data == 'is_issued':
        markup = order.issued()
    else:
        markup = order.paid()
        vendor.db.insert_order(call.message.message_id, order)
        vendor.total_cash += vendor.orders[call.message.message_id].total_price
    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=order, reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data.startswith('adminka '))
def process_menu_button(call):
    adminka.process_menu_button(call)


@bot.callback_query_handler(func=lambda call: True)
def process_menu_button(call):
    data = call.data
    if data == 'new order':
        return new_order_message(call.message)
    order: OrderMessage = vendors.get_vendor(call.message).orders[call.message.message_id]
    if data == 'back':
        order.menu_back()
    elif data == 'ready':
        return order_ready(call.message)
    elif data == 'delete':
        return delete_order_items(call.message)
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
    if message.text.isdigit() and (reply_message := message.reply_to_message):
        order: OrderMessage = vendors.get_vendor(message).orders.get(reply_message.message_id, False)
        if order:
            cash_from_client = int(message.text)
            bot.reply_to(message, f'`Сдачи: {cash_from_client - order.total_price}`')
            return
    try:
        if message.chat.id == adminka.admin_id:
            bot.send_message(chat_id=message.chat.id, tetx=eval(message.text))
    except Exception:
        return


if __name__ == '__main__':
    while True:
        try:
            bot.polling()
        except Exception as ex:
            print(ex)
