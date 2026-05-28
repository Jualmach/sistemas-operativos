"""
dispatcher.py - Despachador de procesos (Dispatcher)
Realiza el cambio de contexto entre procesos
"""

from enums import EstadoProceso, Constantes, TipoInterrupcion
from clock import Clock


class Dispatcher:
    """
    Realiza el cambio de contexto entre procesos.
    Gestiona la ejecución de instrucciones.
    """
    
    def __init__(self, gestor_procesos, tiempo_cambio_contexto=Constantes.TIEMPO_CAMBIO_CONTEXTO):
        """
        Inicializa el dispatcher.
        
        Args:
            gestor_procesos: Referencia al GestorProcesos
            tiempo_cambio_contexto: Tiempo que toma cambiar contexto
        """
        self.gestor_procesos = gestor_procesos
        self.tiempo_cambio_contexto = tiempo_cambio_contexto
        
        # Estadísticas
        self.cambios_contexto_totales = 0
        self.instrucciones_ejecutadas = 0
        self.tiempo_cambio_contexto_total = 0
    
    # ==================== CAMBIO DE CONTEXTO ====================
    
    def cambiar_contexto(self, proceso_entrante):
        """
        Realiza el cambio de contexto para ejecutar un nuevo proceso.
        
        Args:
            proceso_entrante: PCB del proceso a ejecutar
        """
        # Obtener proceso que estaba ejecutando
        proceso_saliente = self.gestor_procesos.obtener_ejecutando()
        
        # Si hay proceso saliente, guardar su contexto
        if proceso_saliente and proceso_saliente != proceso_entrante:
            self._guardar_contexto(proceso_saliente)
        
        # Simular tiempo de cambio de contexto
        self.tiempo_cambio_contexto_total += self.tiempo_cambio_contexto
        
        # Restaurar contexto del proceso entrante
        self._restaurar_contexto(proceso_entrante)
        
        # Establecer como ejecutando
        self.gestor_procesos.establecer_ejecutando(proceso_entrante)
        
        # Incrementar contador
        self.cambios_contexto_totales += 1
    
    def _guardar_contexto(self, proceso):
        """
        Guarda el contexto de un proceso.
        
        Args:
            proceso: PCB del proceso
        """
        contexto = {
            'pc': proceso.get_pc(),
            'registros': proceso.registros.copy(),
            'estado': proceso.get_estado(),
            'timestamp': Clock().obtener_tiempo()
        }
        # Almacenar en algún lugar si es necesario (para validación)
        proceso._contexto_guardado = contexto
    
    def _restaurar_contexto(self, proceso):
        """
        Restaura el contexto de un proceso.
        
        Args:
            proceso: PCB del proceso
        """
        # Si hay contexto guardado, restaurarlo
        if hasattr(proceso, '_contexto_guardado'):
            contexto = proceso._contexto_guardado
            proceso.set_pc(contexto['pc'])
            proceso.registros = contexto['registros'].copy()
    
    # ==================== EJECUCIÓN ====================
    
    def ejecutar_instruccion(self, proceso, quantum=1):
        """
        Ejecuta una instrucción (o cantidad de tiempo) del proceso.
        
        Args:
            proceso: PCB del proceso
            quantum: Unidades de tiempo a ejecutar
            
        Returns:
            dict: Resultado de ejecución con estado y evento si aplica
        """
        if not proceso or proceso.get_estado() != EstadoProceso.EJECUTANDO:
            return {'estado': 'no_ejecucion'}

        for _ in range(quantum):
            proceso.incrementar_pc()
            self.instrucciones_ejecutadas += 1
            proceso.burst_time_restante = max(0, proceso.burst_time_restante - 1)

            if hasattr(proceso, 'quantum_restante'):
                proceso.quantum_restante = max(0, proceso.quantum_restante - 1)

            interrupcion = proceso.obtener_interrupcion_programada()
            if interrupcion:
                proceso.marcar_interrupcion_realizada(interrupcion)
                return {'estado': 'interrupcion', 'evento': interrupcion}

            if proceso.get_burst_time_restante() <= 0:
                return {'estado': 'finalizado'}

        return {'estado': 'continuar'}
    
    def puede_continuar_ejecucion(self, proceso):
        """
        Verifica si el proceso puede continuar ejecutándose.
        
        Args:
            proceso: PCB del proceso
            
        Returns:
            bool: True si puede continuar
        """
        if not proceso:
            return False
        
        # El proceso puede continuar si aún tiene burst time
        return proceso.get_burst_time_restante() > 0 and proceso.get_estado() == EstadoProceso.EJECUTANDO
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_estadisticas(self):
        """
        Retorna estadísticas del dispatcher.
        
        Returns:
            dict: Estadísticas
        """
        return {
            'cambios_contexto_totales': self.cambios_contexto_totales,
            'instrucciones_ejecutadas': self.instrucciones_ejecutadas,
            'tiempo_cambio_contexto_total': self.tiempo_cambio_contexto_total,
            'tiempo_promedio_cambio': (
                self.tiempo_cambio_contexto_total / self.cambios_contexto_totales
                if self.cambios_contexto_totales > 0 else 0
            )
        }
    
    def __str__(self):
        return (f"Dispatcher(cambios={self.cambios_contexto_totales}, "
                f"instrucciones={self.instrucciones_ejecutadas})")
