import sqlite3
from menu_item import MenuItem
from config import db_file

conn = sqlite3.connect(db_file)

food_menu = {}


def get_menu_items(parent_id=0):
    global food_menu
    c = conn.cursor()
    query = f"SELECT * FROM menu " \
            f"WHERE parent_id = {parent_id} " \
            f"ORDER BY order_id"
    c.execute(query)
    rows = c.fetchall()
    menu_items = []
    for row in rows:
        menu_item = MenuItem(row)
        if menu_item.price is None:
            menu_item.children = get_menu_items(row[0])
        else:
            menu_item.text += f' {menu_item.price}'
            food_menu[menu_item.item_id] = menu_item
        menu_items.append(menu_item)
    return menu_items


def form_food_menu() -> str:
    result = ''
    index_size = len(str(len(food_menu)))
    for index, item in enumerate(food_menu.values()):
        name = ' '.join(item.text.split()[:-1])
        price = f'{item.text.split()[-1]} ₽\n'
        if '🥩' in name or '🐥' in name:
            price_just = 6
        else:
            price_just = 7
        result += str(index + 1).rjust(index_size) + ' ' + name.ljust(15) + price.rjust(price_just)
    return f'`{result}`'


menu = get_menu_items()
