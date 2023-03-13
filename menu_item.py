import copy


class MenuItem:
    def __init__(self, row):
        self.item_id = row[0]
        self.text = row[1]
        self.price = row[2]
        self.parent_id = row[3]
        self.children = None

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
