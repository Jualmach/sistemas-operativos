"""
supervisor.py - Modulo supervisor y validador del simulador.

Centraliza validaciones de consistencia para que los errores de proceso
queden registrados en la PCB y en las estadisticas del sistema.
"""

from enums import EstadoProceso


class SupervisorSO:
    """Valida que la actividad de cada proceso sea coherente con el modelo."""

    def __init__(self):
        self.validaciones = 0
        self.fallos_detectados = 0
        self.historial = []

    def validar_proceso(self, pcb, gestor_memoria):
        """Devuelve una lista de errores detectados para un PCB."""
        self.validaciones += 1
        errores = []

        if pcb.get_pc() < 0:
            errores.append("PC negativo")

        if pcb.get_pc() > pcb.get_burst_time():
            errores.append("PC fuera del rango del burst-time")

        if pcb.get_burst_time_restante() < 0:
            errores.append("Burst restante negativo")

        requiere_memoria = pcb.get_estado() not in (EstadoProceso.NUEVO, EstadoProceso.FINALIZADO)
        if requiere_memoria and not gestor_memoria.esta_asignado(pcb.get_pid()):
            errores.append("Proceso activo sin memoria asignada")

        if requiere_memoria and pcb.get_direccion_inicial_fisica() is None:
            errores.append("Proceso activo sin direccion fisica inicial")

        if pcb.codigo_error < 0:
            errores.append("Codigo de error invalido")

        if errores:
            self.fallos_detectados += 1
            self.historial.append({
                'pid': pcb.get_pid(),
                'estado': pcb.get_estado().value,
                'errores': errores
            })

        return errores

    def validar_sistema(self, gestor_procesos, gestor_memoria):
        """Valida todos los procesos activos y devuelve errores por PID."""
        resultado = {}
        for pcb in gestor_procesos.obtener_todos_activos():
            errores = self.validar_proceso(pcb, gestor_memoria)
            if errores:
                resultado[pcb.get_pid()] = errores
        return resultado

    def get_estadisticas(self):
        """Retorna estadisticas resumidas del supervisor."""
        return {
            'validaciones': self.validaciones,
            'fallos_detectados': self.fallos_detectados,
            'ultimos_fallos': self.historial[-10:]
        }
