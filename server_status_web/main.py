from flask import Flask, render_template
import socket

app = Flask(__name__)

@app.route('/')
def index():
    server_IP = '10.0.20.200'
    server_PORT = 49999
    server_name = 'Lastochka server'
    server_status = check_server(server_IP, server_PORT)
    return render_template('index.html', server_name=server_name, server_status=server_status)

def check_server(adres:str, port:int) -> bool:
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        server.connect((adres, port))

        return True
    except:
        return False

if __name__ == '__main__':
    app.run()