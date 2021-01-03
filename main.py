import time
from numpy import linspace, reshape, array, empty, concatenate
from matplotlib import pyplot
from multiprocessing import Pool
import socket
from termcolor import colored
import os
import threading
from pynput import keyboard
import pickle

xmin, xmax = -2.0, 0.5  # x range
ymin, ymax = -1.25, 1.25  # y range
nx, ny = 10000, 10000  # resolution
maxiter = 1000
all_connections = []
all_adresses = []
all_power = []
connectionPhase = True

all_color = ['blue', 'red', 'green', 'yellow']

print_lock = threading.Lock()


def mandelbrot(z):
    c = z

    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z * z + c
    return maxiter


def calculate_power_repartition():
    totalSize = ny
    powerList = []

    powerSum = sum(all_power)
    lastTrack = 0

    for power in all_power:
        relativeSize = int(power) / powerSum
        part = relativeSize * totalSize
        x = lastTrack
        y = int(lastTrack + part)
        lastTrack = y
        powerList.append([x, y])

    powerList[-1][1] = totalSize

    return powerList


def multi(iter=20):
    start = time.time()
    maxiter = iter

    X = linspace(xmin, xmax, nx)  # lists of x and y
    Y = linspace(ymin, ymax, ny)  # pixel co-ordinates

    # print(calculate_power_repartition())
    Yloc = Y[0:1000]

    # main loops
    p = Pool()
    Z = [complex(x, y) for y in Y for x in X]

    N = p.map(mandelbrot, Z)

    N = reshape(N, (len(Yloc), ny))  # change to rectangular array

    print("Mandelbrot generation ")
    print(time.time() - start)

    pyplot.imshow(N)  # plot the image

    pyplot.show()


def on_press(key):
    if key == keyboard.Key.esc:
        return False  # stop listener
    try:
        k = key.char  # single-char keys
    except:
        k = key.name  # other keys
    if k in ['1', '2', 'left', 'right']:  # keys of interest
        # self.keys.append(k)  # store it in global-like variable
        print('connection phase ended')
        global connectionPhase
        connectionPhase = False
        return False


class ClientThread(threading.Thread):
    nb = 0
    img = empty((nx, ny))

    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.caddress = clientAddress
        self.nb = ClientThread.nb
        self.pic = b""
        self.im = []
        ClientThread.nb += 1
        print("New connection added: ", clientAddress, str(self.nb))

    def run(self):
        time.sleep(0.1)
        self.csocket.send(str.encode('Server is working:' + str(self.nb)))
        while True:
            power = self.csocket.recv(8192)
            if not power:
                print('Bye')
                break

            all_adresses.append(addr)
            all_power.append(int(power))
            receptionActive = True
            data = []
            data0 = b""
            while receptionActive:
                lineP = self.csocket.recv(16384)
                data.append(lineP)
                data0 += lineP
                if self.nb == 1:
                    print("-------------------data2-----------")

                    print(len(lineP))
                if self.nb == 0:
                    print("-------------------data1-----------")
                    print(len(lineP))

                if len(lineP) < 16384:
                    break

            # data = pickle.loads(b"".join(data))
            # self.pic = data
            data_arr = pickle.loads(data0)
            data = pickle.loads(b"".join(data))
            self.im = data_arr
            print("all data received")


def show_server_list():
    fullString = ""
    i = 0
    while i < len(all_adresses):
        fullString += colored(
            'serveur {} addresse: {} port :{} puissance :{}'.format(i, all_adresses[i][0], str(all_adresses[i][1]),
                                                                    str(all_power[i])), all_color[i],
            attrs=['reverse']) + '\n'
        i += 1
    return fullString


def show_power_repartition():
    powerSum = sum(all_power)

    return ''.join([colored("█" * int((int(power) / powerSum) * 60), all_color[i])
                    for i, power in enumerate(all_power)])


def send_data_repartition():
    lst = calculate_power_repartition()

    for i, client in enumerate(all_connections):
        data = pickle.dumps([lst[i], [nx, ny], [xmin, xmax], [ymin, ymax], maxiter])
        # client.csocket.send(data)
        client.csocket.send(data)

    return 0


def display_img():
    start = time.time()
    pic = b""

    data = array([[0 for n in range(1000)]])

    for i, client in enumerate(all_connections):
        if client.nb == i:
            pic += client.pic

        pyplot.imshow(all_connections[i].im)  # plot the image

        pyplot.show()
        data = concatenate((data, all_connections[i].im), axis=0)

    pyplot.imshow(data)  # plot the image

    pyplot.show()
    print("displaying img ")
    print(time.time() - start)


if __name__ == '__main__':
    # Programme : mandelbrot.py
    # Langage : Python 3.6 - Pygame 1.9
    # Auteur : Mathieu
    # Description : Calcule et affiche la fractale de Mandelbrot en noir et blanc
    os.system('color')

    # multi()

    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # start to listen on a separate thread

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)

    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print("Lancement du serveur")

    try:
        while connectionPhase:
            s.listen(5)
            # establish connection with client

            os.system('cls')
            print("Waiting for connections")
            print(show_server_list())
            print('{: ^60}'.format("↓↓work charges repartition↓↓"))
            print(show_power_repartition())
            try:
                c, addr = s.accept()

                newThread = ClientThread(addr, c)
                newThread.start()
                all_connections.append(newThread)
                print('Connected to :', addr[0], ':', addr[1])

            except socket.timeout as e:
                if not connectionPhase:
                    break
                else:
                    pass
            # Start a new thread and return its identifier

        input("sending data repartition ?")
        send_data_repartition()

        input()

        display_img()

        s.close()
        print('end')

    except KeyboardInterrupt:
        pass

# branch
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
