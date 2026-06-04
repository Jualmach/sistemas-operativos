"""
verificacion_requerimientos.py - Prueba automatica de cierre del simulador.

Ejecuta:
1. Una carga de 20 procesos.
2. La matriz 4 politicas x 2 contextos x 3 estrategias de memoria.
"""

import contextlib
import io
import random

from main import SimuladorSO


def generar_20_procesos():
    return [
        (f"P{num}", 64 + (num * 8) % 192, 8 + (num * 3) % 28, 1 + (num % 10), num // 2)
        for num in range(1, 21)
    ]


def main():
    random.seed(2601)
    procesos = generar_20_procesos()

    sim = SimuladorSO(politica_teclado='continuar')
    for nombre, tamano, burst, prioridad, ingreso in procesos:
        sim.crear_proceso_usuario(nombre, tamano, burst, prioridad, ingreso)

    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        resumen = sim.ejecutar_sin_interfaz(max_tiempo=5000)

    assert resumen['procesos_finalizados'] == 20, resumen
    assert resumen['tiempo_total'] < 5000, resumen
    assert sim.estadisticas['total_interrupciones'] >= 10, sim.estadisticas

    matriz = SimuladorSO(politica_teclado='continuar')
    salida = io.StringIO()
    with contextlib.redirect_stdout(salida):
        resultados = matriz.comparar_configuraciones(procesos, max_tiempo=5000)

    assert len(resultados) == 24, len(resultados)
    assert min(r['procesos_finalizados'] for r in resultados) == 20, resultados

    print("VERIFICACION OK")
    print(f"Procesos de prueba finalizados: {resumen['procesos_finalizados']}/20")
    print(f"Interrupciones E/S ejecutadas: {sim.estadisticas['total_interrupciones']}")
    print(f"Casos comparativos ejecutados: {len(resultados)}/24")
    print(f"Fragmentacion externa promedio primer caso: {resultados[0]['fragmentacion_externa_promedio']:.2f}%")


if __name__ == "__main__":
    main()
