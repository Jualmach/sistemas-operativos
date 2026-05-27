# ARQUITECTURA DEL SIMULADOR DE SISTEMA OPERATIVO
## Gestión de Procesos, Memoria e E/S

---

## 1. VISIÓN GENERAL

El simulador es un sistema modular que emula las funciones principales de un Sistema Operativo:
- **Gestor de Procesos**: Manejo de estados, transiciones, PCB, scheduling
- **Gestor de Memoria**: Asignación dinámica, fragmentación, estrategias
- **Gestor de E/S**: Simulación de dispositivos y interrupciones

```
┌─────────────────────────────────────────────────────────┐
│                    SIMULADOR DE SO                       │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Gestor de  │  │   Gestor de  │  │   Gestor de  │  │
│  │  Procesos    │  │   Memoria    │  │     E/S      │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
├─────────────────────────────────────────────────────────┤
│         ┌──────────────────────────────────┐            │
│         │   Motor de Simulación (Clock)    │            │
│         └──────────────────────────────────┘            │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────┐   │
│  │          Interfaz Gráfica (Visualización)        │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

---

## 2. ESTRUCTURA DE MÓDULOS

### 2.1 NÚCLEO DEL SISTEMA

```
simulador_so/
├── core/
│   ├── __init__.py
│   ├── clock.py                 # Reloj global del simulador
│   ├── enums.py                 # Enumeraciones (estados, tipos, etc)
│   └── constants.py             # Constantes del sistema
│
├── proceso/
│   ├── __init__.py
│   ├── pcb.py                   # Process Control Block
│   ├── proceso.py               # Clase Proceso
│   ├── estado_proceso.py        # Estados y transiciones
│   └── gestor_procesos.py       # Administrador de procesos
│
├── memoria/
│   ├── __init__.py
│   ├── memoria.py               # Gestor de memoria física
│   ├── bloque_memoria.py        # Representación de bloques
│   ├── estrategias.py           # First-Fit, Best-Fit, Worst-Fit
│   └── mapa_bits.py             # Administración con mapa de bits
│
├── scheduler/
│   ├── __init__.py
│   ├── scheduler.py             # Clase base del planificador
│   ├── politicas.py             # FCFS, SJF, RR, Prioridades
│   └── dispatcher.py            # Cambio de contexto
│
├── io/
│   ├── __init__.py
│   ├── dispositivo.py           # Clase base de dispositivos
│   ├── teclado.py               # Simulación de teclado
│   ├── disco.py                 # Simulación de disco
│   ├── impresora.py             # Simulación de impresora
│   └── gestor_io.py             # Administrador de E/S
│
├── interrupciones/
│   ├── __init__.py
│   ├── interrupcion.py          # Clase de interrupción
│   └── gestor_interrupciones.py # Administrador de interrupciones
│
├── estadisticas/
│   ├── __init__.py
│   ├── estadisticas.py          # Recolector de estadísticas
│   └── generador_reportes.py    # Generación de reportes
│
├── interfaz/
│   ├── __init__.py
│   ├── visualizador.py          # Sistema de visualización
│   └── ui_principal.py          # Interfaz principal
│
└── main.py                       # Punto de entrada
```

---

## 3. COMPONENTES DETALLADOS

### 3.1 ENUMS Y CONSTANTES

#### Estado de Procesos
```python
class EstadoProceso(Enum):
    NUEVO = "NUEVO"
    LISTO = "LISTO"
    EJECUTANDO = "EJECUTANDO"
    BLOQUEADO = "BLOQUEADO"
    FINALIZADO = "FINALIZADO"
```

#### Tipos de Interrupciones
```python
class TipoInterrupcion(Enum):
    TIMER = "TIMER"
    IO_ENTRADA = "IO_ENTRADA"
    IO_SALIDA = "IO_SALIDA"
    FINALIZACION = "FINALIZACION"
    ERROR = "ERROR"
    CREACION_PROCESO = "CREACION_PROCESO"
```

#### Políticas de Scheduling
```python
class PoliticaScheduling(Enum):
    FCFS = "FCFS"              # First Come First Served
    SJF = "SJF"                # Shortest Job First
    RR = "RR"                  # Round Robin
    PRIORIDADES = "PRIORIDADES"
