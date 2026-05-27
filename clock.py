"""
clock.py - Reloj global del simulador de SO
"""


class Clock:
    """
    Mantiene el tiempo de simulación y sincroniza todas las operaciones.
    Es un singleton que proporciona el tiempo actual a todos los módulos.
    """
    
    _instancia = None
    
    def __new__(cls):
        """Implementa patrón singleton"""
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia
    
    def _inicializar(self):
        """Inicializa los atributos del reloj"""
        self.tiempo_actual = 0.0
        self.velocidad = 1.0  # Multiplicador de velocidad
        self.en_ejecucion = False
        self.tiempo_inicio_real = None
        self.historial_tiempos = []
    
    def incrementar_tiempo(self, unidades):
        """
        Incrementa el tiempo de simulación.
        
        Args:
            unidades: Número de unidades a incrementar
        """
        self.tiempo_actual += unidades * self.velocidad
        self.historial_tiempos.append(self.tiempo_actual)
    
    def obtener_tiempo(self):
        """
        Retorna el tiempo actual de la simulación.
        
        Returns:
            float: Tiempo actual en unidades
        """
        return self.tiempo_actual
    
    def obtener_tiempo_ms(self):
        """
        Retorna el tiempo actual en milisegundos (para precisión).
        
        Returns:
            float: Tiempo en ms
        """
        return self.tiempo_actual
    
    def establecer_velocidad(self, velocidad):
        """
        Establece la velocidad de simulación.
        
        Args:
            velocidad: Multiplicador (1.0 = tiempo real, 2.0 = doble velocidad)
        """
        if velocidad > 0:
            self.velocidad = velocidad
    
    def pausar(self):
        """Pausa la simulación"""
        self.en_ejecucion = False
    
    def reanudar(self):
        """Reanuda la simulación"""
        self.en_ejecucion = True
    
    def reset(self):
        """Reinicia el reloj a cero"""
        self.tiempo_actual = 0.0
        self.historial_tiempos = []
    
    def __str__(self):
        return f"Clock(tiempo={self.tiempo_actual:.2f}, velocidad={self.velocidad}x)"
