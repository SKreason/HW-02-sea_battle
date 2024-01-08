# Итоговое задание 2.8 (HW-02)
from random import randint


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return "Точка за пределами игрового поля!"


class BoardUsedException(BoardException):
    def __str__(self):
        return "Уже был такой выстрел!"


class BoardWrongShipException(BoardException):  # невозможно для расположения корабля
    pass


class Dot:
    def __init__(self, x, y):
        self.x = x  # координата по вертикали
        self.y = y  # координата по горизонтали

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f"Dot({self.x}, {self.y})"


class Ship:
    def __init__(self, bow, length, o):
        self.bow = bow  # нос корабля
        self.length = length  # длинна корабля
        self.o = o  # ориентация корабля (0 - вертикальная; 1 - горизонтальная)
        self.lives = length  # количество жизней у корабля

    @property
    def dots(self):
        ship_dots = []  # координаты всех точек корабля
        for i in range(self.length):
            cur_x = self.bow.x
            cur_y = self.bow.y

            if self.o == 0:
                cur_x += i

            elif self.o == 1:
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))

        return ship_dots

    def hit(self, shot):  # проверка на попадание в корабль
        return shot in self.dots


class Board:
    def __init__(self, hid = False, size = 6):
        self.size = size  # размер игрового поля
        self.hid = hid  # параметр скрытия доски

        self.count = 0  # счетчик пораженных кораблей

        self.field = [["O"] * size for _ in range(size)]

        self.busy = []  # занятые клетки
        self.ships = []  # список кораблей

    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:
            res = res.replace("■", "O")  # скрытие кораблей на поле врага
        return res

    def get_busy(self):
        return [self.busy]

    def out(self, dot_s):  # проверка координаты точки вне поля: True - если за пределами поля
        return not ((0 <= dot_s.x < self.size) and (0 <= dot_s.y < self.size))

    def contour(self, ship, verb = False):
        displacement = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 0), (0, 1), (1, -1), (1, 0), (1, 1)]  # отклонение
        for dot_s in ship.dots:  # генератор контура корабля
            for dx, dy in displacement:
                cur = Dot(dot_s.x + dx, dot_s.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def add_ship(self, ship):
        for dot_s in ship.dots:
            if self.out(dot_s) or dot_s in self.busy:
                raise BoardWrongShipException()  # исключение размещение корабля
        for dot_s in ship.dots:
            self.field[dot_s.x][dot_s.y] = "■"
            self.busy.append(dot_s)

        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot_s):
        if self.out(dot_s):
            raise BoardOutException()  # исключение вне игрового поля

        if dot_s in self.busy:
            raise BoardUsedException()  # исключение уже был такой выстрел

        self.busy.append(dot_s)

        for ship in self.ships:  # проверка на попадание
            if ship.hit(dot_s):
                ship.lives -= 1
                self.field[dot_s.x][dot_s.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb = True)
                    print("Корабль потоплен!")
                    return False
                else:
                    print("Корабль подбит!")
                    return True

        self.field[dot_s.x][dot_s.y] = "T"
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):  # метод для потомков класса
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        dot_s = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {dot_s.x + 1} {dot_s.y + 1}")
        return dot_s


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход:\n").split()

            if len(cords) != 2:  # проверка на ввод двух координат
                print("Введите 2 координаты!")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):  # проверка на ввод цифр
                print("Введите два числа от 1 до 6 через пробел!")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size = 6):
        self.size = size
        self.lens = [3, 2, 2, 1, 1, 1, 1]
        player = self.random_board()  # поле игрока
        computer = self.random_board()  # поле ИИ
        computer.hid = True

        self.ai = AI(computer, player)
        self.us = User(player, computer)

    @staticmethod
    def greet():
        print("-------------------")
        print("  Приветствуем вас ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def try_board(self):  # попытка разместить корабли на поле
        board = Board(size = self.size)
        attempts = 0
        for length in self.lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):  # цикл попыток размещения кораблей
        board = None
        while board is None:
            board = self.try_board()
        return board

    def print_boards(self):
        print("-" * 27)
        print("Доска пользователя:")
        print(self.us.board)
        print("-" * 27)
        print("Доска компьютера:")
        print(self.ai.board)
        print("-" * 27)

    def loop(self):
        num = 0
        while True:
            self.print_boards()
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                self.print_boards()
                print("-" * 27)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == 7:
                self.print_boards()
                print("-" * 27)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        input(f"Нажмите \"Enter\" для начала игры!")
        self.loop()


g = Game()
g.start()
