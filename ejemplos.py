"""
ejemplos.py - Ejemplos de uso del Simulador de Sistema Operativo

Este archivo contiene varios ejemplos de cómo usar el simulador
en diferentes escenarios.
"""

from main import SimuladorSO
from enums import PoliticaScheduling, EstrategiaMemoria, Constantes
from clock import Clock


# ==================== EJEMPLO 1: BÁSICO ====================

def ejemplo_1_basico():
    """
    Ejemplo 1: Simulación básica con 4 procesos.
    Usa Round Robin con First-Fit para memoria.
    """
    print("\n" + "="*70)
    print("EJEMPLO 1: SIMULACIÓN BÁSICA")
    print("="*70)
    
    # Crear simulador
    sim = SimuladorSO(
        memoria_total_kb=2048,
        tamaño_bloque_kb=64,
        politica_scheduling=PoliticaScheduling.RR,
        estrategia_memoria=EstrategiaMemoria.FIRST_FIT,
        quantum=5
    )
    
    # Agregar procesos
    # formato: (nombre, tamaño_kb, burst_time, prioridad, momento_ingreso)
    procesos = [
        ("P_A", 128, 20, 5, 0),      # Ingresa en t=0
        ("P_B", 256, 30, 5, 0),      # Ingresa en t=0
        ("P_C", 64, 10, 5, 2),       # Ingresa en t=2
        ("P_D", 192, 25, 5, 5),      # Ingresa en t=5
    ]
    
    for nombre, tam, burst, prio, entrada in procesos:
        sim.crear_proceso_usuario(nombre, tam, burst, prio, entrada)
    
    # Ejecutar
    sim.ejecutar_completo()


# ==================== EJEMPLO 2: COMPARAR POLÍTICAS ====================

def ejemplo_2_comparar_politicas():
    """
    Ejemplo 2: Comparar diferentes políticas con los mismos procesos.
    """
    print("\n" + "="*70)
    print("EJEMPLO 2: COMPARACIÓN DE POLÍTICAS")
    print("="*70)
    
    # Procesos de prueba
    procesos_prueba = [
        ("P1", 100, 15, 5, 0),
        ("P2", 150, 20, 5, 1),
        ("P3", 80, 10, 5, 2),
        ("P4", 200, 25, 5, 3),
        ("P5", 120, 12, 5, 4),
    ]
    
    politicas = [
        (PoliticaScheduling.FCFS, 10),
        (PoliticaScheduling.SJF, 10),
        (PoliticaScheduling.RR, 5),
        (PoliticaScheduling.PRIORIDADES, 10),
    ]
    
    resultados = {}
    
    for politica, quantum in politicas:
        print(f"\n{'─'*70}")
        print(f"Ejecutando con: {politica.value}")
        print(f"{'─'*70}")
        
        # Crear simulador
        sim = SimuladorSO(
            politica_scheduling=politica,
            quantum=quantum
        )
        
        # Agregar procesos
        for nombre, tam, burst, prio, entrada in procesos_prueba:
            sim.crear_proceso_usuario(nombre, tam, burst, prio, entrada)
        
        # Ejecutar
        sim.ejecutar_completo()
        
        # Extraer estadísticas
        procesos_fin = sim.gestor_procesos.obtener_todos_finalizados()
        if procesos_fin:
            tiempos_respuesta = [p.get_tiempo_respuesta() for p in procesos_fin]
            tiempos_espera = [p.get_tiempo_total_espera() for p in procesos_fin]
            
            resultados[politica.value] = {
                'respuesta_prom': sum(tiempos_respuesta) / len(tiempos_respuesta),
                'espera_prom': sum(tiempos_espera) / len(tiempos_espera),
                'procesos': len(procesos_fin)
            }
    
    # Mostrar comparación
    print("\n" + "="*70)
    print("RESUMEN COMPARATIVO")
    print("="*70)
    print(f"\n{'Política':<20} {'Respuesta':<15} {'Espera':<15} {'Procesos':<10}")
    print("─"*70)
    
    for politica, datos in resultados.items():
        print(f"{politica:<20} {datos['respuesta_prom']:<15.2f} "
              f"{datos['espera_prom']:<15.2f} {datos['procesos']:<10}")


# ==================== EJEMPLO 3: COMPARAR ESTRATEGIAS DE MEMORIA ====================

