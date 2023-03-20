import telebot
from telebot import types
from config import admin_id

from vendors_list import vendors


class Admin:
    __chat_id: int = None
    __message_ids = {}

    def __init__(self, chat_id: int):
        self.__chat_id = chat_id

    @property
    def get_chat_id(self):
        return self.__chat_id

    def add_message(self, message: types.Message, admin_message: types.Message):
        self.__message_ids[message.message_id] = admin_message.message_id

    def get_message(self, message: types.Message):
        return self.__message_ids[message.message_id]


class AdminsList:
    __admins = []

    def add_admin(self, chat_id: int):
        self.__admins.append(Admin(chat_id))

    def is_admin(self, message: types.Message):
        for admin in self.__admins:
            if message.chat.id == admin.get_chat_id:
                return True
        return False


class AdminBot(telebot.TeleBot):
    admin_id: int = None
    admins = AdminsList()
    message_ids = {}

    def __init__(self, token: str, **kwargs):
        super().__init__(token, **kwargs)
        self.admin_id = admin_id
        self.admins.add_admin(admin_id)

    def send_message(self, **kwargs) -> types.Message:
        without_admin = kwargs.pop('without_admin', False)
        message = super().send_message(**kwargs)
        if self.admins.is_admin(message) or without_admin:
            return message
        vendor = vendors.get_vendor(message)
        kwargs['text'] = f"`{vendor.chat_id} {vendor.name}`\n{kwargs['text']}"
        kwargs['chat_id'] = self.admin_id
        admin_message = super().send_message(**kwargs)
        self.message_ids[message.message_id] = admin_message.message_id
        return message

    def edit_message_text(self, **kwargs):
        message = super().edit_message_text(**kwargs)
        if self.admins.is_admin(message):
            return message
        vendor = vendors.get_vendor(message)
        kwargs['text'] = f"`{vendor.chat_id} {vendor.name}`\n{kwargs['text']}"
        kwargs['message_id'] = self.message_ids[message.message_id]
        kwargs['chat_id'] = self.admin_id
        super().edit_message_text(**kwargs)

    def reply_to(self, message: types.Message, text: str, **kwargs) -> types.Message:
        return self.send_message(chat_id=message.chat.id, text=text, without_admin=True,
                                 reply_to_message_id=message.message_id, **kwargs)
