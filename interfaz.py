import tkinter as tk
from tkinter import ttk


class SimuladorGUI:

    def __init__(self, root):

        self.root = root

        self.root.title("Simulador de Sistema Operativo")

        self.root.geometry("1200x700")

        # ===== TÍTULO =====

        titulo = tk.Label(
            root,
            text="SIMULADOR DE SISTEMA OPERATIVO",
            font=("Arial", 18, "bold")
        )

        titulo.pack(pady=10)

        # ===== FRAME PRINCIPAL =====

        frame_principal = tk.Frame(root)

        frame_principal.pack(fill="both", expand=True)

        # ===== COLA LISTOS =====

        frame_listos = tk.LabelFrame(
            frame_principal,
            text="COLA DE LISTOS"
        )

        frame_listos.place(x=20, y=20, width=250, height=250)

        self.lista_listos = tk.Listbox(frame_listos)

        self.lista_listos.pack(fill="both", expand=True)

        # ===== PROCESO EJECUTANDO =====

        frame_cpu = tk.LabelFrame(
            frame_principal,
            text="CPU"
        )

        frame_cpu.place(x=300, y=20, width=250, height=150)

        self.label_cpu = tk.Label(
            frame_cpu,
            text="VACÍO",
            font=("Arial", 16)
        )

        self.label_cpu.pack(pady=30)

        # ===== MEMORIA =====

        frame_memoria = tk.LabelFrame(
            frame_principal,
            text="MEMORIA"
        )

        frame_memoria.place(x=600, y=20, width=500, height=300)

        self.text_memoria = tk.Text(frame_memoria)

        self.text_memoria.pack(fill="both", expand=True)

        # ===== LOG =====

        frame_log = tk.LabelFrame(
            frame_principal,
            text="LOG DEL SISTEMA"
        )

        frame_log.place(x=20, y=320, width=1080, height=300)

        self.text_log = tk.Text(frame_log)

        self.text_log.pack(fill="both", expand=True)

    def actualizar_listos(self, cola):

        self.lista_listos.delete(0, tk.END)

        for pcb in cola:

            self.lista_listos.insert(
                tk.END,
                f"P{pcb.pid} - {pcb.nombre}"
            )

    def actualizar_cpu(self, pcb):

        if pcb:

            self.label_cpu.config(
                text=f"P{pcb.pid}\n{pcb.nombre}"
            )

        else:

            self.label_cpu.config(text="VACÍO")

    def actualizar_log(self, mensaje):

        self.text_log.insert(
            tk.END,
            mensaje + "\n"
        )

        self.text_log.see(tk.END)