```

#### Estrategias de Asignación de Memoria
```python
class EstrategiaMemoria(Enum):
    FIRST_FIT = "FIRST_FIT"
    BEST_FIT = "BEST_FIT"
    WORST_FIT = "WORST_FIT"
```

#### Dispositivos de E/S
```python
class DispositivoIO(Enum):
    TECLADO = "TECLADO"
    DISCO = "DISCO"
    IMPRESORA = "IMPRESORA"
```

### 3.2 PCB (PROCESS CONTROL BLOCK)

```python
class PCB:
    """
    Almacena toda la información del estado de un proceso
    """
    - pid: int                          # ID único del proceso
    - nombre: str                       # Nombre del proceso
    - estado: EstadoProceso             # Estado actual
    - contador_programa (PC): int       # Dirección siguiente instrucción
    - direccion_memoria: int            # Dirección base en memoria
    - tamaño_proceso: int               # Bytes requeridos
    - tiempo_creacion: float            # Timestamp de creación
    - tiempo_inicio_ejecucion: float    # Cuando comenzó a ejecutar
    - tiempo_total_cpu: float           # CPU acumulado
    - tiempo_total_io: float            # Tiempo en operaciones E/S
    - burst_time: int                   # Tiempo estimado CPU
    - prioridad: int                    # Nivel de prioridad (1-10)
    - registros: dict                   # Estado de registros (si se requiere)
    - colas_io: list                    # Dispositivos en espera
    - interrupciones: list              # Historial de interrupciones
    - codigo_error: int                 # 0 = sin error, >0 = error
    - contador_interrupciones: int      # Número de E/S realizadas
```

### 3.3 GESTOR DE PROCESOS

```python
class GestorProcesos:
    """
    Administra toda la vida útil de los procesos
    """
    Atributos:
    - cola_procesos: list               # Cola de NUEVO
    - cola_listos: deque                # Cola de LISTO
    - colas_io: dict                    # Colas por dispositivo E/S
    - proceso_ejecutando: Proceso       # Proceso actual en CPU
    - procesos_finalizados: list        # Procesos completados
    - contador_procesos: int            # Para asignar PIDs únicos
    
    Métodos:
    - crear_proceso(tamaño, burst_time, prioridad)
    - agregar_proceso(proceso)
    - cambiar_estado(proceso, nuevo_estado)
    - obtener_proximo_listo()
    - bloquear_proceso(proceso, dispositivo)
    - desbloquear_proceso(proceso)
    - finalizar_proceso(proceso, codigo_error=0)
    - obtener_estadisticas()
```

### 3.4 GESTOR DE MEMORIA

```python
class GestorMemoria:
    """
    Administra la asignación y liberación de memoria física
    """
    Atributos:
    - tamaño_total: int                 # Memoria total del sistema
    - tamaño_bloque: int                # Tamaño estándar de bloques (power of 2)
    - bloques_memoria: list             # Array de bloques
    - estrategia: EstrategiaMemoria     # Estrategia actual
    - mapeo_procesos: dict              # pid -> [bloques asignados]
    - fragmentacion: float              # Porcentaje de desperdicio
    
    Métodos:
    - asignar_memoria(proceso, tamaño) -> direccion_base
    - liberar_memoria(proceso)
    - buscar_bloques_libres(cantidad, estrategia)
    - calcular_fragmentacion()
    - obtener_uso_memoria()
    - cambiar_estrategia(nueva_estrategia)
```

### 3.5 SCHEDULER (PLANIFICADOR)

```python
class Scheduler:
    """
    Planificador multinivel: largo, mediano y corto plazo
    """
    Atributos:
    - gestor_procesos: GestorProcesos
    - politica_corto_plazo: PoliticaScheduling
    - es_expropiativo: bool
    - quantum: int                      # Para Round Robin
    
    Métodos:
    - planificacion_largo_plazo(proceso)
    - planificacion_mediano_plazo()
    - planificacion_corto_plazo()
    - seleccionar_proximo_proceso()
    - aplicar_politica_fcfs()
    - aplicar_politica_sjf()
    - aplicar_politica_rr()
    - aplicar_politica_prioridades()
    - cambiar_quantum(nuevo_quantum)
```

### 3.6 DISPATCHER

```python
class Dispatcher:
    """
    Realiza el cambio de contexto entre procesos
    """
    Métodos:
    - cambiar_contexto(proceso_saliente, proceso_entrante)
    - guardar_contexto(proceso)
    - restaurar_contexto(proceso)
    - ejecutar_instruccion(proceso)
    - tiempo_cambio_contexto: 5-10 unidades
