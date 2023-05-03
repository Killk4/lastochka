#!/usr/bin/env python3
import os
import sys
import time
import socket
import asyncio
import sqlite3
import threading
import configparser

config = configparser.ConfigParser()
config.read('server_conf.ini')

try:
    if(config['CONFIG']):
        pass
except:
    config['CONFIG'] = {
    'local': 'False',
    'port': '49999',
    'work': 'True'
    }

    with open('server_conf.ini', 'w') as configfile:
        config.write(configfile)

def toBool(value):
    '''Принимает текстовое значение'''
    if (value == 'True'):
        return True
    else:
        return False

def myIP():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = s.getsockname()[0]
    s.close()
    return ip

open_files = {}

def log(text, console=True, event: int = 0, event_client: str = 'None'):
    ct_date = time.strftime("%d-%m-%Y", time.localtime())
    ct_time = time.strftime("%H:%M:%S", time.localtime())

    if ct_date in open_files:
        file = open_files[ct_date]
    else:
        file = open('./logs/'+str(ct_date)+'.txt', 'a')
        open_files[ct_date] = file

    try:
        file.writelines(str(ct_time)+' '+text+'\n')
        if console:
            print(str(ct_time)+' '+text)
    except:
        pass

    if event != 0:
        database = sqlite3.connect('main.db')
        cursor = database.cursor()
        cursor.execute(f'INSERT INTO logs (event, client, logtime) SELECT {event}, id, {int(time.time())} FROM swallows WHERE name = "{event_client}"')
        database.commit()
        database.close()



def helpCommand():
    print(' /help - Помощь\n',
          '/stop - Остановить сервер\n',
          '/destroy=[name] - Попрощаться с удалённой машиной, где [name] имя машины в сети\n',
          '/status=[name] - Проверить поключена ли машина к серверу\n')
    
def stopServer():
    global server_work

    log('Остановка сервера')
    time.sleep(.8)
    server_work = False

# Работа с БД
def findSwallowForBase(name: str) -> bool:
    '''Проверяет существование записи клиента в базе.
    Возвращает True если клиент найден'''
    database = sqlite3.connect('main.db')
    cursor = database.cursor()
    cursor.execute(f'SELECT * FROM `swallows` WHERE name = "{name}"')
    count = len(cursor.fetchall())
    database.close()

    if(count > 0):
        return True
    
    return False

def newSwallowForBase(name: str, hash: str = None) -> bool:
    '''Создаёт новую запись о клиенте.
    Возвращает True если запись созданна успешно'''
    ret = False
    database = sqlite3.connect('main.db')
    cursor = database.cursor()
    if(hash == None):
        hash = 'NULL'
    try:
        cursor.execute(f'INSERT INTO swallows ("name", "hash") VALUES ("{name}", "{hash}")')
        database.commit()
        ret = True
    except:
        pass
    finally:
        database.close()
        return ret

def swaalowsList() -> list:
    swallows = []
    database = sqlite3.connect('main.db')
    cursor = database.cursor()
    cursor.execute('SELECT * FROM swallows WHERE status = 1')
    rows = cursor.fetchall()
    for row in rows:
        swallows.append(row[1])
    database.close()
    return swallows

def destroyTask(client: str) -> str:
    database = sqlite3.connect('main.db')
    check = database.cursor()
    cursor = database.cursor()

    check.execute(f'SELECT * FROM destroy_task WHERE client = (SELECT id FROM swallows WHERE name = "{client}")')
    if(len(check.fetchall()) < 1):
        cursor.execute(f'INSERT INTO destroy_task ("client") SELECT id FROM swallows WHERE name = "{client}"')
        database.commit()
        database.close()
        return True, f'Задание на устранение {client} запланировано'
    else:
        database.close()
        return False, f'Задание на устранение {client} уже существует'

def cancelDestroyTask(client: str) -> None:
    database = sqlite3.connect('main.db')
    cursor = database.cursor()
    cursor.execute(f'DELETE FROM destroy_task WHERE client = (SELECT id FROM swallows WHERE name = "{client}")')
    database.commit()
    database.close()

