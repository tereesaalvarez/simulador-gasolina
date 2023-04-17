import threading
import random
import time

class Coche:
    def __init__(self, id):
        self.id = id
    
    def __str__(self):
        return f"Coche {self.id}"

class Gasolinera:
    def __init__(self):
        self.surtidor_disponible = True
        self.cola_espera = []
        self.caja_disponible = True
        
    def asignar_surtidor(self, coche):
        print(f"{coche} llega a la gasolinera")
        with threading.Lock():
            if self.surtidor_disponible:
                self.surtidor_disponible = False
                tiempo_repostaje = random.randint(5, 10)
                print(f"{coche} empieza a repostar durante {tiempo_repostaje} minutos")
                time.sleep(tiempo_repostaje)
                print(f"{coche} ha acabado de repostar")
                self.surtidor_disponible = True
                self.asignar_caja(coche)
            else:
                self.cola_espera.append(coche)
                print(f"{coche} se une a la cola de espera")
    
    def asignar_caja(self, coche):
        print(f"{coche} se dirige a la caja para pagar")
        with threading.Lock():
            while not self.caja_disponible:
                time.sleep(1)
            self.caja_disponible = False
            print(f"{coche} empieza a pagar durante 3 minutos")
            time.sleep(3)
            print(f"{coche} ha acabado de pagar y se va de la gasolinera")
            self.caja_disponible = True
            if self.cola_espera:
                siguiente_coche = self.cola_espera.pop(0)
                self.asignar_surtidor(siguiente_coche)

def simular_gasolinera(num_coches):
    gasolinera = Gasolinera()
    coches = [Coche(i) for i in range(num_coches)]
    threads = []
    
    for coche in coches:
        thread = threading.Thread(target=gasolinera.asignar_surtidor, args=(coche,))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()

simular_gasolinera(50)