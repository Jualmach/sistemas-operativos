"""
enums.py - Enumeraciones y tipos del Simulador de SO
"""

from enum import Enum


class EstadoProceso(Enum):
    """Estados en los que puede estar un proceso"""
    NUEVO = "NUEVO"
    LISTO = "LISTO"
    EJECUTANDO = "EJECUTANDO"
    BLOQUEADO = "BLOQUEADO"
    FINALIZADO = "FINALIZADO"


class TipoInterrupcion(Enum):
    """Tipos de interrupciones del sistema"""
    TIMER = "TIMER"
    IO_ENTRADA = "IO_ENTRADA"
    IO_SALIDA = "IO_SALIDA"
    FINALIZACION = "FINALIZACION"
    ERROR = "ERROR"
    CREACION_PROCESO = "CREACION_PROCESO"


class PoliticaScheduling(Enum):
    """Políticas de planificación disponibles"""
    FCFS = "FCFS"                  # First Come First Served
    SJF = "SJF"                    # Shortest Job First (no expropiativo)
    SRTF = "SRTF"                  # Shortest Remaining Time First (expropiativo)
    RR = "RR"                      # Round Robin
    PRIORIDADES = "PRIORIDADES"    # Por prioridades


class EstrategiaMemoria(Enum):
    """Estrategias de asignación de memoria"""
    FIRST_FIT = "FIRST_FIT"       # Primer bloque que cabe
    BEST_FIT = "BEST_FIT"          # Bloque que mejor se ajusta
    WORST_FIT = "WORST_FIT"        # Bloque más grande disponible


class DispositivoIO(Enum):
    """Tipos de dispositivos de entrada/salida"""
    TECLADO = "TECLADO"
    DISCO = "DISCO"
    IMPRESORA = "IMPRESORA"
    RED = "RED"
    USB = "USB"


class MetodoMemoria(Enum):
    """Métodos de administración de memoria"""
    MAPA_BITS = "MAPA_BITS"
    LISTA_ENCADENADA = "LISTA_ENCADENADA"


# Constantes del sistema
class Constantes:
    """Constantes globales del simulador"""
    
    # Memoria
    MEMORIA_TOTAL_KB = 2048                    # KB
    TAMAÑO_BLOQUE_KB = 64                      # KB (debe ser power of 2)
    TAMAÑO_BLOQUE_BYTES = TAMAÑO_BLOQUE_KB * 1024
    BLOQUE_TAMANO_MIN_KB = 32                  # Mínimo bloque de memoria 2^n
    BLOQUE_TAMANO_MAX_KB = 2048                # Máximo bloque de memoria 2^n
    FACTOR_SEGMENTO_DATOS = 0.25               # 25% del ejecutable
    FACTOR_STACK_HEAP = 0.15                   # 15% del ejecutable
    
    # Scheduling
    QUANTUM_DEFECTO = 10                       # Unidades de tiempo
    TIEMPO_CAMBIO_CONTEXTO = 7                 # Unidades de tiempo
    
    # E/S
    DISPOSITIVOS_DEFECTO = {
        DispositivoIO.TECLADO: {
            'tiempo_min': 5,
            'tiempo_max': 20,
            'nombre': 'Teclado'
        },
        DispositivoIO.DISCO: {
            'tiempo_min': 10,
            'tiempo_max': 50,
            'nombre': 'Disco'
        },
        DispositivoIO.IMPRESORA: {
            'tiempo_min': 20,
            'tiempo_max': 100,
            'nombre': 'Impresora'
        },
        DispositivoIO.RED: {
            'tiempo_min': 8,
            'tiempo_max': 25,
            'nombre': 'Red'
        },
        DispositivoIO.USB: {
            'tiempo_min': 5,
            'tiempo_max': 15,
            'nombre': 'USB'
        }
    }
    
    # Procesos
    TASA_ERROR = 0.005                         # 0.5% (5 por cada 1000)
    MIN_INTERRUPCIONES_POR_PROCESO = 5
    MAX_INTERRUPCIONES_POR_PROCESO = 20
    MIN_DURACION_INTERRUPCION = 5
    MAX_DURACION_INTERRUPCION = 20
    
    # Prioridades
    PRIORIDAD_MINIMA = 1
    PRIORIDAD_MAXIMA = 10
    PRIORIDAD_DEFECTO = 5
    
    # Simulación
    MAX_PROCESOS_SIMULTANEOS = 100
    VELOCIDAD_SIMULACION_DEFECTO = 1.0
