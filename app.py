import tkinter as tk

from main import SimuladorSO
from interfaz import SimuladorGUI


root = tk.Tk()

simulador = SimuladorSO()

gui = SimuladorGUI(root, simulador)

simulador.iniciar()

root.mainloop()