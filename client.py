#!/usr/bin/env python3
import os
import shutil
import random
import socket
from rich.progress import track
from time import sleep
from sys import argv

# Настройки
server_IP = '10.0.20.200'   # Адрес сервера
server_PORT = 49999         # Порт сервера

running = False             # Переменная для запуска цикла
start_one = True            # Переменная для отправки первого сообщения
recon = 5                   # Количество попыток переподключения к серверу
debug = False               # Переменная запуска отладки
delete_files = True         # Если True, то файлы из листа будут удаляться

sa = argv[1:]               # Получение аргументов для запуска скрипта


# Папки для удаления
# Принимает возможности записи ./path/ и D:\\path\\
# Обязательно завершать конец пути
root_list = ['./test/',
             './test1/',
             'C:/todel/'
             ]

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

        # Включение DEBUG
        if ((sa[i] == '--debug') or (sa[i] == '-d')):
            debug = True

        # Выключение удаления файлов. Нужно только для отладки, так как файлы по итогу всё равно перезапишутся.
        if (sa[i] == '--nodelete'):
            delete_files = False

        i += 1

# Создаёт тестовые папки и случайным образом наполняет их
def debugFolders(ran, path):
    try:
        os.mkdir(path)  # Создание папки с именем переменной path
    except:
        pass
    try:
        for step in track(range(ran), description='Create debug folders'): # Красивая отрисовка прогресс бара в консоли ^-^
            random.seed()
            tn = random.randint(0, 2**100)  # Огромное число, используется для имени папкиу
            fn = str(step) + str(tn)
            os.mkdir(f'./{path}/{fn}')
            random.seed()
            if random.randint(0, 1) == 1:   # Если на барабане выпало 1, то создаём файл в папке
                f = open(f'./{path}/{fn}/{str(step)}.txt', 'a')
                f.writelines('TEST')    # Пишем в файл
                f.close()
    except:
        pass

def secure_delete(path, passes=5):
    '''Функция принимает путь к файлу и количество прогонов (по умолчанирю 5)'''

    global success # Использование глобальной переменной success
    with open(path, "ba+") as delfile:
        length = delfile.tell() # Определение размера файла
    with open(path, "br+") as delfile:
        for i in range(passes): # Перезапись содержимого файла случайными данными passes раз
            try:
                delfile.seek(0) # Перемещение указателя в начало файла
                delfile.write(os.urandom(length)) # Запись случайных данных в файл
            except: # Обработка исключений при записи в файл
                success = False # Установка значения success в False при ошибке записи в файл
    try:
        if (delete_files):
            os.remove(path) # Удаление файла после перезаписи его содержимого случайными данными passes раз.
    except: # Обработка исключений при удалении файла.
        print('ОШИБКА УДАЛЕНИЯ ФАЙЛА. ФАЙЛ МОЖЕТ БЫТЬ УНИЧТОЖЕН.') 
        success = False

def isFile(root_list):
    ''' Функция принимает список с путями к папкам которые будут удалены со всем содержимым.
    Проверяет на наличие файлов внутри. Если он есть, то вызывается функция перезаписи и удаления.
    Если нет файлов, но есть папка, тогда вызывается рекурсия на подпапку.'''

    try:
        for r in root_list:
            list = os.listdir(r)

            for l in list:
                if (os.path.isdir(r+l)):
                    isFile([f'{r+l}/'])
                else:
                    secure_delete(f'{r+l}')
    except:
        pass

######## DEBUG ########
if (debug):
    debugFolders(1000, 'test')
    debugFolders(100, 'test1')
#######################

myname = input('Client name: ')

# Подключение к серверу
i = 1
while i <= recon:
    print(f'{i} попытка подключения к серверу...')
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.connect((server_IP, server_PORT))

        running = True
        print('Соединение установленно!')
        break
    except:
        pass

    sleep(.5)
    i += 1

if (running == False):
    print('Подключение к серверу отсутствует')
    isFile(root_list)                           # Удаления файлов в корневом каталоге и во всех подпапках
    if (delete_files):
        for rl in root_list:                        # Удаление корневого каталога 
            try:
                shutil.rmtree(rl)
            except:
                pass
    print('Удалил файлы\nBye ^-^')
    sleep(5)

while running:

    if start_one:
        start_message = 'name:' + myname + ';'
        server.send(start_message.encode())
        start_one = False

    try:
        # Получение данных с сервера
        data = server.recv(2**20).decode()
        data = data.split(';')
        for d in data:
            data = d.split(':')
            if data[0] == 'mes':
                if data[1] == 'way':
                    message = 'mes:imh;'
                    server.send(message.encode())
                    print(data[1])
                
            # Если обращение по имени
            if data[0] == myname:

                # Если команда дестрой
                if data[1] == 'destroy':
                    secure_delete('./test/') # Доработать!
                    message = 'mes:destroy;'
                    server.send(message.encode())
                    server.close()

    except:
        print('Связь с сервером разорвана')
        running = False