import socket
import time
from numpy           import linspace, reshape
from matplotlib      import pyplot
from multiprocessing import Pool
import pickle

maxiter = 20


def get_power():
    return "10"



def mandelbrot(z):
    c=z
    global maxiter
    for n in range(maxiter):
        if abs(z)>2:
            return n
        z=z*z+c
    return maxiter

def mandel(xmin, xmax, ymin, ymax, nx, ny, maxiter, part):
    X = linspace(xmin, xmax, nx)  # lists of x and y
    Y = linspace(ymin, ymax, ny)  # pixel co-ordinates

    Yloc = Y[part[0]:part[1]+1]

    # main loops
    p = Pool()
    Z = [complex(x, y) for y in Yloc for x in X]
    N = p.map(mandelbrot, Z)

    N = reshape(N, (len(Yloc), nx))  # change to rectangular array

    return N

def sendData(mandelList, range):
    i= 0
    rangeTot = range[1]-range[0]
    for line in mandelList:
        if i == rangeTot-1:
            print(i)
            linePickle = pickle.dumps([])
            s.send(linePickle)
            break
        linePickle = pickle.dumps(line)
        s.send(linePickle)
        time.sleep(0.01)
        i+=1


if __name__ == '__main__':
    # Programme : mandelbrot.py
    # Langage : Python 3.6 - Pygame 1.9
    # Auteur : Mathieu
    # Description : Calcule et affiche la fractale de Mandelbrot en noir et blanc

    #mand = mandel(-2.0, 0.5,-1.25, 1.25,1000, 1000,20,[600,1000])
    #sendData(mand)


    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    message = get_power()

    res = s.recv(1024)
    print(res.decode('utf-8'))

    s.send(str.encode(get_power()))
    
    print("waiting for dimensions")
    res = s.recv(1024)
    lst = pickle.loads(res)
    
    range = lst[0]
    nx,ny = lst[1]
    xmin, xmax = lst[2]
    ymin, ymax = lst[3]
    maxiter = lst[4]

    mandelList = mandel(xmin,xmax,ymin,ymax,nx,ny,maxiter,range)

    print("sending data")
    sendData(mandelList,range)










    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        s.sendall(b'Hello, world')
        data = s.recv(1024)
    """

