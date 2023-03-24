#!/usr/bin/env python3
import socket
import time
import os
import sys


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

class Lastochka:
    ''' Класс Lastochka сожержит информацию о клиенте'''
    def __init__(self, cl_socket, cl_adress):
        self.conn = cl_socket   # Сокет клиента
        self.addr = cl_adress   # Адрес клиента
        self.name = 'Unknow'    # Имя клиента. До объявления по умолчанию Unknow

# Настройки
server_IP =  myIP()         # IP сервера
server_PORT = 49999         # Порт сервера
server_work = True          # Переменная работы сервера
command = False             # Переменная отправки команды

client_list = []            # Список активных клиентов

sa = sys.argv[1:]           # Получение аргументов для запуска скрипта

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

        """ Небольшое пояфснение. В смене ip на иной, нет смысла. Но ингода может возникнуть конфликт
        с множественным количеством сетевых адаптеров. Серверная часть скрипта сама определяет адрес полученный от маршрутизатора,
        но во избежания проблем есть флаг --change_ip"""
        if (sa[i] == '--change_ip'):
            server_IP == sa[i+1]

        i += 1

# Запуск сервера
main_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # AF_INET работа с IPv4, SOCK_STREAM работа с TCP
main_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1) # Указывает на то, что не надо отправлять собранные пакеты, а слать информацию сразу
main_socket.bind((server_IP, server_PORT)) # Завязка сокета с IP и портом
main_socket.setblocking(0) # Не останавливать выполнение программы пока получаем данные
main_socket.listen(5) # Включение прослушки порта. 5 говорит о количестве одновременно подключаемых клиентов. 5 не максимальное количество клиентов!

log(f'Сервер запущен с адресом {server_IP}:{server_PORT}')

# Создание отладочного окна
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
                        
                        # destroy - сообщение о удалении файлов
                        if data[1] == 'destroy':
                            log(cl.name + ' сообщил о удалении файлов')
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
                    command_text = 'L3:destroy;'
                    cl.conn.send(command_text.encode())
            # Если не удалось отправить, то значит клиент оффлайн
            except:
                log(cl.name + ' > отключился')
                client_list.remove(cl)
                cl.conn.close()

    # Проверка нажатия Ctrl + C
    except KeyboardInterrupt:
        break

# В случае остановки цикла завершаем работу сервера
log('Сервер остановлен')
time.sleep(5)
main_socket.close()