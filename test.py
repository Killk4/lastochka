import os

list = os.listdir('./test/')

for l in list:
    if (os.path.isdir(l)):
        continue
    else:
        print(f'{l} файл')
        print(os.path.isdir(l))