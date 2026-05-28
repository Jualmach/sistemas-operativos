import tkinter as tk
from tkinter import ttk, messagebox

from enums import (
    PoliticaScheduling,
    EstrategiaMemoria,
    MetodoMemoria,
    Constantes,
    DispositivoIO
)


class SimuladorGUI:
    """Interfaz gráfica del simulador de Sistema Operativo."""

    def __init__(self, root):
        self.root = root
        self.root.title("Simulador de Sistema Operativo")
        self.root.geometry("1500x920")
        self.root.minsize(1400, 840)

        self.auto_running = False
        self.auto_job = None
        self.simulador = None

        self.politica_var = tk.StringVar(value=PoliticaScheduling.RR.value)
        self.estrategia_var = tk.StringVar(value=EstrategiaMemoria.FIRST_FIT.value)
        self.metodo_var = tk.StringVar(value=MetodoMemoria.MAPA_BITS.value)

        self._crear_widgets()
        self._reiniciar_simulador()
        self._actualizar_ui()

    def _crear_widgets(self):
        titulo = ttk.Label(
            self.root,
            text="SIMULADOR DE SISTEMA OPERATIVO",
            font=("Segoe UI", 22, "bold")
        )
        titulo.pack(pady=8)

        contenido = ttk.Frame(self.root)
        contenido.pack(fill="both", expand=True, padx=8, pady=4)

        panel_izq = ttk.Frame(contenido)
        panel_izq.pack(side="left", fill="y", padx=(0, 8))

        panel_centro = ttk.Frame(contenido)
        panel_centro.pack(side="left", fill="both", expand=True)

        panel_der = ttk.Frame(contenido)
        panel_der.pack(side="right", fill="y", padx=(8, 0))

        self._crear_panel_cpu(panel_izq)
        self._crear_panel_colas(panel_izq)
        self._crear_panel_controles(panel_izq)

        self._crear_panel_memoria(panel_centro)
        self._crear_panel_io(panel_centro)

        self._crear_panel_estadisticas(panel_der)
        self._crear_panel_proceso_form(panel_der)
        self._crear_panel_log(self.root)

    def _crear_panel_cpu(self, parent):
        frame = ttk.LabelFrame(parent, text="Panel del Procesador / PCB")
        frame.pack(fill="x", pady=4)

        self.label_tiempo = ttk.Label(frame, text="Tiempo: 0", font=("Segoe UI", 12, "bold"))
        self.label_tiempo.pack(anchor="w", pady=(6, 0), padx=8)

        self.label_cpu_nombre = ttk.Label(frame, text="CPU: vacío", font=("Segoe UI", 14, "bold"))
        self.label_cpu_nombre.pack(anchor="w", padx=8, pady=(10, 0))

        self.text_cpu_info = tk.Text(frame, width=44, height=14, padx=8, pady=4)
        self.text_cpu_info.config(state="disabled", bg="#f5f5f5")
        self.text_cpu_info.pack(fill="x", padx=8, pady=(4, 10))

    def _crear_panel_colas(self, parent):
        frame = ttk.LabelFrame(parent, text="Colas de Procesos")
        frame.pack(fill="both", pady=4)

        subframe = ttk.Frame(frame)
        subframe.pack(fill="both", padx=8, pady=4)

        listos_frame = ttk.LabelFrame(subframe, text="Listos")
        listos_frame.pack(side="left", fill="both", expand=True, padx=(0, 4))
        self.lista_listos = tk.Listbox(listos_frame, height=10)
        self.lista_listos.pack(fill="both", expand=True, padx=4, pady=4)

        ejec_frame = ttk.LabelFrame(subframe, text="Ejecutando")
        ejec_frame.pack(side="left", fill="both", expand=True, padx=4)
        self.lista_ejecutando = tk.Listbox(ejec_frame, height=10)
        self.lista_ejecutando.pack(fill="both", expand=True, padx=4, pady=4)

        fin_frame = ttk.LabelFrame(subframe, text="Terminados / Abortados")
        fin_frame.pack(side="left", fill="both", expand=True, padx=(4, 0))
        self.lista_finalizados = tk.Listbox(fin_frame, height=10)
        self.lista_finalizados.pack(fill="both", expand=True, padx=4, pady=4)

    def _crear_panel_controles(self, parent):
        frame = ttk.LabelFrame(parent, text="Control de Simulación")
        frame.pack(fill="x", pady=4)

        boton_frame = ttk.Frame(frame)
        boton_frame.pack(fill="x", padx=8, pady=6)

        self.btn_paso = ttk.Button(boton_frame, text="Tick", command=self._paso_simulacion)
        self.btn_paso.pack(side="left", padx=4, pady=4)

        self.btn_auto = ttk.Button(boton_frame, text="Correr Auto", command=self._iniciar_auto)
        self.btn_auto.pack(side="left", padx=4, pady=4)

        self.btn_detener = ttk.Button(boton_frame, text="Detener", command=self._detener_auto)
        self.btn_detener.pack(side="left", padx=4, pady=4)

        self.btn_reset = ttk.Button(boton_frame, text="Reiniciar", command=self._reiniciar_simulador)
        self.btn_reset.pack(side="left", padx=4, pady=4)

        self.btn_cargar20 = ttk.Button(frame, text="Cargar 20 procesos de prueba", command=self._cargar_procesos_prueba)
        self.btn_cargar20.pack(fill="x", padx=8, pady=(0, 6))

        selector_frame = ttk.Frame(frame)
        selector_frame.pack(fill="x", padx=8, pady=4)

        ttk.Label(selector_frame, text="Política:").grid(row=0, column=0, sticky="w", pady=2)
        self.combo_politica = ttk.Combobox(
            selector_frame,
            textvariable=self.politica_var,
            state="readonly",
            values=[p.value for p in PoliticaScheduling]
        )
        self.combo_politica.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(selector_frame, text="Estrategia memoria:").grid(row=1, column=0, sticky="w", pady=2)
        self.combo_estrategia = ttk.Combobox(
            selector_frame,
            textvariable=self.estrategia_var,
            state="readonly",
            values=[e.value for e in EstrategiaMemoria]
        )
        self.combo_estrategia.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(selector_frame, text="Método memoria:").grid(row=2, column=0, sticky="w", pady=2)
        self.combo_metodo = ttk.Combobox(
            selector_frame,
            textvariable=self.metodo_var,
            state="readonly",
            values=[m.value for m in MetodoMemoria]
        )
        self.combo_metodo.grid(row=2, column=1, sticky="ew", padx=4, pady=2)

        selector_frame.columnconfigure(1, weight=1)

    def _crear_panel_memoria(self, parent):
        frame = ttk.LabelFrame(parent, text="Memoria Física (Múltiplos de 2^n)")
        frame.pack(fill="both", expand=True, pady=4)

        self.canvas_memoria = tk.Canvas(frame, bg="#ffffff", height=280)
        self.canvas_memoria.pack(fill="x", padx=8, pady=(8, 4))

        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.label_mem_total = ttk.Label(info_frame, text="Memoria Total: 0 KB")
        self.label_mem_total.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.label_mem_ocupada = ttk.Label(info_frame, text="Uso: 0 KB")
        self.label_mem_ocupada.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.label_frag_interna = ttk.Label(info_frame, text="Fragmentación interna total: 0 KB")
        self.label_frag_interna.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.label_desperdicio = ttk.Label(info_frame, text="Desperdicio en KB: 0 KB")
        self.label_desperdicio.grid(row=1, column=1, sticky="w", padx=4, pady=2)
        self.label_frag_externa = ttk.Label(info_frame, text="Fragmentación externa: 0 %")
        self.label_frag_externa.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.label_bloques = ttk.Label(info_frame, text="Bloques libres: 0")
        self.label_bloques.grid(row=2, column=1, sticky="w", padx=4, pady=2)

    def _crear_panel_io(self, parent):
        frame = ttk.LabelFrame(parent, text="Gestión de E/S")
        frame.pack(fill="both", expand=True, pady=4)

        io_frame = ttk.Frame(frame)
        io_frame.pack(fill="both", expand=True, padx=8, pady=8)

        self._crear_panel_dispositivo(io_frame, DispositivoIO.TECLADO, 0)
        self._crear_panel_dispositivo(io_frame, DispositivoIO.DISCO, 1)
        self._crear_panel_dispositivo(io_frame, DispositivoIO.IMPRESORA, 2)

    def _crear_panel_dispositivo(self, parent, dispositivo, columna):
        frame = ttk.LabelFrame(parent, text=dispositivo.value)
        frame.grid(row=0, column=columna, sticky="nsew", padx=4, pady=2)
        parent.columnconfigure(columna, weight=1)

        self._create_io_label(frame, dispositivo)

    def _create_io_label(self, parent, dispositivo):
        label = ttk.Label(parent, text="Procesos bloqueados")
        label.pack(anchor="w", padx=4, pady=(4, 2))

        listbox = tk.Listbox(parent, height=10)
        listbox.pack(fill="both", expand=True, padx=4, pady=4)
        setattr(self, f"lista_{dispositivo.name.lower()}", listbox)

    def _crear_panel_estadisticas(self, parent):
        frame = ttk.LabelFrame(parent, text="Resumen y Estadísticas")
        frame.pack(fill="both", expand=True, pady=4)

        self.label_resumen = ttk.Label(frame, text="Procesos finalizados: 0 | Errores: 0", wraplength=280)
        self.label_resumen.pack(anchor="w", padx=8, pady=(6, 4))

        self.text_estadisticas = tk.Text(frame, width=34, height=18, padx=8, pady=4)
        self.text_estadisticas.config(state="disabled", bg="#f5f5f5")
        self.text_estadisticas.pack(fill="both", expand=True, padx=8, pady=4)

    def _crear_panel_proceso_form(self, parent):
        frame = ttk.LabelFrame(parent, text="Ingreso Manual de Procesos")
        frame.pack(fill="x", pady=4)

        form = ttk.Frame(frame)
        form.pack(fill="x", padx=8, pady=8)

        ttk.Label(form, text="Nombre:").grid(row=0, column=0, sticky="w", pady=2)
        self.entry_nombre = ttk.Entry(form)
        self.entry_nombre.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Tamaño KB:").grid(row=1, column=0, sticky="w", pady=2)
        self.entry_tamaño = ttk.Entry(form)
        self.entry_tamaño.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Burst Time:").grid(row=2, column=0, sticky="w", pady=2)
        self.entry_burst = ttk.Entry(form)
        self.entry_burst.grid(row=2, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Prioridad:").grid(row=3, column=0, sticky="w", pady=2)
        self.entry_prioridad = ttk.Entry(form)
        self.entry_prioridad.grid(row=3, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(form, text="Ingreso en t:").grid(row=4, column=0, sticky="w", pady=2)
        self.entry_ingreso = ttk.Entry(form)
        self.entry_ingreso.grid(row=4, column=1, sticky="ew", padx=4, pady=2)

        form.columnconfigure(1, weight=1)

        self.btn_agregar = ttk.Button(frame, text="Agregar Proceso", command=self._agregar_proceso)
        self.btn_agregar.pack(fill="x", padx=8, pady=(0, 8))

    def _crear_panel_log(self, parent):
        frame = ttk.LabelFrame(parent, text="Log del Sistema")
        frame.pack(fill="x", pady=4, padx=8)

        self.text_log = tk.Text(frame, height=8, padx=8, pady=4)
        self.text_log.config(state="disabled", bg="#f5f5f5")
        self.text_log.pack(fill="both", expand=True, padx=4, pady=4)

    def _reiniciar_simulador(self):
        from main import SimuladorSO

        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
            self.auto_running = False

        politica = PoliticaScheduling(self.politica_var.get())
        estrategia = EstrategiaMemoria(self.estrategia_var.get())
        metodo = MetodoMemoria(self.metodo_var.get())

        self.simulador = SimuladorSO(
            politica_scheduling=politica,
            estrategia_memoria=estrategia,
            tamaño_bloque_kb=Constantes.TAMAÑO_BLOQUE_KB
        )
        self.simulador.gestor_memoria.metodo = metodo
        self._log("Simulador reiniciado.")

    def _cargar_procesos_prueba(self):
        procesos = [
            (f"P{num}", 64 + (num * 8) % 192, 8 + (num * 3) % 28, 1 + (num % 10), num // 2)
            for num in range(1, 21)
        ]
        for nombre, tamaño, burst, prioridad, ingreso in procesos:
            self.simulador.crear_proceso_usuario(nombre, tamaño, burst, prioridad, ingreso)
        self._log("Cargados 20 procesos de prueba.")

    def _agregar_proceso(self):
        nombre = self.entry_nombre.get().strip() or f"USR_{len(self.simulador.procesos_cola_entrada) + 1}"
        try:
            tamaño = int(self.entry_tamaño.get())
            burst = int(self.entry_burst.get())
            prioridad = int(self.entry_prioridad.get())
            ingreso = int(self.entry_ingreso.get())
        except ValueError:
            messagebox.showwarning("Entrada inválida", "Todos los campos numéricos deben estar completos.")
            return

        if tamaño <= 0 or burst <= 0 or prioridad < Constantes.PRIORIDAD_MINIMA or prioridad > Constantes.PRIORIDAD_MAXIMA:
            messagebox.showwarning("Entrada inválida", "Valores fuera de rango o no permitidos.")
            return

        self.simulador.crear_proceso_usuario(nombre, tamaño, burst, prioridad, ingreso)
        self._log(f"Proceso {nombre} agregado para t={ingreso}.")
        self.entry_nombre.delete(0, tk.END)
        self.entry_tamaño.delete(0, tk.END)
        self.entry_burst.delete(0, tk.END)
        self.entry_prioridad.delete(0, tk.END)
        self.entry_ingreso.delete(0, tk.END)

    def _paso_simulacion(self):
        if not self.simulador.en_ejecucion:
            if not self.simulador.procesos_cola_entrada:
                self._log("No hay procesos por ingresar. Agrega procesos primero.")
                return
            self.simulador.iniciar_simulacion(max_tiempo=10000)
            self._log("Simulación iniciada.")

        avance = self.simulador.ejecutar_paso()
        if not avance:
            self._log("La simulación ha terminado.")
            self._detener_auto()

    def _iniciar_auto(self):
        if self.auto_running:
            return
        if not self.simulador.en_ejecucion:
            if not self.simulador.procesos_cola_entrada:
                self._log("No hay procesos por ingresar. Agrega procesos primero.")
                return
            self.simulador.iniciar_simulacion(max_tiempo=10000)
            self._log("Simulación iniciada en modo automático.")

        self.auto_running = True
        self._auto_step()

    def _auto_step(self):
        if not self.auto_running:
            return
        avance = self.simulador.ejecutar_paso()
        if avance:
            self.auto_job = self.root.after(400, self._auto_step)
        else:
            self._log("Simulación finalizada.")
            self.auto_running = False
            self.auto_job = None

    def _detener_auto(self):
        if self.auto_job:
            self.root.after_cancel(self.auto_job)
            self.auto_job = None
        self.auto_running = False
        self._log("Ejecución automática detenida.")

    def _log(self, mensaje):
        self.text_log.config(state="normal")
        self.text_log.insert(tk.END, f"{mensaje}\n")
        self.text_log.see(tk.END)
        self.text_log.config(state="disabled")

    def _actualizar_ui(self):
        self.label_tiempo.config(text=f"Tiempo: {self.simulador.clock.obtener_tiempo():.0f}")

        ejecutando = self.simulador.gestor_procesos.obtener_ejecutando()
        self.lista_ejecutando.delete(0, tk.END)
        self.lista_listos.delete(0, tk.END)
        self.lista_finalizados.delete(0, tk.END)

        if ejecutando:
            self.lista_ejecutando.insert(tk.END, f"P{ejecutando.get_pid()} - {ejecutando.get_nombre()}")
            self._actualizar_cpu_info(ejecutando)
        else:
            self._limpiar_cpu_info()

        for pcb in list(self.simulador.gestor_procesos.cola_listos):
            self.lista_listos.insert(tk.END, f"P{pcb.get_pid()} - {pcb.get_nombre()}")

        for pcb in self.simulador.gestor_procesos.obtener_todos_finalizados():
            estado = "ERR" if pcb.codigo_error != 0 else "OK"
            self.lista_finalizados.insert(tk.END, f"P{pcb.get_pid()} - {pcb.get_nombre()} [{estado}]")

        self._actualizar_io_queues()
        self._actualizar_memoria()
        self._actualizar_estadisticas()

        self.root.after(250, self._actualizar_ui)

    def _actualizar_cpu_info(self, pcb):
        texto = (
            f"PID: {pcb.get_pid()}\n"
            f"Nombre: {pcb.get_nombre()}\n"
            f"Estado: {pcb.get_estado().value}\n"
            f"PC: {pcb.get_pc()}\n"
            f"Burst restante: {pcb.get_burst_time_restante()}\n"
            f"Quantum restante: {getattr(pcb, 'quantum_restante', 0)}\n"
            f"Dirección física: {pcb.get_direccion_inicial_fisica()}\n"
            f"Tamaño total: {pcb.get_tamaño()} KB\n"
            f"Ejecutable: {pcb.get_tamaño_ejecutable()} KB\n"
            f"Datos: {pcb.get_segmento_datos()} KB\n"
            f"Stack/Heap: {pcb.get_stack_heap()} KB\n"
            f"Frag. interna proceso: {pcb.get_fragmentacion_interna()} KB\n"
            f"Dispositivo actual: {pcb.dispositivo_actual or 'Ninguno'}\n"
            f"Interrupciones totales: {pcb.contador_interrupciones}\n"
            f"Interrupciones pendientes: {sum(1 for ev in pcb.interrupciones_programadas if not ev['realizada'])}"
        )
        self.text_cpu_info.config(state="normal")
        self.text_cpu_info.delete("1.0", tk.END)
        self.text_cpu_info.insert(tk.END, texto)
        self.text_cpu_info.config(state="disabled")

    def _limpiar_cpu_info(self):
        self.label_cpu_nombre.config(text="CPU: vacío")
        self.text_cpu_info.config(state="normal")
        self.text_cpu_info.delete("1.0", tk.END)
        self.text_cpu_info.config(state="disabled")

    def _actualizar_io_queues(self):
        for dispositivo in [DispositivoIO.TECLADO, DispositivoIO.DISCO, DispositivoIO.IMPRESORA]:
            lista = getattr(self, f"lista_{dispositivo.name.lower()}")
            lista.delete(0, tk.END)
            items = self.simulador.gestor_interrupciones.colas_dispositivo.get(dispositivo, [])
            for item in items:
                pcb = item['pcb']
                restante = item['duracion_restante']
                lista.insert(tk.END, f"P{pcb.get_pid()} - {pcb.get_nombre()} ({restante}u)")

    def _actualizar_memoria(self):
        uso = self.simulador.gestor_memoria.get_uso_memoria()
        self.label_mem_total.config(text=f"Memoria Total: {uso['memoria_total_kb']} KB")
        self.label_mem_ocupada.config(text=f"Uso: {uso['memoria_ocupada_kb']} KB / {uso['memoria_libre_kb']} KB")
        self.label_frag_interna.config(text=f"Fragmentación interna total: {uso['fragmentacion_interna']:.0f} KB")
        self.label_desperdicio.config(text=f"Desperdicio en KB: {uso['desperdicio_memoria']} KB")
        self.label_frag_externa.config(text=f"Fragmentación externa: {uso['fragmentacion_externa']:.1f} %")
        self.label_bloques.config(text=f"Bloques libres: {uso['bloques_libres']}")

        self.canvas_memoria.delete("all")
        bloques = self.simulador.gestor_memoria.bloques
        columnas = min(16, len(bloques))
        tamaño = 28
        spacing = 4
        for i, bloque in enumerate(bloques):
            row = i // columnas
            col = i % columnas
            x0 = spacing + col * (tamaño + spacing)
            y0 = spacing + row * (tamaño + spacing)
            x1 = x0 + tamaño
            y1 = y0 + tamaño
            color = "#d4edda" if bloque.es_libre else "#f8d7da"
            self.canvas_memoria.create_rectangle(x0, y0, x1, y1, fill=color, outline="#555")
            if not bloque.es_libre:
                self.canvas_memoria.create_text(
                    (x0 + x1) / 2,
                    (y0 + y1) / 2,
                    text=f"P{bloque.pid_ocupante}",
                    font=("Segoe UI", 7, "bold")
                )

    def _actualizar_estadisticas(self):
        finalizados = self.simulador.gestor_procesos.obtener_todos_finalizados()
        total_errores = self.simulador.gestor_procesos.total_errores
        self.label_resumen.config(text=f"Procesos finalizados: {len(finalizados)} | Errores: {total_errores}")

        texto = (
            f"Total creados: {self.simulador.gestor_procesos.total_procesos_creados}\n"
            f"Total activos: {len(self.simulador.gestor_procesos.obtener_todos_activos())}\n"
            f"Cambios de contexto: {self.simulador.dispatcher.cambios_contexto_totales}\n"
            f"Instrucciones ejecutadas: {self.simulador.dispatcher.instrucciones_ejecutadas}\n"
            f"Interrupciones ejecutadas: {self.simulador.estadisticas.get('total_interrupciones', 0)}\n"
        )
        self.text_estadisticas.config(state="normal")
        self.text_estadisticas.delete("1.0", tk.END)
        self.text_estadisticas.insert(tk.END, texto)
        self.text_estadisticas.config(state="disabled")