def ejemplo_3_comparar_memoria():
    """
    Ejemplo 3: Comparar First-Fit, Best-Fit y Worst-Fit.
    """
    print("\n" + "="*70)
    print("EJEMPLO 3: COMPARACIÓN DE ESTRATEGIAS DE MEMORIA")
    print("="*70)
    
    procesos_prueba = [
        ("P1", 128, 15, 5, 0),
        ("P2", 256, 20, 5, 1),
        ("P3", 64, 10, 5, 2),
        ("P4", 192, 18, 5, 3),
        ("P5", 100, 12, 5, 4),
        ("P6", 200, 22, 5, 5),
    ]
    
    estrategias = [
        EstrategiaMemoria.FIRST_FIT,
        EstrategiaMemoria.BEST_FIT,
        EstrategiaMemoria.WORST_FIT,
    ]
    
    resultados = {}
    
    for estrategia in estrategias:
        print(f"\n{'─'*70}")
        print(f"Estrategia: {estrategia.value}")
        print(f"{'─'*70}")
        
        # Crear simulador
        sim = SimuladorSO(
            politica_scheduling=PoliticaScheduling.RR,
            estrategia_memoria=estrategia,
            quantum=5
        )
        
        # Agregar procesos
        for nombre, tam, burst, prio, entrada in procesos_prueba:
            sim.crear_proceso_usuario(nombre, tam, burst, prio, entrada)
        
        # Ejecutar
        sim.ejecutar_completo()
        
        # Extraer estadísticas de memoria
        uso_final = sim.gestor_memoria.get_uso_memoria()
        
        resultados[estrategia.value] = {
            'fragmentacion': uso_final['fragmentacion_externa'],
            'uso_porcentaje': uso_final['porcentaje_uso'],
            'procesos_finalizados': len(sim.gestor_procesos.obtener_todos_finalizados())
        }
    
    # Mostrar comparación
    print("\n" + "="*70)
    print("RESUMEN COMPARATIVO DE MEMORIA")
    print("="*70)
    print(f"\n{'Estrategia':<20} {'Fragmentación':<20} {'Uso':<15} {'Procesos':<10}")
    print("─"*70)
    
    for estrategia, datos in resultados.items():
        print(f"{estrategia:<20} {datos['fragmentacion']:<20.2f}% "
              f"{datos['uso_porcentaje']:<15.2f}% {datos['procesos_finalizados']:<10}")


# ==================== EJEMPLO 4: PROCESOS CON DIFERENTES PRIORIDADES ====================

def ejemplo_4_prioridades():
    """
    Ejemplo 4: Demostrar planificación por prioridades.
    """
    print("\n" + "="*70)
    print("EJEMPLO 4: PLANIFICACIÓN POR PRIORIDADES")
    print("="*70)
    
    # Procesos con diferentes prioridades
    # Prioridad 1 = baja, 10 = alta
    procesos = [
        ("BAJO_1", 100, 15, 1, 0),      # Baja prioridad
        ("ALTO_1", 150, 20, 10, 0),     # Alta prioridad
        ("MEDIO_1", 120, 18, 5, 1),     # Media prioridad
        ("ALTO_2", 100, 12, 9, 2),      # Alta prioridad
        ("BAJO_2", 200, 25, 2, 3),      # Baja prioridad
    ]
    
    sim = SimuladorSO(
        politica_scheduling=PoliticaScheduling.PRIORIDADES,
        quantum=5
    )
    
    for nombre, tam, burst, prio, entrada in procesos:
        sim.crear_proceso_usuario(nombre, tam, burst, prio, entrada)
    
    sim.ejecutar_completo()
    
    # Mostrar orden de ejecución
    print("\n" + "="*70)
    print("ANÁLISIS DE PRIORIDADES")
    print("="*70)
    
    procesos_fin = sim.gestor_procesos.obtener_todos_finalizados()
    print("\nOrden de Finalización:")
    for i, pcb in enumerate(procesos_fin, 1):
        print(f"{i}. {pcb.get_nombre()} (Prioridad: {pcb.get_prioridad()})")


# ==================== EJEMPLO 5: EJECUCIÓN PASO A PASO ====================

