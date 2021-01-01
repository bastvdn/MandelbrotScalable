import socket
import time

def get_power():
    return "10"

if __name__ == '__main__':
    # Programme : mandelbrot.py
    # Langage : Python 3.6 - Pygame 1.9
    # Auteur : Mathieu
    # Description : Calcule et affiche la fractale de Mandelbrot en noir et blanc

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    message = get_power()

    res = s.recv(1024)
    print(res.decode('utf-8'))
    while True:
        input0 = input('msg')

        s.send(str.encode(input0))
        print("waiting resp")
        res = s.recv(1024)
        print("received resp :")
        print(res.decode('utf-8'))



    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
    """


    print('Received', repr(data))
