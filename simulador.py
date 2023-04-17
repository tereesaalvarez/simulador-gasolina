import threading
import time
import random

surtidores = 1
cajas = 1
coches = 50
repostados = 0
pagados = 0
semSurtidores = threading.Semaphore(surtidores)
semCajas = threading.Semaphore(cajas)
semCola = threading.Semaphore(1)
cola = threading.Condition(semCola)
surtidor = threading.Condition(semSurtidores)
caja = threading.Condition(semCajas)

# Definición de la clase coche
class Coche(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.repostado = False
        self.pagado = False

    def run(self):
        global repostados
        global pagados
        # Añadir el coche a la cola de espera
        cola.acquire()
        print("El coche %s se ha unido a la cola de espera" % (self.name))
        cola.notify()
        cola.release()
        # Esperar a que reposte
        cola.acquire()
        while not self.repostado:
            cola.wait()
        print("El coche %s ha terminado de repostar" % (self.name))
        cola.release()
        # Esperar a que se le atienda en la caja
        caja.acquire()
        while not self.pagado:
            caja.wait()
        print("El coche %s ha terminado de pagar" % (self.name))
        caja.release()
        # Aumentar el número de coches repostados
        repostados += 1
        # Aumentar el número de coches pagados
        pagados += 1
    
    def repostar(self):
        # Repostar el coche
        tiempo =time.sleep(random.randint(5, 10))
        print("El coche %s está repostando" % (self.name))
        self.repostado = True
        # Avisar a la cola de espera
        cola.acquire()
        cola.notify()
        cola.release()

    def pagar(self):
        # Pagar el coche
        print("El coche %s está pagando" % (self.name))
        time.sleep(3)
        self.pagado = True
        # Avisar a la cola de espera
        caja.acquire()
        caja.notify()
        caja.release()

    


