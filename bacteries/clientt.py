import socket
import tkinter as tk
from tkinter import ttk
import tkinter.messagebox
import pygame
import math

name = ""
color = ""
colors = ['Maroon', 'DarkRed', 'FireBrick', 'Red', 'Salmon', 'Tomato', 'Coral', 'OrangeRed', 'Chocolate', 'SandyBrown',
          'DarkOrange', 'Orange', 'DarkGoldenrod', 'Goldenrod', 'Gold', 'Olive', 'Yellow', 'YellowGreen', 'GreenYellow',
          'Chartreuse', 'LawnGreen', 'Green', 'Lime', 'SpringGreen', 'MediumSpringGreen', 'Turquoise',
          'LightSeaGreen', 'MediumTurquoise', 'Teal', 'DarkCyan', 'Aqua', 'Cyan', 'DeepSkyBlue', 'DodgerBlue',
          'RoyalBlue', 'Navy', 'DarkBlue', 'MediumBlue']


def login():
    global name
    name = name_row.get()
    if name and color:
        root.destroy()
        root.quit()
    else:
        tk.messagebox.showerror("Ошибка", "Ты не выбрал цвет или не ввёл имя!")


def scroll(event):
    global color
    color = combo.get()
    stail.configure("TCombobox", fieldbackground=color, background="white")


root = tk.Tk()
root.title('logigi')
root.geometry('300x200')
stail = ttk.Style()
stail.theme_use('clam')

name_label = tk.Label(root, text='введи имя:')
name_label.pack()
name_row = tk.Entry(root, width=30, justify='center')
name_row.pack()
color_label = tk.Label(root, text='выбери цвет')
color_label.pack()
combo = ttk.Combobox(root, values=colors, textvariable=color)
combo.bind("<<ComboboxSelected>>", scroll)
combo.pack()
btn = tk.Button(root, text='НАЧАТЬ', command=login)
btn.pack()
root.mainloop()


def drow_text(x, y, r, text, color):
    font = pygame.font.Font(None, r)
    text = font.render(text, True, color)
    rect = text.get_rect(center=(x, y))
    screen.blit(text, rect)

def find(info: str):
    first = None
    for index, value in enumerate(info):
        if value == "<":
            first = index
        if value == ">" and first is not None:
            second = index
            result = info[first + 1:second].split(",")
            return result
    return ""



def draw_bacterias(data: list[str]):
    for num, bact in enumerate(data):
        data = bact.split(" ")  # Разбиваем по пробелам подстроку одной бактерии
        x = CC[0] + int(data[0])
        y = CC[1] + int(data[1])
        size = int(data[2])
        color = data[3]
        pygame.draw.circle(screen, color, (x, y), size)


sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1.семейство адресов ipv4 2.тип подключения
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                1)  # 3. выбрали парамметр и отключили пакетированиеб для отсуцтвия задержки
sock.connect(("localhost", 10000))  # 4.привзывае подкл к определенному серверу и порту
sock.send(f"color:<{name},{color}>".encode())
pygame.init()

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
                msg = f"<{vector[0]},{vector[1]}>"
                sock.send(msg.encode())

    data = sock.recv(1024).decode()
    print(data)
    data=find(data)
    screen.fill("gray")
    if data!=['']:
        draw_bacterias(data)
    pygame.draw.circle(screen,color,CC, radius)
    drow_text(CC[0], CC[1], radius // 2, name, (0, 0, 0))
    pygame.display.update()
pygame.quit()
