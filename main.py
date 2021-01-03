import json
import timeit
import pygame
import time
from numpy           import linspace, reshape, array, empty, int8, concatenate
from matplotlib      import pyplot
from multiprocessing import Pool
import socket
from termcolor import colored
import os
from _thread import *
import threading
from pynput import keyboard
import pickle
import sys

def main(iter = 20):
    # Constantes
    MAX_ITERATION = iter  # nombre d'itérations maximales avant de considérer que la suite converge
    XMIN, XMAX, YMIN, YMAX = -2, +0.5, -1.25, +1.25  # bornes du repère
    LARGEUR, HAUTEUR = 1000, 1000  # taille de la fenêtre en pixels
    # Initialisation et création d'une fenêtre aux dimensions spécifiéés munie d'un titre
    pygame.init()
    screen = pygame.display.set_mode((LARGEUR, HAUTEUR))
    pygame.display.set_caption("Fractale de Mandelbrot")
    # Création de l'ensemble de Mandelbrot
    # Principe : on balaye l'écran pixel par pixel en convertissant le pixel en un point du plan de notre repère
    # Si la suite converge, le point appartient à l'ensemble de Mandelbrot et on colore le pixel en noir
    # Sinon la suite diverge, le point n'appartient pas à l'ensemble et on colore le pixel en blanc
    for y in range(HAUTEUR):
        for x in range(LARGEUR):
            # Les deux lignes suivantes permettent d'associer à chaque pixel de l'écran de coordonnées (x;y)
            # un point C du plan de coordonnées (cx;cy) dans le repère défini par XMIN:XMAX et YMIN:YMAX
            cx = (x * (XMAX - XMIN) / LARGEUR + XMIN)
            cy = (y * (YMIN - YMAX) / HAUTEUR + YMAX)
            xn = 0
            yn = 0
            n = 0
            while (
                    xn * xn + yn * yn) < 4 and n < MAX_ITERATION:  # on teste que le carré de la distance est inférieur à 4 -> permet d'économiser un calcul de racine carrée coûteux en terme de performances
                # Calcul des coordonnes de Mn
                tmp_x = xn
                tmp_y = yn
                xn = tmp_x * tmp_x - tmp_y * tmp_y + cx
                yn = 2 * tmp_x * tmp_y + cy
                n = n + 1
            if n == MAX_ITERATION:
                screen.set_at((x, y), (0, 0, 0))  # On colore le pixel en noir -> code RGB : (0,0,0)
            else:
                screen.set_at((x, y), (255, 255, 255))  # On colore le pixel en blanc -> code RGB : (255,255,255)
    pygame.display.flip()  # Mise à jour et rafraîchissement de la fenêtre graphique pour affichage
    print("--- Temps de recherche : %s secondes---" % (time.time() - start_time))
    # Boucle infinie permettant d'afficher à l'écran la fenêtre graphique
    # Sans ça, la fenêtre apparaît et disparaît aussitôt
    loop = True
    while loop:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Pour quitter l'application en fermant la fenêtre
                loop = False

    pygame.quit()

       # max iterations
xmin, xmax = -2.0, 0.5  # x range
ymin, ymax = -1.25, 1.25  # y range
nx, ny = 1000, 1000  # resolution
maxiter = 1000
all_connections = []
all_adresses = []
all_power = []
connectionPhase = True


all_color = ['blue','red','green','yellow']

print_lock = threading.Lock()


def mandelbrot(z):
    c=z

    for n in range(maxiter):
        if abs(z)>2:
            return n
        z=z*z+c
    return maxiter

def calculate_power_repartition():

    totalSize = ny
    powerList= []
    relativeList = []

    i = 0
    j = 0
    powerSum = 0


    while i < len(all_power):

        powerSum += int(all_power[i])
        i += 1

    lastTrack = 0

    while j < len(all_power):

        relativeSize = int(all_power[j])/powerSum
        relativeList.append(relativeSize)
        part = relativeSize*totalSize
        x=lastTrack
        y=int(lastTrack+part)
        lastTrack = y

        powerList.append([x,y])
        j += 1

    powerList[-1][1] = totalSize
    return powerList


