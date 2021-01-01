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


def show_server_list():
    powerString = "█"
    fullString = ""
    i = 0
    while i < len(all_adresses):

        fullString += colored('serveur {} addresse: {} port :{}'.format(i,all_adresses[i][0],str(all_adresses[i][1])),all_color[i], attrs=['reverse'])  + '\n'
        i += 1
    return fullString

def threaded(c):

    # data received from client
    print('waiting')
    c.send(str.encode('Server is working:'))
    while True:
        data = c.recv(1024)
        if not data:
            print('Bye')

            # lock released on exit
            print_lock.release()
            break
        resp = 'Server message: ' + data.decode('utf-8')
        print('response :' + resp)
        c.sendall(str.encode(resp))

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


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((HOST, PORT))
    except socket.error as e:
        print(str(e))
    print("Lancement du serveur")
    s.listen(5)

    while True:
        # establish connection with client
        print("waiting for new")
        c, addr = s.accept()

        # lock acquired by client
        print_lock.acquire()
        print('Connected to :', addr[0], ':', addr[1])
        start_new_thread(threaded, (c,))



        # Start a new thread and return its identifier


    s.close()



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
