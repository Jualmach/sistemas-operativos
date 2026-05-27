# GUÍA DE USO - SIMULADOR DE SISTEMA OPERATIVO

## Estado Actual del Proyecto

Se ha completado la **ARQUITECTURA** y el **CÓDIGO BASE** del simulador con:

✅ Diseño modular completo (8 módulos principales)
✅ Implementación de PCB (Process Control Block)
✅ Gestor de Procesos con 5 estados
✅ Gestor de Memoria con 3 estrategias (FF, BF, WF)
✅ Scheduler con 4 políticas (FCFS, SJF, RR, Prioridades)
✅ Dispatcher con cambio de contexto
✅ Clock sincronizado para toda la simulación
✅ Sistema de estadísticas integrado

---

## Estructura de Archivos

```
simulador_so/
├── ARQUITECTURA_SIMULADOR_SO.md     # Documentación detallada
├── enums.py                          # Enumeraciones y constantes
├── clock.py                          # Reloj global
├── pcb.py                            # Process Control Block
├── gestor_procesos.py                # Administrador de procesos
├── gestor_memoria.py                 # Administrador de memoria
├── scheduler.py                      # Planificador de procesos
├── dispatcher.py                     # Despachador/cambio de contexto
├── main.py                           # Punto de entrada
│
├── SIGUIENTE A IMPLEMENTAR:
├── gestor_io.py                      # Gestor de E/S
├── dispositivos.py                   # Simulación de dispositivos
├── gestor_interrupciones.py          # Administrador de interrupciones
├── interfaz_visual.py                # GUI (tkinter o similar)
└── README.md                         # Documentación final
```

---

## Cómo Ejecutar la Versión Actual

### Prerrequisitos
```bash
# Python 3.7+
python --version

# No se requieren librerías externas para la versión actual
```

### Ejecución Básica

```bash
# En el directorio del proyecto
python main.py

# Salida esperada:
# ======================================================================
# INICIANDO SIMULADOR DE SISTEMA OPERATIVO
# ======================================================================
# Política: RR
# Estrategia Memoria: FIRST_FIT
# Quantum: 5
# Procesos a procesar: 4
# ======================================================================
```

### Ejemplo de Código para Usar el Simulador

```python
from main import SimuladorSO
from enums import PoliticaScheduling, EstrategiaMemoria

# Crear simulador
sim = SimuladorSO(
    memoria_total_kb=2048,
    tamaño_bloque_kb=64,
    politica_scheduling=PoliticaScheduling.RR,
    estrategia_memoria=EstrategiaMemoria.FIRST_FIT,
    quantum=10
)

# Crear procesos (nombre, tamaño_kb, burst_time, prioridad, momento_ingreso)
sim.crear_proceso_usuario("Proceso_1", 128, 20, 5, 0)
sim.crear_proceso_usuario("Proceso_2", 256, 30, 3, 2)
sim.crear_proceso_usuario("Proceso_3", 64, 10, 7, 5)

# Ejecutar simulación
sim.ejecutar_completo()

# O ejecutar paso a paso
sim.iniciar_simulacion(max_tiempo=1000)
while sim.ejecutar_paso():
    if clock.obtener_tiempo() % 100 == 0:
        sim.mostrar_estado()
```

---

## PRÓXIMOS PASOS (ORDEN DE PRIORIDAD)

### Fase 1: COMPLETAR E/S (SEMANA 1)

**1.1 - Implementar Gestor de E/S** (`gestor_io.py`)
- Administración de colas de dispositivos
- Generación de interrupciones de E/S
- Control de tiempos de operación

```python
class GestorIO:
    - dispositivos: dict
    - colas_espera: dict
    - solicitar_io(proceso, dispositivo)
    - procesar_io(dispositivo)
    - completar_io()
```

**1.2 - Implementar Dispositivos** (`dispositivos.py`)
- Clase base: Dispositivo
- Subclases: Teclado, Disco, Impresora
- Simulación de tiempos aleatorios (5-20 unidades)

```python
class Dispositivo:
    - tipo: DispositivoIO
    - cola_espera: deque
    - tiempo_operacion_min/max
    - procesar()

class Teclado(Dispositivo):
    - Capturar señal (cancelación/continuación)

class Disco(Dispositivo):
    - Tiempos realistas de lectura/escritura

class Impresora(Dispositivo):
    - Simulación de impresión
```

**1.3 - Gestor de Interrupciones** (`gestor_interrupciones.py`)
- Tipos de interrupciones (TIMER, IO_ENTRADA, IO_SALIDA, ERROR)
- Cola de interrupciones
- Manejo de cada tipo

