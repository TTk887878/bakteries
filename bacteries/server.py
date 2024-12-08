import socket
import time

main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 1.семейство адресов ipv4 2.тип подключения
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY,
                       1)  # 3. выбрали парамметр и отключили пакетированиеб для отсуцтвия задержки
main_socket.bind(("localhost", 10000))  # 4.привзывае подкл к определенному серверу и порту
main_socket.setblocking(False)  # 5 непрерывность,не ожидает ответа при Fals  ждет если True
main_socket.listen(5)  # 6 прослушка входящих соединений 5 одновремменно
print("сокет создан")
players = []
while True:
    try:
        new_sock, addr = main_socket.accept()
        print("подключился", addr, new_sock)
        new_sock.setblocking(False)
        players.append(new_sock)
    except BlockingIOError:
        pass
    for sock in players:
        try:
            data = sock.recv(1024).decode()
            print(data)
        except:
            pass
    time.sleep(1)
