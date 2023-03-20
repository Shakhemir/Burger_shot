from telebot.types import Message
import sqlite3
from config import db_file
import datetime
from order import Order
from form_menu import food_menu
from menu_item import MenuItem


class OrderDB:
    def __init__(self, message: Message = None):
        self.chat_id = message.chat.id
        self.date = datetime.datetime.now().strftime("%Y-%m-%d")
        self.table_name = self.get_table_name()
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()
        if not self.check_table_exists():
            self.create_table()
        else:
            pass

    def get_table_name(self):
        return f'{self.date}_{self.chat_id}'

    def check_table_exists(self):
        query = f"SELECT count(name) FROM sqlite_master WHERE type='table' AND name='{self.table_name}';"
        self.cursor.execute(query)
        return bool(self.cursor.fetchone()[0])

    def create_table(self):
        query = f'CREATE TABLE [{self.table_name}] (message_id  INTEGER UNIQUE, ' \
                f'order_id    INTEGER UNIQUE, ' \
                f'items       STRING, ' \
                f'items_count INTEGER, ' \
                f'total_price INTEGER);'
        self.cursor.execute(query)
        self.conn.commit()

    def insert_order(self, message_id: int, order: Order):
        items = ','.join(f'{item_id} {count[1]}' for item_id, count in order.items.items())
        query = f'INSERT INTO [{self.table_name}] ' \
                f'(message_id, order_id, items, items_count, total_price) ' \
                f'VALUES ({message_id}, {order.order_id}, "{items}", {order.items_count}, {order.total_price});'
        self.cursor.execute(query)
        self.conn.commit()

    def get_orders(self):
        orders = {}
        total_cash = 0
        query = f'SELECT * FROM [{self.table_name}];'
        self.cursor.execute(query)
        for record in self.cursor.fetchall():
            order = Order(record[1])
            orders[record[0]] = order
            for item in record[2].split(','):
                item_id: int = int(item.split()[0])
                count: int = int(item.split()[1])
                order.items[item_id] = [food_menu[item_id], count]
                order.items_count += count
                menu_item: MenuItem = food_menu[item_id]
                order.total_price += menu_item.price * count
            total_cash += order.total_price
        return orders, total_cash, self.date


if __name__ == '__main__':
    a = OrderDB()
    print(a.get_orders())
