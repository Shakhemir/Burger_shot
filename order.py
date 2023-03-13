from menu_item import MenuItem
from form_menu import menu
import telebot


class Order:
    def __init__(self, order_id):
        self.order_id = order_id
        self.menu_levels_stack = [menu.copy()]
        self.items = {}
        self.items_count = 0
        self.total_price = 0
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
        key = menu_item.item_id
        if menu_item.item_id not in self.items:
            menu_item = menu_item.copy()
            count = 1
            self.items[key] = [menu_item, count]
            self.menu_levels_stack[0].append(menu_item)
            menu_item.text = ' '.join(menu_item.text.split()[:-1]) + ' 1 шт'
        else:
            self.items[key][1] += 1
            self.items[key][0].text = f"{' '.join(self.items[key][0].text.split()[:-2])} {self.items[key][1]} шт"
        self.items_count += 1
        self.total_price += menu_item.price

    def remove(self, menu_item: MenuItem):
        count = self.items[menu_item.item_id][1]
        self.items_count -= count
        del self.items[menu_item.item_id]

    @property
    def __ready_order_buttons__(self):
        markup = telebot.types.InlineKeyboardMarkup()
        if not self.is_paid:
            markup.add(telebot.types.InlineKeyboardButton('Заказ оплачен', callback_data='is_payed'))
        if not self.is_issued:
            markup.add(telebot.types.InlineKeyboardButton('Заказ выдан', callback_data='is_issued'))
        return markup

    def paid(self):
        self.is_paid = True
        return self.__ready_order_buttons__

    def issued(self):
        self.is_issued = True
        return self.__ready_order_buttons__

    def __str__(self):
        order_check = f'_Заказ № {self.order_id}_\n'
        if self.items:
            order_check += '\n*'
            for item in self.items.values():
                order_check += item[0].text + '\n'
            order_check += '*\n'
        order_check += f'К оплате: *{self.total_price} ₽*'
        return order_check
