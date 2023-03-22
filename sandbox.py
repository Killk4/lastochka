'''Пока что лючший шредер из найденных
Надо разобрать код и внедрить в существующий
https://github.com/alec-jensen/file-shredder
Было заменено sys.argv[1] на статичное имя файла'''


import os
from termcolor import colored
import colorama

colorama.init() # Инициализация colorama для работы с цветным текстом в консоли
success = True # Глобальная переменная для отслеживания успешности выполнения операций


def secure_delete(path, passes=5):
    global success # Использование глобальной переменной success
    with open(path, "ba+") as delfile:
        length = delfile.tell() # Определение размера файла
    with open(path, "br+") as delfile:
        for i in range(passes): # Перезапись содержимого файла случайными данными passes раз
            try:
                delfile.seek(0) # Перемещение указателя в начало файла
                delfile.write(os.urandom(length)) # Запись случайных данных в файл
                print(colored(f'ПРОХОД {i + 1} УСПЕШНО', 'green')) # Вывод сообщения об успешном прохождении итерации
            except: # Обработка исключений при записи в файл
                print(colored(f'ПРОХОД {i + 1} НЕУДАЧНО', 'red')) # Вывод сообщения об ошибке при прохождении итерации
                success = False # Установка значения success в False при ошибке записи в файл
    try:
        os.remove(path) # Удаление файла после перезаписи его содержимого случайными данными passes раз.
        print(colored('ФАЙЛ УСПЕШНО УДАЛЕН.', 'green')) # Вывод сообщения об успешном удалении файла.
    except: # Обработка исключений при удалении файла.
        print(colored('ОШИБКА УДАЛЕНИЯ ФАЙЛА. ФАЙЛ МОЖЕТ БЫТЬ УНИЧТОЖЕН.', 'red')) 
        success = False


file = './vid.mp4' 

print(colored('ВЫ УВЕРЕНЫ ЧТО ХОТИТЕ ПРОДОЛЖИТЬ С УНИЧТОЖЕНИЕМ ФАЙЛА? Y/N', 'yellow'))
check = bool(input()) 

if check: 
    print(colored('УНИЧТОЖЕНИЕ ФАЙЛА', 'yellow'))
    secure_delete(file) 
    if success: 
        print(colored('УСПЕСНО ЗАВЕРШЕН. Нажмите любую клавишу чтобы продолжить.', 'green'))
        input()
    else:
        print(colored('Неудача одного или нескольких элементов. Пожалуйста попробуйте еще раз.', 'red'))
        input()