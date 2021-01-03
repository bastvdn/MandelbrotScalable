import socket
import time
from numpy import linspace, reshape
from multiprocessing import Pool
import pickle
import sys
from psutil import cpu_count, cpu_freq

maxiter = 30

def get_power():
    ratio = 1

    if len(sys.argv) > 1:
        ratio = int(sys.argv[1])/100

    cpu_frequency = cpu_freq()

    return int(cpu_count() * ratio * cpu_frequency.max/1000)


def mandelbrot(z):
    c = z
    global maxiter
    for n in range(maxiter):
        if abs(z) > 2:
            return n
        z = z * z + c
    return maxiter


def mandel(xmin, xmax, ymin, ymax, nx, ny, part):
    start = time.time()
    X = linspace(xmin, xmax, nx)  # lists of x and y
    Y = linspace(ymin, ymax, ny)  # pixel co-ordinates
    Yloc = Y[part[0]:part[1] + 1]

    # main loops
    p = Pool()
    Z = [complex(x, y) for y in Yloc for x in X]
    N = p.map(mandelbrot, Z)

    N = reshape(N, (len(Yloc), nx))  # change to rectangular array
    print("Mandelbrot generation " + str(part[0]) + "to" + str(part[1]))
    print(time.time()-start)
    return N

def sendData(mandelList):
    start = time.time()
    file = pickle.dumps(mandelList)
    print('data size : {}'.format(sys.getsizeof(file)))
    s.send(file)
    print("Data sent ")
    print(time.time() - start)

def test_send():
    dat = [1 for n in range(1000)]
    file = pickle.dumps(dat)
    print('array lenght : {}'.format(len(dat)))
    print('data size : {}'.format(sys.getsizeof(file)))
    s.send(file)
    print('sent')
    try:
        time.sleep(100)
    except:
        pass
    sys.exit()
    s.close()

if __name__ == '__main__':
    # Programme : mandelbrot.py
    # Langage : Python 3.6 - Pygame 1.9
    # Auteur : Mathieu
    # Description : Calcule et affiche la fractale de Mandelbrot en noir et blanc

    # mand = mandel(-2.0, 0.5,-1.25, 1.25,1000, 1000,20,[600,1000])
    # sendData(mand)

    HOST = '127.0.0.1'  # The server's hostname or IP address
    PORT = 65432  # The port used by the server

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    message = get_power()

    res = s.recv(1024)
    print(res.decode('utf-8'))

    test_send()

    s.send(str.encode(str(get_power())))

    print("waiting for dimensions")
    res = s.recv(1024)
    lst = pickle.loads(res)

    part = lst[0]
    nx, ny = lst[1]
    xmin, xmax = lst[2]
    ymin, ymax = lst[3]
    maxiter = lst[4]
    print("Dimension received, we handle computation !")

    mandelList = mandel(xmin, xmax, ymin, ymax, nx, ny, part)
    print("sending data")
    sendData(mandelList)
