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
        # Dimensión inicial sugerida para evitar desbordes en pantallas pequeñas
        self.root.geometry("1200x700")
        self.root.minsize(900, 600)

        self.auto_running = False
        self.auto_job = None
        self.simulador = None

        self.politica_var = tk.StringVar(value="Round Robin (RR)")
        self.estrategia_var = tk.StringVar(value="First Fit")
        self.metodo_var = tk.StringVar(value=MetodoMemoria.MAPA_BITS.value)
        self.quantum_var = tk.StringVar(value="4")

        # Métricas de rendimiento iniciales
        self.tiempo_espera_promedio = 0.0
        self.tiempo_retorno_promedio = 0.0
        self.eficiencia_sistema = 0.0
        self.utilizacion_cpu = 0.0

        # Contadores acumulados de interrupciones (visual)
        self.count_interrupciones_temporizador = 0
        self.count_interrupciones_teclado = 0
        self.count_interrupciones_disco = 0

        # Contadores y etiquetas adicionales para la UI
        self.label_total_procesos = None
        self.label_procesos_ejecutando = None
        self.label_procesos_listos = None
        self.label_procesos_bloqueados = None
        self.label_utilizacion_cpu = None
        self.label_uso_memoria = None
        self.label_distrib_ejecutando = None
        self.label_distrib_listos = None
        self.label_distrib_bloqueados = None
        self.label_distrib_terminados = None
        self.label_tiempo_espera = None
        self.label_tiempo_retorno = None
        self.label_cambios_contexto = None
        self.label_eficiencia = None
        self.label_sin_procesos = None

        # Listas mostradas en combobox (nombres técnicos solicitados)
        self._politica_display_names = [
            "First Come First Served (FCFS)",
            "Shortest Job First (SJF)",
            "Round Robin (RR)",
            "Priority Scheduling"
        ]
        self._estrategia_display_names = ["First Fit", "Best Fit", "Worst Fit"]

        # Mapeos display -> enum (se construyen intentando emparejar nombres/valores)
        self._politica_map = {}
        for member in PoliticaScheduling:
            for name in self._politica_display_names:
                if member.name in name or str(member.value) in name:
                    self._politica_map[name] = member

        self._estrategia_map = {}
        for member in EstrategiaMemoria:
            for name in self._estrategia_display_names:
                if member.name.replace("_", " ") in name or str(member.value) in name:
                    self._estrategia_map[name] = member

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

        # Usar un Canvas con scrollbar vertical para permitir scroll cuando la UI excede la altura
        self.canvas = tk.Canvas(self.root)
        self.v_scroll = ttk.Scrollbar(self.root, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.v_scroll.set)
        self.v_scroll.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        # Frame interno que contendrá el layout principal
        contenido = ttk.Frame(self.canvas)
        self.canvas_window = self.canvas.create_window((0, 0), window=contenido, anchor="nw")

        # Ajuste de tamaño inicial y bindings para mantener el scrollregion actualizado
        def _on_frame_config(event):
            self.canvas.configure(scrollregion=self.canvas.bbox("all"))

        contenido.bind("<Configure>", _on_frame_config)

        # Hacer que la rueda del ratón también desplace el canvas
        def _on_mousewheel(event):
            # Windows / macOS
            if hasattr(event, 'delta'):
                self.canvas.yview_scroll(int(-1 * (event.delta / 120)), 'units')
            else:
                # X11 systems (Button-4/Button-5)
                if event.num == 4:
                    self.canvas.yview_scroll(-1, 'units')
                elif event.num == 5:
                    self.canvas.yview_scroll(1, 'units')

        # Bind global wheel events to canvas for convenience
        self.canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self.canvas.bind_all("<Button-4>", _on_mousewheel)
        self.canvas.bind_all("<Button-5>", _on_mousewheel)

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
        self._crear_panel_log(panel_der)

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
        frame = ttk.LabelFrame(parent, text="Planificador de Procesos")
        frame.pack(fill="x", pady=4)

        # Área de configuración (comboboxes y quantum) arriba de los botones
        config_frame = ttk.Frame(frame)
        config_frame.pack(fill="x", padx=8, pady=(6, 4))

        ttk.Label(config_frame, text="Planificador:").grid(row=0, column=0, sticky="w", pady=2)
        self.combo_politica = ttk.Combobox(
            config_frame,
            textvariable=self.politica_var,
            state="readonly",
            values=self._politica_display_names
        )
        self.combo_politica.grid(row=0, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(config_frame, text="Asignación Memoria:").grid(row=1, column=0, sticky="w", pady=2)
        self.combo_estrategia = ttk.Combobox(
            config_frame,
            textvariable=self.estrategia_var,
            state="readonly",
            values=self._estrategia_display_names
        )
        self.combo_estrategia.grid(row=1, column=1, sticky="ew", padx=4, pady=2)

        ttk.Label(config_frame, text="Quantum:").grid(row=0, column=2, sticky="w", padx=(12, 0))
        self.entry_quantum = ttk.Entry(config_frame, width=6, textvariable=self.quantum_var)
        self.entry_quantum.grid(row=0, column=3, sticky="w", padx=4, pady=2)

        config_frame.columnconfigure(1, weight=1)

        boton_frame = ttk.Frame(frame)
        boton_frame.pack(fill="x", padx=8, pady=6)

        self.btn_paso = ttk.Button(boton_frame, text="Tick", command=self._paso_simulacion)
        self.btn_paso.pack(side="left", padx=4, pady=4)

        self.btn_auto = ttk.Button(boton_frame, text="Iniciar", command=self._iniciar_auto)
        self.btn_auto.pack(side="left", padx=4, pady=4)

        self.btn_detener = ttk.Button(boton_frame, text="Detener", command=self._detener_auto)
        self.btn_detener.pack(side="left", padx=4, pady=4)

        self.btn_reset = ttk.Button(boton_frame, text="Reiniciar", command=self._reiniciar_simulador)
        self.btn_reset.pack(side="left", padx=4, pady=4)

        self.btn_limpiar_log = ttk.Button(boton_frame, text="Limpiar Log", command=self._limpiar_log)
        self.btn_limpiar_log.pack(side="left", padx=4, pady=4)

        self.btn_cargar20 = ttk.Button(frame, text="Agregar Muestra", command=self._cargar_procesos_prueba)
        self.btn_cargar20.pack(fill="x", padx=8, pady=(0, 6))

        # Nota: los combobox de Planificador y Asignación Memoria se muestran arriba en el área de configuración
        # El combobox de 'Método memoria' permanece accesible en la interfaz (junto a los demás controles)
        self.combo_metodo = ttk.Combobox(
            frame,
            textvariable=self.metodo_var,
            state="readonly",
            values=[m.value for m in MetodoMemoria]
        )
        # Ubicamos el método en la parte inferior de controles como antes
        # Se añadirá discretamente a la izquierda para mantener la disposición
        self.combo_metodo.pack(fill="x", padx=8, pady=(0, 4))

    def _crear_panel_memoria(self, parent):
        frame = ttk.LabelFrame(parent, text="Memoria Física (Múltiplos de 2^n)")
        frame.pack(fill="both", expand=True, pady=4)

        self.canvas_memoria = tk.Canvas(frame, bg="#ffffff", height=280)
        self.canvas_memoria.pack(fill="x", padx=8, pady=(8, 4))

        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=8, pady=(0, 8))

        self.label_mem_total = ttk.Label(info_frame, text="Total: 0 KB")
        self.label_mem_total.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.label_mem_ocupada = ttk.Label(info_frame, text="Ocupado / Libre: 0 KB / 0 KB")
        self.label_mem_ocupada.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.label_mem_utilizacion = ttk.Label(info_frame, text="Utilización: 0.0 %")
        self.label_mem_utilizacion.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.label_algoritmo_asignacion = ttk.Label(info_frame, text="Asignación: First Fit")
        self.label_algoritmo_asignacion.grid(row=1, column=1, sticky="w", padx=4, pady=2)
        self.label_frag_interna = ttk.Label(info_frame, text="Fragmentación interna total: 0 KB")
        self.label_frag_interna.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.label_desperdicio = ttk.Label(info_frame, text="Desperdicio en KB: 0 KB")
        self.label_desperdicio.grid(row=2, column=1, sticky="w", padx=4, pady=2)
        self.label_frag_externa = ttk.Label(info_frame, text="Fragmentación externa: 0 %")
        self.label_frag_externa.grid(row=3, column=0, sticky="w", padx=4, pady=2)
        self.label_bloques = ttk.Label(info_frame, text="Bloques libres: 0")
        self.label_bloques.grid(row=3, column=1, sticky="w", padx=4, pady=2)

    def _crear_panel_io(self, parent):
        frame = ttk.LabelFrame(parent, text="Gestión de E/S")
        frame.pack(fill="both", expand=True, pady=4)

        # Contadores visuales de interrupciones
        counts_frame = ttk.Frame(frame)
        counts_frame.pack(fill="x", padx=8, pady=(6, 0))

        self.label_int_temp = ttk.Label(counts_frame, text=f"Temporizador: {self.count_interrupciones_temporizador}")
        self.label_int_temp.pack(side="left", padx=(0, 12))
        self.label_int_teclado = ttk.Label(counts_frame, text=f"Teclado: {self.count_interrupciones_teclado}")
        self.label_int_teclado.pack(side="left", padx=(0, 12))
        self.label_int_disco = ttk.Label(counts_frame, text=f"Disco: {self.count_interrupciones_disco}")
        self.label_int_disco.pack(side="left", padx=(0, 12))

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

        sistema_frame = ttk.Frame(frame)
        sistema_frame.pack(fill="x", padx=8, pady=(6, 4))

        self.label_total_procesos = ttk.Label(sistema_frame, text="Total de Procesos: 0", font=("Segoe UI", 11, "bold"))
        self.label_total_procesos.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.label_procesos_ejecutando = ttk.Label(sistema_frame, text="Procesos Ejecutándose: 0")
        self.label_procesos_ejecutando.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.label_procesos_nuevos = ttk.Label(sistema_frame, text="Procesos Nuevos: 0")
        self.label_procesos_nuevos.grid(row=0, column=2, sticky="w", padx=4, pady=2)
        self.label_procesos_listos = ttk.Label(sistema_frame, text="Procesos Listos: 0")
        self.label_procesos_listos.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.label_procesos_bloqueados = ttk.Label(sistema_frame, text="Procesos Bloqueados: 0")
        self.label_procesos_bloqueados.grid(row=1, column=1, sticky="w", padx=4, pady=2)
        self.label_utilizacion_cpu = ttk.Label(sistema_frame, text="Utilización de CPU: 0.0 %")
        self.label_utilizacion_cpu.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        self.label_uso_memoria = ttk.Label(sistema_frame, text="Uso de Memoria: 0.0 %")
        self.label_uso_memoria.grid(row=2, column=1, sticky="w", padx=4, pady=2)

        distrib_frame = ttk.LabelFrame(frame, text="Distribución de Procesos")
        distrib_frame.pack(fill="x", padx=8, pady=(0, 4))

        self.label_distrib_ejecutando = ttk.Label(distrib_frame, text="Ejecutando 0")
        self.label_distrib_ejecutando.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.label_distrib_listos = ttk.Label(distrib_frame, text="Listos 0")
        self.label_distrib_listos.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.label_distrib_bloqueados = ttk.Label(distrib_frame, text="Bloqueados 0")
        self.label_distrib_bloqueados.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.label_distrib_terminados = ttk.Label(distrib_frame, text="Terminados 0")
        self.label_distrib_terminados.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        perf_frame = ttk.LabelFrame(frame, text="Métricas de Rendimiento")
        perf_frame.pack(fill="x", padx=8, pady=(0, 4))

        self.label_tiempo_espera = ttk.Label(perf_frame, text=f"Tiempo Promedio de Espera: {self.tiempo_espera_promedio:.1f}ms")
        self.label_tiempo_espera.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        self.label_tiempo_retorno = ttk.Label(perf_frame, text=f"Tiempo Promedio de Retorno: {self.tiempo_retorno_promedio:.1f}ms")
        self.label_tiempo_retorno.grid(row=0, column=1, sticky="w", padx=4, pady=2)
        self.label_cambios_contexto = ttk.Label(perf_frame, text=f"Cambios de Contexto: 0")
        self.label_cambios_contexto.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        self.label_eficiencia = ttk.Label(perf_frame, text=f"Eficiencia del Sistema: {self.eficiencia_sistema:.1f}%")
        self.label_eficiencia.grid(row=1, column=1, sticky="w", padx=4, pady=2)

        self.label_resumen = ttk.Label(frame, text="Procesos finalizados: 0 | Errores: 0", wraplength=280)
        self.label_resumen.pack(anchor="w", padx=8, pady=(0, 4))

        self.text_estadisticas = tk.Text(frame, width=34, height=14, padx=8, pady=4)
        self.text_estadisticas.config(state="disabled", bg="#f5f5f5")
        self.text_estadisticas.pack(fill="both", expand=True, padx=8, pady=4)

        self.text_estadisticas.config(state="normal")
        self.text_estadisticas.delete("1.0", tk.END)
        inicial_text = (
            f"Tiempo Promedio de Espera: {self.tiempo_espera_promedio:.1f}ms\n"
            f"Tiempo Promedio de Retorno: {self.tiempo_retorno_promedio:.1f}ms\n"
            f"Eficiencia del Sistema: {self.eficiencia_sistema:.1f}%\n"
            f"Utilización de CPU: {self.utilizacion_cpu:.1f}%\n\n"
        )
        self.text_estadisticas.insert(tk.END, inicial_text)
        self.text_estadisticas.config(state="disabled")

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
        self.btn_agregar.pack(fill="x", padx=8, pady=(0, 4))

        self.label_sin_procesos = ttk.Label(
            frame,
            text="No hay procesos en el sistema. Agrega un proceso para comenzar la simulación.",
            foreground="#666",
            wraplength=260
        )
        self.label_sin_procesos.pack(fill="x", padx=8, pady=(0, 8))

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

        # Mapear selección visual a miembros de enum usando los mapeos construidos
        politica_seleccion = self.politica_var.get()
        estrategia_seleccion = self.estrategia_var.get()

        politica = self._politica_map.get(politica_seleccion, None)
        if politica is None:
            try:
                politica = PoliticaScheduling(politica_seleccion)
            except Exception:
                politica = list(PoliticaScheduling)[0]

        estrategia = self._estrategia_map.get(estrategia_seleccion, None)
        if estrategia is None:
            try:
                estrategia = EstrategiaMemoria(estrategia_seleccion)
            except Exception:
                estrategia = list(EstrategiaMemoria)[0]
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

    def _limpiar_log(self):
        self.text_log.config(state="normal")
        self.text_log.delete("1.0", tk.END)
        self.text_log.config(state="disabled")
        self._log("Log limpiado.")

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

        self._actualizar_contadores_generales()
        self._actualizar_io_queues()
        self._actualizar_memoria()
        self._actualizar_estadisticas()

        self.root.after(250, self._actualizar_ui)

    def _actualizar_contadores_generales(self):
        conteo = self.simulador.gestor_procesos.contar_por_estado()
        nuevos = len(self.simulador.procesos_cola_entrada)
        ejecutando = conteo.get('EJECUTANDO', 0)
        listos = conteo.get('LISTO', 0)
        bloqueados = conteo.get('BLOQUEADO', 0)
        terminados = conteo.get('FINALIZADO', 0)

        self.label_total_procesos.config(text=f"Total de Procesos: {self.simulador.gestor_procesos.total_procesos_creados}")
        self.label_procesos_ejecutando.config(text=f"Procesos Ejecutándose: {ejecutando}")
        self.label_procesos_nuevos.config(text=f"Procesos Nuevos: {nuevos}")
        self.label_procesos_listos.config(text=f"Procesos Listos: {listos}")
        self.label_procesos_bloqueados.config(text=f"Procesos Bloqueados: {bloqueados}")
        self.label_utilizacion_cpu.config(text=f"Utilización de CPU: {self.utilizacion_cpu:.1f}%")
        self.label_uso_memoria.config(text=f"Uso de Memoria: {self.simulador.gestor_memoria.get_uso_memoria()['porcentaje_uso']:.1f}%")
        self.label_distrib_ejecutando.config(text=f"Ejecutando {ejecutando}")
        self.label_distrib_listos.config(text=f"Listos {listos}")
        self.label_distrib_bloqueados.config(text=f"Bloqueados {bloqueados}")
        self.label_distrib_terminados.config(text=f"Terminados {terminados}")

        if self.simulador.gestor_procesos.total_procesos_creados == 0:
            self.label_sin_procesos.config(text="No hay procesos en el sistema. Agrega un proceso para comenzar la simulación.")
        else:
            self.label_sin_procesos.config(text="")

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

        # Actualizar contadores visuales de interrupciones (intentando leer del motor)
        stats = getattr(self.simulador, 'estadisticas', {}) if self.simulador else {}
        temp = stats.get('interrupciones_temporizador', self.count_interrupciones_temporizador)
        tecla = stats.get('interrupciones_teclado', self.count_interrupciones_teclado)
        disco = stats.get('interrupciones_disco', self.count_interrupciones_disco)

        try:
            self.label_int_temp.config(text=f"Temporizador: {temp}")
            self.label_int_teclado.config(text=f"Teclado: {tecla}")
            self.label_int_disco.config(text=f"Disco: {disco}")
        except AttributeError:
            pass

    def _actualizar_memoria(self):
        uso = self.simulador.gestor_memoria.get_uso_memoria()
        self.label_mem_total.config(text=f"Total: {uso['memoria_total_kb']} KB")
        self.label_mem_ocupada.config(text=f"Ocupado / Libre: {uso['memoria_ocupada_kb']} KB / {uso['memoria_libre_kb']} KB")
        self.label_mem_utilizacion.config(text=f"Utilización: {uso['porcentaje_uso']:.1f} %")
        self.label_algoritmo_asignacion.config(text=f"Asignación: {self.simulador.gestor_memoria.estrategia.value}")
        self.label_frag_interna.config(text=f"Fragmentación interna total: {uso['fragmentacion_interna']:.0f} KB")
        self.label_desperdicio.config(text=f"Desperdicio en KB: {uso['desperdicio_memoria']} KB")
        self.label_frag_externa.config(text=f"Fragmentación externa: {uso['fragmentacion_externa']:.1f} %")
        self.label_bloques.config(text=f"Bloques libres: {uso['bloques_libres']}")

        self.canvas_memoria.delete("all")
        bloques = self.simulador.gestor_memoria.bloques
        # Calcular columnas y tamaño dinámicamente según el ancho disponible
        spacing = 4
        default_block = 28

        # Forzar actualización de geometría para obtener ancho real
        self.canvas_memoria.update_idletasks()
        canvas_width = self.canvas_memoria.winfo_width() or self.canvas_memoria.winfo_reqwidth() or 800

        # Número máximo de columnas que deseamos mostrar (mantener legibilidad)
        desired_cols = min(16, max(1, len(bloques)))

        # Calcular cuántas columnas caben con el tamaño por defecto
        cols_fit = max(1, canvas_width // (default_block + spacing))

        columnas = min(desired_cols, cols_fit)

        # Si no caben las columnas deseadas, reducir el tamaño de bloque para ajustarlas
        tamaño = default_block
        if columnas < desired_cols and columnas > 0:
            tamaño = max(12, int((canvas_width - (columnas + 1) * spacing) / columnas))

        # Finalmente dibujar en filas/columnas calculadas
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
                    font=("Segoe UI", max(7, int(tamaño / 4)), "bold")
                )

    def _actualizar_estadisticas(self):
        finalizados = self.simulador.gestor_procesos.obtener_todos_finalizados()
        total_errores = self.simulador.gestor_procesos.total_errores
        self.label_resumen.config(text=f"Procesos finalizados: {len(finalizados)} | Errores: {total_errores}")

        # Intentar obtener métricas del motor; si no existen, usar los valores almacenados
        stats = getattr(self.simulador, 'estadisticas', {}) if self.simulador else {}
        self.tiempo_espera_promedio = stats.get('tiempo_espera_promedio', self.tiempo_espera_promedio)
        self.tiempo_retorno_promedio = stats.get('tiempo_retorno_promedio', self.tiempo_retorno_promedio)
        self.eficiencia_sistema = stats.get('eficiencia_sistema', self.eficiencia_sistema)
        self.utilizacion_cpu = stats.get('utilizacion_cpu', self.utilizacion_cpu)

        self.label_tiempo_espera.config(text=f"Tiempo Promedio de Espera: {self.tiempo_espera_promedio:.1f}ms")
        self.label_tiempo_retorno.config(text=f"Tiempo Promedio de Retorno: {self.tiempo_retorno_promedio:.1f}ms")
        self.label_cambios_contexto.config(text=f"Cambios de Contexto: {self.simulador.dispatcher.cambios_contexto_totales}")
        self.label_eficiencia.config(text=f"Eficiencia del Sistema: {self.eficiencia_sistema:.1f}%")

        texto_metricas = (
            f"Tiempo Promedio de Espera: {self.tiempo_espera_promedio:.1f}ms\n"
            f"Tiempo Promedio de Retorno: {self.tiempo_retorno_promedio:.1f}ms\n"
            f"Eficiencia del Sistema: {self.eficiencia_sistema:.1f}%\n"
            f"Utilización de CPU: {self.utilizacion_cpu:.1f}%\n\n"
        )

        texto = (
            f"Total creados: {self.simulador.gestor_procesos.total_procesos_creados}\n"
            f"Total activos: {len(self.simulador.gestor_procesos.obtener_todos_activos())}\n"
            f"Cambios de contexto: {self.simulador.dispatcher.cambios_contexto_totales}\n"
            f"Instrucciones ejecutadas: {self.simulador.dispatcher.instrucciones_ejecutadas}\n"
            f"Interrupciones ejecutadas: {self.simulador.estadisticas.get('total_interrupciones', 0)}\n"
        )

        self.text_estadisticas.config(state="normal")
        self.text_estadisticas.delete("1.0", tk.END)
        self.text_estadisticas.insert(tk.END, texto_metricas + texto)
        self.text_estadisticas.config(state="disabled")
