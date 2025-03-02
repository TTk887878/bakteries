import socket

import pygame
import psycopg2
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:1@localhost/bakteriy")

Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session()


def findVector(vector: str):
    first = None
    for index, value in enumerate(vector):
        if value == "<":
            first = index
        if value == ">" and first is not None:
            second = index
            result = list(map(float, vector[first + 1:second].split(",")))
            return result
    return ""


def findcolor(info: str):
    first = None
    for index, value in enumerate(info):
        if value == "<":
            first = index
        if value == ">" and first is not None:
            second = index
            result = info[first + 1:second].split(",")
            return result
    return ""


pygame.init()
WIDTH_ROOM, HEIGHT_ROOM = (4000, 4000)
WIDTH_SERVER, HEIGHT_SERVER = (300, 300)
FPS = 100
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue', 'DodgerBlue',
          'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']

skreem = pygame.display.set_mode((WIDTH_SERVER, HEIGHT_SERVER))
pygame.display.set_caption("serveer")
clock = pygame.time.Clock()


class Player(Base):
    __tablename__ = "gamers"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(250))
    address = Column(String)
    x = Column(Integer, default=500)
    y = Column(Integer, default=500)
    size = Column(Integer, default=50)
    errors = Column(Integer, default=0)
    abs_speed = Column(Integer, default=2)
    speed_x = Column(Integer, default=2)
    speed_y = Column(Integer, default=2)
    color = Column(String(250), default="red")  # Добавили цвет
    w_vision = Column(Integer, default=800)
    h_vision = Column(Integer, default=600)  # Добавили размер квадрат

    def __init__(self, name, address):
        self.name = name
        self.address = address


# Локальный класс игроковj
class LocalPlayer:
    def __init__(self, id, name, sock, addr):
        self.id = id
        self.db: Player = s.get(Player, self.id)
        self.sock = sock
        self.name = name
        self.address = addr
        self.x = 500
        self.y = 500
        self.size = 50
        self.errors = 0
        self.abs_speed = 2
        self.speed_x = 2
        self.speed_y = 2
        self.color = "red"
        self.w_vision = 800
        self.h_vision = 600

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y

    def changSpid(self, vector):
        vector = findVector(vector)
        if vector[0] == 0 and vector[1] == 0:
            self.speed_x = self.speed_y = 0
        else:
            vector = vector[0] * self.abs_speed, vector[1] * self.abs_speed
            self.speed_x = vector[0]
            self.speed_y = vector[1]

    def load(self):
        self.size = self.db.size
        self.abs_speed = self.db.abs_speed
        self.speed_x = self.db.speed_x
        self.speed_y = self.db.speed_y
        self.errors = self.db.errors
        self.x = self.db.x
        self.y = self.db.y
        self.color = self.db.color
        self.w_vision = self.db.w_vision
        self.h_vision = self.db.h_vision
        return self

    def sync(self):
        self.db.size = self.size
        self.db.abs_speed = self.abs_speed
        self.db.speed_x = self.speed_x
        self.db.speed_y = self.speed_y
        self.db.errors = self.errors
        self.db.x = self.x
        self.db.y = self.y
        self.db.color = self.color
        self.db.w_vision = self.w_vision
        self.db.h_vision = self.h_vision
        s.merge(self.db)
        s.commit()


Base.metadata.create_all(engine)

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1.семейство адресов ipv4 2.тип подключения
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                       1)  # 3. выбрали парамметр и отключили пакетированиеб для отсуцтвия задержки
main_socket.bind(("localhost", 10000))  # 4.привзывае подкл к определенному серверу и порту
main_socket.setblocking(False)  # 5 непрерывность, не ожидает ответа при False ждет если True
main_socket.listen(5)  # 6 прослушка входящих соединений 5 одновременно
print("сокет создан")
players = {}
run = True
while run:
    clock.tick(FPS)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
    try:
        new_sock, addr = main_socket.accept()
        print("подключился", addr, new_sock)
        new_sock.setblocking(False)
        player = Player("олег", addr)
        login = new_sock.recv(1024).decode()
        if login.startswith("color"):
            data = findcolor(login[6:])
            player.name, player.color = data
        s.merge(player)
        s.commit()
        addr = f"({addr[0]},{addr[1]})"
        data = s.query(Player).filter(Player.address == addr)
        for user in data:
            player = LocalPlayer(user.id, "олег", new_sock, addr).load()
            players[user.id] = player
    except BlockingIOError:
        pass
    for id in list(players):
        try:
            data = players[id].sock.recv(1024).decode()
            print(data)
            players[id].changSpid(data)
        except:
            pass
    visible_bacterias = {}
    for id in list(players):
        visible_bacterias[id] = []
    pairs = list(players.items())
    for i in range(0, len(pairs)):
        for j in range(i + 1, len(pairs)):
            hero_1: LocalPlayer = pairs[i][1]
            hero_2: LocalPlayer = pairs[j][1]
            dist_x = hero_2.x - hero_1.x
            dist_y = hero_2.y - hero_1.y
            # игрок i видит игрока j
            if abs(dist_x) <= hero_1.w_vision // 2 + hero_2.size and abs(dist_y) <= hero_1.h_vision // 2 + hero_2.size:
                x_ = str(round(dist_x))
                y_ = str(round(dist_y))
                size_ = str(round(hero_2.size))
                color_ = hero_2.color
                data = f"{x_} {y_} {size_} {color_}"
                visible_bacterias[hero_1.id].append(data)
            # игрок j видит игрока i
            if abs(dist_x) <= hero_2.w_vision // 2 + hero_1.size and abs(dist_y) <= hero_2.h_vision // 2 + hero_1.size:
                x_ = str(round(-dist_x))
                y_ = str(round(-dist_y))
                size_ = str(round(hero_2.size))
                color_ = hero_2.color
                data = f"{x_} {y_} {size_} {color_}"
                visible_bacterias[hero_2.id].append(data)
    for id in list(players):
        visible_bacterias[id] = '<' + ','.join(visible_bacterias[id]) + '>'

    for id in list(players):
        try:
            players[id].sock.send(visible_bacterias[id].encode())
        except:
            players[id].sock.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()
            print("сокет закрыт")
    skreem.fill("black")
    for id in list(players):
        player = players[id]
        x = player.x * WIDTH_SERVER // WIDTH_ROOM
        y = player.y * WIDTH_SERVER // WIDTH_ROOM
        size = player.size * WIDTH_SERVER // WIDTH_ROOM
        pygame.draw.circle(skreem, player.color, (x, y), size)
        pygame.display.update()

    for id in list(players):
        player = players[id]
        players[id].update()
        players[id].sync()
    pygame.display.update()

pygame.quit()
main_socket.close()
s.query(Player).delete()
s.commit()











