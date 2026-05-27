import random
from enums import TipoInterrupcion

class GestorInterrupciones:

    def generar_interrupcion(self, proceso):

        tipos = [
            TipoInterrupcion.TIMER,
            TipoInterrupcion.IO_ENTRADA,
            TipoInterrupcion.IO_SALIDA
        ]

        tipo = random.choice(tipos)

        duracion = random.randint(5, 20)

        proceso.contador_interrupciones += 1

        proceso.historial_interrupciones.append({
            'tipo': tipo,
            'duracion': duracion
        })

        return tipo, duracion