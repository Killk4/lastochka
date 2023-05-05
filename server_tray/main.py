import sys
import socket
import configparser
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer

class SystemTrayIcon(QtWidgets.QSystemTrayIcon):
    def __init__(self, icon, parent=None) -> None:
        QtWidgets.QSystemTrayIcon.__init__(self, icon, parent)
        self.setToolTip(f'Проверка доступности сервера Lastochka')
        menu = QtWidgets.QMenu(parent)
        exitAction = menu.addAction("Закрыть")
        exitAction.triggered.connect(lambda: sys.exit())
        self.setContextMenu(menu)

    def check_connection(self, adres:str, port:int) -> None:
        try:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            server.connect((adres, port))
            self.setIcon(QIcon("online.ico"))

            start_message = 'name:checking;'
            server.send(start_message.encode())
        except:
            self.setIcon(QIcon("offline.ico"))

def main(adres:str, port:int) -> None:
    app = QtWidgets.QApplication(sys.argv)
    w = SystemTrayIcon(QIcon("offline.ico"))
    w.show()
    timer = QTimer()
    timer.timeout.connect(lambda: w.check_connection(adres, port))
    timer.start(10000)
    sys.exit(app.exec_())


if __name__ == '__main__':
    config = configparser.ConfigParser()
    config.read('config.ini')

    try:
        if(config['CONFIG']):
            pass
    except:
        config['CONFIG'] = {
            'server_ip' : '83.169.242.38',
            'server_port' : 49999
        }

        with open('config.ini', 'w') as configfile:
            config.write(configfile)

    ip = config['CONFIG']['server_ip']
    port = int(config['CONFIG']['server_port'])
    main(ip, port)