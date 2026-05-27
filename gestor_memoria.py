"""
gestor_memoria.py - Administrador de memoria física
Implementa asignación de memoria con mapas de bits o listas encadenadas
"""

import math
from enums import Constantes, EstrategiaMemoria, MetodoMemoria


class BloqueMB:
    """Representa un bloque de memoria"""
    
    def __init__(self, numero, tamaño_kb):
        """
        Args:
            numero: Número/índice del bloque
            tamaño_kb: Tamaño en KB del bloque
        """
        self.numero = numero
        self.tamaño_kb = tamaño_kb
        self.pid_ocupante = None  # None si está libre, PID si está ocupado
        self.es_libre = True
    
    def ocupar(self, pid):
        """Marca el bloque como ocupado"""
        self.pid_ocupante = pid
        self.es_libre = False
    
    def liberar(self):
        """Marca el bloque como libre"""
        self.pid_ocupante = None
        self.es_libre = True
    
    def __str__(self):
        estado = "LIBRE" if self.es_libre else f"P{self.pid_ocupante}"
        return f"B{self.numero}({estado})"


class GestorMemoria:
    """
    Administra la asignación y liberación de memoria física.
    Soporta múltiples estrategias: First-Fit, Best-Fit, Worst-Fit
    """
    
    def __init__(self, 
                 memoria_total_kb=Constantes.MEMORIA_TOTAL_KB,
                 tamaño_bloque_kb=Constantes.TAMAÑO_BLOQUE_KB,
                 estrategia=EstrategiaMemoria.FIRST_FIT,
                 metodo=MetodoMemoria.MAPA_BITS):
        """
        Inicializa el gestor de memoria.
        
        Args:
            memoria_total_kb: Tamaño total en KB
            tamaño_bloque_kb: Tamaño de cada bloque en KB (debe ser power of 2)
            estrategia: EstrategiaMemoria a usar
            metodo: Método de administración (MAPA_BITS o LISTA_ENCADENADA)
        """
        # Validar que tamaño_bloque es power of 2
        if not self._es_power_of_2(tamaño_bloque_kb):
            raise ValueError(f"El tamaño de bloque {tamaño_bloque_kb} no es potencia de 2")
        
        self.memoria_total_kb = memoria_total_kb
        self.tamaño_bloque_kb = tamaño_bloque_kb
        self.estrategia = estrategia
        self.metodo = metodo
        
        # Calcular número de bloques
        self.num_bloques = memoria_total_kb // tamaño_bloque_kb
        
        # Crear bloques
        self.bloques = [
            BloqueMB(i, tamaño_bloque_kb) 
            for i in range(self.num_bloques)
        ]
        
        # Mapeo de procesos: pid -> lista de bloques asignados
        self.mapeo_procesos = {}
        
        # Estadísticas
        self.fragmentacion_interna = 0.0
        self.fragmentacion_externa = 0.0
        self.asignaciones_totales = 0
        self.liberaciones_totales = 0
    
    # ==================== VALIDACIÓN ====================
    
    @staticmethod
    def _es_power_of_2(n):
        """Verifica si n es potencia de 2"""
        return n > 0 and (n & (n - 1)) == 0
    
    def _calcular_bloques_requeridos(self, tamaño_kb):
        """Calcula cuántos bloques se necesitan para el tamaño"""
        return math.ceil(tamaño_kb / self.tamaño_bloque_kb)
    
    # ==================== ASIGNACIÓN ====================
    
    def asignar_memoria(self, pcb):
        """
        Asigna memoria a un proceso.
        
        Args:
            pid: ID del proceso
            tamaño_kb: Tamaño requerido en KB
            
        Returns:
            int: Dirección base asignada, o None si falla
        """
        # Calcular bloques necesarios
        bloques_necesarios = self._calcular_bloques_requeridos(
            pcb.tamaño_proceso
        )
        
        # Encontrar bloques libres según la estrategia
        bloques_asignados = self._buscar_bloques(bloques_necesarios)
        
        if bloques_asignados is None:
            return None  # No hay memoria disponible
        
        # Ocupar los bloques
        direccion_base = None
        for bloque_num in bloques_asignados:
            self.bloques[bloque_num].ocupar(pcb.pid)
            if direccion_base is None:
                direccion_base = bloque_num * self.tamaño_bloque_kb * 1024  # Convertir a bytes
        
        pcb.set_direccion_memoria(direccion_base)
        
        # Registrar asignación
        self.mapeo_procesos[pcb.pid] = bloques_asignados
        self.asignaciones_totales += 1
        
        memoria_asignada = bloques_necesarios * self.tamaño_bloque_kb

        desperdicio = memoria_asignada - pcb.tamaño_proceso

        self.desperdicio_memoria += desperdicio
        # Actualizar estadísticas
        self._calcular_fragmentacion()
        
        return direccion_base
    
    def _buscar_bloques(self, cantidad):
        """
        Busca bloques libres según la estrategia.
        
        Args:
            cantidad: Número de bloques consecutivos necesarios
            
        Returns:
            list: Números de bloques a usar, o None si falla
        """
        if self.estrategia == EstrategiaMemoria.FIRST_FIT:
            return self._first_fit(cantidad)
        elif self.estrategia == EstrategiaMemoria.BEST_FIT:
            return self._best_fit(cantidad)
        elif self.estrategia == EstrategiaMemoria.WORST_FIT:
            return self._worst_fit(cantidad)
    
    def _first_fit(self, cantidad):
        """
        First-Fit: Usa los primeros bloques libres encontrados.
        Eficiente en tiempo.
        """
        bloques = []
        for i, bloque in enumerate(self.bloques):
            if bloque.es_libre:
                bloques.append(i)
                if len(bloques) == cantidad:
                    return bloques
        return None  # No hay suficiente memoria contigua
    
    def _best_fit(self, cantidad):
        """
        Best-Fit: Encuentra el hueco más pequeño que cabe el proceso.
        Minimiza fragmentación interna.
        """
        mejor_hueco = None
        mejor_tamaño = float('inf')
        
        i = 0
        while i < len(self.bloques):
            if self.bloques[i].es_libre:
                # Contar bloques libres consecutivos
                j = i
                while j < len(self.bloques) and self.bloques[j].es_libre:
                    j += 1
                
                tamaño_hueco = j - i
                
                # Si este hueco es lo suficientemente grande y es mejor
                if tamaño_hueco >= cantidad and tamaño_hueco < mejor_tamaño:
                    mejor_tamaño = tamaño_hueco
                    mejor_hueco = list(range(i, i + cantidad))
                
                i = j
            else:
                i += 1
        
        return mejor_hueco
    
    def _worst_fit(self, cantidad):
        """
        Worst-Fit: Encuentra el hueco más grande disponible.
        Busca mantener huecos grandes para procesos grandes.
        """
        peor_hueco = None
        peor_tamaño = -1
        
        i = 0
        while i < len(self.bloques):
            if self.bloques[i].es_libre:
                # Contar bloques libres consecutivos
                j = i
                while j < len(self.bloques) and self.bloques[j].es_libre:
                    j += 1
                
                tamaño_hueco = j - i
                
                # Si este hueco es lo suficientemente grande y es el mayor
                if tamaño_hueco >= cantidad and tamaño_hueco > peor_tamaño:
                    peor_tamaño = tamaño_hueco
                    peor_hueco = list(range(i, i + cantidad))
                
                i = j
            else:
                i += 1
        
        return peor_hueco
    
    # ==================== LIBERACIÓN ====================
    
    def liberar_memoria(self, pid):
        """
        Libera la memoria asignada a un proceso.
        
        Args:
            pid: ID del proceso
            
        Returns:
            bool: True si fue exitoso, False si el proceso no existe
        """
        if pid not in self.mapeo_procesos:
            return False
        
        # Liberar los bloques
        bloques_asignados = self.mapeo_procesos[pid]
        for bloque_num in bloques_asignados:
            self.bloques[bloque_num].liberar()
        
        # Remover del mapeo
        del self.mapeo_procesos[pid]
        self.liberaciones_totales += 1
        
        # Actualizar estadísticas
        self._calcular_fragmentacion()
        
        return True
    
    # ==================== ESTADÍSTICAS ====================
    
    def _calcular_fragmentacion(self):
        """Calcula los índices de fragmentación"""
        # Fragmentación interna: espacio no usado en bloques asignados
        total_asignado = 0
        espacio_util = 0
        
        for pid, bloques_ids in self.mapeo_procesos.items():
            # Asumir que el proceso usa todo el bloque (sin fragmentación interna real)
            total_asignado += len(bloques_ids) * self.tamaño_bloque_kb
            espacio_util += len(bloques_ids) * self.tamaño_bloque_kb
        
        # Fragmentación externa: huecos libres pequeños e inutilizables
        bloques_libres = sum(1 for b in self.bloques if b.es_libre)
        bloques_ocupados = sum(1 for b in self.bloques if not b.es_libre)
        
        if self.num_bloques > 0:
            self.fragmentacion_externa = (bloques_libres / self.num_bloques) * 100
        
        if total_asignado > 0:
            self.fragmentacion_interna = 100 - (espacio_util / total_asignado * 100)
        else:
            self.fragmentacion_interna = 0
            self.desperdicio_memoria = 0
    
    def get_uso_memoria(self):
        """
        Retorna el uso actual de memoria.
        
        Returns:
            dict: Información de uso
        """
        bloques_libres = sum(1 for b in self.bloques if b.es_libre)
        bloques_ocupados = self.num_bloques - bloques_libres
        
        memoria_libre_kb = bloques_libres * self.tamaño_bloque_kb
        memoria_ocupada_kb = bloques_ocupados * self.tamaño_bloque_kb
        porcentaje_uso = (memoria_ocupada_kb / self.memoria_total_kb * 100) if self.memoria_total_kb > 0 else 0
        
        return {
            'memoria_total_kb': self.memoria_total_kb,
            'memoria_ocupada_kb': memoria_ocupada_kb,
            'memoria_libre_kb': memoria_libre_kb,
            'porcentaje_uso': porcentaje_uso,
            'bloques_ocupados': bloques_ocupados,
            'bloques_libres': bloques_libres,
            'fragmentacion_interna': self.fragmentacion_interna,
            'fragmentacion_externa': self.fragmentacion_externa,
            'desperdicio_memoria': self.desperdicio_memoria,
            'procesos_activos': len(self.mapeo_procesos)
        }
    
    def cambiar_estrategia(self, nueva_estrategia):
        """
        Cambia la estrategia de asignación.
        
        Args:
            nueva_estrategia: Nueva EstrategiaMemoria
        """
        self.estrategia = nueva_estrategia
    
    # ==================== CONSULTAS ====================
    
    def obtener_direccion_proceso(self, pid):
        """Obtiene la dirección base de un proceso"""
        bloques = self.mapeo_procesos.get(pid)
        if bloques:
            return bloques[0] * self.tamaño_bloque_kb * 1024
        return None
    
    def obtener_bloques_proceso(self, pid):
        """Obtiene los bloques asignados a un proceso"""
        return self.mapeo_procesos.get(pid, [])
    
    def esta_asignado(self, pid):
        """Verifica si un proceso tiene memoria asignada"""
        return pid in self.mapeo_procesos
    
    # ==================== VISUALIZACIÓN ====================
    
    def visualizar_memoria(self, max_bloques=64):
        """
        Muestra una representación visual de la memoria.
        
        Args:
            max_bloques: Máximo número de bloques a mostrar
        """
        print("\n" + "="*60)
        print("MAPA DE MEMORIA")
        print("="*60)
        
        bloques_mostrar = min(len(self.bloques), max_bloques)
        
        # Mostrar bloques
        for i in range(0, bloques_mostrar, 10):
            fila = ""
            for j in range(i, min(i + 10, bloques_mostrar)):
                if self.bloques[j].es_libre:
                    fila += "[ ]"
                else:
                    fila += f"[P{self.bloques[j].pid_ocupante % 10}]"
            print(f"B{i:3d}-B{min(i+9, bloques_mostrar-1):3d}: {fila}")
        
        # Estadísticas
        uso = self.get_uso_memoria()
        print("\nESTADÍSTICAS:")
        print(f"  Memoria Total: {uso['memoria_total_kb']} KB")
        print(f"  Memoria Ocupada: {uso['memoria_ocupada_kb']} KB ({uso['porcentaje_uso']:.1f}%)")
        print(f"  Memoria Libre: {uso['memoria_libre_kb']} KB")
        print(f"  Fragmentación Externa: {uso['fragmentacion_externa']:.1f}%")
        print(f"  Procesos Activos: {uso['procesos_activos']}")
        print(f"  Desperdicio Memoria: {uso['desperdicio_memoria']} KB")
        print()
    
    def __str__(self):
        uso = self.get_uso_memoria()
        return (f"GestorMemoria({uso['memoria_ocupada_kb']}/{uso['memoria_total_kb']}KB, "
                f"{uso['porcentaje_uso']:.1f}% usado, "
                f"estrategia={self.estrategia.value})")
