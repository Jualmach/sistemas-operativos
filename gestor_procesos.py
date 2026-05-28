"""
gestor_procesos.py - Administrador central de procesos
Maneja la creación, transición de estados y finalización de procesos
"""

from collections import deque
import random
from enums import EstadoProceso, TipoInterrupcion, DispositivoIO, Constantes
from clock import Clock
from pcb import PCB


class GestorProcesos:
    """
    Administra el ciclo de vida completo de los procesos del sistema.
    Mantiene las colas de procesos en diferentes estados.
    """
    
    def __init__(self):
        """Inicializa el gestor de procesos"""
        # Colas de procesos por estado
        self.cola_nuevo = []                           # Procesos por ingresar
        self.cola_listos = deque()                     # Procesos listos para ejecutar
        self.colas_io = {                              # Procesos esperando E/S
            DispositivoIO.TECLADO: deque(),
            DispositivoIO.DISCO: deque(),
            DispositivoIO.IMPRESORA: deque(),
            DispositivoIO.RED: deque(),
            DispositivoIO.USB: deque()
        }
        
        # Proceso actualmente ejecutando
        self.proceso_ejecutando = None
        
        # Procesos finalizados (histórico)
        self.procesos_finalizados = []
        
        # Contador para asignar PIDs únicos
        self.contador_pids = 0
        
        # Diccionario de búsqueda rápida: pid -> PCB
        self.procesos_activos = {}
        
        # Estadísticas
        self.total_procesos_creados = 0
        self.total_procesos_finalizados = 0
        self.total_errores = 0
    
    # ==================== CREACIÓN DE PROCESOS ====================
    
    def crear_proceso(self, nombre, tamaño_proceso_kb, burst_time, prioridad=Constantes.PRIORIDAD_DEFECTO):
        """
        Crea un nuevo proceso.
        
        Args:
            nombre: Nombre identificador del proceso
            tamaño_proceso_kb: Tamaño en KB requerido
            burst_time: Tiempo estimado de CPU
            prioridad: Nivel de prioridad (1-10)
            
        Returns:
            PCB: El proceso creado, o None si hay error
        """
        # Validar parámetros
        if tamaño_proceso_kb <= 0 or burst_time <= 0:
            return None
        
        # Generar PID único
        pid = self.contador_pids
        self.contador_pids += 1
        
        # Crear PCB
        pcb = PCB(
            pid=pid,
            nombre=nombre,
            tamaño_proceso=tamaño_proceso_kb,
            burst_time=burst_time,
            prioridad=prioridad
        )

        # Determinar si es proceso del sistema
        pcb.es_sistema = nombre.upper().startswith("SO_")
        
        # Simulación de errores aleatorios (0.5%)

        if random.random() < Constantes.TASA_ERROR:

            pcb.set_codigo_error(
                1,
                "Segmentation Fault"
            )

            self.total_errores += 1
        # Registrar en diccionario
        self.procesos_activos[pid] = pcb
        self.total_procesos_creados += 1
        
        return pcb
    
    def agregar_proceso(self, pcb):
        """
        Agrega un proceso a la cola de nuevos.
        
        Args:
            pcb: PCB del proceso a agregar
        """
        if pcb.get_estado() != EstadoProceso.NUEVO:
            print(f"Advertencia: Proceso {pcb.get_pid()} no está en estado NUEVO")
        self.cola_nuevo.append(pcb)
    
    def obtener_proximo_nuevo(self):
        """
        Obtiene el próximo proceso de la cola de nuevos.
        
        Returns:
            PCB: Proceso, o None si la cola está vacía
        """
        if self.cola_nuevo:
            return self.cola_nuevo.pop(0)
        return None
    
    # ==================== TRANSICIONES DE ESTADO ====================
    
    def planificacion_largo_plazo(self, pcb):
        """
        Planificación a largo plazo: toma un proceso en estado NUEVO 
        y lo transfiere a la cola de LISTOS.
        
        Args:
            pcb: PCB del proceso a admitir
        """
        self.agregar_a_listos(pcb)
    
    
    
    def cambiar_estado(self, pcb, nuevo_estado):
        """
        Cambia el estado de un proceso.
        
        Args:
            pcb: PCB del proceso
            nuevo_estado: Nuevo EstadoProceso
        """
        estado_anterior = pcb.get_estado()
        
        # Registrar cambio de tiempo según la transición
        if nuevo_estado == EstadoProceso.EJECUTANDO:
            pcb.iniciar_ejecucion()
        
        pcb.set_estado(nuevo_estado)
        
        # Registrar en log/estadísticas
        # print(f"[{Clock().obtener_tiempo():.1f}] P{pcb.get_pid()} {estado_anterior.value} → {nuevo_estado.value}")
    
    def cambiar_estado_multiple(self, procesos, nuevo_estado):
        """
        Cambia estado de múltiples procesos a la vez.
        
        Args:
            procesos: Lista de PCBs
            nuevo_estado: Nuevo EstadoProceso
        """
        for pcb in procesos:
            self.cambiar_estado(pcb, nuevo_estado)
    
    # ==================== GESTIÓN DE COLAS ====================
    
    def agregar_a_listos(self, pcb):
        """
        Agrega un proceso a la cola de listos asegurando la transición de estado.
        
        Args:
            pcb: PCB del proceso
        """
        if pcb.get_estado() != EstadoProceso.LISTO:
            self.cambiar_estado(pcb, EstadoProceso.LISTO)
        
        # Evita duplicados exactos en la cola por seguridad
        if pcb not in self.cola_listos:
            self.cola_listos.append(pcb)

    
    def obtener_siguiente_listo(self):
        """
        Obtiene el siguiente proceso listo para ejecutar.
        
        Returns:
            PCB: Proceso listo, o None si la cola está vacía
        """
        if self.cola_listos:
            return self.cola_listos.popleft()
        return None
    
    def contar_listos(self):
        """Retorna el número de procesos en cola de listos"""
        return len(self.cola_listos)
    
    # ==================== E/S ====================
    
    def bloquear_en_dispositivo(self, pcb, dispositivo, duracion):
        """
        Bloquea un proceso en espera de un dispositivo.
        
        Args:
            pcb: PCB del proceso
            dispositivo: Nombre del dispositivo (TECLADO, DISCO, IMPRESORA)
            duracion: Tiempo de atención del dispositivo
        """
        self.cambiar_estado(pcb, EstadoProceso.BLOQUEADO)
        if self.proceso_ejecutando == pcb:
            self.liberar_cpu()

        pcb.set_dispositivo_actual(dispositivo)
        tipo_interrupcion = TipoInterrupcion.IO_ENTRADA if dispositivo == DispositivoIO.TECLADO else TipoInterrupcion.IO_SALIDA
        pcb.agregar_interrupcion(tipo_interrupcion, duracion)

        if dispositivo in self.colas_io:
            self.colas_io[dispositivo].append(pcb)
    
    def desbloquear_de_dispositivo(self, pcb):
        """
        Desbloquea un proceso de E/S.
        
        Args:
            pcb: PCB del proceso
        """
        dispositivo = pcb.dispositivo_actual
        if dispositivo and dispositivo in self.colas_io:
            try:
                self.colas_io[dispositivo].remove(pcb)
            except ValueError:
                pass
        
        pcb.set_dispositivo_actual(None)

        # Volver a cola de listos
        self.agregar_a_listos(pcb)
    
    def obtener_siguientes_io(self, dispositivo):
        """
        Obtiene procesos esperando en un dispositivo.
        
        Args:
            dispositivo: Nombre del dispositivo
            
        Returns:
            deque: Procesos en ese dispositivo
        """
        return self.colas_io.get(dispositivo, deque())
    
    def contar_bloqueados(self):
        """Retorna el total de procesos bloqueados en E/S"""
        total = 0
        for cola in self.colas_io.values():
            total += len(cola)
        return total
    
    def obtener_bloqueados_por_dispositivo(self):
        """
        Retorna un diccionario con procesos bloqueados por dispositivo.
        
        Returns:
            dict: {dispositivo: [procesos]}
        """
        resultado = {}
        for dispositivo, cola in self.colas_io.items():
            resultado[dispositivo] = list(cola)
        return resultado
    
    # ==================== EJECUCIÓN ====================
    
    def establecer_ejecutando(self, pcb):
        """
        Establece un proceso como ejecutando.
        
        Args:
            pcb: PCB del proceso
        """
        self.proceso_ejecutando = pcb
        self.cambiar_estado(pcb, EstadoProceso.EJECUTANDO)
        # Simulación de interrupción TIMER
        pcb.agregar_interrupcion(
            TipoInterrupcion.TIMER,
            random.randint(5, 20)
        )
    
    def obtener_ejecutando(self):
        """Retorna el proceso actualmente ejecutando"""
        return self.proceso_ejecutando
    
    def liberar_cpu(self):
        """Libera la CPU del proceso actual"""
        self.proceso_ejecutando = None
    
    # ==================== FINALIZACIÓN ====================
    
    def finalizar_proceso(self, pcb, codigo_error=0, mensaje_error=""):
        """
        Finaliza un proceso.
        
        Args:
            pcb: PCB del proceso
            codigo_error: Código de error (0 = exitoso)
            mensaje_error: Descripción del error
        """
        # Registrar error si aplica
        if codigo_error != 0:
            pcb.set_codigo_error(codigo_error, mensaje_error)
            self.total_errores += 1
        
        # Cambiar estado
        self.cambiar_estado(pcb, EstadoProceso.FINALIZADO)
        
        # Liberar de estructura activa
        if pcb.get_pid() in self.procesos_activos:
            del self.procesos_activos[pcb.get_pid()]
        
        # Agregar a histórico
        self.procesos_finalizados.append(pcb)
        self.total_procesos_finalizados += 1
        
        # Liberar CPU si estaba ejecutando
        if self.proceso_ejecutando == pcb:
            self.liberar_cpu()
    
    # ==================== BÚSQUEDA ====================
    
    def obtener_proceso(self, pid):
        """
        Obtiene un proceso por su PID.
        
        Args:
            pid: ID del proceso
            
        Returns:
            PCB: El proceso, o None si no existe
        """
        return self.procesos_activos.get(pid)
    
    def obtener_todos_activos(self):
        """Retorna lista de todos los procesos activos"""
        return list(self.procesos_activos.values())
    
    def obtener_todos_finalizados(self):
        """Retorna lista de todos los procesos finalizados"""
        return self.procesos_finalizados.copy()
    
    # ==================== ESTADÍSTICAS ====================
    
    def contar_por_estado(self):
        """
        Retorna contador de procesos por estado.
        
        Returns:
            dict: {estado: cantidad}
        """
        conteo = {
            'NUEVO': len(self.cola_nuevo),
            'LISTO': len(self.cola_listos),
            'EJECUTANDO': 1 if self.proceso_ejecutando else 0,
            'BLOQUEADO': self.contar_bloqueados(),
            'FINALIZADO': len(self.procesos_finalizados)
        }
        return conteo
    
    def get_estadisticas(self):
        """
        Retorna estadísticas generales.
        
        Returns:
            dict: Estadísticas del sistema
        """
        return {
            'Total creados': self.total_procesos_creados,
            'Total finalizados': self.total_procesos_finalizados,
            'Total activos': len(self.procesos_activos),
            'Total con error': self.total_errores,
            'Procesos por estado': self.contar_por_estado()
        }
    
    def mostrar_estado(self):
        """Muestra el estado actual del sistema"""
        print("\n" + "="*60)
        print(f"ESTADO DEL GESTOR DE PROCESOS (t={Clock().obtener_tiempo():.1f})")
        print("="*60)
        
        print(f"\nNUEVO ({len(self.cola_nuevo)}): ", end="")
        print(", ".join([f"P{p.get_pid()}" for p in self.cola_nuevo]) if self.cola_nuevo else "vacío")
        
        print(f"LISTO ({len(self.cola_listos)}): ", end="")
        print(", ".join([f"P{p.get_pid()}" for p in self.cola_listos]) if self.cola_listos else "vacío")
        
        print(f"EJECUTANDO: ", end="")
        if self.proceso_ejecutando:
            tipo = "SO" if self.proceso_ejecutando.es_sistema else "USR"

            print(
            f"P{self.proceso_ejecutando.get_pid()} [{tipo}]"
            )
        else:
            print("vacío")
        
        print(f"BLOQUEADO ({self.contar_bloqueados()}):")
        for dispositivo, cola in self.colas_io.items():
            if cola:
                pids = ", ".join([f"P{p.get_pid()}" for p in cola])
                nombre_disp = dispositivo.value if hasattr(dispositivo, 'value') else str(dispositivo)
                print(f"  {nombre_disp}: {pids}")
        
        print(f"\nFINALIZADO ({len(self.procesos_finalizados)}): ", end="")
        print(", ".join([f"P{p.get_pid()}" for p in self.procesos_finalizados[-5:]]) if self.procesos_finalizados else "vacío")
        print()