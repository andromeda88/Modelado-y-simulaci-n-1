# -*- coding: utf-8 -*-
"""
Created on Sat Feb  8 15:57:07 2020

@author: Luz
"""

""" Llamado de los modulos necesarios
        sys: que permite la lectura y escritura de los archivos de entrada y salida
        random: que permite utilizar numeros aleatorios
        collections: permite el uso de contenedores de datos, en este caso de tipo tupla
        datetime: permite trabajar con tiempo, fechas y horas
        sortedcontainers: permite el uso de contenedores que almacenan de forma ordenada
        en este caso de tipo lista
"""

import sys
import random
from collections import namedtuple 
from datetime import datetime
from sortedcontainers import SortedKeyList

""" Crea una tupla, que contiene dos campos uno llamado evento
    y el otro con los atributos del evento:
    Tiempo en que ocurre el evento (llegada a la red)
    Identificacion del nodo
    Tipo de nodo
"""

Evento = namedtuple("Evento", ["tiempo", "nodo", "tipo"])

""" Creacion de la clase nodo que representa los puntos de servicio de la red
    Definicion e iniciacion de sus atributos
    
    Atrbutos:
        tipo_n: es un string que indica el tipo de nodo, si es de "llegada" u "otro"
        t_llegadas: tiempo promedio entre llegadas
        t_servicio: tiempo promedio de servicio
        capacidad: cantidad que indica la capacidad de atencion en el nodo
        i_suc: es un vector de enteros que almacena los sucesores del nodo
        prob_suc: es un vector de reales que contiene la probabilidad de cada sucesor
        t_total_esp: indica el tiempo total de espera
        t_even_prev: indica el timepo del evento anterior
        llegaron: cantidad de personas que llegaron a la red
        cola: indica la cantidad de personas en la cola
        t_vacio: muestra el tiempo que estuvo sin personas el nodo
        cola_max: muestra la cantidad maxima de personas que estuvo en la cola del nodo
        servidos: cantidad de personas que fueron atendidas en el nodo
        util_pond: uso ponderado del nodo
        utilizacion: uso del nodo 
"""
class Nodo:
    def __init__(
        self, tipo_n, t_llegadas, t_servicio, capacidad, suc, prob_suc
    ):
        self.tipo_n = tipo_n
        self.t_llegadas = float(t_llegadas)
        self.t_servicio = float(t_servicio)
        self.capacidad = int(capacidad)
        self.i_suc = [int(s) for s in suc]
        self.prob_suc = [float(ps) for ps in prob_suc]
        self.t_total_esp = 0
        self.t_even_prev = 0
        self.llegaron = 0
        self.cola = 0
        self.t_vacio = 0
        self.cola_max = 0
        self.servidos = 0
        self.util_pond = 0
        self.utilizacion = 0
        self.cola_ini = 0

""" Implementacion de la clase red
    Definicion e iniciacion de sus atributos y metodos
"""

