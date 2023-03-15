import sqlite3
from menu_item import MenuItem
from config import db_file

conn = sqlite3.connect(db_file)


def get_menu_items(parent_id=0):
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
        menu_items.append(menu_item)
    return menu_items


menu = get_menu_items()
