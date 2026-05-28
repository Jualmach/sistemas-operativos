"""
pcb.py - Process Control Block (Bloque de Control de Proceso)
Almacena toda la información de estado de un proceso
"""

from enums import EstadoProceso, Constantes, DispositivoIO
from clock import Clock


class PCB:
    """
    Process Control Block - Contiene todo el estado e información de un proceso.
    """
    
    def __init__(self, pid, nombre, tamaño_proceso, burst_time, prioridad=Constantes.PRIORIDAD_DEFECTO):
        """
        Inicializa un nuevo PCB.
        
        Args:
            pid: ID único del proceso
            nombre: Nombre identificador del proceso
            tamaño_proceso: Tamaño en KB que requiere
            burst_time: Tiempo estimado de uso CPU
            prioridad: Nivel de prioridad (1-10)
        """
        # Información básica
        self.pid = pid
        self.nombre = nombre
        self.tamaño_proceso = tamaño_proceso  # KB
        self.burst_time = burst_time           # Unidades de tiempo
        self.burst_time_restante = burst_time  # Para tracking
        self.prioridad = max(1, min(10, prioridad))  # Validar rango
        
        # Estado
        self.estado = EstadoProceso.NUEVO
        # Tipo de proceso
        self.es_sistema = False
        
        # Información de memoria
        self.tamaño_ejecutable_kb = tamaño_proceso
        self.segmento_datos_kb = self._calcular_segmento_datos()
        self.stack_heap_kb = self._calcular_stack_heap()
        self.tamaño_total_kb = self._calcular_tamaño_total()
        self.bloque_memoria_kb = self._calcular_bloque_memoria()
        self.direccion_inicial_fisica = None      # Dirección física inicial
        self.tamaño_utilizado_kb = self.tamaño_total_kb
        self.direccion_memoria = None             # Dirección base asignada
        self.registros = {                        # Simulación de registros
            'R0': 0, 'R1': 0, 'R2': 0, 'R3': 0,
            'R4': 0, 'R5': 0, 'R6': 0, 'R7': 0,
        }
        
        # Program Counter (Contador de Programa)
        self.pc = 0  # Dirección relativa dentro del proceso
        
        # Cronometraje
        self.tiempo_creacion = Clock().obtener_tiempo()
        self.tiempo_inicio_ejecucion = None
        self.tiempo_primera_ejecucion = None   # Para tiempo de respuesta
        self.tiempo_total_cpu = 0.0
        self.tiempo_total_io = 0.0
        self.tiempo_total_espera = 0.0
        
        # E/S
        self.dispositivo_actual = None         # En qué dispositivo espera
        self.contador_operaciones_io = 0       # Número de operaciones E/S
        self.historial_io = []                 # Lista de operaciones E/S
        
        # Interrupciones
        self.contador_interrupciones = 0       # Total de interrupciones recibidas
        self.historial_interrupciones = []     # [(tipo, tiempo, duracion), ...]
        
        # Errores
        self.codigo_error = 0                  # 0 = sin error, >0 = con error
        self.mensaje_error = None
        
        # Interrupciones programadas
        self.interrupciones_programadas = self._crear_interrupciones_programadas()
        self.interrupciones_realizadas = 0

        # Estadísticas
        self.num_cambios_contexto = 0
        self.accesos_memoria = 0
        self.quantum_restante = 0              # Para Round Robin
        
    # ==================== GETTERS ====================
    
    def get_pid(self):
        """Retorna el ID del proceso"""
        return self.pid
    
    def get_nombre(self):
        """Retorna el nombre del proceso"""
        return self.nombre
    
    def get_estado(self):
        """Retorna el estado actual"""
        return self.estado
    
    def get_tamaño(self):
        """Retorna el tamaño total en KB (ejecutable + datos + stack/heap)"""
        return self.tamaño_total_kb

    def get_tamaño_ejecutable(self):
        """Retorna el tamaño del ejecutable en KB"""
        return self.tamaño_ejecutable_kb

    def get_segmento_datos(self):
        """Retorna el tamaño del segmento de datos en KB"""
        return self.segmento_datos_kb

    def get_stack_heap(self):
        """Retorna el tamaño combinado de stack y heap en KB"""
        return self.stack_heap_kb

    def get_bloque_memoria(self):
        """Retorna el tamaño del bloque de memoria asignado en KB"""
        return self.bloque_memoria_kb

    def get_direccion_inicial_fisica(self):
        """Retorna la dirección física inicial asignada"""
        return self.direccion_inicial_fisica

    def get_fragmentacion_interna(self):
        """Retorna el desperdicio de memoria por fragmentación interna"""
        return self.bloque_memoria_kb - self.tamaño_total_kb
    
    def get_burst_time(self):
        """Retorna el burst time original"""
        return self.burst_time
    
    def get_burst_time_restante(self):
        """Retorna el burst time que falta"""
        return self.burst_time_restante
    
    def get_direccion_memoria(self):
        """Retorna la dirección base en memoria"""
        return self.direccion_memoria
    
    def get_prioridad(self):
        """Retorna la prioridad"""
        return self.prioridad
    
    def get_pc(self):
        """Retorna el program counter"""
        return self.pc
    
    # ==================== SETTERS ====================
    
    def set_estado(self, nuevo_estado):
        """
        Cambia el estado del proceso.
        
        Args:
            nuevo_estado: Nuevo EstadoProceso
        """
        self.estado = nuevo_estado
    
    def set_direccion_memoria(self, direccion):
        """
        Establece la dirección base en memoria.
        
        Args:
            direccion: Dirección base asignada
        """
        self.direccion_memoria = direccion
        self.direccion_inicial_fisica = direccion
    
    def set_pc(self, direccion):
        """
        Establece el program counter.
        
        Args:
            direccion: Nueva dirección del PC
        """
        self.pc = direccion
    
    def incrementar_pc(self, incremento=1):
        """Incrementa el program counter"""
        self.pc += incremento
    
    def set_dispositivo_actual(self, dispositivo):
        """Establece el dispositivo en el que espera"""
        self.dispositivo_actual = dispositivo
    
    def set_codigo_error(self, codigo, mensaje=""):
        """
        Establece un código de error.
        
        Args:
            codigo: Código numérico de error
            mensaje: Descripción del error
        """
        self.codigo_error = codigo
        self.mensaje_error = mensaje
    
    # ==================== OPERACIONES ====================
    
    def iniciar_ejecucion(self):
        """Registra el inicio de ejecución"""
        if self.tiempo_inicio_ejecucion is None:
            self.tiempo_inicio_ejecucion = Clock().obtener_tiempo()
        if self.tiempo_primera_ejecucion is None:
            self.tiempo_primera_ejecucion = Clock().obtener_tiempo()
    
    def pausar_ejecucion(self, tiempo_pausado):
        """
        Registra el tiempo de pausa.
        
        Args:
            tiempo_pausado: Tiempo que estuvo ejecutando
        """
        self.tiempo_total_cpu += tiempo_pausado
        self.burst_time_restante = max(0, self.burst_time_restante - tiempo_pausado)
    
    def agregar_tiempo_io(self, tiempo):
        """
        Agrega tiempo de E/S.
        
        Args:
            tiempo: Tiempo gastado en E/S
        """
        self.tiempo_total_io += tiempo
        self.contador_operaciones_io += 1
        self.historial_io.append({
            'timestamp': Clock().obtener_tiempo(),
            'duracion': tiempo,
            'dispositivo': self.dispositivo_actual
        })
    
    def agregar_interrupcion(self, tipo_interrupcion, duracion):
        """
        Registra una interrupción.
        
        Args:
            tipo_interrupcion: Tipo de TipoInterrupcion
            duracion: Duración de la interrupción
        """
        self.contador_interrupciones += 1
        self.historial_interrupciones.append({
            'timestamp': Clock().obtener_tiempo(),
            'tipo': tipo_interrupcion,
            'duracion': duracion
        })
    
    def guardar_contexto(self):
        """Guarda el contexto actual (registros, PC, etc)"""
        contexto = {
            'pc': self.pc,
            'registros': self.registros.copy(),
            'timestamp': Clock().obtener_tiempo()
        }
        self.num_cambios_contexto += 1
        return contexto

    def _siguiente_potencia_de_dos(self, valor):
        """Calcula la siguiente potencia de dos en KB"""
        if valor <= 0:
            return Constantes.BLOQUE_TAMANO_MIN_KB
        potencia = Constantes.BLOQUE_TAMANO_MIN_KB
        while potencia < valor:
            potencia <<= 1
            if potencia > Constantes.BLOQUE_TAMANO_MAX_KB:
                return Constantes.BLOQUE_TAMANO_MAX_KB
        return potencia

    def _calcular_segmento_datos(self):
        """Calcula el segmento de datos como porcentaje del ejecutable"""
        return max(1, int(round(self.tamaño_ejecutable_kb * Constantes.FACTOR_SEGMENTO_DATOS)))

    def _calcular_stack_heap(self):
        """Calcula stack+heap como porcentaje del ejecutable"""
        return max(1, int(round(self.tamaño_ejecutable_kb * Constantes.FACTOR_STACK_HEAP)))

    def _calcular_tamaño_total(self):
        """Suma ejecutable, datos y stack/heap para definir el tamaño del proceso"""
        return self.tamaño_ejecutable_kb + self.segmento_datos_kb + self.stack_heap_kb

    def _calcular_bloque_memoria(self):
        """Calcula el tamaño del bloque de memoria necesario, como potencia de dos."""
        return self._siguiente_potencia_de_dos(self.tamaño_total_kb)

    def calcular_interrupciones_objetivo(self):
        """Calcula la cantidad de interrupciones E/S según tamaño y burst time."""
        base = (self.tamaño_total_kb // 64) + (self.burst_time // 8)
        cantidad = 5 + (base % 16)
        return min(Constantes.MAX_INTERRUPCIONES_POR_PROCESO,
                   max(Constantes.MIN_INTERRUPCIONES_POR_PROCESO, cantidad))

    def _crear_interrupciones_programadas(self):
        """Genera la lista de interrupciones programadas con su momento de PC."""
        total = self.calcular_interrupciones_objetivo()
        interrupciones = []
        for idx in range(total):
            dispositivo = self.seleccionar_dispositivo_interrupcion(idx)
            duracion = self.calcular_duracion_interrupcion(idx)
            objetivo_pc = max(1, round((idx + 1) * self.burst_time / (total + 1)))
            interrupciones.append({
                'indice': idx,
                'dispositivo': dispositivo,
                'duracion': duracion,
                'objetivo_pc': objetivo_pc,
                'realizada': False
            })
        return interrupciones

    def obtener_interrupcion_programada(self):
        """Obtiene la interrupción que debe ocurrir en el PC actual."""
        for evento in self.interrupciones_programadas:
            if not evento['realizada'] and evento['objetivo_pc'] == self.pc:
                return evento
        return None

    def marcar_interrupcion_realizada(self, evento):
        """Marca una interrupción programada como realizada."""
        evento['realizada'] = True
        self.interrupciones_realizadas += 1

    def calcular_duracion_interrupcion(self, indice):
        """Calcula la duración de una interrupción según tamaño, burst time e índice."""
        valor_base = (self.tamaño_total_kb // 32) + (self.burst_time // 5) + indice
        duracion = 5 + (valor_base % 16)
        return min(Constantes.MAX_DURACION_INTERRUPCION,
                   max(Constantes.MIN_DURACION_INTERRUPCION, duracion))

    def seleccionar_dispositivo_interrupcion(self, indice):
        """Selecciona uno de los tres dispositivos físicos basados en fórmula determinista."""
        lista_dispositivos = [
            DispositivoIO.TECLADO,
            DispositivoIO.DISCO,
            DispositivoIO.IMPRESORA
        ]
        valor = ((self.tamaño_total_kb // 64) + (self.burst_time // 10) + indice) % len(lista_dispositivos)
        return lista_dispositivos[valor]

    def generar_plan_interrupciones(self):
        """Genera un plan de interrupciones determinista para el proceso."""
        total = self.calcular_interrupciones_objetivo()
        return [
            {
                'indice': idx,
                'dispositivo': self.seleccionar_dispositivo_interrupcion(idx),
                'duracion': self.calcular_duracion_interrupcion(idx)
            }
            for idx in range(total)
        ]
    
    def restaurar_contexto(self, contexto):
        """
        Restaura un contexto previo.
        
        Args:
            contexto: Diccionario con PC y registros
        """
        self.pc = contexto['pc']
        self.registros = contexto['registros'].copy()
    
    # ==================== ESTADÍSTICAS ====================
    
    def get_tiempo_respuesta(self):
        """
        Calcula el tiempo de respuesta.
        (desde creación hasta primera ejecución)
        """
        if self.tiempo_primera_ejecucion is not None:
            return self.tiempo_primera_ejecucion - self.tiempo_creacion
        return 0
    
    def get_tiempo_total_espera(self):
        """
        Calcula el tiempo total de espera.
        """
        tiempo_total = Clock().obtener_tiempo() - self.tiempo_creacion
        tiempo_activo = self.tiempo_total_cpu + self.tiempo_total_io
        return max(0, tiempo_total - tiempo_activo)
    
    def get_tiempo_finalizacion(self):
        """Retorna el tiempo de finalización"""
        if self.estado == EstadoProceso.FINALIZADO:
            return Clock().obtener_tiempo()
        return None
    
    def get_info_resumen(self):
        """
        Retorna un resumen de la información del PCB.
        
        Returns:
            dict: Información resumida
        """
        return {
            'PID': self.pid,
            'Nombre': self.nombre,
            'Estado': self.estado.value,
            'Prioridad': self.prioridad,
            'PC': self.pc,
            'Dirección Física': self.direccion_inicial_fisica,
            'Bloque Memoria (KB)': self.bloque_memoria_kb,
            'Fragmentación Interna': self.get_fragmentacion_interna(),
            'Ejecutable (KB)': self.tamaño_ejecutable_kb,
            'Datos (KB)': self.segmento_datos_kb,
            'Stack/Heap (KB)': self.stack_heap_kb,
            'Tamaño Total (KB)': self.tamaño_total_kb,
            'SO': self.es_sistema,
            'Burst Time': self.burst_time,
            'Restante': self.burst_time_restante,
            'CPU Total': f"{self.tiempo_total_cpu:.2f}",
            'IO Total': f"{self.tiempo_total_io:.2f}",
            'Interrupciones': self.contador_interrupciones,
            'Operaciones E/S': self.contador_operaciones_io,
            'Error': self.codigo_error,
            'Tiempo Respuesta': f"{self.get_tiempo_respuesta():.2f}"
        }
    
    def __str__(self):
        return f"PCB(PID={self.pid}, {self.nombre}, {self.estado.value}, CPU={self.tiempo_total_cpu:.1f})"
    
    def __repr__(self):
        return f"PCB({self.pid}, {self.nombre}, {self.estado.value})"