#!/usr/bin/env python3
import random
import socket
import configparser
from sys import argv

# Настройки
server_IP = '10.0.20.200'    # Адрес сервера
server_PORT = 49999          # Порт сервера
recon = 5       # Количество попыток переподключения к серверу
sa = argv[1:]   # Получение аргументов для запуска скрипта
con = False     # Переменная подключения

myname = socket.gethostname()   # Имя клиента (имя компьютера)

# Перебор ключени и работа с ними
if (sa != []):
    i = 0
    while i < len(sa):
        # если аргумент --port или -p, то меняем порт на указанный
        if ((sa[i] == '--port') or (sa[i] == '-p')):
            server_PORT = int(sa[i+1])

        # То же самое для IP
        if (sa[i] == '--ip'):
            server_IP = sa[i+1]

        if (sa[i] == '--recon'):
            recon = int(sa[i+1])

        i += 1

# Подключение к серверу
i = 1
while i <= recon:
    print(f'{i} попытка подключения к {server_IP}:{server_PORT}')
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.connect((server_IP, server_PORT))

        start_message = 'name:' + myname + ';'
        check_message = 'check:check;'
        server.send(f'{start_message}{check_message}'.encode())

        con = True
        print('Соединение установленно!')
        break
    except:
        con = False

    i += 1

if (con == False):
    print('Подключение к серверу отсутствует')

server.close()

input('Нажмите Enter для выхода')