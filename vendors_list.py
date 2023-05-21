from telebot.types import Message
from staffing import staff
from vendor import Vendor


class Vendors:
    def __init__(self):
        self.vendors = {}

    def add(self, message: Message):
        if message.chat.id in staff.get_staff:
            self.vendors[message.chat.id] = Vendor(message)
            return True
        else:
            self.check_new_vendor(Vendor(message))
            return False

    def get_vendor(self, message: Message) -> Vendor:
        if message.chat.id not in self.vendors:
            self.add(message)
        return self.vendors.get(message.chat.id, None)

    def check_new_vendor(self, vendor: Vendor):
        pass


vendors = Vendors()