def selectAllWaitingDestroy() -> list:
    database = sqlite3.connect('main.db')
    cursor = database.cursor()
    cursor.execute('SELECT dt.*, s.name AS name FROM destroy_task AS dt JOIN swallows AS s ON s.id = dt.client')
    rows = cursor.fetchall()
    database.close()
    return rows

def checkDestroy(client):
        database = sqlite3.connect('main.db')
        cursor = database.cursor()
        cursor.execute(f'SELECT * FROM destroy_task WHERE client = (SELECT id FROM swallows WHERE name = "{client}")')
        if(len(cursor.fetchall()) > 0):
            database.close()
            return True
        else:
            database.close()
            return False
class Lastochka:
    ''' Класс Lastochka сожержит информацию о клиенте'''
    def __init__(self, cl_socket, cl_adress):
        self.conn = cl_socket   # Сокет клиента
        self.addr = cl_adress   # Адрес клиента
        self.name = 'Unknow'    # Имя клиента. До объявления по умолчанию Unknow

logotype = (
'                                                                               ',
' __    __     ______     __  __     ______     __  __     ______     __        ',
'/\ "-./  \   /\  __ \   /\ \/ /    /\  ___\   /\ \_\ \   /\  ___\   /\ \       ',
'\ \ \-./\ \  \ \  __ \  \ \  _"-.  \ \___  \  \ \  __ \  \ \  __\   \ \ \____  ',
' \ \_\ \ \_\  \ \_\ \_\  \ \_\ \_\  \/\_____\  \ \_\ \_\  \ \_____\  \ \_____\ ',
'  \/_/  \/_/   \/_/\/_/   \/_/\/_/   \/_____/   \/_/\/_/   \/_____/   \/_____/ ',
'                                                                               ',
'       __  __     __    __     __   __                                         ',
'      /\ \/ /    /\ "-./  \   /\ \ / /                                         ',
'      \ \  _"-.  \ \ \-./\ \  \ \ \\\'/                                          ',
'       \ \_\ \_\  \ \_\ \ \_\  \ \_/                                          ',
'        \/_/\/_/   \/_/  \/_/   \//                                           ',
'                                                                               ',
'                                                                               ')

# Настройки
server_IP =  myIP()                             # IP сервера
server_PORT = int(config['CONFIG']['port'])     # Порт сервера
server_work = toBool(config['CONFIG']['work'])  # Переменная работы сервера
local_work = toBool(config['CONFIG']['local'])  # Будет ли сервер работать локально

command = False     # Переменная отправки команды
command_text = ''   # Переменная самого сообщения

client_list = []    # Список активных клиентов
noWriteClient = ['checking', 'telebot']

sa = sys.argv[1:]   # Получение аргументов для запуска скрипта

rewrite = False  # Для флага перезаписи ini файла (--rewrite)

command_old = ''    # Обнулённые переменные для истории команд
command_new = ''

# Список команд поддерживаемые для ввода
command_list = ['help',
                'destroy',
                'status',
                'stop']

if(local_work):
    server_IP = 'localhost'

# Перебор ключени и работа с ними
if (sa != []):
    i = 0
    while i < len(sa):

        # если аргумент --port или -p, то меняем порт на указанный
        if ((sa[i] == '--port') or (sa[i] == '-p')):
            server_PORT = int(sa[i+1])

        # Запуск сервера локально (127.0.0.1) Процесс будет виден только на локальной машине
        if ((sa[i] == '--local') or (sa[i] == '-l')):
            server_IP = 'localhost'
            local_work = True

        # Вывод сервера из локального состояния
        if(sa[i] == '--nolocal'):
            server_IP = myIP()
            local_work = False

        """ Небольшое пояфснение. В смене ip на иной, нет смысла. Но ингода может возникнуть конфликт
        с множественным количеством сетевых адаптеров. Серверная часть скрипта сама определяет адрес полученный от маршрутизатора,
        но во избежания проблем есть флаг --change_ip"""
        if (sa[i] == '--change_ip'):
            server_IP == sa[i+1]

        if (sa[i] == '--rewrite'):
            rewrite = True

        i += 1