```

### 3.7 GESTOR DE E/S

```python
class GestorIO:
    """
    Administra los dispositivos de E/S y sus colas
    """
    Atributos:
    - dispositivos: dict                # DispositivoIO -> Dispositivo
    - colas_espera: dict                # DispositivoIO -> deque de procesos
    
    Métodos:
    - solicitar_io(proceso, dispositivo)
    - procesar_io(dispositivo)
    - completar_io(dispositivo)
    - generar_interrupcion_io(dispositivo, proceso)
```

### 3.8 DISPOSITIVOS DE E/S

```python
class Dispositivo:
    """Clase base para todos los dispositivos"""
    - tipo: DispositivoIO
    - tiempo_operacion_min: int         # 5 unidades
    - tiempo_operacion_max: int         # 20 unidades
    - cola_espera: deque
    - dispositivo_actual: Proceso

class Teclado(Dispositivo):
    - Captura señal de entrada
    - Puede cancelar o continuar proceso

class Disco(Dispositivo):
    - Simula lectura/escritura
    - Tiempos variables según operación

class Impresora(Dispositivo):
    - Simula impresión
    - Tiempos de espera realistas
```

### 3.9 GESTOR DE INTERRUPCIONES

```python
class Interrupcion:
    - timestamp: float                  # Momento de ocurrencia
    - tipo: TipoInterrupcion
    - proceso_afectado: Proceso
    - dispositivo: DispositivoIO (si aplica)
    - codigo: int                       # Código de error (si aplica)

class GestorInterrupciones:
    - cola_interrupciones: deque
    - procesar_interrupcion(interrupcion)
    - generar_interrupcion_aleatoria(proceso)
    - manejar_timer()
    - manejar_io()
    - manejar_error()
```

### 3.10 RELOJ DEL SIMULADOR

```python
class Clock:
    """
    Sincroniza todas las operaciones del simulador
    """
    - tiempo_actual: float              # Tiempo en unidades
    - velocidad: float                  # Multiplicador de velocidad
    - en_ejecucion: bool
    
    Métodos:
    - incrementar_tiempo(unidades)
    - obtener_tiempo()
    - pausar()
    - reanudar()
    - reset()
```

---

## 4. FLUJO DE EJECUCIÓN

### 4.1 CICLO PRINCIPAL

```
Inicialización
    ↓
┌─────────────────────────────────────────────┐
│ MIENTRAS simulacion_activa:                 │
│  1. Procesar interrupciones pendientes      │
│  2. Ejecutar instrucción del proceso actual │
│  3. Actualizar tiempos de E/S              │
│  4. Verificar cambios de estado            │
│  5. Invocar scheduler si es necesario      │
│  6. Actualizar visualización               │
│  7. Incrementar reloj                      │
└─────────────────────────────────────────────┘
    ↓
Generación de reportes
    ↓
Fin
```

### 4.2 CREACIÓN DE UN PROCESO

```
Usuario ingresa proceso
    ↓
GestorProcesos.crear_proceso()
    ↓
GestorMemoria.asignar_memoria()
    ├─ Seleccionar bloques libres
    ├─ Actualizar estado de memoria
    └─ Guardar dirección en PCB
    ↓
Crear PCB con todos los campos
    ↓
Estado: NUEVO
    ↓
Scheduler.planificacion_largo_plazo()
    ↓
Estado: LISTO
    ↓
Agregar a cola_listos
```

### 4.3 CAMBIO DE ESTADO DE UN PROCESO

```
NUEVO → LISTO: Por planificación largo plazo
LISTO → EJECUTANDO: Por decisión del scheduler
EJECUTANDO → LISTO: Por interrupción de TIMER (RR) o finalización de quantum
EJECUTANDO → BLOQUEADO: Por solicitud E/S
BLOQUEADO → LISTO: Por finalización de E/S
EJECUTANDO → FINALIZADO: Por finalización natural
EJECUTANDO → FINALIZADO: Por error (con código de error)
```

### 4.4 MANEJO DE INTERRUPCIONES

```
Interrupción Ocurre
    ↓
GestorInterrupciones.procesar_interrupcion()
    ↓
