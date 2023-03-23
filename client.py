import os
import shutil
import random
import socket
from rich.progress import track
from time import sleep

# Настройки
SERVER_IP = '10.0.20.200'   # Адрес сервера
SERVER_PORT = 10000         # Порт сервера

running = False             # Переменная для запуска цикла
start_one = True            # Переменная для отправки первого сообщения

recon = 5                   # Количество попыток переподключения к серверу

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
                # print(f'ПРОХОД {i + 1} УСПЕШНО') # Вывод сообщения об успешном прохождении итерации
            except: # Обработка исключений при записи в файл
                # print(f'ПРОХОД {i + 1} НЕУДАЧНО') # Вывод сообщения об ошибке при прохождении итерации
                success = False # Установка значения success в False при ошибке записи в файл
    try:
        os.remove(path) # Удаление файла после перезаписи его содержимого случайными данными passes раз.
        # print('ФАЙЛ УСПЕШНО УДАЛЕН.') # Вывод сообщения об успешном удалении файла.
    except: # Обработка исключений при удалении файла.
        print('ОШИБКА УДАЛЕНИЯ ФАЙЛА. ФАЙЛ МОЖЕТ БЫТЬ УНИЧТОЖЕН.') 
        success = False

def isFile(root_path):
    root_list = os.listdir(root_path)

    for rl in root_list:
        if (os.path.isdir(root_path+rl)):
            isFile(root_path+rl)
        else:
            secure_delete(root_path+'/'+rl)

def memoryEat():
    pass

######## DEBUG ########
debugFolders(100)
#######################

myname = input('Client name: ')

# Подключение к серверу
i = 1
while i <= recon:
    print(f'{i} попытка подключения к серверу...')
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.connect((SERVER_IP, SERVER_PORT))

        running = True
        print('Соединение установленно!')
        break
    except:
        pass

    sleep(.5)
    i += 1

if (running == False):
    print('Подключение к серверу отсутствует')
    isFile('./test/') # Доработать!
    shutil.rmtree('./test/')
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