def multi(iter = 20):
    start = time.time()
    maxiter = iter

    X = linspace(xmin,xmax,nx) # lists of x and y
    Y = linspace(ymin,ymax,ny) # pixel co-ordinates

    #print(calculate_power_repartition())
    Yloc = Y[0:1000]

    # main loops
    p = Pool()
    Z = [complex(x,y) for y in Y for x in X]




    N = p.map(mandelbrot,Z)

    N = reshape(N, (len(Yloc),ny)) # change to rectangular array

    print("Mandelbrot generation ")
    print(time.time() - start)

    pyplot.imshow(N) # plot the image

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
    img = empty((nx,ny))
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.caddress = clientAddress
        self.nb = ClientThread.nb
        self.pic = b""
        self.im = []
        ClientThread.nb += 1
        print ("New connection added: ", clientAddress , str(self.nb))
    def run(self):
        time.sleep(0.1)
        self.csocket.send(str.encode('Server is working:' + str(self.nb)))
        while True:
            power = self.csocket.recv(8192)
            if not power:
                print('Bye')
                break

            all_adresses.append(addr)
            all_power.append(power)
            receptionActive = True
            '''
            while receptionActive:
                lineP = self.csocket.recv(16384)
                
                line = pickle.loads(lineP)
                if len(line) == 0:
                    receptionActive = False
                self.part.append(line)
            '''
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

            data_arr = pickle.loads(data0)
            data = pickle.loads(b"".join(data))
            self.im = data_arr
            print("all data received")








def show_server_list():

    fullString = ""
    i = 0
    while i < len(all_adresses):
        fullString += colored('serveur {} addresse: {} port :{} puissance :{}'.format(i,all_adresses[i][0],str(all_adresses[i][1]),str(all_power[i])),all_color[i], attrs=['reverse'])  + '\n'
        i += 1
    return fullString
"""
def threaded(c):

    c.send(str.encode('Server is working:'))
    while True:
        power = c.recv(1024)
        if not power:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break

        resp = power.decode('utf-8')
        all_power.append(resp)

        res = input('waiting')
        c.sendall(str.encode(res))

    # all_power.append(data)
    # reverse the given string from client
    # print(all_power)
    # print(show_server_list())

    # send back reversed string to client

    # connection closed
    c.close()
"""





def show_power_repartition():
    powericn = "█"
    powerString = ""
    i=0
    j=0
    powerSum = 0
    while i < len(all_power):
        powerSum += int(all_power[i])
        i +=1

    while j < len(all_power):
        powerString += colored(powericn*int((int(all_power[j])/powerSum)*60),all_color[j])
        j +=1

    return powerString


def send_data_repartition():
    lst = calculate_power_repartition()
    i=0

    for client in all_connections:
        data = pickle.dumps([lst[i],[nx,ny],[xmin,xmax],[ymin,ymax],maxiter])
        #client.csocket.send(data)
        client.csocket.send(data)
        i+=1

    return 0


def display_img():
    """
    start = time.time()

    for client in all_connections:
        N = client.part

    print("displaying img ")
    print(time.time() - start)

    print(N[0])
    pyplot.imshow(N)  # plot the image

    pyplot.show()

    :return:
    """


    start = time.time()

    i = 0
    data = array([[0 for n in range(1000)]])
    for client in all_connections:
        print(i)
        if client.nb == i:
            pyplot.imshow(all_connections[i].im)  # plot the image

            pyplot.show()
            data = concatenate((data,all_connections[i].im), axis=0)

            i+=1

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

    #multi()


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




    """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind((HOST, PORT))
                print("Lancement du serveur")
                finish = False

                while not finish:

                    s.listen()
                    conn, addr = s.accept()
                    s.setblocking(True)

                    all_connections.append(conn)
                    all_adresses.append(addr)
                    powerData = conn.recv(1024)
                    os.system('cls')
                    print(show_server_list())"""






    """
        s.listen()
        conn, addr = s.accept()
        with conn:
            time.sleep(1)
            print('connection à', addr)
            start_time = time.time()
            try:

                print("Démarrage de MandelBrot")
                conn.sendall(b'ok')
                print("en attente des instruction du client")
                data = conn.recv(1024)

                print("nombre d'itérations [client]: " + str(int(data)))
                start_time = time.time()
                multi(int(data))

                print(maxiter)
                time.sleep(2)
                #conn.sendall(data)
            except KeyboardInterrupt:
                print("Key Interruption")"""






#branch


# See PyCharm help at https://www.jetbrains.com/help/pycharm/
