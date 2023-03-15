import sqlite3
from config import db_file


class Employee:
    def __init__(self, row: list):
        self.chat_id = row[0]
        self.is_admin = bool(row[1])
        self.name = row[2]
        self.device = row[3]

    def __str__(self):
        if self.__dict__:
            return str(self.__dict__)

    def __repr__(self):
        if self.__dict__:
            return str(self.__dict__)


class Staffing:
    staff = {}

    def __init__(self):
        self.conn = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.conn.cursor()

    def query_get_staff(self):
        self.cursor.execute("SELECT * FROM staff")
        staff = {}
        for record in c.fetchall():
            staff[record[0]] = Employee(record)
        self.staff = staff

    @property
    def get_staff(self):
        return self.staff

    def add_staff(self, chat_id, name, device):
        query = f"INSERT INTO staff (chat_id, is_admin, name, device) " \
                f"VALUES ({chat_id}, 0, '{name}', '{device}');"
        print(query)
        self.cursor.execute(query)
        self.conn.commit()
        self.staff[chat_id] = Employee([chat_id, False, name, device])


staff = Staffing()
