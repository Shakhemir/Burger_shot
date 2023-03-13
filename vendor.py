class Vendor:
    def __init__(self, message):
        name = message.chat.first_name if message.chat.first_name is not None else ''
        name += message.chat.last_name if message.chat.last_name is not None else ''
        name += message.chat.username if not name else ''
        name += 'сестра' if not name else ''
        self.name = name
        self.chat_id = message.chat.id
        self.orders = {}
        self.total_cash = 0

    def __str__(self):
        return self.name