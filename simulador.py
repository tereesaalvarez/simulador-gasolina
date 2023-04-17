import threading
import time
import random

# Definición de variables globales
# Número de surtidores
surtidores = 1
# Número de cajas
cajas = 1
# Número de coches
coches = 50
# Número de coches repostados
repostados = 0
# Número de coches pagados
pagados = 0

# Definición de semáforos
# Semáforo para controlar el acceso a los surtidores
semSurtidores = threading.Semaphore(surtidores)
# Semáforo para controlar el acceso a las cajas
semCajas = threading.Semaphore(cajas)
# Semáforo para controlar el acceso a la cola de espera
semCola = threading.Semaphore(1)

# Definición de variables de condición
# Variable de condición para controlar la cola de espera
cola = threading.Condition(semCola)
# Variable de condición para controlar los surtidores
surtidor = threading.Condition(semSurtidores)
# Variable de condición para controlar las cajas
caja = threading.Condition(semCajas)

# Definición de la clase coche
class Coche(threading.Thread):
    def __init__(self, tipo, litros):
        threading.Thread.__init__(self)
        self.repostado = False
        self.pagado = False

    def run(self):
        global repostados
        global pagados
        # Añadir el coche a la cola de espera
        cola.acquire()
        print("El coche se ha unido a la cola de espera" % (self.name))
        cola.notify()
        cola.release()
        # Esperar a que se le atienda
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
        print("El coche %s está repostando" % (self.name))
        time.sleep(random.randint(5, 10))
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

    


