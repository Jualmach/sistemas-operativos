import tkinter as tk


class SimuladorGUI:

    def __init__(self, root, simulador):

        self.root = root
        self.simulador = simulador

        self.root.title("Simulador de Sistema Operativo")

        self.root.geometry("1400x800")

        # ===== TITULO =====

        titulo = tk.Label(
            root,
            text="SIMULADOR DE SISTEMA OPERATIVO",
            font=("Arial", 20, "bold")
        )

        titulo.pack(pady=10)

        # ===== FRAMES =====

        self.frame_izq = tk.Frame(root)
        self.frame_izq.pack(side="left", fill="y", padx=10)

        self.frame_centro = tk.Frame(root)
        self.frame_centro.pack(side="left", fill="both", expand=True)

        self.frame_der = tk.Frame(root)
        self.frame_der.pack(side="right", fill="y", padx=10)

        # ===== LISTOS =====

        tk.Label(
            self.frame_izq,
            text="COLA LISTOS"
        ).pack()

        self.lista_listos = tk.Listbox(
            self.frame_izq,
            width=30,
            height=15
        )

        self.lista_listos.pack()

        # ===== BLOQUEADOS =====

        tk.Label(
            self.frame_izq,
            text="BLOQUEADOS"
        ).pack()

        self.lista_bloqueados = tk.Listbox(
            self.frame_izq,
            width=30,
            height=10
        )

        self.lista_bloqueados.pack()

        # ===== CPU =====

        tk.Label(
            self.frame_centro,
            text="CPU",
            font=("Arial", 16, "bold")
        ).pack()

        self.label_cpu = tk.Label(
            self.frame_centro,
            text="VACÍO",
            font=("Arial", 18)
        )

        self.label_cpu.pack(pady=20)

        # ===== MEMORIA =====

        tk.Label(
            self.frame_der,
            text="MEMORIA"
        ).pack()

        self.text_memoria = tk.Text(
            self.frame_der,
            width=40,
            height=30
        )

        self.text_memoria.pack()

        # ===== LOG =====

        tk.Label(
            root,
            text="LOG DEL SISTEMA"
        ).pack()

        self.text_log = tk.Text(
            root,
            height=12
        )

        self.text_log.pack(fill="x")

        # Actualización automática
        self.actualizar()

    def actualizar(self):

        gestor = self.simulador.gestor_procesos

        # ===== LISTOS =====

        self.lista_listos.delete(0, tk.END)

        for pcb in gestor.cola_listos:

            self.lista_listos.insert(
                tk.END,
                f"P{pcb.pid} - {pcb.nombre}"
            )

        # ===== BLOQUEADOS =====

        self.lista_bloqueados.delete(0, tk.END)

        for dispositivo, cola in gestor.colas_io.items():

            for pcb in cola:

                self.lista_bloqueados.insert(
                    tk.END,
                    f"{pcb.pid} - {dispositivo}"
                )

        # ===== CPU =====

        ejecutando = gestor.obtener_ejecutando()

        if ejecutando:

            self.label_cpu.config(
                text=(
                    f"P{ejecutando.pid}\n"
                    f"{ejecutando.nombre}\n"
                    f"PC={ejecutando.pc}\n"
                    f"BT={ejecutando.burst_time_restante}"
                )
            )

        else:

            self.label_cpu.config(text="VACÍO")

        # ===== MEMORIA =====

        self.text_memoria.delete("1.0", tk.END)

        for bloque in self.simulador.gestor_memoria.bloques:

            if bloque.es_libre:
                self.text_memoria.insert(tk.END, "[ ]")

            else:
                self.text_memoria.insert(
                    tk.END,
                    f"[P{bloque.pid_ocupante}]"
                )

        self.root.after(1000, self.actualizar)