├─ TIMER:
│   └─ Cambiar EJECUTANDO → LISTO (si RR)
│       └─ Invocar Scheduler
│
├─ IO_SALIDA:
│   └─ Cambiar BLOQUEADO → LISTO
│       └─ Invocar Scheduler
│
├─ IO_ENTRADA:
│   └─ Cambiar EJECUTANDO → BLOQUEADO
│       └─ Encolar en dispositivo
│       └─ Invocar Scheduler
│
└─ ERROR:
    └─ Cambiar EJECUTANDO → FINALIZADO
        └─ Guardar código de error
        └─ Liberar memoria
        └─ Invocar Scheduler
```

---

## 5. PARÁMETROS DE ENTRADA

### 5.1 CONFIGURACIÓN DEL SISTEMA

```python
PARAMETROS_SISTEMA = {
    'memoria_total': 2048,              # KB (32KB a 2MB mínimo)
    'tamaño_bloque': 64,                # KB (debe ser power of 2)
    'politica_scheduling': 'RR',        # FCFS, SJF, RR, PRIORIDADES
    'quantum': 10,                      # Unidades de tiempo
    'es_expropiativo': True,
    'estrategia_memoria': 'FIRST_FIT',  # FIRST_FIT, BEST_FIT, WORST_FIT
    'velocidad_simulacion': 1.0,        # 1.0 = tiempo real
    'tasa_error': 0.005,                # 0.5% (5 por cada 1000)
    'dispositivos_io': {
        'TECLADO': {'tiempo_min': 5, 'tiempo_max': 20},
        'DISCO': {'tiempo_min': 10, 'tiempo_max': 50},
        'IMPRESORA': {'tiempo_min': 20, 'tiempo_max': 100}
    }
}
```

### 5.2 CREACIÓN DE PROCESOS

```
Entrada manual o aleatoria:
- PID (asignado automáticamente)
- Nombre
- Tamaño del proceso (KB)
- Burst Time (unidades de tiempo)
- Prioridad (1-10, donde 10 es máxima)
```

---

## 6. GENERACIÓN DE VALORES ALEATORIOS

### 6.1 FÓRMULAS PARA ALEATORIEDAD

```python
# Interrupciones por proceso (5-20)
import random
num_interrupciones = random.randint(5, 20)

# Duración de interrupciones (5-20 unidades)
duracion_interrupcion = random.randint(5, 20)

# Procesos con error (0.5% de 1000 procesos = 5 errores)
tiene_error = random.random() < 0.005

# Dispositivo E/S aleatorio
dispositivo = random.choice(['TECLADO', 'DISCO', 'IMPRESORA'])

# Tiempo de operación del dispositivo
tiempo_operacion = random.randint(5, 20)
```

### 6.2 DISTRIBUCIÓN

```
- Distribución uniforme para duración de E/S
- Distribución de Poisson para llegada de interrupciones
- Generación uniforme para asignación de dispositivos
```

---

## 7. SALIDAS Y VISUALIZACIÓN

### 7.1 INFORMACIÓN EN TIEMPO REAL

```
┌────────────────────────────────────────────────┐
│         SIMULADOR DE SISTEMA OPERATIVO         │
├────────────────────────────────────────────────┤
│                                                │
│  Tiempo: 1250 unidades                        │
│  Proceso Ejecutando: P5 (EJECUTANDO)          │
│  PC: 0x2048                                   │
│                                                │
├─ ESTADO DE PROCESOS ───────────────────────┤
│  NUEVO:      [P1, P2]                        │
│  LISTO:      [P3, P4, P6]                    │
│  EJECUTANDO: P5                              │
│  BLOQUEADO:  [P7-DISCO, P8-IMPRESORA]       │
│  FINALIZADO: [P0, P9, P10]                  │
│                                                │
├─ MEMORIA ──────────────────────────────────┤
│  Usada: 1024 KB / 2048 KB (50%)             │
│  Fragmentación: 12.5%                        │
│  Bloques Libres: 4/32                        │
│                                                │
├─ DISPOSITIVOS E/S ─────────────────────────┤
│  Teclado: Disponible                         │
│  Disco:   Procesando P7 (8/20 unidades)    │
│  Impresora: Cola=[P8, P11]                  │
│                                                │
├─ ESTADÍSTICAS ─────────────────────────────┤
│  Total Procesos: 12                          │
│  Finalizados: 3                              │
│  Errores: 0                                  │
│  CPU Utilizada: 65%                          │
│                                                │
└────────────────────────────────────────────────┘
```

### 7.2 ESTADÍSTICAS POR PROCESO

```
Para cada uno de los 20 procesos evaluados:
- Tiempo de Espera Total
- Tiempo de Respuesta (desde llegada hasta primer uso CPU)
- Tiempo de Uso CPU
- Número de E/S realizadas
- Código de error (si aplica)
```

### 7.3 REPORTES COMPARATIVOS

```
Comparación de políticas (FCFS, SJF, RR, PRIORIDADES):
- Tiempo promedio de respuesta
- Tiempo promedio de espera
- Varianza de tiempos

