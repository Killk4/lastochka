#!/usr/bin/env python3
import os
import shutil
import random
import socket
import configparser
import win32security
from sys import argv
from time import sleep
import ntsecuritycon as con
from rich.progress import track

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
        'path1' : './test/',
        'path2' : './test1/',
        'path3' : 'C:/todel/'
    }

    with open('client_config.ini', 'w') as configfile:
        config.write(configfile)

def toBool(value):
    '''Принимает текстовое значение'''
    if (value == 'True'):
        return True
    else:
        return False

# Настройки
server_IP = config['CONFIG']['server_ip']           # Адрес сервера
server_PORT = int(config['CONFIG']['server_port'])  # Порт сервера

recon = int(config['CONFIG']['recon'])              # Количество попыток переподключения к серверу
debug = toBool(config['CONFIG']['debug'])           # Переменная запуска отладки
running = toBool(config['CONFIG']['running'])       # Переменная для запуска цикла
delete_files = toBool(config['CONFIG']['delete'])   # Если True, то файлы из листа будут удаляться
start_one = True                # Переменная для отправки первого сообщения
myname = socket.gethostname()   # Имя клиента (имя компьютера)

sa = argv[1:]                   # Получение аргументов для запуска скрипта

root_list = []   # Список удаляемых директорий
rewrite = False  # Для флага перезаписи ini файла (--rewrite)

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

        if (sa[i] == '--recon'):
            recon = int(sa[i+1])

        if (sa[i] == '--rewrite'):
            rewrite = True

        i += 1

# Перезапись ini файла
if(rewrite):
    config['CONFIG'] = {
        'server_ip':server_IP,
        'server_port':server_PORT,
        'running':running,
        'recon':recon,
        'debug':debug,
        'delete':delete_files
    }

    with open('client_config.ini', 'w') as configfile:
        config.write(configfile)

    rewrite = False

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

def set_permissions(path:str, perm:int, need=True) -> None:

    '''Установка прав доступа к файлу или каталогу.
    Принимает путь и выбор прав доступа.
    1 - все и администраторы
    2 - пользователи и администраторы
    3 - только администраторы
    4 - нет прав ни у кого'''

    if(need):
        set_permissions(path, 4, False)

    try:
        # Получаем информацию о безопасности файла или папки
        sd = win32security.GetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION)
        
        if perm == 1:
            # Создаем новый список управления доступом (DACL)
            dacl = win32security.ACL()
            # Добавляем полные права доступа для всех пользователей
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, win32security.ConvertStringSidToSid('S-1-1-0'))
            # Добавляем полные права доступа для администраторов
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, win32security.ConvertStringSidToSid('S-1-5-32-544'))
        elif perm == 2:
            # Создаем новый список управления доступом (DACL)
            dacl = win32security.ACL()
            # Добавляем полные права доступа для аутентифицированных пользователей
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, win32security.ConvertStringSidToSid('S-1-5-11'))
            # Добавляем полные права доступа для администраторов
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, win32security.ConvertStringSidToSid('S-1-5-32-544'))
        elif perm == 3:
            # Создаем новый список управления доступом (DACL)
            dacl = win32security.ACL()
            # Добавляем полные права доступа для администраторов
            dacl.AddAccessAllowedAce(win32security.ACL_REVISION, con.FILE_ALL_ACCESS, win32security.ConvertStringSidToSid('S-1-5-32-544'))
        elif perm == 4:
            # Создаем новый пустой список управления доступом (DACL)
            dacl = win32security.ACL()
        
        # Устанавливаем новый список управления доступом (DACL)
        sd.SetSecurityDescriptorDacl(1, dacl, 0)
        # Применяем изменения к файлу или папке
        win32security.SetFileSecurity(path, win32security.DACL_SECURITY_INFORMATION, sd)
    except Exception as e:
        if(debug):
            print(f'172: {e}')

def environ(path):
    # Находим индекс первого вхождения символа '&' в строке path
    fpo = path.find('&')

    # Проверяем, есть ли символ '&' в строке path
    if(fpo != -1):
        # Находим индекс последнего вхождения символа '&' в строке path
        fpe = path.rfind('&')
        
        # Получаем значение переменной окружения с именем, указанным между символами '&' в строке path
        temp = os.environ.get(path[fpo+1:fpe])
        # Заменяем часть строки path между символами '&' на значение переменной окружения
        path = temp + path[fpe+1:]

    # Возвращаем измененную строку path
    return path

def secure_delete(path, passes=5):
    '''Функция принимает путь к файлу и количество прогонов (по умолчанирю 5)'''

    global success # Использование глобальной переменной success

    set_permissions(path, 1)

    try:
        with open(path, "ba+") as delfile:
            length = delfile.tell() # Определение размера файла
        with open(path, "br+") as delfile:
            for i in range(passes): # Перезапись содержимого файла случайными данными passes раз
                try:
                    delfile.seek(0) # Перемещение указателя в начало файла
                    delfile.write(os.urandom(length)) # Запись случайных данных в файл
                except Exception as e: # Обработка исключений при записи в файл
                    if(debug):
                        print(f'208: {e}')
                    success = False # Установка значения success в False при ошибке записи в файл
    except Exception as e:
        if(debug):
            print(f'212: {e}')

    try:
        if (delete_files):
            os.remove(path) # Удаление файла после перезаписи его содержимого случайными данными passes раз.
    except Exception as e: # Обработка исключений при удалении файла.
        if(debug):
            print(f'219: {e}') 
        success = False

def isFile(root_list):
    ''' Функция принимает список с путями к папкам которые будут удалены со всем содержимым.
    Проверяет на наличие файлов внутри. Если он есть, то вызывается функция перезаписи и удаления.
    Если нет файлов, но есть папка, тогда вызывается рекурсия на подпапку.'''

    for r in root_list:
        set_permissions(r, 1)
        list = os.listdir(r)

        for l in list:
            if (os.path.isdir(r+l)):
                set_permissions(f'{r+l}/', 1)
                isFile([f'{r+l}/'])
                try:
                    shutil.rmtree(f'{r+l}/')
                except Exception as e:
                    if(debug):
                        print(f'238: {e}')
            else:
                secure_delete(f'{r+l}')

# Удаление всех файлов по путям из ini файла
def allDestroy():
    global config
    global root_list
    global delete_files

    for rol in config['DELETE_PATH'].values():
        if (rol == 'first'):
            continue

        rol = environ(rol)
        set_permissions(rol, 1)
        root_list.append(rol)

    isFile(root_list)               # Удаления файлов в корневом каталоге и во всех подпапках
    if (delete_files):
        for rl in root_list:        # Удаление корневого каталога 
            try:
                shutil.rmtree(rl)
            except Exception as e:
                if(debug):
                    print(f'263: {e}')
    print('Удалил файлы\nBye ^-^')

######## DEBUG ########
if (debug):
    debugFolders(1000, 'test')
    debugFolders(100, 'test1')
    myname = input('Client name: ')
#######################

# Подключение к серверу
i = 1
while i <= recon:
    print(f'{i} попытка подключения к {server_IP}:{server_PORT}')
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
    allDestroy()
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
                    server.send('mes:preDestroy;'.encode())
                    allDestroy()
                    server.send('mes:destroy;'.encode())
                    server.close()

    except:
        print('Связь с сервером разорвана')
        running = False