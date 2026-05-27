from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.live import Live

console = Console()

"""
main.py - Simulador de Sistema Operativo
Punto de entrada del sistema
"""

from enums import (
    Constantes, EstadoProceso, PoliticaScheduling, 
    EstrategiaMemoria, TipoInterrupcion, DispositivoIO
)
from clock import Clock
from pcb import PCB
from gestor_procesos import GestorProcesos
from gestor_memoria import GestorMemoria
from scheduler import Scheduler
from dispatcher import Dispatcher
import random


class SimuladorSO:
    
    def __init__(self,
                 memoria_total_kb=Constantes.MEMORIA_TOTAL_KB,
                 tamaño_bloque_kb=Constantes.TAMAÑO_BLOQUE_KB,
                 politica_scheduling=PoliticaScheduling.RR,
                 estrategia_memoria=EstrategiaMemoria.FIRST_FIT,
                 quantum=Constantes.QUANTUM_DEFECTO):
        """
        Inicializa el simulador.
        
        Args:
            memoria_total_kb: Tamaño total de memoria
            tamaño_bloque_kb: Tamaño de cada bloque
            politica_scheduling: Política de scheduling a usar
            estrategia_memoria: Estrategia de asignación de memoria
            quantum: Quantum para Round Robin
        """
        self.clock = Clock()
        self.gestor_procesos = GestorProcesos()
        self.gestor_memoria = GestorMemoria(
            memoria_total_kb=memoria_total_kb,
            tamaño_bloque_kb=tamaño_bloque_kb,
            estrategia=estrategia_memoria
        )
        self.scheduler = Scheduler(
            self.gestor_procesos,
            politica=politica_scheduling,
            quantum=quantum
        )
        self.dispatcher = Dispatcher(self.gestor_procesos)
        
        # Control de simulación
        self.en_ejecucion = False
        self.max_tiempo = 10000  # Máximo tiempo de simulación
        self.procesos_cola_entrada = []  # Procesos pendientes por ingresar
        self.tiempo_proximo_ingreso = 0
        
        # Estadísticas
        self.estadisticas = {
            'tiempo_inicio': 0,
            'tiempo_fin': 0,
            'total_cambios_contexto': 0,
            'total_interrupciones': 0
        }
    
    # ==================== GESTIÓN DE PROCESOS ====================
    
    def crear_proceso_usuario(self, nombre, tamaño_kb, burst_time, prioridad=5, momento_ingreso=0):
        """
        Crea un proceso de usuario para ingreso futuro.
        
        Args:
            nombre: Nombre del proceso
            tamaño_kb: Tamaño en KB
            burst_time: Tiempo estimado de CPU
            prioridad: Nivel de prioridad
            momento_ingreso: En qué momento ingresa a la simulación
        """
        pcb = self.gestor_procesos.crear_proceso(nombre, tamaño_kb, burst_time, prioridad)
        if pcb:
            self.procesos_cola_entrada.append({
                'pcb': pcb,
                'momento': momento_ingreso
            })
            # Ordenar por momento de ingreso
            self.procesos_cola_entrada.sort(key=lambda x: x['momento'])
    
    def ingresar_proceso(self, pcb):
        """
        Ingresa un proceso al sistema (NUEVO).
        
        Args:
            pcb: PCB del proceso
            
        Returns:
            bool: True si fue exitoso
        """
        # Intentar asignar memoria
        direccion = self.gestor_memoria.asignar_memoria(pcb)
        
        if direccion is None:
            # No hay memoria disponible
            return False
        
        # Asignar dirección al PCB
        pcb.set_direccion_memoria(direccion)
        
        # Agregar a colas del gestor
        self.gestor_procesos.agregar_proceso(pcb)
        
        return True
    
    # ==================== CONTROL DE SIMULACIÓN ====================
    
    def iniciar_simulacion(self, max_tiempo=10000):
        """
        Inicia la simulación.
        
        Args:
            max_tiempo: Tiempo máximo de simulación
        """
        self.en_ejecucion = True
        self.max_tiempo = max_tiempo
        self.estadisticas['tiempo_inicio'] = self.clock.obtener_tiempo()
        
        print(f"\n{'='*70}")
        print("INICIANDO SIMULADOR DE SISTEMA OPERATIVO")
        print(f"{'='*70}")
        print(f"Política: {self.scheduler.politica.value}")
        print(f"Estrategia Memoria: {self.gestor_memoria.estrategia.value}")
        print(f"Quantum: {self.scheduler.quantum}")
        print(f"Procesos a procesar: {len(self.procesos_cola_entrada)}")
        print(f"{'='*70}\n")
    
    def detener_simulacion(self):
        """Detiene la simulación"""
        self.en_ejecucion = False
        self.estadisticas['tiempo_fin'] = self.clock.obtener_tiempo()
    
    def ejecutar_paso(self):
        """
        Ejecuta un paso de la simulación.
        
        Returns:
            bool: True si hay algo que ejecutar, False si terminó
        """
        if not self.en_ejecucion:
            return False
        
        tiempo_actual = self.clock.obtener_tiempo()
        
        # ==================== CONDICIÓN DE PARADA CORRECTA ====================
        # Si no hay procesos pendientes por entrar, ni nuevos, ni listos, ni en CPU, ni bloqueados: terminamos.
        if (len(self.procesos_cola_entrada) == 0 and 
            len(self.gestor_procesos.cola_nuevo) == 0 and 
            len(self.gestor_procesos.cola_listos) == 0 and 
            self.gestor_procesos.obtener_ejecutando() is None and 
            self.gestor_procesos.contar_bloqueados() == 0):
            self.detener_simulacion()
            return False
        # ======================================================================
        
        # 1. Verificar procesos a ingresar
        self._ingresar_procesos_pendientes(tiempo_actual)
        
        # 2. Invocar scheduler si no hay proceso ejecutando
        if not self.gestor_procesos.obtener_ejecutando():
            siguiente = self._invocar_scheduler_corto_plazo()
            if siguiente:
                self.dispatcher.cambiar_contexto(siguiente)
        
        # 3. Ejecutar instrucción del proceso actual
        proceso_actual = self.gestor_procesos.obtener_ejecutando()
        if proceso_actual:
            proceso_actual.pausar_ejecucion(1)  # Simular 1 unidad de tiempo ejecutando
            self.dispatcher.ejecutar_instruccion(proceso_actual, quantum=1)
            
            # Verificar si terminó
            if proceso_actual.get_burst_time_restante() <= 0:
                self.gestor_procesos.finalizar_proceso(proceso_actual, codigo_error=0)
                print(f"[{tiempo_actual:.1f}] Proceso P{proceso_actual.get_pid()} FINALIZADO")
            
            # Para RR, verificar si quantum se agotó
            elif self.scheduler.politica == PoliticaScheduling.RR:
                if hasattr(proceso_actual, 'quantum_restante') and proceso_actual.quantum_restante <= 0:
                    # Invocar scheduler expropiativo
                    siguiente = self.scheduler.invocar_expropiativo("QUANTUM_EXPIRADO")
                    if siguiente:
                        self.dispatcher.cambiar_contexto(siguiente)
        
        # 4. Incrementar reloj
        self.clock.incrementar_tiempo(1)
        
        # 5. Verificar condición de finalización por tiempo máximo de seguridad
        if tiempo_actual >= self.max_tiempo:
            self.detener_simulacion()
            return False
        
        return True
    
    def _ingresar_procesos_pendientes(self, tiempo_actual):
        """
        Ingresa procesos pendientes en el momento adecuado.
        
        Args:
            tiempo_actual: Tiempo actual de simulación
        """
        while self.procesos_cola_entrada:
            item = self.procesos_cola_entrada[0]
            if item['momento'] <= tiempo_actual:
                pcb = item['pcb']
                if self.ingresar_proceso(pcb):
                    # Ingreso exitoso
                    self.gestor_procesos.planificacion_largo_plazo(pcb)
                    print(f"[{tiempo_actual:.1f}] Proceso P{pcb.get_pid()} INGRESADO ({pcb.get_tamaño()}KB)")
                    self.procesos_cola_entrada.pop(0)
                else:
                    # No hay memoria, esperar
                    print(f"[{tiempo_actual:.1f}] ⚠️ No hay memoria para P{pcb.get_pid()}")
                    break
            else:
                break
    
    def _invocar_scheduler_corto_plazo(self):
        """Invoca el scheduler de corto plazo"""
        return self.scheduler.planificacion_corto_plazo()
    
    # ==================== EJECUCIÓN COMPLETA ====================
    
    def ejecutar_completo(self):
        """
        Ejecuta la simulación completa mostrando la interfaz dinámica en línea.
        """
        import time
        total_procesos_esperados = len(self.procesos_cola_entrada)
        
        self.iniciar_simulacion()
        
        while self.ejecutar_paso():
            # Dibujamos el panel de control actualizado en este tick de tiempo
            self.renderizar_interfaz_linea()
            
            # Control de velocidad (0.2 segundos por paso para que sea legible en consola)
            time.sleep(0.2)
            
            # Verificación del Criterio de Parada Exacto
            finalizados = len(self.gestor_procesos.obtener_todos_finalizados())
            if finalizados == total_procesos_esperados:
                break
        
        # Una última renderización al finalizar el ciclo de vida del último proceso
        self.renderizar_interfaz_linea()
        
        # Detener el simulador e imprimir el reporte formal exigido por la rúbrica
        self.detener_simulacion()
        self.mostrar_resultados()

    def renderizar_interfaz_linea(self):
        """
        Interfaz visual moderna usando Rich.
        """

        import os

        os.system('cls' if os.name == 'nt' else 'clear')

        tiempo_actual = self.clock.obtener_tiempo()
        conteo = self.gestor_procesos.contar_por_estado()

        # =========================
        # TABLA CPU
        # =========================
        tabla_cpu = Table(title="CPU / Dispatcher")

        tabla_cpu.add_column("Campo", style="cyan")
        tabla_cpu.add_column("Valor", style="green")

        proceso_cpu = self.gestor_procesos.obtener_ejecutando()

        if proceso_cpu:
            tabla_cpu.add_row("Proceso", proceso_cpu.get_nombre())
            tabla_cpu.add_row("PID", str(proceso_cpu.get_pid()))
            tabla_cpu.add_row("Burst Restante", str(proceso_cpu.get_burst_time_restante()))
            tabla_cpu.add_row("Quantum", str(proceso_cpu.quantum_restante))
            tabla_cpu.add_row("PC", str(proceso_cpu.get_pc()))
        else:
            tabla_cpu.add_row("Estado", "CPU IDLE")

        # =========================
        # TABLA COLAS
        # =========================
        tabla_colas = Table(title="Colas del Sistema")

        tabla_colas.add_column("Cola", style="magenta")
        tabla_colas.add_column("Contenido", style="yellow")

        listos = [f"P{p.get_pid()}" for p in self.gestor_procesos.cola_listos]

        tabla_colas.add_row(
            "Ready",
            ", ".join(listos) if listos else "Vacía"
        )

        bloqueados_dict = self.gestor_procesos.obtener_bloqueados_por_dispositivo()

        for dev, q in bloqueados_dict.items():
            procesos = [f"P{p.get_pid()}" for p in q]

            tabla_colas.add_row(
                f"Block {dev}",
                ", ".join(procesos) if procesos else "Vacía"
            )

        # =========================
        # TABLA MEMORIA
        # =========================
        uso = self.gestor_memoria.get_uso_memoria()

        tabla_memoria = Table(title="Estado de Memoria")

        tabla_memoria.add_column("Métrica", style="blue")
        tabla_memoria.add_column("Valor", style="red")

        tabla_memoria.add_row(
            "Uso",
            f"{uso['memoria_ocupada_kb']} / {uso['memoria_total_kb']} KB"
        )

        tabla_memoria.add_row(
            "Porcentaje",
            f"{uso['porcentaje_uso']:.1f}%"
        )

        tabla_memoria.add_row(
            "Fragmentación",
            f"{uso['fragmentacion_externa']:.1f}%"
        )

        # =========================
        # HEADER
        # =========================
        console.rule(f"[bold green]SIMULADOR SO UNI-FIIS | t={tiempo_actual:.1f}")

        console.print(
            f"[cyan]Política:[/cyan] {self.scheduler.politica.value}   "
            f"[yellow]Quantum:[/yellow] {self.scheduler.quantum}"
        )

        console.print(
            f"[green]Nuevos:[/green] {conteo.get('NUEVO',0)}   "
            f"[blue]Listos:[/blue] {conteo.get('LISTO',0)}   "
            f"[red]Bloqueados:[/red] {conteo.get('BLOQUEADO',0)}   "
            f"[magenta]Finalizados:[/magenta] {conteo.get('FINALIZADO',0)}"
        )

        console.print(tabla_cpu)
        console.print(tabla_colas)
        console.print(tabla_memoria)
        
    # ==================== REPORTE Y ESTADÍSTICAS ====================
    
    def mostrar_estado(self):
        """Muestra el estado actual del simulador"""
        print("\n" + "="*70)
        print(f"ESTADO DEL SIMULADOR (t={self.clock.obtener_tiempo():.1f})")
        print("="*70)
        
        # Procesos
        conteo = self.gestor_procesos.contar_por_estado()
        print(f"\nPROCESOS:")
        for estado, cantidad in conteo.items():
            print(f"  {estado}: {cantidad}")
        
        # Memoria
        uso = self.gestor_memoria.get_uso_memoria()
        print(f"\nMEMORIA:")
        print(f"  Usada: {uso['memoria_ocupada_kb']}/{uso['memoria_total_kb']} KB ({uso['porcentaje_uso']:.1f}%)")
        print(f"  Fragmentación Externa: {uso['fragmentacion_externa']:.1f}%")
        print(f"  Procesos Activos: {uso['procesos_activos']}")
        
        # Scheduler
        print(f"\nSCHEDULER:")
        print(f"  Política: {self.scheduler.politica.value}")
        print(f"  Invocaciones: {self.scheduler.invocaciones}")
        print(f"  Cambios de Contexto: {self.scheduler.cambios_contexto}")
        
        print()
    
    def mostrar_resultados(self):
        """
        Muestra el informe final con las estadísticas reales del sistema.
        """
        print("\n" + "="*70)
        print("                      RESULTADOS DE LA SIMULACIÓN")
        print("="*70)
        tiempo_final = self.clock.obtener_tiempo()
        print(f"Tiempo Total de Simulación: {tiempo_final:.2f} unidades")
        
        finalizados = self.gestor_procesos.obtener_todos_finalizados()
        print(f"Procesos Finalizados: {len(finalizados)}")
        print("\nESTADÍSTICAS POR PROCESO:")
        print(f"{'PID':<6}{'Nombre':<15}{'Resp':<10}{'Espera':<10}{'CPU':<10}{'E/S':<10}")
        print("-"*70)
        
        suma_espera = 0
        suma_respuesta = 0
        
        # Ordenamos por PID para que la salida sea consistente
        for pcb in sorted(finalizados, key=lambda x: x.get_pid()):
            t_resp = pcb.get_tiempo_respuesta()
            t_espera = pcb.get_tiempo_total_espera()
            
            suma_respuesta += t_resp
            suma_espera += t_espera
            
            print(f"{pcb.get_pid():<6}"
                  f"{pcb.get_nombre():<15}"
                  f"{t_resp:<10.1f}"
                  f"{t_espera:<10.1f}"
                  f"{pcb.tiempo_total_cpu:<10.1f}"
                  f"{pcb.tiempo_total_io:<10.1f}")
                  
        print("-"*70)
        if finalizados:
            print(f"{'PROM':<21}{suma_respuesta/len(finalizados):<10.1f}{suma_espera/len(finalizados):<10.1f}")
        print("="*70 + "\n")
    
    def comparar_politicas(self, procesos_test):
        """
        Compara diferentes políticas de scheduling.
        
        Args:
            procesos_test: Lista de (nombre, tamaño, burst_time, prioridad, entrada)
        """
        politicas = [
            (PoliticaScheduling.FCFS, 10),
            (PoliticaScheduling.SJF, 10),
            (PoliticaScheduling.RR, 5),
            (PoliticaScheduling.PRIORIDADES, 10)
        ]
        
        resultados = {}
        
        for politica, quantum in politicas:
            print(f"\n\n{'='*70}")
            print(f"EJECUTANDO CON POLÍTICA: {politica.value}")
            print(f"{'='*70}")
            
            # Crear nuevo simulador
            sim = SimuladorSO(
                politica_scheduling=politica,
                quantum=quantum
            )
            
            # Agregar procesos
            for nombre, tamaño, burst, prio, entrada in procesos_test:
                sim.crear_proceso_usuario(nombre, tamaño, burst, prio, entrada)
            
            # Ejecutar
            sim.ejecutar_completo()
            
            # Guardar resultados
            procesos_fin = sim.gestor_procesos.obtener_todos_finalizados()
            if procesos_fin:
                tiempos_respuesta = [p.get_tiempo_respuesta() for p in procesos_fin]
                tiempos_espera = [p.get_tiempo_total_espera() for p in procesos_fin]
                
                resultados[politica.value] = {
                    'tiempo_respuesta_promedio': sum(tiempos_respuesta) / len(tiempos_respuesta),
                    'tiempo_espera_promedio': sum(tiempos_espera) / len(tiempos_espera),
                    'procesos_finalizados': len(procesos_fin)
                }
        
        # Mostrar comparación
        print(f"\n\n{'='*70}")
        print("COMPARACIÓN DE POLÍTICAS")
        print(f"{'='*70}")
        print(f"{'Política':<20} {'Respuesta Prom':<20} {'Espera Prom':<20}")
        print("-" * 60)
        
        for politica, datos in resultados.items():
            print(f"{politica:<20} {datos['tiempo_respuesta_promedio']:<20.2f} "
                  f"{datos['tiempo_espera_promedio']:<20.2f}")


# ==================== EJEMPLOS DE USO ====================

def ejemplo_basico():
    """Ejemplo básico de uso del simulador"""
    print("\n" + "="*70)
    print("EJEMPLO BÁSICO")
    print("="*70)
    
    sim = SimuladorSO(
        politica_scheduling=PoliticaScheduling.RR,
        quantum=5
    )
    
    # Crear algunos procesos
    procesos = [
        ("P1", 128, 15, 5, 0),   # nombre, tamaño, burst_time, prioridad, entrada
        ("P2", 256, 20, 5, 0),
        ("P3", 64, 10, 7, 2),
        ("P4", 192, 25, 3, 5),
    ]
    
    for nombre, tamaño, burst, prio, entrada in procesos:
        sim.crear_proceso_usuario(nombre, tamaño, burst, prio, entrada)
    
    # Ejecutar
    sim.ejecutar_completo()


if __name__ == "__main__":
    ejemplo_basico()



