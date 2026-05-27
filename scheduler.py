"""
scheduler.py - Planificador de procesos (Scheduler)
Implementa múltiples políticas de planificación
"""

from enums import PoliticaScheduling, EstadoProceso, Constantes
from clock import Clock


class Scheduler:
    """
    Planificador multinivel de procesos.
    Implementa diferentes políticas de scheduling.
    """
    
    def __init__(self, gestor_procesos, politica=PoliticaScheduling.RR, es_expropiativo=True, quantum=10):
        """
        Inicializa el scheduler.
        
        Args:
            gestor_procesos: Referencia al GestorProcesos
            politica: PoliticaScheduling a usar
            es_expropiativo: Si la política es expropiativa
            quantum: Quantum de tiempo para Round Robin
        """
        self.gestor_procesos = gestor_procesos
        self.politica = politica
        self.es_expropiativo = es_expropiativo
        self.quantum = quantum
        
        # Estadísticas
        self.invocaciones = 0
        self.cambios_contexto = 0
        self.decisiones = []  # Historial de decisiones
    
    # ==================== PLANIFICACIÓN MULTINIVEL ====================
    
    def planificacion_largo_plazo(self, proceso):
        """
        Planificación a largo plazo: NUEVO → LISTO
        
        Args:
            proceso: PCB del proceso
        """
        # Simplemente cambiar de NUEVO a LISTO
        self.gestor_procesos.cambiar_estado(proceso, EstadoProceso.LISTO)
        self.gestor_procesos.agregar_a_listos(proceso)
    
    def planificacion_mediano_plazo(self):
        """
        Planificación a mediano plazo: BLOQUEADO → LISTO (cuando E/S termina)
        Se invoca cuando se completa una operación de E/S.
        """
        # Esto se maneja en el módulo de E/S
        pass
    
    def planificacion_corto_plazo(self):
        """
        Planificación a corto plazo: selecciona siguiente proceso a ejecutar.
        
        Returns:
            PCB: Siguiente proceso a ejecutar, o None
        """
        self.invocaciones += 1
        
        # Obtener siguiente según política
        siguiente = self._seleccionar_siguiente()
        
        if siguiente:
            self.cambios_contexto += 1
            self._registrar_decision(siguiente)
        
        return siguiente
    
    # ==================== SELECCIÓN DE PROCESO ====================
    
    def _seleccionar_siguiente(self):
        """
        Selecciona el siguiente proceso según la política.
        
        Returns:
            PCB: Siguiente proceso, o None
        """
        if self.politica == PoliticaScheduling.FCFS:
            return self._politica_fcfs()
        elif self.politica == PoliticaScheduling.SJF:
            return self._politica_sjf(expropiativo=False)
        elif self.politica == PoliticaScheduling.SRTF:
            return self._politica_sjf(expropiativo=True)
        elif self.politica == PoliticaScheduling.RR:
            return self._politica_rr()
        elif self.politica == PoliticaScheduling.PRIORIDADES:
            return self._politica_prioridades()
    
    def _politica_fcfs(self):
        """
        FCFS (First Come, First Served)
        Procesa en orden de llegada. No expropiativo.
        """
        if self.gestor_procesos.contar_listos() > 0:
            siguiente = self.gestor_procesos.obtener_siguiente_listo()
            siguiente.quantum_restante = self.quantum
            return siguiente
        return None
    
    def _politica_sjf(self, expropiativo=False):
        """
        SJF (Shortest Job First) - No expropiativo por defecto.
        SRTF (Shortest Remaining Time First) - Si es expropiativo.
        
        Args:
            expropiativo: Si debe ser expropiativo (SRTF)
        """
        listos = list(self.gestor_procesos.cola_listos)
        
        if not listos:
            return None
        
        # Seleccionar con menor burst time restante
        siguiente = min(listos, key=lambda p: p.get_burst_time_restante())
        
        # Remover de la cola
        try:
            self.gestor_procesos.cola_listos.remove(siguiente)
        except ValueError:
            pass
        
        siguiente.quantum_restante = siguiente.get_burst_time_restante()
        return siguiente
    
    def _politica_rr(self):
        """
        RR (Round Robin)
        Cada proceso obtiene un quantum de tiempo.
        Siempre expropiativo.
        """
        if self.gestor_procesos.contar_listos() > 0:
            siguiente = self.gestor_procesos.obtener_siguiente_listo()
            siguiente.quantum_restante = self.quantum
            return siguiente
        return None
    
    def _politica_prioridades(self):
        """
        Planificación por prioridades.
        Mayor número = mayor prioridad.
        Puede ser expropiativo.
        """
        listos = list(self.gestor_procesos.cola_listos)
        
        if not listos:
            return None
        
        # Seleccionar con mayor prioridad
        siguiente = max(listos, key=lambda p: p.get_prioridad())
        
        # Remover de la cola
        try:
            self.gestor_procesos.cola_listos.remove(siguiente)
        except ValueError:
            pass
        
        siguiente.quantum_restante = self.quantum
        return siguiente
    
    # ==================== INVOCACIÓN DEL SCHEDULER ====================
    
    def invocar_no_expropiativo(self, razon):
        """
        Invoca el scheduler de forma no expropiativa.
        Ocurre cuando el proceso en ejecución libera la CPU voluntariamente.
        
        Args:
            razon: Razón de la invocación
        """
        # El proceso actual ya no está ejecutando
        self.gestor_procesos.liberar_cpu()
        
        # Seleccionar siguiente
        siguiente = self.planificacion_corto_plazo()
        
        return siguiente
    
    def invocar_expropiativo(self, razon):
        """
        Invoca el scheduler de forma expropiativa.
        Ocurre cuando algo le quita la CPU al proceso en ejecución.
        
        Args:
            razon: Razón de la invocación (TIMER, IO, etc)
        """
        proceso_actual = self.gestor_procesos.obtener_ejecutando()
        
        # Si hay proceso ejecutando, devolverlo a listos
        if proceso_actual and proceso_actual.get_estado() == EstadoProceso.EJECUTANDO:
            self.gestor_procesos.cambiar_estado(proceso_actual, EstadoProceso.LISTO)
            self.gestor_procesos.agregar_a_listos(proceso_actual)
        
        # Liberar CPU
        self.gestor_procesos.liberar_cpu()
        
        # Seleccionar siguiente
        siguiente = self.planificacion_corto_plazo()
        
        return siguiente
    
    # ==================== MANEJO DE QUANTUM ====================
    
    def cambiar_quantum(self, nuevo_quantum):
        """
        Cambia el quantum para Round Robin.
        
        Args:
            nuevo_quantum: Nuevo valor del quantum
        """
        if nuevo_quantum > 0:
            self.quantum = nuevo_quantum
    
    def obtener_quantum_actual(self):
        """Retorna el quantum actual"""
        return self.quantum
    
    # ==================== CAMBIO DE POLÍTICA ====================
    
    def cambiar_politica(self, nueva_politica, nuevo_quantum=10):
        """
        Cambia la política de scheduling.
        
        Args:
            nueva_politica: Nueva PoliticaScheduling
            nuevo_quantum: Quantum para políticas que lo requieren
        """
        self.politica = nueva_politica
        self.quantum = nuevo_quantum
    
    def cambiar_expropiacion(self, es_expropiativo):
        """
        Cambia si el scheduler es expropiativo.
        
        Args:
            es_expropiativo: True o False
        """
        self.es_expropiativo = es_expropiativo
    
    # ==================== ESTADÍSTICAS ====================
    
    def _registrar_decision(self, proceso):
        """Registra una decisión del scheduler"""
        self.decisiones.append({
            'timestamp': Clock().obtener_tiempo(),
            'proceso': proceso.get_pid(),
            'politica': self.politica.value,
            'quantum': getattr(proceso, 'quantum_restante', self.quantum)
        })
    
    def get_estadisticas(self):
        """
        Retorna estadísticas del scheduler.
        
        Returns:
            dict: Estadísticas
        """
        return {
            'politica_actual': self.politica.value,
            'quantum_actual': self.quantum,
            'expropiativo': self.es_expropiativo,
            'invocaciones_totales': self.invocaciones,
            'cambios_contexto': self.cambios_contexto,
            'decisiones_registradas': len(self.decisiones)
        }
    
    def __str__(self):
        return (f"Scheduler({self.politica.value}, "
                f"quantum={self.quantum}, "
                f"expropiativo={self.es_expropiativo})")
