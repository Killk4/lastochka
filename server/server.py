#!/usr/bin/env python3
import os
import sys
import time
import rich
import socket
import asyncio
import threading
import configparser

config = configparser.ConfigParser()
config.read('./server_conf.ini')

try:
    if(config['CONFIG']):
        pass
except:
    config['CONFIG'] = {
    'local': 'False',
    'port': '49999',
    'work': 'True'
    }

    with open('./server_conf.ini', 'w') as configfile:
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

def log(text):
    ''' Запись логов в файл logs.txt '''
    ct_date = time.strftime("%d-%m-%Y", time.localtime())    # Текущий день
    ct_time = time.strftime("%H:%M:%S", time.localtime())    # Текущее время
    try:
        file = open('./logs/'+str(ct_date)+'.txt', 'a')          # Открыть файл
        file.writelines(str(ct_time)+' '+text+'\n')              # Записать в файл
        print(str(ct_time)+' '+text)                             # Вывести в консоль
        file.close()                                             # Закрыть файл
    except:
        os.makedirs('logs', 744)
        log(text)

def helpCommand():
    print(' /help - Помощь\n',
          '/stop - Остановить сервер\n',
          '/restart - Перезагрузить сервер\n',
          '/destroy [name] - Попрощаться с удалённой машиной, где [name] имя машины в сети\n',
          '/status  [name] - Проверить поключена ли машина к серверу\n')
    
def stopServer():
    global server_work

    log('Остановка сервера')
    time.sleep(.8)
    server_work = False

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

sa = sys.argv[1:]   # Получение аргументов для запуска скрипта

rewrite = False  # Для флага перезаписи ini файла (--rewrite)

command_old = ''    # Обнулённые переменные для истории команд
command_new = ''

# Список команд поддерживаемые для ввода
command_list = ['help',
                'destroy',
                'status',
                'stop',
                'restart']

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

    with open('./server_conf.ini', 'w') as configfile:
        config.write(configfile)

    rewrite = False

# Запуск сервера
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET работа с IPv4, SOCK_STREAM работа с TCP
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Указывает на то, что не надо отправлять собранные пакеты, а слать информацию сразу
main_socket.bind((server_IP, server_PORT)) # Завязка сокета с IP и портом
main_socket.setblocking(0) # Не останавливать выполнение программы пока получаем данные
main_socket.listen(5) # Включение прослушки порта. 5 говорит о количестве одновременно подключаемых клиентов. 5 не максимальное количество клиентов!

for logo in logotype:
    print(logo)

log(f'Сервер запущен с адресом {server_IP}:{server_PORT}')

# Функция принимающая значение от пользователя
async def print_input():
    while server_work:
        global command_new

        input_str = await asyncio.get_event_loop().run_in_executor(None, input)
        input_str = input_str.replace(' ', '')
        if (input_str != ''):
            command_new = input_str

# Создание отладочного окна
async def main():
    global command

    while server_work:
        try:
            time.sleep(1)
            try:
                client_socket, client_addr = main_socket.accept() # Получаем новое подключение. Сокет и адрес клиента.
                client_socket.setblocking(0)
                
                new_client = Lastochka(client_socket, client_addr) # Создаём нового клиента
                client_list.append(new_client) # Записываем клиента в список

            except:
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
                            cl.name = data[1]
                            log(cl.name + ' > подключился')

                        # Если тип сообщения mes
                        if data[0] == 'mes':
                            # imh - i'm here (Я тут) сообщение о выполняемой работе
                            if data[1] == 'imh':
                                pass

                            if data[1] == 'preDestroy':
                                log(f'{cl.name} > сообщил о готовности удалить файлы')
                            
                            # destroy - сообщение о удалении файлов
                            if data[1] == 'destroy':
                                log(cl.name + ' > сообщил о удалении файлов')
                                #  command = False
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
                    log(cl.name + ' > отключился')
                    client_list.remove(cl)
                    cl.conn.close()

            global command_old
            global command_new

            no_command = False

            if (command_old != command_new):
                if (command_new[:1] != '/'):
                    print('Все комманды вводятся начинаются с /')
                    command_old = command_new = 'un_/'
                    continue

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
        except KeyboardInterrupt:
            break

# Запуск основных циклов
input_thread = threading.Thread(target=asyncio.run, args=(print_input(),))
input_thread.start()

asyncio.run(main())

# В случае остановки цикла завершаем работу сервера
log('Сервер остановлен')
time.sleep(3)
main_socket.close()