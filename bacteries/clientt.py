import socket
import time

sock= socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1.семейство адресов ipv4 2.тип подключения
sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                   1)  # 3. выбрали парамметр и отключили пакетированиеб для отсуцтвия задержки
sock.connect(("localhost", 10000))  # 4.привзывае подкл к определенному серверу и порту
while True:
    sock.send("привет".encode())