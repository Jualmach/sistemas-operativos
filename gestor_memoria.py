"""
gestor_memoria.py - Administrador de memoria física
Implementa asignación de memoria con mapas de bits o listas encadenadas
"""

import math
from enums import Constantes, EstrategiaMemoria, MetodoMemoria


class BloqueMB:
    """Representa un bloque de memoria física."""

    def __init__(self, numero, tamaño_kb):
        self.numero = numero
        self.tamaño_kb = tamaño_kb
        self.pid_ocupante = None
        self.es_libre = True

    def ocupar(self, pid):
        self.pid_ocupante = pid
        self.es_libre = False

    def liberar(self):
        self.pid_ocupante = None
        self.es_libre = True

    def __str__(self):
        estado = "LIBRE" if self.es_libre else f"P{self.pid_ocupante}"
        return f"B{self.numero}({estado})"


class GestorMemoria:
    """Administra la memoria física segmentada en bloques de tamaño 2^n."""

    def __init__(self,
                 memoria_total_kb=Constantes.MEMORIA_TOTAL_KB,
                 tamaño_bloque_kb=Constantes.TAMAÑO_BLOQUE_KB,
                 estrategia=EstrategiaMemoria.FIRST_FIT,
                 metodo=MetodoMemoria.MAPA_BITS):
        if not self._es_power_of_2(tamaño_bloque_kb):
            raise ValueError(f"El tamaño de bloque {tamaño_bloque_kb} no es potencia de 2")
        if memoria_total_kb % tamaño_bloque_kb != 0:
            raise ValueError("La memoria total debe ser divisible por el tamaño de bloque")

        self.memoria_total_kb = memoria_total_kb
        self.tamaño_bloque_kb = tamaño_bloque_kb
        self.estrategia = estrategia
        self.metodo = metodo
        self.num_bloques = memoria_total_kb // tamaño_bloque_kb

        self.bloques = [BloqueMB(i, tamaño_bloque_kb) for i in range(self.num_bloques)]
        self.bitmap = [True] * self.num_bloques
        self.lista_libre = [(0, self.num_bloques)]

        self.mapeo_procesos = {}

        self.fragmentacion_interna = 0.0
        self.fragmentacion_externa = 0.0
        self.desperdicio_memoria = 0
        self.asignaciones_totales = 0
        self.liberaciones_totales = 0

    @staticmethod
    def _es_power_of_2(n):
        return n > 0 and (n & (n - 1)) == 0

    def _calcular_bloques_requeridos(self, pcb):
        bloque_proceso_kb = max(pcb.get_bloque_memoria(), self.tamaño_bloque_kb)
        if bloque_proceso_kb % self.tamaño_bloque_kb != 0:
            bloque_proceso_kb = self._siguiente_potencia_de_dos(bloque_proceso_kb)
        pcb.bloque_memoria_kb = bloque_proceso_kb
        return bloque_proceso_kb // self.tamaño_bloque_kb

    def _siguiente_potencia_de_dos(self, valor):
        potencia = self.tamaño_bloque_kb
        while potencia < valor:
            potencia <<= 1
            if potencia > Constantes.BLOQUE_TAMANO_MAX_KB:
                return Constantes.BLOQUE_TAMANO_MAX_KB
        return potencia

    def asignar_memoria(self, pcb):
        bloques_necesarios = self._calcular_bloques_requeridos(pcb)
        bloques_asignados = self._buscar_bloques(bloques_necesarios)
        if bloques_asignados is None:
            return None

        for indice in bloques_asignados:
            self.bloques[indice].ocupar(pcb.pid)
            self.bitmap[indice] = False

        if self.metodo == MetodoMemoria.LISTA_ENCADENADA:
            self._remover_segmento_lista_libre(bloques_asignados)

        direccion_base = bloques_asignados[0] * self.tamaño_bloque_kb * 1024
        pcb.set_direccion_memoria(direccion_base)
        self.mapeo_procesos[pcb.pid] = {'pcb': pcb, 'bloques': bloques_asignados}
        self.asignaciones_totales += 1
        self._calcular_fragmentacion()
        return direccion_base

    def _buscar_bloques(self, cantidad):
        if self.metodo == MetodoMemoria.MAPA_BITS:
            return self._buscar_bloques_bitmap(cantidad)
        return self._buscar_bloques_lista(cantidad)

    def _buscar_bloques_bitmap(self, cantidad):
        if self.estrategia == EstrategiaMemoria.FIRST_FIT:
            return self._first_fit_bitmap(cantidad)
        if self.estrategia == EstrategiaMemoria.BEST_FIT:
            return self._best_fit_bitmap(cantidad)
        if self.estrategia == EstrategiaMemoria.WORST_FIT:
            return self._worst_fit_bitmap(cantidad)
        return None

    def _buscar_bloques_lista(self, cantidad):
        if self.estrategia == EstrategiaMemoria.FIRST_FIT:
            return self._first_fit_lista(cantidad)
        if self.estrategia == EstrategiaMemoria.BEST_FIT:
            return self._best_fit_lista(cantidad)
        if self.estrategia == EstrategiaMemoria.WORST_FIT:
            return self._worst_fit_lista(cantidad)
        return None

    def _first_fit_bitmap(self, cantidad):
        bloques = []
        for i, libre in enumerate(self.bitmap):
            if libre:
                bloques.append(i)
                if len(bloques) == cantidad:
                    return bloques
            else:
                bloques = []
        return None

    def _best_fit_bitmap(self, cantidad):
        mejor_hueco = None
        mejor_tamaño = float('inf')
        i = 0
        while i < self.num_bloques:
            if self.bitmap[i]:
                j = i
                while j < self.num_bloques and self.bitmap[j]:
                    j += 1
                tamaño_hueco = j - i
                if cantidad <= tamaño_hueco < mejor_tamaño:
                    mejor_tamaño = tamaño_hueco
                    mejor_hueco = list(range(i, i + cantidad))
                i = j
            else:
                i += 1
        return mejor_hueco

    def _worst_fit_bitmap(self, cantidad):
        peor_hueco = None
        peor_tamaño = -1
        i = 0
        while i < self.num_bloques:
            if self.bitmap[i]:
                j = i
                while j < self.num_bloques and self.bitmap[j]:
                    j += 1
                tamaño_hueco = j - i
                if tamaño_hueco >= cantidad and tamaño_hueco > peor_tamaño:
                    peor_tamaño = tamaño_hueco
                    peor_hueco = list(range(i, i + cantidad))
                i = j
            else:
                i += 1
        return peor_hueco

    def _first_fit_lista(self, cantidad):
        return self._buscar_segmento_lista(cantidad, mejor=False)

    def _best_fit_lista(self, cantidad):
        return self._buscar_segmento_lista(cantidad, mejor=True)

    def _worst_fit_lista(self, cantidad):
        return self._buscar_segmento_lista(cantidad, peor=True)

    def _buscar_segmento_lista(self, cantidad, mejor=False, peor=False):
        segmento_resultado = None
        if mejor:
            mejor_longitud = float('inf')
            for inicio, longitud in self.lista_libre:
                if longitud >= cantidad and longitud < mejor_longitud:
                    mejor_longitud = longitud
                    segmento_resultado = (inicio, cantidad)
        elif peor:
            peor_longitud = -1
            for inicio, longitud in self.lista_libre:
                if longitud >= cantidad and longitud > peor_longitud:
                    peor_longitud = longitud
                    segmento_resultado = (inicio, cantidad)
        else:
            for inicio, longitud in self.lista_libre:
                if longitud >= cantidad:
                    segmento_resultado = (inicio, cantidad)
                    break
        if segmento_resultado is None:
            return None
        inicio, longitud = segmento_resultado
        return list(range(inicio, inicio + longitud))

    def _remover_segmento_lista_libre(self, bloques_asignados):
        inicio = bloques_asignados[0]
        longitud = len(bloques_asignados)
        nueva_lista = []
        for seg_inicio, seg_longitud in self.lista_libre:
            seg_fin = seg_inicio + seg_longitud
            if seg_inicio <= inicio < seg_fin:
                if seg_inicio < inicio:
                    nueva_lista.append((seg_inicio, inicio - seg_inicio))
                if seg_fin > inicio + longitud:
                    nueva_lista.append((inicio + longitud, seg_fin - (inicio + longitud)))
            else:
                nueva_lista.append((seg_inicio, seg_longitud))
        self.lista_libre = sorted(nueva_lista, key=lambda s: s[0])

    def _insertar_segmento_libre(self, inicio, longitud):
        segmentos = self.lista_libre + [(inicio, longitud)]
        segmentos = sorted(segmentos, key=lambda s: s[0])
        fusionados = []
        for seg_inicio, seg_longitud in segmentos:
            if not fusionados:
                fusionados.append((seg_inicio, seg_longitud))
                continue
            ultimo_inicio, ultimo_longitud = fusionados[-1]
            if ultimo_inicio + ultimo_longitud == seg_inicio:
                fusionados[-1] = (ultimo_inicio, ultimo_longitud + seg_longitud)
            else:
                fusionados.append((seg_inicio, seg_longitud))
        self.lista_libre = fusionados

    def liberar_memoria(self, pid):
        if pid not in self.mapeo_procesos:
            return False
        bloques_asignados = self.mapeo_procesos[pid]['bloques']
        for indice in bloques_asignados:
            self.bloques[indice].liberar()
            self.bitmap[indice] = True
        if self.metodo == MetodoMemoria.LISTA_ENCADENADA:
            self._insertar_segmento_libre(bloques_asignados[0], len(bloques_asignados))
        del self.mapeo_procesos[pid]
        self.liberaciones_totales += 1
        self._calcular_fragmentacion()
        return True

    def _obtener_segmentos_libres(self):
        if self.metodo == MetodoMemoria.LISTA_ENCADENADA:
            return self.lista_libre.copy()
        segmentos = []
        i = 0
        while i < self.num_bloques:
            if self.bitmap[i]:
                inicio = i
                while i < self.num_bloques and self.bitmap[i]:
                    i += 1
                segmentos.append((inicio, i - inicio))
            else:
                i += 1
        return segmentos

    def _calcular_fragmentacion(self):
        self.desperdicio_memoria = sum(
            entrada['pcb'].get_fragmentacion_interna()
            for entrada in self.mapeo_procesos.values()
        )
        self.fragmentacion_interna = self.desperdicio_memoria
        segmentos_libres = self._obtener_segmentos_libres()
        total_libre_kb = sum(longitud * self.tamaño_bloque_kb for _, longitud in segmentos_libres)
        if total_libre_kb == 0:
            self.fragmentacion_externa = 0.0
            return
        mayor_libre_kb = max(longitud * self.tamaño_bloque_kb for _, longitud in segmentos_libres)
        self.fragmentacion_externa = ((total_libre_kb - mayor_libre_kb) / total_libre_kb) * 100

    def get_uso_memoria(self):
        bloques_ocupados = sum(len(entrada['bloques']) for entrada in self.mapeo_procesos.values())
        memoria_ocupada_kb = bloques_ocupados * self.tamaño_bloque_kb
        memoria_libre_kb = self.memoria_total_kb - memoria_ocupada_kb
        porcentaje_uso = (memoria_ocupada_kb / self.memoria_total_kb * 100) if self.memoria_total_kb else 0
        return {
            'memoria_total_kb': self.memoria_total_kb,
            'memoria_ocupada_kb': memoria_ocupada_kb,
            'memoria_libre_kb': memoria_libre_kb,
            'porcentaje_uso': porcentaje_uso,
            'bloques_ocupados': bloques_ocupados,
            'bloques_libres': self.num_bloques - bloques_ocupados,
            'fragmentacion_interna': self.fragmentacion_interna,
            'fragmentacion_externa': self.fragmentacion_externa,
            'desperdicio_memoria': self.desperdicio_memoria,
            'procesos_activos': len(self.mapeo_procesos)
        }

    def cambiar_estrategia(self, nueva_estrategia):
        self.estrategia = nueva_estrategia

    def obtener_direccion_proceso(self, pid):
        proceso = self.mapeo_procesos.get(pid)
        if proceso:
            return proceso['bloques'][0] * self.tamaño_bloque_kb * 1024
        return None

    def obtener_bloques_proceso(self, pid):
        proceso = self.mapeo_procesos.get(pid)
        return proceso['bloques'] if proceso else []

    def esta_asignado(self, pid):
        return pid in self.mapeo_procesos

    def visualizar_memoria(self, max_bloques=64):
        print("\n" + "="*60)
        print("MAPA DE MEMORIA")
        print("="*60)
        bloques_mostrar = min(len(self.bloques), max_bloques)
        for i in range(0, bloques_mostrar, 10):
            fila = ""
            for j in range(i, min(i + 10, bloques_mostrar)):
                if self.bloques[j].es_libre:
                    fila += "[ ]"
                else:
                    fila += f"[P{self.bloques[j].pid_ocupante % 10}]"
            print(f"B{i:3d}-B{min(i+9, bloques_mostrar-1):3d}: {fila}")
        uso = self.get_uso_memoria()
        print("\nESTADÍSTICAS:")
        print(f"  Memoria Total: {uso['memoria_total_kb']} KB")
        print(f"  Memoria Ocupada: {uso['memoria_ocupada_kb']} KB ({uso['porcentaje_uso']:.1f}%)")
        print(f"  Memoria Libre: {uso['memoria_libre_kb']} KB")
        print(f"  Fragmentación Externa: {uso['fragmentacion_externa']:.1f}%")
        print(f"  Fragmentación Interna: {uso['fragmentacion_interna']:.1f} KB")
        print(f"  Desperdicio Memoria: {uso['desperdicio_memoria']} KB")
        print(f"  Procesos Activos: {uso['procesos_activos']}")
        print()

    def __str__(self):
        uso = self.get_uso_memoria()
        return (f"GestorMemoria({uso['memoria_ocupada_kb']}/{uso['memoria_total_kb']}KB, "
                f"{uso['porcentaje_uso']:.1f}% usado, estrategia={self.estrategia.value})")
