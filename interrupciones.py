import random
from enums import DispositivoIO


class GestorInterrupciones:
    """Administra las colas de dispositivos físicos TECLADO, DISCO e IMPRESORA."""

    def __init__(self, gestor_procesos):
        self.gestor_procesos = gestor_procesos
        self.colas_dispositivo = {
            DispositivoIO.TECLADO: [],
            DispositivoIO.DISCO: [],
            DispositivoIO.IMPRESORA: []
        }

    def ingresar_proceso(self, pcb, dispositivo, duracion):
        """Agrega un proceso a la cola de un dispositivo con duración de atención."""
        if dispositivo not in self.colas_dispositivo:
            return False

        self.colas_dispositivo[dispositivo].append({
            'pcb': pcb,
            'duracion_restante': duracion,
            'duracion_original': duracion,
            'dispositivo': dispositivo
        })
        return True

    def procesar_tick(self):
        """Descuenta tiempo de atención de cada proceso bloqueado en dispositivos."""
        completados = []
        for dispositivo, cola in self.colas_dispositivo.items():
            for item in list(cola):
                item['duracion_restante'] -= 1
                if item['duracion_restante'] <= 0:
                    cola.remove(item)
                    completados.append(item)
        return completados

    def resolver_teclado(self, pcb):
        """Simula la señal de Teclado: continuar o cancelar."""
        if random.choice([True, False]):
            return 'continuar'
        return 'cancelar'

    def obtener_procesos_por_dispositivo(self, dispositivo):
        """Devuelve la lista de procesos pendientes para un dispositivo."""
        return [item['pcb'] for item in self.colas_dispositivo.get(dispositivo, [])]