def ejemplo_5_paso_a_paso():
    """
    Ejemplo 5: Ejecutar la simulación paso a paso con visualización.
    """
    print("\n" + "="*70)
    print("EJEMPLO 5: EJECUCIÓN PASO A PASO")
    print("="*70)
    
    # Crear simulador con pocos procesos
    sim = SimuladorSO(
        politica_scheduling=PoliticaScheduling.FCFS,
        quantum=5
    )
    
    # Solo 2 procesos para visualización clara
    sim.crear_proceso_usuario("Proceso_1", 128, 10, 5, 0)
    sim.crear_proceso_usuario("Proceso_2", 256, 15, 5, 1)
    
    # Iniciar
    sim.iniciar_simulacion(max_tiempo=100)
    
    # Ejecutar paso a paso
    paso = 0
    mientras_ejecuta = True
    
    while mientras_ejecuta:
        paso += 1
        mientras_ejecuta = sim.ejecutar_paso()
        
        # Mostrar cada paso
        if paso % 5 == 0:  # Mostrar cada 5 pasos
            tiempo = Clock().obtener_tiempo()
            proceso = sim.gestor_procesos.obtener_ejecutando()
            
            print(f"\nPaso {paso} (t={tiempo:.0f}):")
            if proceso:
                print(f"  Ejecutando: P{proceso.get_pid()} ({proceso.get_nombre()})")
                print(f"  CPU usado: {proceso.tiempo_total_cpu:.1f}/{proceso.get_burst_time()}")
            else:
                print(f"  CPU: inactiva")
            
            # Mostrar colas
            conteo = sim.gestor_procesos.contar_por_estado()
            print(f"  Estados: NUEVO={conteo['NUEVO']}, LISTO={conteo['LISTO']}, "
                  f"BLOQUEADO={conteo['BLOQUEADO']}, FINALIZADO={conteo['FINALIZADO']}")


# ==================== EJEMPLO 6: PROCESOS GRANDES Y PEQUEÑOS ====================

def ejemplo_6_mezcla_procesos():
    """
    Ejemplo 6: Mezcla de procesos grandes y pequeños.
    Útil para observar fragmentación de memoria.
    """
    print("\n" + "="*70)
    print("EJEMPLO 6: MEZCLA DE PROCESOS GRANDES Y PEQUEÑOS")
    print("="*70)
    
    procesos = [
        # Procesos grandes
        ("GRANDE_1", 512, 30, 5, 0),
        ("GRANDE_2", 768, 35, 5, 1),
        ("GRANDE_3", 512, 28, 5, 2),
        
        # Procesos medianos
        ("MEDIO_1", 256, 20, 5, 1),
        ("MEDIO_2", 256, 20, 5, 2),
        
        # Procesos pequeños
        ("PEQUEÑO_1", 64, 10, 5, 0),
        ("PEQUEÑO_2", 64, 10, 5, 1),
        ("PEQUEÑO_3", 64, 10, 5, 2),
        ("PEQUEÑO_4", 64, 10, 5, 3),
        ("PEQUEÑO_5", 64, 10, 5, 4),
    ]
    
    # Comparar Best-Fit vs Worst-Fit para fragmentación
    for estrategia in [EstrategiaMemoria.BEST_FIT, EstrategiaMemoria.WORST_FIT]:
        print(f"\n{'─'*70}")
        print(f"Estrategia: {estrategia.value}")
        print(f"{'─'*70}")
        
        sim = SimuladorSO(
            politica_scheduling=PoliticaScheduling.RR,
            estrategia_memoria=estrategia,
            quantum=5
        )
        
        for nombre, tam, burst, prio, entrada in procesos:
            sim.crear_proceso_usuario(nombre, tam, burst, prio, entrada)
        
        sim.ejecutar_completo()
        
        # Mostrar fragmentación final
        uso = sim.gestor_memoria.get_uso_memoria()
        print(f"\nFragmentación Final: {uso['fragmentacion_externa']:.2f}%")
        print(f"Memoria Libre: {uso['memoria_libre_kb']} KB")


# ==================== FUNCIÓN PRINCIPAL ====================

def main():
    """Ejecuta los ejemplos"""
    
    ejemplos = {
        '1': ('Básico', ejemplo_1_basico),
        '2': ('Comparar Políticas', ejemplo_2_comparar_politicas),
        '3': ('Comparar Memoria', ejemplo_3_comparar_memoria),
        '4': ('Prioridades', ejemplo_4_prioridades),
        '5': ('Paso a Paso', ejemplo_5_paso_a_paso),
        '6': ('Mezcla de Procesos', ejemplo_6_mezcla_procesos),
    }
    
    print("\n" + "="*70)
    print("EJEMPLOS DEL SIMULADOR DE SISTEMA OPERATIVO")
    print("="*70)
    
    print("\nEligir ejemplo:")
    for clave, (nombre, _) in ejemplos.items():
        print(f"  {clave}: {nombre}")
    print("  0: Salir")
    
    opcion = input("\nOpción: ").strip()
    
    if opcion in ejemplos:
        nombre, funcion = ejemplos[opcion]
        print(f"\nEjecutando: {nombre}")
        funcion()
    elif opcion == '0':
        print("Saliendo...")
    else:
        print("Opción inválida")


if __name__ == "__main__":
    # Ejecutar ejemplo específico o menú
    # ejemplo_1_basico()  # Descomenta para ejecutar automáticamente
    
    # O mostrar menú
    main()
