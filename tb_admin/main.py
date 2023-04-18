import time
import socket
import telebot
import sqlite3

bot = telebot.TeleBot('6163267213:AAHU6vh2OUCT3eYbLF-7pru93zFPvP2C78g')

admins = []

server_IP = '10.0.5.200'
server_PORT = 49999

def newAdmin(name: str, nick: str, chatid: str) -> None:
    ''' Функция для подачи заявки в администраторы
    Принимает Имя, Ник и chatid тележки.'''
    database = sqlite3.connect('telegram.db')
    count_ta = database.cursor()
    cursor = database.cursor()

    count_ta.execute(f"SELECT COUNT(*) AS `COUNT` FROM adminTemp WHERE `chatid` = {chatid}")
    count_ta = count_ta.fetchall()
    for count in count_ta:
        if count[0] > 0:
            bot.send_message(chatid, 'Вы уже подавали заявку ранее. Пожалуйста ожидайте.')
        else:
            cursor.execute(f'INSERT INTO adminTemp ("name", "nickname", "chatid") VALUES ("{name}", "{nick}", {chatid})')
            database.commit()
            bot.send_message(chatid, 'Заявка подана. Пожалуйста ожидайте.')
    database.close()

def allAdmins() -> None:
    '''Функция переписывает массив с chatid администраторов бота для дальнейшей идентификации'''
    database = sqlite3.connect('telegram.db')
    cursor = database.cursor()
    cursor.execute("SELECT * from admins")
    rows = cursor.fetchall()
    for row in rows:
        admins.append(row[3])
    database.close()

def TempAdminList(chatid) -> None:
    '''Функция выбирает всех админов из темпа и выводит список для решения'''
    buttons = []
    tempAdmin = ''
    database = sqlite3.connect('telegram.db')
    cursor = database.cursor()
    cursor.execute("SELECT * FROM adminTemp")
    rows = cursor.fetchall()
    for row in rows:
        tempAdmin += f'{row[0]}: {row[1]} ({row[2]}) TelegramID: {row[3]}\n'
        buttons.append(telebot.types.InlineKeyboardButton(text=f'✅ Принять {row[1]}', callback_data=f'NEWADMINS:yes:{row[0]}:{row[3]}'))
        buttons.append(telebot.types.InlineKeyboardButton(text=f'🚫 Отклонить {row[1]}', callback_data=f'NEWADMINS:no:{row[0]}:{row[3]}'))

    buttons.append(telebot.types.InlineKeyboardButton(text=f'Скрыть клавиатуру', callback_data=f'NEWADMINS:hide:key:board'))
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*list(buttons))
    bot.send_message(chatid, f'Список заявок в администраторы:\n{tempAdmin}', reply_markup=keyboard)


def AdminAllow(id, chatid) -> None:
    '''Функция одобрения нового администратора'''
    database = sqlite3.connect('telegram.db')
    add_admin = database.cursor()
    del_admin = database.cursor()
    cursor = database.cursor()
    
    cursor.execute(f'SELECT * FROM adminTemp WHERE id = {id}')
    row = cursor.fetchone()
    add_admin.execute(f'INSERT INTO admins ("name", "nickname", "chatid") VALUES ("{row[1]}", "{row[2]}", "{row[3]}")')
    del_admin.execute(f'DELETE FROM adminTemp WHERE  id={id}')
    database.commit()

    bot.send_message(chatid, 'Вам было одобрено стать администратором системы!')

    allAdmins()

def AdminDeny(id, chatid) -> None:
    '''Функция отказа в привелегии администратора'''
    database = sqlite3.connect('telegram.db')
    cursor = database.cursor()
    cursor.execute(f'DELETE FROM adminTemp WHERE id={id}')
    database.commit()
    database.close()
    bot.send_message(chatid, 'Вам не было одобрено стать администратором системы!')

