import os
import shutil
import random
import socket
from rich.progress import track
from time import sleep

# Настройки
SERVER_IP = 'localhost' # Адрес сервера
SERVER_PORT = 10000     # Порт сервера

running = False         # Переменная для запуска цикла
start_one = True        # Переменная для отправки первого сообщения

def debugFolders(ran):
    try:
        os.mkdir('./test')
    except:
        pass
    try:
        for step in track(range(ran), description='Create debug folders'):
            random.seed()
            tn = random.randint(0, 2**100)
            fn = str(step) + str(tn)
            os.mkdir('./test/'+fn)
            random.seed()
            if random.randint(0, 1) == 1:
                f = open('./test/'+fn+'/'+str(step)+'.txt', 'a')
                f.writelines('TEST')
                f.close()
    except:
        pass

def destroydir(path):
    dirs = os.listdir(path)
    for d in track(dirs, description='Remove folders'):
        shutil.rmtree(path+d)

def memoryEat():
    pass

######## DEBUG ########
debugFolders(10000)
# destroydir('./test/')
# os.mkdir('./test')
#######################

myname = input('Client name: ')

# Подключение к серверу
try:
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    server.connect((SERVER_IP, SERVER_PORT))

    running = True
except:
    print('Подключение к серверу отсутствует')
    destroydir('./test/')
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
                    destroydir('./test/')
                    message = 'mes:destroy;'
                    server.send(message.encode())
                    server.close()

    except:
        print('Связь с сервером разорвана')
        running = False