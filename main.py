import timeit
import pygame
import time
from numpy           import linspace, reshape
from matplotlib      import pyplot
from multiprocessing import Pool
import socket
from termcolor import colored
import os
from _thread import *
import threading
from pynput import keyboard

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
maxiter = 20
all_connections = []
all_adresses = []
all_power = []

all_color = ['blue','red','green','yellow']

print_lock = threading.Lock()


def mandelbrot(z):
    c=z

    for n in range(maxiter):
        if abs(z)>2:
            return n
        z=z*z+c
    return maxiter

def multi(iter = 20):

    maxiter = iter
    print(maxiter)
    time.sleep(2)
    X = linspace(xmin,xmax,nx) # lists of x and y
    Y = linspace(ymin,ymax,ny) # pixel co-ordinates

    # main loops
    p = Pool()
    Z = [complex(x,y) for y in Y for x in X]
    N = p.map(mandelbrot,Z)

    N = reshape(N, (nx,ny)) # change to rectangular array

    pyplot.imshow(N) # plot the image
    print("--- Temps de recherche : %s secondes---" % (time.time() - start_time))
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
        print('Key pressed: ' + k)

class ClientThread(threading.Thread):
    def __init__(self,clientAddress,clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.caddress = clientAddress
        print ("New connection added: ", clientAddress)
    def run(self):
        print ("Connection from : ", self.caddress)
        #self.csocket.send(bytes("Hi, This is from Server..",'utf-8'))
        msg = ''
        while True:
            data = self.csocket.recv(2048)
            msg = data.decode()
            if msg=='bye':
              break
            print ("from client", msg)
            self.csocket.send(bytes(msg,'UTF-8'))
        print ("Client at ", self.caddress , " disconnected...")

def show_server_list():
    powerString = "█"
    fullString = ""
    i = 0
    while i < len(all_adresses):

        fullString += colored('serveur {} addresse: {} port :{} puissance :{}'.format(i,all_adresses[i][0],str(all_adresses[i][1]),str(all_power[i])),all_color[i], attrs=['reverse'])  + '\n'
        i += 1
    return fullString

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
        print(show_server_list())
        res = input('waiting')
        c.sendall(str.encode(res))

    # all_power.append(data)
    # reverse the given string from client
    # print(all_power)
    # print(show_server_list())

    # send back reversed string to client

    # connection closed
    c.close()

if __name__ == '__main__':
    # Programme : mandelbrot.py
    # Langage : Python 3.6 - Pygame 1.9
    # Auteur : Mathieu
    # Description : Calcule et affiche la fractale de Mandelbrot en noir et blanc
    os.system('color')

    HOST = '0.0.0.0'  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)

    listener = keyboard.Listener(on_press=on_press)
    listener.start()  # start to listen on a separate thread

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print("Lancement du serveur")
    s.listen(5)
    try:
        while True:
            # establish connection with client

            c, addr = s.accept()

            # lock acquired by client
            # print_lock.acquire()
            print('Connected to :', addr[0], ':', addr[1])
            all_adresses.append(addr)
            start_new_thread(threaded, (c,))

            #listener.join()  # remove if main thread is polling self.keys



            # Start a new thread and return its identifier


        s.close()
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