class Red:
    """ Constructor de red, compuesto por la cantidad de nodos que estan en la red
    """
    def __init__(self, nodos):
        self.nodos = nodos
        for nodo in self.nodos:
            nodo.suc = [nodos[i - 1] for i in nodo.i_suc]
    """ Funcion que escribe las estadisticas de servicio de cada uno de los nodos en un archivo
        Primero abre el archivo
        Identifica el nodo, si es un nodo de tipo llegada externas:
        Especifica el tiempo entre llegadas al servicio
        Especifica el tiempo de servicio
        Capacidad de servicio
        Cantidad de nodos sucesores
        Si es un nodo de tipo otro:
        Especifica el tiempo de servicio
        Capacidad de servicio
        Cantidad de nodos sucesores
        Recibe como parametros al nodo y el nombre del archivo de salida
    """
    def imprime_red(self, a_salida=sys.stdout):
        if type(a_salida) == str:
            f = open(a_salida, "w+")
        else:
            f = a_salida
        for i, nodo in enumerate(self.nodos):
            f.write(f"Nodo: {i+1:2d}    Tipo: {nodo.tipo_n.title()}\n")
            if nodo.tipo_n == "llegada":
                f.write(f"T_E_llegadas: {nodo.t_llegadas:.2f}    ")
            f.write(
                f"T_Servicio: {nodo.t_servicio:.2f}    Capacidad: {nodo.capacidad:2d}\n"
            )
            if nodo.suc:
                l_suc = [
                    f"{i_suc} ({prob_suc})"
                    for i_suc, prob_suc in zip(nodo.i_suc, nodo.prob_suc)
                ]
                suc = "    ".join(l_suc)
            else:
                suc = ""
            f.write(f"Sucesores: {suc}\n\n")
        if type(a_salida) == str:
            f.close()
            
    """ Funcion que escribe en un archivo las estadisticas del servicio en la red:
            Cantidad de usuarios que llegaron al sistema
            Cantidad de usuarios que fueron atendidos
            Cantidad de usuarios que quedaron siendo atendidos cuando terminó el tiempo de simulación
            Cantidad de usuarios que quedaron en cola cuando terminó el tiempo de simulación
            Cantidad de máxima de usuarios que estuvieron en espera para ser atendidos
            Tiempo promedio de espera para ser atendidos
            Cantidad promedio de ususarios que estuvieron en espera
            Tiempo que estuvo vacio el nodo
            Porcentaje de ocupación del nodo
            Recibe como parametros el nodo, tiempo de simulacion y el nombre del archivo de salida
    """
    def imprime_salida(self, TSIM, t_dif, a_salida=sys.stdout):
        if type(a_salida) == str:
            f = open(a_salida, "a+")
        else:
            f = a_salida
        t_dif += datetime(2020, 1, 1, 0, 0, 0)
        f.write(f"Tiempo de simulacion: {TSIM:8.0f}    ")
        secs = f"{t_dif.second + t_dif.microsecond / 1e6:.2f}"  # f'{dif:%-S.%f}'[:-4]
        f.write(f"Tiempo de corrida:  {secs} s\n")
        f.write(
            "Nod Llega  Servi  EnSer LCol  LColM ColI  TProEsp LProCol  T Vacio  OcupPro\n"
        )
        f.write(
            "=== ====== ====== ===== ===== ===== ===== ======= ======= ========= =======\n"
        )
        for i, nodo in enumerate(self.nodos):
            if nodo.utilizacion == 0:
                nodo.t_vacio += TSIM - nodo.t_even_prev
            else:
                nodo.util_pond += nodo.utilizacion * (TSIM - nodo.t_even_prev)
                nodo.t_total_esp += nodo.cola * (TSIM - nodo.t_even_prev)
            f.write(
                f"{i + 1:3d} {nodo.llegaron:6d} {nodo.servidos:6d} {nodo.utilizacion:5d} "
            )
            f.write(f"{nodo.cola:5d} {nodo.cola_max:5d} {nodo.cola_ini:5d} ")
            f.write(
                f"{nodo.t_total_esp / nodo.llegaron:7.1f} {nodo.t_total_esp / TSIM:7.1f} "
            )
            f.write(f"{nodo.t_vacio:9.2f} {nodo.util_pond / TSIM:7.2f}\n")
        if type(a_salida) == str:
            f.close()
            
    """ Funcion que lee un archivo, el cual tiene las definiciones de la red:
            Tiempo de simulacion
            Tiempo de nodo, si es de llegada o de tipo otro
            Tiempo entre llegadas al nodo tipo de llegada
            Tiempo de sevicio
            Capacidad de servicio
            Cantidad de nodos sucesores
            Identificacion de los nodos sucesores
            Probabilidad acumulada de los nodos sucesores
        A medida que lee el archivo va guardando los atributos para cada nodo
        perteneciente a la red
        Recibe como parametro un archivo tipo DEF
    """
    def lee_red(a_entrada):

        with open(a_entrada) as arch_red:
            TSIM, num_cli = arch_red.readline().strip().split()[:2]
            nodos = []
            otro_nodo = arch_red.readline().strip()[:1]
            while otro_nodo:
                tipo = otro_nodo
                if tipo == "1":
                    tipo_n = "llegada"
                    t_llegadas, t_servicio, capacidad = (
                            arch_red.readline().strip().split()[:3]
                    )   
                else:
                    tipo_n = "otro"
                    t_llegadas = "0"
                    t_servicio, capacidad = arch_red.readline().strip().split()[:2]
                num_suc = int(arch_red.readline().strip()[:1])
                if num_suc != 0:
                    suc = arch_red.readline().strip().split()[:num_suc]
                    prob_suc = arch_red.readline().strip().split()[:num_suc]
                else:
                    suc = []
                    prob_suc = []
                nodo = Nodo(
                    tipo_n, t_llegadas, t_servicio, capacidad, suc, prob_suc
                )
                nodos.append(nodo)
                otro_nodo = arch_red.readline().strip()[:1]
            red = Red(nodos)
            i = 0
            num_cli = int(num_cli)
            for j in range(num_cli):
                red.nodos[i].cola += 1
                i += 1
                if i >= len(red.nodos):
                    i = 0
        return red, float(TSIM)

    """ Feuncion que se encarga de crear una lista ordenada de eventos
        Cada vez que llegue un usuario al nodo de tipo llegada, se crea un evento
        Recibe como parametro a la red y devuelve la lista de eventos
    """
    def inicia_LEP(red):
        LEP = SortedKeyList(key=lambda evento: evento.tiempo)
        for nodo in red.nodos:
            if nodo.tipo_n == "llegada":
                evento = Evento(
                        random.expovariate(1 / nodo.t_llegadas), nodo, "llegada_e"
                )
                LEP.add(evento)
        return LEP
    
    """ Programa principal que describe la simulacion de la red de servicio
        Abre el archivo que describe la red
        Lee el archivo de entrada, identifico la red y el tiempo de simulacion
        Abre el archivo de salida 
        Escribe la parte de las estadisticas en el archivo de salida
        Inicializa el tiempo simulado
        Crea la lista de eventos
    """
    if __name__ == "__main__":
        random.seed(5)
        a_entrada = sys.argv[1]
        red, TSIM = lee_red(a_entrada)
        a_salida = sys.argv[2]
        red.imprime_red(a_salida)
        t_inicial = datetime.now()
        tiempo_sim = 0
        LEP = inicia_LEP(red)
        """ Crea un bucle que se repite mientras el tiempo de simulacion sea menor
            al tiempo de la simulacion descrito por el archivo de entrada
            Saca un elemento de la lista de eventos,lee sus atributos y va guardando
            los valores para el calculo de las estadisticas
            
        """
        while tiempo_sim < TSIM:
            evento = LEP.pop(0)
            tiempo_sim = evento.tiempo
            nodo = evento.nodo
            nodo.t_total_esp += nodo.cola * (tiempo_sim - nodo.t_even_prev)
            nodo.util_pond += nodo.utilizacion * (tiempo_sim - nodo.t_even_prev)
            if evento.tipo != "salida":
                nodo.llegaron += 1
                if nodo.utilizacion == nodo.capacidad:
                    nodo.cola += 1
                    if nodo.cola > nodo.cola_max:
                        nodo.cola_max = nodo.cola
                else:
                    if nodo.utilizacion == 0:
                        nodo.t_vacio += tiempo_sim - nodo.t_even_prev
                    evento_n = Evento(
                        tiempo_sim + random.expovariate(1 / nodo.t_servicio),
                        nodo,
                        "salida",
                    )
                    LEP.add(evento_n)
                    nodo.utilizacion += 1
                if evento.tipo == "llegada_e":
                    evento_n = Evento(
                            tiempo_sim + random.expovariate(1 / nodo.t_llegadas),
                            nodo,
                            "llegada_e",
                    )
                    LEP.add(evento_n)
            else:
                if len(nodo.suc) > 0:
                    nodo_i = random.choices(nodo.suc, cum_weights=nodo.prob_suc)[0]
                    evento_n = Evento(tiempo_sim, nodo_i, "llegada_i")
                    LEP.add(evento_n)
                nodo.servidos += 1
                if nodo.cola > 0:
                    nodo.cola -= 1
                    evento_n = Evento(
                            tiempo_sim + random.expovariate(1 / nodo.t_servicio),
                            nodo,
                            "salida",
                    )
                    LEP.add(evento_n)
                else:
                    nodo.utilizacion -= 1
            nodo.t_even_prev = tiempo_sim
        """ Escribe el tiempo de simulacion, el tiempo simulado
            y las estadisticas de cada nodo en el archivo de salida 
        """
        t_final = datetime.now()
        t_dif = t_final - t_inicial
        red.imprime_salida(TSIM, t_dif, a_salida)