Comparación de estrategias de memoria (FF, BF, WF):
- Fragmentación promedio
- Número de bloques libres
- Eficiencia de asignación
```

---

## 8. CONSIDERACIONES TÉCNICAS

### 8.1 MANEJO DE MEMORIA

- **Tamaños de bloques**: Múltiplos de 2^n (32KB, 64KB, 128KB, etc.)
- **Direccionamiento físico**: No se usa MMU
- **Asignación dinámica**: Stack y Heap dentro del proceso
- **Fragmentación externa**: Espacio entre procesos
- **Fragmentación interna**: Espacio no usado dentro de bloques asignados

### 8.2 ALGORITMOS DE SCHEDULING

```python
# FCFS (No expropiativo)
- Procesa en orden de llegada
- Sin cambios involuntarios

# SJF (Puede ser expropiativo)
- Selecciona proceso con menor burst time
- SRTF = Shortest Remaining Time First (expropiativo)

# RR (Siempre expropiativo)
- Cada proceso obtiene quantum de tiempo
- Vuelve a cola de listos si no termina

# Prioridades (Puede ser expropiativo)
- Mayor prioridad se ejecuta primero
- Envejecimiento opcional
```

### 8.3 CAMBIO DE CONTEXTO

- Tiempo simulado: 5-10 unidades
- Guarda: PC, registros, estado
- Restaura: Estado del nuevo proceso
- Actualiza PCB con nuevo estado

### 8.4 MANEJO DE ERRORES

- 0.5% de procesos tienen error (5 de cada 1000)
- Generación aleatoria
- Registro en PCB y estadísticas
- Liberación automática de recursos

---

## 9. ESTRUCTURA DE DATOS CLAVE

### 9.1 COLAS

```python
from collections import deque

cola_procesos_nuevo: list              # Ordenada
cola_listos: deque                     # FIFO o por prioridad
colas_io: {
    'TECLADO': deque,
    'DISCO': deque,
    'IMPRESORA': deque
}
cola_interrupciones: deque             # Prioridad por timestamp
procesos_finalizados: list             # Historial
```

### 9.2 MAPA DE BITS

```python
mapa_bits = [
    0,  # Bloque 0: libre (0), ocupado (1)
    1,
    1,
    0,
    ...
]
# 0 = bloque libre, 1 = bloque ocupado
```

### 9.3 LISTA ENCADENADA

```python
class NodoMemoria:
    - proceso_id: int
    - direccion_inicio: int
    - tamaño: int
    - siguiente: NodoMemoria
    - estado: 'OCUPADO' | 'LIBRE'
```

---

## 10. TIMELINE DE DESARROLLO

```
Fase 1: Núcleo básico
├─ Estructuras de datos
├─ Clock y temporización
└─ Gestor de procesos básico

Fase 2: Scheduling
├─ Implementar políticas
├─ Dispatcher
└─ Cambio de contexto

Fase 3: Memoria
├─ Gestor de memoria
├─ Estrategias de asignación
└─ Cálculo de fragmentación

Fase 4: E/S
├─ Dispositivos
├─ Interrupciones
└─ Cambios de estado

Fase 5: Interfaz
├─ Visualización en tiempo real
├─ Estadísticas
└─ Reportes

Fase 6: Testing
├─ 20 procesos de prueba
├─ Comparación de políticas
└─ Generación de reportes
```

---

## 11. REFERENCIAS DE IMPLEMENTACIÓN

Esta arquitectura sigue los principios de:
- **Separación de responsabilidades**: Cada módulo tiene una función clara
- **Escalabilidad**: Fácil agregar nuevos dispositivos o políticas
- **Realismo**: Simula comportamientos reales de SO
- **Documentabilidad**: Estructura clara para el informe final