```python
class GestorInterrupciones:
    - cola_interrupciones: deque
    - procesar_interrupcion(interrupcion)
    - generar_interrupcion_aleatoria()
```

### Fase 2: INTEGRACIÓN E/S (SEMANA 2)

**2.1 - Integrar módulos de E/S en main.py**
- Conectar GestorIO con GestorProcesos
- Manejar cambios de estado (EJECUTANDO → BLOQUEADO → LISTO)
- Invocar scheduler cuando proceso se bloquea

**2.2 - Manejo de errores**
- Generar errores aleatorios (0.5%)
- Registrar en PCB
- Actualizar estadísticas

**2.3 - Generación aleatoria mejorada**
```python
# Número de interrupciones por proceso (5-20)
num_interrupciones = random.randint(5, 20)

# Duración de cada interrupción (5-20)
duracion = random.randint(5, 20)

# Generación de errores
tiene_error = random.random() < 0.005

# Fórmulas matemáticas a documentar en informe
```

### Fase 3: INTERFAZ GRÁFICA (SEMANA 3)

**3.1 - Crear interfaz visual** (`interfaz_visual.py`)

Opciones:
- **Opción A: Tkinter** (Sin dependencias)
  ```python
  import tkinter as tk
  from tkinter import ttk
  
  class InterfazSO:
      - mostrar_estado_real_time()
      - graficar_procesos()
      - visualizar_memoria()
      - mostrar_dispositivos()
  ```

- **Opción B: PyGame** (Para gráficos más avanzados)
  - Instalación: `pip install pygame`
  - Mejor para animaciones

- **Opción C: Consola mejorada** (Más simple, sin dependencias)
  - Usar ANSI colors
  - ASCII art para visualización

**3.2 - Pantalla principal debe mostrar:**

```
┌──────────────────────────────────────────────────────────┐
│         SIMULADOR DE SISTEMA OPERATIVO v1.0             │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  Tiempo: 2550 | Velocidad: 1.0x | Pausa: [P]           │
│                                                          │
│  ┌─ PROCESOS ──────────────────────────────────────┐    │
│  │ NUEVO (2):      [P5, P6]                        │    │
│  │ LISTO (3):      [P1, P3, P7]                    │    │
│  │ EJECUTANDO:     P2 (CPU: 15.5/20)              │    │
│  │ BLOQUEADO (2):  [P4-DISCO(8/30), P8-IMPRE...]  │    │
│  │ FINALIZADO (4): [P0, P9, P10, P11]             │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ MEMORIA ───────────────────────────────────────┐    │
│  │ [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]     │    │
│  │ 1024/2048 KB (50.0%) | Fragmentación: 12.5%    │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  ┌─ DISPOSITIVOS ──────────────────────────────────┐    │
│  │ Teclado:   [Libre]                              │    │
│  │ Disco:     [P4: 8/30] Cola: 2 procesos        │    │
│  │ Impresora: [P8: 15/40] Cola: 3 procesos       │    │
│  └─────────────────────────────────────────────────┘    │
│                                                          │
│  [Ejecutar]  [Pausa]  [Paso]  [Reset]  [Salir]         │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

### Fase 4: EVALUACIÓN CON 20 PROCESOS (SEMANA 4)

**4.1 - Crear suite de prueba**

```python
# 20 procesos predefinidos
PROCESOS_PRUEBA = [
    ("P1", 64, 10, 5, 0),
    ("P2", 128, 15, 3, 1),
    ("P3", 256, 25, 7, 2),
    # ... hasta 20 procesos
]

# Ejecutar con cada política
politicas = [
    PoliticaScheduling.FCFS,
    PoliticaScheduling.SJF,
    PoliticaScheduling.RR,
    PoliticaScheduling.PRIORIDADES
]

