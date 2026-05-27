# 🖥️ SIMULADOR DE SISTEMA OPERATIVO

[![Python 3.7+](https://img.shields.io/badge/python-3.7%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Development](https://img.shields.io/badge/Status-Development-orange)](https://github.com)
[![Version: 1.0](https://img.shields.io/badge/Version-1.0-green)](https://github.com)

---

## 📖 Descripción

Un simulador de **Sistema Operativo** que emula la gestión de:

- **Procesos** - 5 estados, PCB, transiciones automáticas
- **Memoria** - Asignación dinámica, fragmentación, 3 estrategias
- **Scheduling** - 4 políticas diferentes (FCFS, SJF, RR, Prioridades)
- **E/S** - Dispositivos y interrupciones (próximamente)

Desarrollado con arquitectura modular en **Python puro** (sin dependencias externas).

---

## 🚀 Inicio Rápido

### Instalación

```bash
# Solo requiere Python 3.7+
git clone <repositorio>
cd simulador_so
python --version  # Verificar
```

### Primer Programa

```bash
# Ejecutar simulador con ejemplo por defecto
python main.py

# O ver menú de ejemplos
python ejemplos.py
```

### Ejemplo Mínimo en Código

```python
from main import SimuladorSO
from enums import PoliticaScheduling

# Crear simulador
sim = SimuladorSO(politica_scheduling=PoliticaScheduling.RR)

# Agregar procesos (nombre, tamaño_KB, burst_time, prioridad, entrada)
sim.crear_proceso_usuario("P1", 128, 20, 5, 0)
sim.crear_proceso_usuario("P2", 256, 30, 5, 1)

# Ejecutar simulación
sim.ejecutar_completo()
```

---

## 📚 Documentación

### Documentos Principales

| Documento | Descripción | Páginas |
|-----------|-------------|---------|
| [`ARQUITECTURA_SIMULADOR_SO.md`](ARQUITECTURA_SIMULADOR_SO.md) | Diseño técnico detallado | 20 |
| [`GUIA_DE_USO.md`](GUIA_DE_USO.md) | Cómo usar + próximos pasos | 15 |
| [`RESUMEN_EJECUTIVO.md`](RESUMEN_EJECUTIVO.md) | Estado del proyecto | 10 |
| [`ejemplos.py`](ejemplos.py) | 6 ejemplos prácticos | código |

### Lectura Recomendada

1. **Principiante:** Comienza aquí (README) ← Estás aquí
2. **Usuario:** Luego lee `GUIA_DE_USO.md`
3. **Desarrollador:** Luego `ARQUITECTURA_SIMULADOR_SO.md`
4. **Aprendizaje:** Ejecuta `ejemplos.py`

---

## 🏗️ Arquitectura

### Componentes Principales

```
┌─────────────────────────────────────────────────────┐
│         SIMULADOR DE SISTEMA OPERATIVO              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────┐  ┌──────────────┐               │
│  │ Gestor de    │  │ Gestor de    │               │
│  │ Procesos     │  │ Memoria      │               │
│  └──────────────┘  └──────────────┘               │
│         │                  │                       │
│  ┌──────────────┐         │                       │
│  │   Scheduler  │←────────┘                       │
│  └──────────────┘                                 │
│         │                                         │
│  ┌──────────────┐                                 │
│  │  Dispatcher  │                                 │
│  └──────────────┘                                 │
│         │                                         │
│  ┌─────────────────────────────────┐              │
│  │  Clock Global (Sincronización)  │              │
│  └─────────────────────────────────┘              │
└─────────────────────────────────────────────────────┘
```

### Módulos Disponibles

| Módulo | Líneas | Descripción |
|--------|--------|-------------|
| **enums.py** | 80 | Enumeraciones y constantes |
| **clock.py** | 90 | Reloj sincronizado global |
| **pcb.py** | 350 | Process Control Block |
| **gestor_procesos.py** | 350 | Administrador de procesos |
| **gestor_memoria.py** | 450 | Asignación y fragmentación |
| **scheduler.py** | 300 | Planificador (4 políticas) |
| **dispatcher.py** | 150 | Cambio de contexto |
| **main.py** | 400 | Simulador integrado |

---

## 💻 Uso Avanzado

### Cambiar Política de Scheduling

```python
from enums import PoliticaScheduling, EstrategiaMemoria

sim = SimuladorSO(
    politica_scheduling=PoliticaScheduling.SJF,  # Shortest Job First
    estrategia_memoria=EstrategiaMemoria.BEST_FIT,
    quantum=5
)
```

### Políticas Disponibles

- **FCFS** (First Come First Served) - No expropiativo
- **SJF** (Shortest Job First) - No expropiativo
- **RR** (Round Robin) - Expropiativo con quantum
- **PRIORIDADES** - Por nivel de prioridad

### Estrategias de Memoria

- **FIRST_FIT** - Primer bloque disponible (rápido)
- **BEST_FIT** - Mejor ajuste (minimiza fragmentación)
- **WORST_FIT** - Peor ajuste (mantiene huecos grandes)

### Ejecución Paso a Paso

```python
# Ejecutar 1 paso a la vez
sim.iniciar_simulacion(max_tiempo=1000)
while sim.ejecutar_paso():
    # Hacer algo después de cada paso
    if sim.clock.obtener_tiempo() % 100 == 0:
        sim.mostrar_estado()
```

### Acceder a Estadísticas

```python
# Obtener procesos finalizados
procesos_fin = sim.gestor_procesos.obtener_todos_finalizados()

for pcb in procesos_fin:
    print(f"P{pcb.get_pid()}: Respuesta={pcb.get_tiempo_respuesta():.1f}")

# Estadísticas de memoria
uso = sim.gestor_memoria.get_uso_memoria()
print(f"Fragmentación: {uso['fragmentacion_externa']:.1f}%")

# Estadísticas del scheduler
stats = sim.scheduler.get_estadisticas()
print(f"Cambios de contexto: {stats['cambios_contexto']}")
```

---

## 📊 Ejemplos Disponibles

Ejecutar desde `ejemplos.py`:

```bash
python ejemplos.py
```

1. **Básico** - 4 procesos simples
2. **Comparar Políticas** - FCFS vs SJF vs RR vs Prioridades
3. **Comparar Memoria** - FF vs BF vs WF
4. **Prioridades** - Demostración de planificación por prioridades
5. **Paso a Paso** - Ejecución con visualización detallada
6. **Mezcla de Procesos** - Fragmentación con procesos variados

---

## 🧪 Características Implementadas

### ✅ Completado

- [x] Gestión de 5 estados de procesos
- [x] PCB con 25+ campos
- [x] Asignación de memoria en bloques (power of 2)
- [x] Cálculo de fragmentación
- [x] Scheduler con 4 políticas
- [x] Dispatcher con cambio de contexto
- [x] Clock sincronizado
- [x] Estadísticas completas

### 🚧 En Desarrollo (Fase 2)

- [ ] Gestor de E/S
- [ ] Dispositivos (Teclado, Disco, Impresora)
- [ ] Interrupciones
- [ ] Interfaz gráfica
- [ ] Suite de 20 procesos
- [ ] Comparación de combinaciones

### 📋 Planificado (Fases 3-5)

- [ ] GUI Tkinter/PyGame
- [ ] Reportes PDF
- [ ] Análisis estadístico
- [ ] Informe final
- [ ] Presentación

---

## 📈 Rendimiento

### Complejidad

| Operación | Complejidad | Notas |
|-----------|-------------|-------|
| Crear proceso | O(1) | Constante |
| Asignar memoria | O(n) | Recorre bloques |
| Scheduling (FCFS) | O(1) | Toma primero |
| Scheduling (SJF) | O(m) | Busca mínimo (m = procesos listos) |
| Cambio contexto | O(1) | Constante |

### Limites Teóricos

- **Máx procesos simultáneos:** 100 (configurable)
- **Máx memoria:** 2 GB (configurable)
- **Máx tiempo simulación:** ilimitado
- **Máx dispositivos E/S:** 3 (configurables)

---

## 🐛 Solución de Problemas

### Error: "ModuleNotFoundError"

```bash
# Asegurate que los archivos .py están en el mismo directorio
ls *.py  # Deberías ver enums.py, clock.py, etc.
```

### No hay salida

```python
# Asegurate de llamar a mostrar_resultados()
sim.ejecutar_completo()  # Esto incluye mostrar_resultados()

# O manualmente:
sim.mostrar_estado()
sim.mostrar_resultados()
```

### Procesos no ingresan

```python
# Verifica que hay suficiente memoria
memoria = sim.gestor_memoria.get_uso_memoria()
print(f"Disponible: {memoria['memoria_libre_kb']} KB")
```

---

## 🤝 Contribuciones

Para agregar nuevo código:

1. Seguir estructura modular existente
2. Documentar con docstrings
3. Usar type hints
4. Probar con `ejemplos.py`

---

## 📋 Estructura de Directorios

```
simulador_so/
├── README.md                        (este archivo)
├── ARQUITECTURA_SIMULADOR_SO.md     (documentación detallada)
├── GUIA_DE_USO.md                  (próximos pasos)
├── RESUMEN_EJECUTIVO.md            (estado del proyecto)
│
├── Código Principal:
├── main.py                         (punto de entrada)
├── enums.py                        (tipos y constantes)
├── clock.py                        (sincronización)
│
├── Gestión de Procesos:
├── pcb.py                          (bloque de control)
├── gestor_procesos.py              (administrador)
│
├── Gestión de Memoria:
├── gestor_memoria.py               (asignador y liberador)
│
├── Scheduling:
├── scheduler.py                    (planificador)
├── dispatcher.py                   (ejecutor/contexto)
│
├── Ejemplos:
├── ejemplos.py                     (6 ejemplos prácticos)
│
└── Próximas Fases:
    ├── gestor_io.py               (por implementar)
    ├── dispositivos.py            (por implementar)
    ├── gestor_interrupciones.py   (por implementar)
    └── interfaz_visual.py         (por implementar)
```

---

## 📞 Ayuda y Soporte

### Preguntas Frecuentes

**P: ¿Puedo ejecutar esto sin dependencias externas?**  
R: Sí, Python 3.7+ es lo único necesario.

**P: ¿Cuántos procesos puedo simular?**  
R: Teóricamente ilimitados, pero recomendado máximo 100 simultáneos.

**P: ¿Cómo cambio la memoria total?**  
R: Parámetro `memoria_total_kb` en SimuladorSO()

**P: ¿Puedo agregar más dispositivos E/S?**  
R: Sí, en la fase de E/S (Fase 2)

### Documentación Adicional

- Arquitectura: [`ARQUITECTURA_SIMULADOR_SO.md`](ARQUITECTURA_SIMULADOR_SO.md)
- Uso: [`GUIA_DE_USO.md`](GUIA_DE_USO.md)
- Estado: [`RESUMEN_EJECUTIVO.md`](RESUMEN_EJECUTIVO.md)

---

## 📄 Licencia

Este proyecto está bajo licencia MIT. Ver detalles en LICENSE.

---

## 👨‍💻 Autores

Equipo de Desarrollo - Universidad  
Junio 2026

---

## 🎓 Referencias de SO

Conceptos implementados basados en:
- Tanenbaum & Bos - "Sistemas Operativos Modernos"
- Silberschatz et al. - "Operating System Concepts"
- Estándares POSIX

---

## 📊 Estado del Proyecto

```
Fase 1: Arquitectura y Código Base    ✅ 100%
Fase 2: Gestión de E/S                🔄  0%
Fase 3: Interfaz Gráfica              🔄  0%
Fase 4: Evaluación y Pruebas          🔄  0%
Fase 5: Documentación Final           🔄  0%
                                      ────────
TOTAL                                 ✅ 20%
```

---

## 🚀 Próximos Pasos

1. Lee [`GUIA_DE_USO.md`](GUIA_DE_USO.md) para próximas fases
2. Ejecuta [`ejemplos.py`](ejemplos.py) para entender el sistema
3. Revisa [`ARQUITECTURA_SIMULADOR_SO.md`](ARQUITECTURA_SIMULADOR_SO.md) para detalles técnicos
4. Continúa con Fase 2: Gestión de E/S

---

**¡Gracias por usar el Simulador de Sistema Operativo!** 🎉

Para reportar bugs o sugerencias, consulta la documentación o contacta al equipo.

---

*Última actualización: Mayo 25, 2026*  
*Versión: 1.0 (Base completada)*