def DestroyKeyboard(chatid, client):
    '''Функция выводит сообщение перед устранением клиентской машины'''
    buttons = []

    buttons.append(telebot.types.InlineKeyboardButton(text=f'Да', callback_data=f'DESTROY:yes:{client}'))
    buttons.append(telebot.types.InlineKeyboardButton(text=f'Нет', callback_data=f'DESTROY:no:{client}'))
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*list(buttons))

    bot.send_message(chatid, f'Вы уверены что хотите уничтожить {client}?', reply_markup=keyboard)

def Destroy(client):
    '''Функция отправляет на сервер команду на ликвидацию клиента'''
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.connect((server_IP, server_PORT))

        start_message = 'name:telebot;'
        destroy_message = f'telebotdestroy:{client};'
        server.send(f'{start_message}{destroy_message}'.encode())
    except Exception as e:
        print(e)

def WhoOnLine(chatid):
    '''Отправляет на сервер запрос и получает ответ со списком клиентов в сети'''
    onlines = ''

    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.connect((server_IP, server_PORT))

        start_message = 'name:telebot;'
        wol_message = 'wol:telebot;'        # wol - who online
        server.send(f'{start_message}{wol_message}'.encode())

        data = server.recv(2**20).decode();
        data = data.split(';')

        for d in data:
            da = d.split(':')
            if da[0] == 'telebot' or da[0] == 'checking':
                clients = da[1].split(',')
                
                buttons = []
                for client in clients:
                    if client == 'telebot' or client == '':
                        continue
                    onlines = onlines + f'{client}\n'
                    button = telebot.types.InlineKeyboardButton(text=f'Уничтожить {client}', callback_data=f'DANGER:{client}')
                    buttons.append(button)

                button = telebot.types.InlineKeyboardButton(text='Скрыть клавиатуру', callback_data='DANGER:hidekeyboard')
                buttons.append(button)
                keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
                keyboard.add(*list(buttons))

        bot.send_message(chatid, f'Список клиентов в сети:\n{onlines}', reply_markup=keyboard)


    except Exception as e:
        print(e)
        bot.send_message(chatid, 'Сервер недоступен!')

allAdmins() 

@bot.message_handler(commands=['start', 'opme', 'list', 'temps'])
def handle_command(message):
    text = message.text

    # Команды которые могут выполнить все
    if('/opme' in text):
        if(message.chat.id in admins):
            bot.send_message(message.chat.id, 'Вы уже являетесь администратором!')
        else:
            newAdmin(message.from_user.first_name, message.from_user.username, message. chat.id)

    # Только авторизованные
    if (message.chat.id in admins):
        if('/start' in text):
            bot.send_message(message.chat.id, ':)')

        if('/list' in text):
            WhoOnLine(message.chat.id)

        if('/temps' in text):
            TempAdminList(message.chat.id)
    else:
        # Команды которые могут выполнить только не авторизованные
        pass

# Клавиатура списка клиентов
@bot.callback_query_handler(func=lambda call: call.data.startswith('DANGER:'))
def on_danger_button_clicked(call):
    client = call.data.split(':')[1] # получаем имя клиента из callback_data
    chatid = call.message.chat.id

    # Скрыть клавиатуру
    if client == 'hidekeyboard':
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    else:
        DestroyKeyboard(chatid, client)

@bot.callback_query_handler(func=lambda call: call.data.startswith('DESTROY:'))
def on_danger_button_clicked(call):
    choice = call.data.split(':')[1] # получаем выбор из callback_data
    client = call.data.split(':')[2] # получаем имя клиента из callback_data

    if(choice == 'yes'):
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"{client} уничтожен!")
        Destroy(client)
    if(choice == 'no'):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('NEWADMINS:'))
def on_danger_button_clicked(call):
    choice = call.data.split(':')[1] # получаем выбор из callback_data
    user_id = call.data.split(':')[2] # получаем id A_I клиента из callback_data
    chat_id = call.data.split(':')[3] # получаем chaid клиента из callback_data

    if(choice == 'yes'):
        AdminAllow(user_id, chat_id)
    if(choice == 'no'):
        AdminDeny(user_id, chat_id)
    if(choice == 'hide'):
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

bot.polling()