# Ejecutar con cada estrategia de memoria
estrategias = [
    EstrategiaMemoria.FIRST_FIT,
    EstrategiaMemoria.BEST_FIT,
    EstrategiaMemoria.WORST_FIT
]
```

**4.2 - Generar reportes comparativos**

Para cada combinación (política × estrategia):
- Tiempo promedio de respuesta
- Tiempo promedio de espera
- Fragmentación de memoria promedio
- Total de cambios de contexto

**4.3 - Crear tabla de resultados**

```
┌─────────────────┬──────────┬───────────┬─────────────────┐
│ Política        │ Respuesta│ Espera    │ Fragmentación   │
├─────────────────┼──────────┼───────────┼─────────────────┤
│ FCFS (FF)       │  125.5   │   245.3   │     15.2%       │
│ FCFS (BF)       │  125.5   │   245.3   │     12.8%       │
│ FCFS (WF)       │  125.5   │   245.3   │     18.5%       │
│ SJF (FF)        │   95.2   │   180.5   │     14.5%       │
│ ...             │   ...    │   ...     │      ...        │
└─────────────────┴──────────┴───────────┴─────────────────┘
```

### Fase 5: DOCUMENTACIÓN FINAL (SEMANA 5)

**5.1 - Informe Técnico**

```
Índice del Informe:
1. Objetivo general y específicos
2. Problemática resuelta
3. Análisis del sistema
4. Diseño e implementación
5. Resultados y conclusiones
   - Mejor política de scheduling
   - Mejor estrategia de memoria
   - Análisis de fragmentación
6. Apéndices (código, manuales)
```

**5.2 - Manuales**

- Manual de instalación
- Manual de usuario
- Manual técnico (arquitectura)
- Documentación de API (docstrings)

**5.3 - Presentación PowerPoint**

30 minutos total:
- 15 min: Explicación del proyecto (5 slides por integrante)
- 10 min: Demostración en vivo
- 5 min: Preguntas

---

## Checklist de Implementación

### Fase 1: E/S (Semana 1)
- [ ] Implementar `gestor_io.py`
- [ ] Implementar `dispositivos.py` (3 dispositivos)
- [ ] Implementar `gestor_interrupciones.py`
- [ ] Integrar módulos en `main.py`
- [ ] Pruebas básicas de E/S

### Fase 2: Integración (Semana 2)
- [ ] Manejo de cambios de estado por E/S
- [ ] Generación de interrupciones aleatorias
- [ ] Manejo de errores (0.5%)
- [ ] Fórmulas matemáticas documentadas
- [ ] Pruebas de interrupciones

### Fase 3: Interfaz (Semana 3)
- [ ] Crear interfaz visual
- [ ] Mostrar estados en tiempo real
- [ ] Visualizar memoria
- [ ] Mostrar dispositivos
- [ ] Controles (play, pause, step)

### Fase 4: Evaluación (Semana 4)
- [ ] Crear suite de 20 procesos
- [ ] Ejecutar 4 políticas × 3 estrategias
- [ ] Recolectar estadísticas
- [ ] Generar tablas comparativas
- [ ] Análisis de resultados

### Fase 5: Documentación (Semana 5)
- [ ] Redactar informe técnico
- [ ] Crear manuales
- [ ] Generar presentación
- [ ] Prueba de presentación
- [ ] Validación final

---

## Comandos Útiles

```bash
# Ejecutar simulador actual
python main.py

# Ejecutar con debugging
python -m pdb main.py

# Ejecutar pruebas unitarias (cuando existan)
python -m pytest tests/

# Generar reporte de cobertura
coverage run -m pytest && coverage report

# Limpiar caché
find . -type d -name __pycache__ -exec rm -r {} +
```

---

## Tips para Desarrollo

1. **Usar el Clock singleton** para sincronizar todo
2. **Registrar en PCB** todos los cambios importantes
3. **Usar enumeraciones** en lugar de strings
4. **Documentar con docstrings** en cada función
5. **Validar parámetros** al inicio de funciones
6. **Usar type hints** (Python 3.7+)

---

## Referencias de Código Útil

### Generar números aleatorios
```python
import random

# Interrupciones: 5-20
num_int = random.randint(5, 20)

# Duración: 5-20
duracion = random.randint(5, 20)

# Errores: 0.5% (5 de 1000)
tiene_error = random.random() < 0.005

# Elemento aleatorio
dispositivo = random.choice(['TECLADO', 'DISCO', 'IMPRESORA'])
```

### Usar deque para colas
```python
from collections import deque

cola = deque()
cola.append(item)           # Agregar
item = cola.popleft()       # Sacar
cola.remove(item)           # Remover específico
len(cola)                   # Contar
```

### Enumeraciones
```python
from enum import Enum

class Estado(Enum):
    NUEVO = "NUEVO"
    LISTO = "LISTO"

estado = Estado.NUEVO
print(estado.value)  # "NUEVO"
```

---

## Contacto y Soporte

Para dudas específicas durante el desarrollo:
1. Revisar ARQUITECTURA_SIMULADOR_SO.md
2. Revisar docstrings del código
3. Consultar con el grupo de trabajo

---

**Última actualización: 2026**
**Versión: 0.1 (Base completada)**
