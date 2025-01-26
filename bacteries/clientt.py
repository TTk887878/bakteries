import socket
import time
import pygame
import math


def drow_text(x, y, r, text, color):
    font = pygame.font.Font(None, r)
    text = font.render(text, True, color)
    rect = text.get_rect(center=(x,y))
    screen.blit(text,rect)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1.семейство адресов ipv4 2.тип подключения
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                1)  # 3. выбрали парамметр и отключили пакетированиеб для отсуцтвия задержки
sock.connect(("localhost", 10000))  # 4.привзывае подкл к определенному серверу и порту

pygame.init()
name = "амебиус"

WIDTH = 800
HEIGHT = 700
CC = (WIDTH // 2, HEIGHT // 2)
old = (0, 0)
radius = 50
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("амёба VS амёба")

run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if pygame.mouse.get_focused():
            pos = pygame.mouse.get_pos()
            print(pos)
            vector = pos[0] - CC[0], pos[1] - CC[1]
            lenv = math.sqrt(vector[0] ** 2 + vector[1] ** 2)
            vector = vector[0] / lenv, vector[1] / lenv
            if lenv <= radius:
                vector = 0, 0

            if vector != old:
                old = vector
                msg = f"{vector[0]},{vector[1]}"
                sock.send(msg.encode())

    data = sock.recv(1024).decode()
    print(data)
    screen.fill("gray")
    pygame.draw.circle(screen, (255, 0, 0), CC, radius)
    drow_text(CC[0],CC[1],radius//2,name,(0,0,0))
    pygame.display.update()
pygame.quit()
