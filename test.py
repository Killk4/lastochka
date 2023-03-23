import os

path = './test/'
list = os.listdir(path)
list_dir = []

def isFile(root_path):
    root_list = os.listdir(root_path)

    for rl in root_list:
        if (os.path.isdir(root_path+rl)):
            isFile(root_path+rl)
        else:
            print(f'{root_path}/{rl} файл')
            os.remove(root_path+'/'+rl)

isFile(path)