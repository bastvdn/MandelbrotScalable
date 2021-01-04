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
import sys

from py2 import maxiter

xmin, xmax = -2.0, 0.5  # x range
ymin, ymax = -1.25, 1.25  # y range
nx, ny = 4000, 4000  # resolution
all_connections = []
all_adresses = []
all_power = []
connectionPhase = True
allReceived = False

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
        relativeSize = power / powerSum
        part = relativeSize * totalSize
        x = lastTrack
        y = int(lastTrack + part)
        lastTrack = y
        powerList.append([x, y])

    powerList[-1][1] = totalSize

    return powerList

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

            data = b""
            bufferSize= 1048576

            while receptionActive:
                #print("received on : {}".format(self.nb))
                lineP = self.csocket.recv(bufferSize)
                #print(len(lineP))
                data += lineP



                if lineP == b'':
                    print("all data received")
                    break


            data_arr = pickle.loads(data)
            self.im = data_arr



def show_server_list():

    return '\n'.join([colored(
        'serveur {} addresse: {} port :{} puissance :{}'.format(i, elem[0], str(elem[1]),
                                                                str(all_power[i])), all_color[i%len(all_color)],
        attrs=['reverse']) for i, elem in enumerate(all_adresses)])

def check_data_received():
    allEnd = True

    for client in all_connections:
        if len(client.im) == 0:
            allEnd = False
    return allEnd


def show_power_repartition():
    powerSum = sum(all_power)

    return ''.join([colored("█" * int((power / powerSum) * 60), all_color[i%len(all_color)])
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

    data = array([[0 for n in range(nx)]])

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

def test_send():

    c, addr = s.accept()
    time.sleep(0.5)
    c.send(b'hello')

    buff = 4096
    print("buffer size : {}".format(buff))
    data0 = b""
    while True:
        lineP = c.recv(buff)
        print('data size {}'.format(sys.getsizeof(lineP)))
        lineP2 = c.recv(buff)
        print('data2 size {}'.format(sys.getsizeof(lineP2)))
        data0 += lineP

        if len(lineP) < 1000:
            break



    print('total data size {}'.format(sys.getsizeof(data0)))
    data_arr = pickle.loads(lineP)
    print(len(data_arr))
    print("all data received")
    sys.exit()
    #print(data_arr)
    c.recv(4096)
    c.recv(4096)
    sys.exit()





if __name__ == '__main__':
    os.system('color')

    HOST = ''  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # start to listen on a separate thread

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(4)

    startTimer = time.time()

    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print("Lancement du serveur")



    try:
        while connectionPhase:

            s.listen(5)
            #test_send()
            #print("test ended")
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

        startTimer = time.time()
        send_data_repartition()


        while not check_data_received():
            time.sleep(0.01)

        print("data received in {}".format(time.time() - startTimer))

        input()

        display_img()

        s.close()
        print('end')

    except KeyboardInterrupt:
        pass

# branch
# See PyCharm help at https://www.jetbrains.com/help/pycharm/
