import socket

import pygame
import psycopg2
from sqlalchemy import create_engine, Column, String, Integer
from sqlalchemy.orm import declarative_base, sessionmaker

engine = create_engine("postgresql+psycopg2://postgres:1@localhost/bakteriy")

Base = declarative_base()
Session = sessionmaker(bind=engine)
s = Session()

pygame.init()
WIDTH_ROOM, HEIGHT_ROOM = (4000, 4000)
WIDTH_SERVER, HEIGHT_SERVER = (300, 300)
FPS = 100
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
    abs_speed = Column(Integer, default=1)
    speed_x = Column(Integer, default=0)
    speed_y = Column(Integer, default=0)
    color = Column(String(250), default="red")  # Добавили цвет
    w_vision = Column(Integer, default=800)
    h_vision = Column(Integer, default=600)  # Добавили размер квадрат

    def __init__(self, name, address):
        self.name = name
        self.address = address


# Локальный класс игроков
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
        self.abs_speed = 1
        self.speed_x = 0
        self.speed_y = 0
        self.color = "red"
        self.w_vision = 800
        self.h_vision = 600


Base.metadata.create_all(engine)

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1.семейство адресов ipv4 2.тип подключения
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                       1)  # 3. выбрали парамметр и отключили пакетированиеб для отсуцтвия задержки
main_socket.bind(("localhost", 10000))  # 4.привзывае подкл к определенному серверу и порту
main_socket.setblocking(False)  # 5 непрерывность,не ожидает ответа при Fals  ждет если True
main_socket.listen(5)  # 6 прослушка входящих соединений 5 одновремменно
print("сокет создан")
players = {}
while True:
    clock.tick(FPS)
    try:
        new_sock, addr = main_socket.accept()
        print("подключился", addr, new_sock)
        new_sock.setblocking(False)
        player = Player("олег", addr)
        s.merge(player)
        s.commit()
        addr = f"({addr[0]},{addr[1]})"
        data = s.query(Player).filter(Player.address == addr)
        for user in data:
            player = LocalPlayer(user.id, "олег", new_sock, addr)
            players[user.id] = player
    except BlockingIOError:
        pass
    for id in list(players):
        try:
            data = players[id].sock.recv(1024).decode()
            print(data)
        except:
            pass
    for id in list(players):
        try:
            players[id].sock.send("фхф".encode())
        except:
            players[id].sock.close()
            del players[id]
            s.query(Player).filter(Player.id == id).delete()
            s.commit()
            print("сокет закрыт")
