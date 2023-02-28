class Com:
    def __init__(self, client, command):
        self.cl = client
        self.cm = command

command_list = []

while True:
    com = input('> ')

    if com[0] == '/':
        if com[1:] == 'help':
            print('/destroy [name] - запустить процедуру удаления файлов\n'+
                  '/status - список клиентов в сети\n'+
                  '/status [name] - проверить статус клиента по имени')
        else:
            com = com[1:].split(' ')
            
            if com[0] == 'destroy':
                try:
                    print('На компьютер ' + str(com[1] + ' отправлена команда на удаление файлов'))
                except:
                    print('Неправильно указана команда. /help для списка всех команд')