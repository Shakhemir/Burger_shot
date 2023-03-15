from telebot.types import Message
from staffing import staff


class Vendor:
    name = ''

    def __init__(self, message: Message):
        self.chat_id = message.chat.id
        if self.chat_id in staff.get_staff:
            self.name = staff.get_staff[self.chat_id].name
        self.orders = {}
        self.total_cash = 0

    @staticmethod
    def get_name(message: Message):
        name = message.chat.first_name if message.chat.first_name is not None else ''
        name += message.chat.last_name if message.chat.last_name is not None else ''
        name += message.chat.username if not name else ''
        name += 'сестра' if not name else ''
        return name

    def __str__(self):
        return self.name
