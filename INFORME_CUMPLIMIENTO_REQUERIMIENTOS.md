# Informe de Cumplimiento de Requerimientos

## Estado general

El simulador queda preparado para una entrega funcional: ejecuta procesos, administra memoria, simula E/S, muestra interfaz de monitoreo, calcula metricas y permite comparar politicas de planificacion y estrategias de memoria.

## Evidencia tecnica

- Punto de entrada GUI: `app.py`
- Motor principal: `main.py`
- PCB y campos obligatorios: `pcb.py`
- Scheduler: `scheduler.py`
- Dispatcher y cambio de contexto: `dispatcher.py`
- Memoria fisica por bloques: `gestor_memoria.py`
- Colas y estados de procesos: `gestor_procesos.py`
- E/S e interrupciones: `interrupciones.py`
- Supervisor/validador: `supervisor.py`
- Verificacion automatica: `verificacion_requerimientos.py`

## Requerimientos cubiertos

| Requerimiento | Estado | Evidencia |
| --- | --- | --- |
| 5 estados de proceso | Cumple | `EstadoProceso` y transiciones en `gestor_procesos.py` |
| PCB con PC y direccion fisica inicial | Cumple | `pcb.py` |
| Cola total, listos y E/S | Cumple | `gestor_procesos.py` |
| Minimo 5 dispositivos simulados en colas | Cumple | TECLADO, DISCO, IMPRESORA, RED, USB |
| Scheduler largo, mediano y corto plazo | Cumple | admision, desbloqueo E/S y seleccion CPU |
| FCFS, SJF, Round Robin y Prioridades | Cumple | `scheduler.py` |
| Expropiativo y no expropiativo | Cumple | parametro `es_expropiativo` en `SimuladorSO` |
| Quantum inicial y modificable | Cumple | `Scheduler.cambiar_quantum` y GUI |
| Cambio de contexto | Cumple | `dispatcher.py` |
| Supervisor de errores | Cumple | `supervisor.py` |
| Tasa de fallo 0.5% acumulada | Cumple | `gestor_procesos.py` |
| Interrupciones por proceso 5 a 20 | Cumple | formula aleatoria en `pcb.py` |
| Duracion de interrupciones 5 a 20 | Cumple | formula aleatoria en `pcb.py` |
| Carga total en memoria antes de iniciar | Cumple | `ingresar_proceso` asigna memoria antes de pasar a listos |
| Direccionamiento fisico puro | Cumple | direccion base fisica en PCB |
| Stack/Heap y datos estaticos | Cumple | calculos en `pcb.py` |
| Bloques potencia de 2 | Cumple | validacion en `gestor_memoria.py` |
| Fragmentacion interna/externa | Cumple | `gestor_memoria.py` y resumen comparativo |
| Mapa de bits y lista encadenada | Cumple | `MetodoMemoria` en `gestor_memoria.py` |
| First-Fit, Best-Fit, Worst-Fit | Cumple | `gestor_memoria.py` |
| Teclado, disco e impresora | Cumple | `interrupciones.py` y GUI |
| Cancelacion/continuacion por teclado | Cumple | botones en `interfaz.py` y decisiones en `interrupciones.py` |
| Minimo 10 interrupciones totales | Cumple en prueba de 20 procesos | `verificacion_requerimientos.py` |
| Carga de 20 procesos | Cumple | GUI y script de verificacion |
| Metricas CPU, espera y respuesta | Cumple | `main.py` |
| Comparacion 4 x 2 x 3 | Cumple | `comparar_configuraciones` |
| Interfaz de monitoreo | Cumple | `interfaz.py` |

## Como verificar

Ejecutar:

```bash
python verificacion_requerimientos.py
```

Resultado esperado:

```text
VERIFICACION OK
Procesos de prueba finalizados: 20/20
Casos comparativos ejecutados: 24/24
```

Para abrir la interfaz:

```bash
python app.py
```
