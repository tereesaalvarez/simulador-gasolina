from simulador import *

def main():
    # Crear los coches
    for i in range(1, coches + 1):
        tipo = random.choice(["gasolina", "diesel", "gasoil"])
        litros = random.randint(1, 20)
        coche = Coche()
        coche.start()
        time.sleep(0.1)

    # Repostar los coches
    while repostados < coches:
        surtidor.acquire()
        cola.acquire()
        for coche in threading.enumerate():
            if coche.name != "MainThread":
                if not coche.repostado:
                    coche.repostar()
                    break
        cola.release()
        surtidor.release()



    

