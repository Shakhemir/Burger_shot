import copy


class MenuItem:
    def __init__(self, row):
        self.item_id: int = row[0]
        self.text: str = row[1]
        self.price: int = row[2]
        self.parent_id: int = row[3]
        self.children: list = None

    def copy(self):
        return copy.copy(self)

    # def inc_count(self):


    def __str__(self):
        return str(self.__dict__)

    def __repr__(self):
        return f'{self.item_id} {self.text}'


if __name__ == '__main__':
    a = MenuItem([1, 2, 3, 4])
    b = a.copy()
    b.text = 'sdsd'
    print(a, b)
