from simulador import *

def main():
    # Crear los coches
    for i in range(1, coches + 1):
        tipo = random.choice(["gasolina", "diesel", "gasoil"])
        litros = random.randint(1, 20)
        coche = Coche(tipo, litros)
        coche.start()
        time.sleep(0.1)

    # Repostar los coches
    while repostados < coches:
        surtidor.acquire()
        surtidor.notify()
        surtidor.release()
        time.sleep(0.1)

    # Pagar los coches
    while pagados < coches:
        caja.acquire()
        caja.notify()
        caja.release()
        time.sleep(0.1)

