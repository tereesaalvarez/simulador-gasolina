import tkinter as tk
from tkinter import messagebox
import random
import time
from concurrent.futures import ThreadPoolExecutor

class Coche:
    def __init__(self, id):
        self.id = id
    
    def __str__(self):
        return f"Coche {self.id}"

class Gasolinera:
    def __init__(self, num_surtidores, tam_buffer):
        self.surtidores_disponibles = [True] * num_surtidores
        self.cola_espera = [[] for _ in range(num_surtidores)]
        self.buffer_espera = []
        self.tam_buffer = tam_buffer
        self.caja_disponible = True
        self.tiempo_repostaje_total = 0
        self.num_repostajes_total = 0
        self.executor = ThreadPoolExecutor(max_workers=num_surtidores+1)
        
    def asignar_surtidor(self, coche, callback):
        surtidor = self.obtener_surtidor()
        tiempo_repostaje = random.randint(5, 10)
        self.tiempo_repostaje_total += tiempo_repostaje
        self.num_repostajes_total += 1
        time.sleep(tiempo_repostaje)
        self.liberar_surtidor(surtidor)
        callback(coche, tiempo_repostaje)
    
    def obtener_surtidor(self):
        surtidor_libre = None
        min_cola = float("inf")
        for i in range(len(self.surtidores_disponibles)):
            if self.surtidores_disponibles[i]:
                return i
            if len(self.cola_espera[i]) < min_cola:
                surtidor_libre = i
                min_cola = len(self.cola_espera[i])
        if len(self.buffer_espera) < self.tam_buffer:
            self.buffer_espera.append(None)
            self.cola_espera[surtidor_libre].append(None)
        return surtidor_libre
    
    def liberar_surtidor(self, surtidor):
        self.surtidores_disponibles[surtidor] = True
        if self.cola_espera[surtidor]:
            coche = self.cola_espera[surtidor].pop(0)
            tiempo_repostaje = random.randint(5, 10)
            self.surtidores_disponibles[surtidor] = False
            self.executor.submit(self.asignar_surtidor, coche, self.callback_repostaje)
        elif self.buffer_espera:
            coche = self.buffer_espera.pop(0)
            surtidor = self.obtener_surtidor()
            self.surtidores_disponibles[surtidor] = False
            self.executor.submit(self.asignar_surtidor, coche, self.callback_repostaje)
    
    def asignar_caja(self, coche):
        while not self.caja_disponible:
            time.sleep(1)
        self.caja_disponible = False
        time.sleep(3)
        self.callback_pago(coche)
        self.caja_disponible = True
        
    def obtener_tiempo_repostaje_medio(self):
        return self.tiempo_repostaje_total / self.num_repostajes_total

class Vista:
    def __init__(self, root, controlador):
        self.controlador = controlador
        self.frame_coches = tk.Frame(root)
        self.frame_coches.pack(side="left")
        self.coches = []
        for i in range(50):
            coche = Coche(i+1)
            self.coches.append(coche)
            boton = tk.Button(self.frame_coches, text=f"Coche {i+1}", command=lambda c=coche: self.controlador.anadir_coche(c))
            boton.pack()
        
        self.frame_gasolinera = tk.Frame(root)
        self.frame_gasolinera.pack(side="right")
        self.surtidores = []
        for i in range(4):
            frame_surtidor = tk.Frame(self.frame_gasolinera, bd=2, relief="raised")
            frame_surtidor.pack(side="top", pady=5)
            label_surtidor = tk.Label(frame_surtidor, text=f"Surtidor {i+1}")
            label_surtidor.pack(side="top")
            label_coche = tk.Label(frame_surtidor, text="Vacío")
            label_coche.pack(side="top")
            label_tiempo = tk.Label(frame_surtidor, text="Tiempo: ---")
            label_tiempo.pack(side="top")
            self.surtidores.append((label_coche, label_tiempo))
        
        self.frame_estadisticas = tk.Frame(root)
        self.frame_estadisticas.pack(side="bottom")
        self.label_repostajes = tk.Label(self.frame_estadisticas, text="Repostajes realizados: 0")
        self.label_repostajes.pack(side="left")
        self.label_tiempo_medio = tk.Label(self.frame_estadisticas, text="Tiempo medio de repostaje: ---")
        self.label_tiempo_medio.pack(side="right")
    
    def actualizar_surtidor(self, surtidor, coche, tiempo):
        label_coche, label_tiempo = self.surtidores[surtidor]
        if coche is None:
            label_coche.config(text="Vacío")
            label_tiempo.config(text="Tiempo: ---")
        else:
            label_coche.config(text=str(coche))
            label_tiempo.config(text=f"Tiempo: {tiempo}")
    
    def actualizar_estadisticas(self, num_repostajes, tiempo_medio):
        self.label_repostajes.config(text=f"Repostajes realizados: {num_repostajes}")
        self.label_tiempo_medio.config(text=f"Tiempo medio de repostaje: {tiempo_medio:.2f} s")
    
    def mostrar_mensaje(self, mensaje):
        messagebox.showinfo("Aviso", mensaje)

class Controlador:
    def __init__(self, gasolinera, vista):
        self.gasolinera = gasolinera
        self.vista = vista
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=10)
        self.futuros = []
        self.num_repostajes = 0
        self.tiempo_medio = 0.0
    
    def anadir_coche(self, coche):
        futuro = self.executor.submit(self.gasolinera.llegada_coche, coche)
        futuro.add_done_callback(self.coche_finalizado)
        self.futuros.append(futuro)
    
    def coche_finalizado(self, futuro):
        coche, tiempo = futuro.result()
        self.vista.mostrar_mensaje(f"El coche {coche.id} ha terminado de repostar en {tiempo:.2f} s")
        surtidor = coche.surtidor
        self.vista.actualizar_surtidor(surtidor, None, None)
        self.num_repostajes += 1
        self.tiempo_medio = (self.tiempo_medio*(self.num_repostajes-1) + tiempo) / self.num_repostajes
        self.vista.actualizar_estadisticas(self.num_repostajes, self.tiempo_medio)
        siguiente = self.gasolinera.siguiente_coche(surtidor)
        if siguiente is not None:
            futuro = self.executor.submit(self.gasolinera.llegada_coche, siguiente)
            futuro.add_done_callback(self.coche_finalizado)
            self.futuros.append(futuro)
        self.futuros.remove(futuro)

if __name__ == '__main__':
    gasolinera = Gasolinera(num_surtidores=4,  tam_buffer=10)
    root = tk.Tk()
    vista = Vista(root=root)
    controlador = Controlador(gasolinera, vista)
    vista.establecer_controlador(controlador)
    vista.iniciar()