# Перезапись ini файла
if(rewrite):
    config['CONFIG'] = {
        'local': local_work,
        'port': server_PORT,
        'work': server_work
    }

    with open('server_conf.ini', 'w') as configfile:
        config.write(configfile)

    rewrite = False

# Запуск сервера
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET работа с IPv4, SOCK_STREAM работа с TCP
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Указывает на то, что не надо отправлять собранные пакеты, а слать информацию сразу
main_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 1)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 3)
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 5)
main_socket.bind((server_IP, server_PORT)) # Завязка сокета с IP и портом
main_socket.setblocking(0) # Не останавливать выполнение программы пока получаем данные
main_socket.listen(5) # Включение прослушки порта. 5 говорит о количестве одновременно подключаемых клиентов. 5 не максимальное количество клиентов!

for logo in logotype:
    print(logo)

log(f'Сервер запущен с адресом {server_IP}:{server_PORT}', event=5, event_client='SERVER')

# Функция принимающая значение от пользователя
async def print_input():
    while server_work:
        global command_new

        try:
            input_str = await asyncio.get_event_loop().run_in_executor(None, input)
            input_str = input_str.replace(' ', '')
            if (input_str != ''):
                command_new = input_str
        except:
            print('Попробуйте ещё раз')


# Создание отладочного окна
async def main():
    global command
    global noWriteClient

    while server_work:
        try:
            time.sleep(1)
            try:
                client_socket, client_addr = main_socket.accept() # Получаем новое подключение. Сокет и адрес клиента.
                client_socket.setblocking(0)
                
                new_client = Lastochka(client_socket, client_addr) # Создаём нового клиента
                client_list.append(new_client) # Записываем клиента в список

            except Exception as e:
                pass

            # Чтение сообщений от клиентов
            for cl in client_list:
                try:
                    # Парсинг сообщений на блоки
                    # Из mes:1;mes:2;mes:3; получаем [['mes', '1'], ['mes', '2'], ['mes', '3']]
                    data = cl.conn.recv(2**20).decode() # Получение сообщений
                    data = data.split(';')
                    for d in data:
                        data = d.split(':')

                        # Первым сообщением передаётся имя клиента
                        if data[0] == 'name':
                            if data[1] in noWriteClient:
                                cl.name = data[1]
                                continue
                            cl.name = data[1]      

                            global command_new                      

                            # Если ласточка ещё не существует в базе, то создать, а если существует, то проверить отложенные задания
                            if(findSwallowForBase(cl.name)):
                                if(checkDestroy(cl.name)):
                                    command_new = f'/destroy={cl.name}'
                                    cancelDestroyTask(cl.name)
                            else:
                                newSwallowForBase(cl.name)
                            log(f'{cl.name} > подключился',event=1, event_client=cl.name)

                        # Если тип сообщения mes
                        if data[0] == 'mes':
                            # imh - i'm here (Я тут) сообщение о выполняемой работе
                            if data[1] == 'imh':
                                pass
                            
                            # Сообщение о начале удаления
                            if data[1] == 'preDestroy':
                                log(f'{cl.name} > сообщил о начале удаления файлов', event=3, event_client=cl.name)
                            
                            # Сообщение о завершении удаления
                            if data[1] == 'destroy':
                                log(cl.name + ' > сообщил о завершении удаления файлов', event=4, event_client=cl.name)
                                #  command = False

                        if data[0] == 'check':
                            log(f'{cl.name} > проверка подключения к серверу', event=7, event_client=cl.name)

                        # Обработчик запроса бота. Отправляет список машин в онлайне.
                        if data[0] == 'wol' and data[1] == 'telebot':
                            clients = 'telebot:'
                            for client in client_list:
                                clients = clients + client.name + ','
                            clients = clients + ';'
                            cl.conn.send(clients.encode())

                        # Обработчик запроса бота. Отправляет список всех зарагестрированных в базе машин.
                        if data[0] == 'alc' and data[1] == 'telebot':
                            clients = 'telebot:'
                            tmp = swaalowsList()
                            for client in tmp:
                                clients = clients + client + ','
                            clients = clients + ';'
                            cl.conn.send(clients.encode())

                        # Получает от бота имя и команду на уничтожение.
                        if data[0] == 'telebotdestroy':
                            clientNameInOnline = []
                            for cl in client_list:
                                clientNameInOnline.append(cl.name)
                            if(data[1] in clientNameInOnline):
                                command_new = f'/destroy={data[1]}'
                                if(checkDestroy(data[1])):
                                    cancelDestroyTask(data[1])
                                cl.conn.send(f'{data[1]} начал процедуру удаления'.encode())
                            else:
                                stat_task, text_task = destroyTask(data[1])
                                cl.conn.send(text_task.encode())
                            clientNameInOnline = []

                        # Отмена уничтожения машины
                        if data[0] == 'telebotUNdestroy':
                            cancelDestroyTask(data[1])
                            cl.conn.send(f'Отменено уничтожение {data[1]}'.encode())

                        # Получение списка всех машин в очереди на уничтожение 
                        if data[0] == 'selectAllWait':
                            waiting = 'telebot:'
                            rows = selectAllWaitingDestroy()
                            for row in rows:
                                waiting += f'{row[2]},'
                            waiting += ';'
                            cl.conn.send(waiting.encode())

                except:
                    pass

            # Отправка сообщений клиенту
            for cl in client_list:
                try:

                    # way - Where are you (Где ты?) должен вернуть imh
                    cl.conn.send('mes:way;'.encode())
                    
                    # Если есть команда, то отправить её
                    if command:
                        cl.conn.send(command_text.encode())
                        command_text = ''  
                        command = False                      
                    
                # Если не удалось отправить, то значит клиент оффлайн
                except:
                    if cl.name in noWriteClient:
                        continue
                
                    log(cl.name + ' > отключился', event=2, event_client=cl.name)
                    client_list.remove(cl)
                    cl.conn.close()

            global command_old

            no_command = False

            # Если появилась новая команда
            if (command_old != command_new):
                if (command_new[:1] != '/'):
                    print('Все комманды вводятся начинаются с /')
                    command_old = command_new = 'un_/'
                    continue

                log(command_new, console=False)
                command_new = command_new.replace('/', '')
                
                for cl in command_list:
                    if(len(command_new.split('=')) > 1):
                        clist = command_new.split('=')[0]
                    else:
                        clist = command_new

                    if (cl == clist):

                        if (len(command_new.split('=')) > 1):
                            command_new = command_new.split('=')

                            if (command_new[0] == 'destroy'):
                                command_text = f'{command_new[1]}:destroy;'
                                command = True
                                log(f'На компьютер {command_new[1]} отправлена команда на удаление')

                            if(command_new[0] == 'status'):
                                client = command_new[1]
                                check_client = False

                                for cl in client_list:
                                    if(cl.name == client):
                                        check_client = True

                                if(check_client):
                                    log(f'{client} в сети')
                                else:
                                    log(f'не удалось получить ответ от {client}')


                        if (command_new == 'help'):
                            helpCommand()

                        if (command_new == 'stop'):
                            stopServer()

                        command_old = command_new = f'/ok'
                        no_command = False
                        break
                    else:
                        no_command = True
                        command_old = command_new

                if (no_command):
                    print('Ошибка при вводе команды. /help - список всех комманд.')
                    command_old = command_new = f'/ko'
                    no_command = False

        # Проверка нажатия Ctrl + C
        except Exception as e:
            print(e)

# Запуск основных циклов
input_thread = threading.Thread(target=asyncio.run, args=(print_input(),))
input_thread.start()

asyncio.run(main())

# В случае остановки цикла завершаем работу сервера
log('Сервер остановлен', event=6, event_client='SERVER')
time.sleep(.1)
main_socket.close()