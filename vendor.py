from telebot.types import Message
from staffing import staff
from orders_DB import OrderDB


class Vendor:
    name = ''

    def __init__(self, message: Message):
        self.chat_id = message.chat.id
        if self.chat_id in staff.get_staff:
            self.name = staff.get_staff[self.chat_id].name
        else:
            self.name = self.get_name(message)
        self.db = OrderDB(message)
        self.orders, self.total_cash, self.date = self.db.get_orders()

    @staticmethod
    def get_name(message: Message):
        first_name = message.chat.first_name if message.chat.first_name is not None else ''
        last_name = message.chat.last_name if message.chat.last_name is not None else ''
        name = ' '.join((first_name, last_name)).strip()
        name += message.chat.username if not name else ''
        name += 'сестра' if not name else ''
        return name

    def __str__(self):
        return self.name
