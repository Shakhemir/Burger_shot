from menu_item import MenuItem
from form_menu import menu
import telebot

TEXT_CHECK_WIDTH = 15


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.items = {}
        self.items_count = 0
        self.total_price = 0

    def add(self, menu_item: MenuItem):
        key = menu_item.item_id
        if menu_item.item_id not in self.items:
            self.items[key] = [menu_item, 1]
        else:
            self.items[key][1] += 1
            self.items[key][0].text = f"{' '.join(self.items[key][0].text.split()[:-2])} ({self.items[key][1]} шт)"
        self.items_count += 1
        self.total_price += menu_item.price

    def remove(self, item_id: int):
        count = self.items[item_id][1]
        self.items_count -= count
        self.total_price -= count * self.items[item_id][0].price
        del self.items[item_id]


class OrderMessage(Order):
    def __init__(self, order_id):
        super().__init__(order_id)
        self.menu_levels_stack = [menu.copy()]
        self.is_paid = False
        self.is_issued = False

    @property
    def curr_menu(self):
        return self.menu_levels_stack[-1]

    def menu_next(self, menu):
        self.menu_levels_stack.append(menu)

    def menu_back(self):
        self.menu_levels_stack.pop()
        return self.curr_menu

    def menu_reset(self):
        self.menu_levels_stack = [self.menu_levels_stack[0]]

    def add(self, menu_item: MenuItem):
        if menu_item.item_id not in self.items:
            menu_item = menu_item.copy()
            menu_item.text = ' '.join(menu_item.text.split()[:-1]) + ' (1 шт)'
            self.menu_levels_stack[0].append(menu_item)
        super().add(menu_item)

    def remove(self, item_id: int):
        super().remove(item_id)
        for index, menu_item in enumerate(self.menu_levels_stack[0]):
            if menu_item.item_id == item_id:
                self.menu_levels_stack[0].pop(index)
                return

    @property
    def __ready_order_buttons__(self):
        markup = telebot.types.InlineKeyboardMarkup()
        if not self.is_paid:
            markup.add(telebot.types.InlineKeyboardButton('💰 Заказ оплачен', callback_data='is_payed'))
        # if not self.is_issued:
        #     markup.add(telebot.types.InlineKeyboardButton('Посчитать сдачу', callback_data='is_issued'))
        return markup

    @property
    def items_for_delete_buttons(self):
        markup = telebot.types.InlineKeyboardMarkup()
        for item_id, item in self.items.items():
            markup.add(telebot.types.InlineKeyboardButton('➖ ' + item[0].text, callback_data=f'del {item_id}'))
        return markup

    def paid(self):
        self.is_paid = True
        return self.__ready_order_buttons__

    def issued(self):
        self.is_issued = True
        return self.__ready_order_buttons__

    def __str__(self):
        order_check = f'`Заказ № {str(self.order_id).zfill(3)}`\n'
        if self.items:
            order_check += '\n`'
            for item in self.items.values():
                item_menu: MenuItem = item[0]
                count: int = item[1]
                text = '"' + ' '.join(item_menu.text.split()[:-2]) + '"'
                order_check += text + f' {count}x{item_menu.price}\n= {item_menu.price * count}\n'
            order_check += f'\nИтого: {self.total_price} ₽`'
        return order_check
