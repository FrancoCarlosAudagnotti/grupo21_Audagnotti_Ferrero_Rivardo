from simpleai.search import astar, SearchProblem

class RoverProblem(SearchProblem):

    def __init__(self, initial_state, zonas_sombra):
        super().__init__(initial_state)
        self.zonas_sombra = zonas_sombra

    def actions(self, state):
        #
        # posibles_acciones = (
        #    #accion, valor
        #    #los desplazamientos son en fila, columna
        #    ("moverse",(1,0)), #derecha
        #    ("moverse",(0,1)), #arriba
        #    ("moverse",(-1,0)), #izquierda
        #    ("moverse",(0,-1)), #abajo
        #    ("sobremarcha",(2,0)), #derecha
        #    ("sobremarcha",(0,2)), #ariba
        #    ("sobremarcha",(-2,0)), #izquierda
        #    ("sobremarcha",(0,-2)), #abajo
        #    ("equipar","termico"), #taladro térmico
        #    ("equipar","percusion"), #taladro de percusion
        #    ("recolectar","ignea"), #muestra ignea
        #    ("recolectar","sedimentaria"),#muestra sedimentaria
        #    ("depositar", None), #depositar
        #    ("recargar", None) #recargar
        # )
        #
        # reemplazamos iterar sobre posibles acciones por generar solo las acciones válidas según el estado actual, para optimizar la búsqueda
        #

        #desempaquetamos todos los valores del estado
        posicion_rover, bateria_actual, igneas_restantes, sed_restantes, taladro_equipado, muestras_almacenadas = state
        acciones_validas = []

        rover_fila, rover_columna = posicion_rover
        total_muestras_restantes = len(igneas_restantes) + len(sed_restantes)

        #- coste 0 ----------------------
        if bateria_actual < 20 and posicion_rover not in self.zonas_sombra:
            acciones_validas.append(('recargar', None))

        #- coste 1 ----------------------
        if bateria_actual > 1:
            # cada posible movimiento
            for mover_fila, mover_columna in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                acciones_validas.append(('moverse', (rover_fila + mover_fila, rover_columna + mover_columna)))

            # si está en muestra ignea
            if posicion_rover in igneas_restantes and taladro_equipado != 'termico':
                acciones_validas.append(('equipar', 'termico'))
            # si está en muestra sedimentaria
            elif posicion_rover in sed_restantes and taladro_equipado != 'percusion':
                acciones_validas.append(('equipar', 'percusion'))

            # depositar cuando tiene 2 o cuando tiene 1 pero no quedan muestras
            if muestras_almacenadas == 2 or (muestras_almacenadas == 1 and total_muestras_restantes == 0):
                acciones_validas.append(('depositar', None))

        #- coste 3 ----------------------
        if bateria_actual > 3 and muestras_almacenadas < 2:
            if taladro_equipado == 'termico' and posicion_rover in igneas_restantes:
                acciones_validas.append(('recolectar', 'ignea'))
            elif taladro_equipado == 'percusion' and posicion_rover in sed_restantes:
                acciones_validas.append(('recolectar', 'sedimentaria'))

        #- coste 4 ----------------------
        if bateria_actual > 4:
            # cada posible sobremarcha
            for mover_fila, mover_columna in ((2, 0), (0, 2), (-2, 0), (0, -2)):
                acciones_validas.append(('sobremarcha', (rover_fila + mover_fila, rover_columna + mover_columna)))
        return tuple(acciones_validas)
    
    def result(self, state, action):
        #desempaquetamos accion y estado
        accion, valor = action
        posicion_rover, bateria_actual, igneas_restantes, sed_restantes, taladro_equipado, muestras_alamacenadas = state

        #batería -1
        if accion == 'moverse':
            posicion_rover = valor
            bateria_actual -= 1
        if accion == 'equipar':
            taladro_equipado = valor
            bateria_actual -= 1
        if accion == 'depositar':
            muestras_alamacenadas = 0
            bateria_actual -= 1
        #batería -3
        if accion == 'recolectar':
            if(valor == "ignea"):
                igneas_restantes = tuple(m for m in igneas_restantes if m != posicion_rover)
            else:
                sed_restantes = tuple(m for m in sed_restantes if m != posicion_rover)
            muestras_alamacenadas += 1
            bateria_actual -= 3
        #batería -4
        if accion == 'sobremarcha':
            posicion_rover = valor
            bateria_actual -= 4
        #batería +10 caso <20
        if accion == 'recargar':
            bateria_actual = min(20, bateria_actual + 10)
        #batería +10 caso <=10
        #if accion == 'recargar':
        #    bateria_actual += 10
        return (posicion_rover, bateria_actual, igneas_restantes, sed_restantes, taladro_equipado, muestras_alamacenadas)

    def cost(self,state,action, state2):
        costo = 0 #segundos
        accion, _ = action
        muestras_almacenadas = state[5]
        # - coste 1 minuto --------------
        if accion == 'moverse':
            costo = 1
        elif accion == 'sobremarcha':
            costo = 1
        # - coste 2 o 1 minuto --------------
        elif accion == 'depositar':
            if muestras_almacenadas == 2:
                costo = 2
            else:
                costo = 1
        # - coste 3 batería --------------
        elif accion == 'recolectar':
            costo = 2
        # - coste 3 minutos --------------
        elif accion == 'equipar':
            costo = 3
        # - coste 4 minutos --------------
        elif accion == 'recargar':
            costo = 4
        return costo

    def is_goal(self, state):
        #desempaquetamos estado
        _, _, igneas_restantes, sed_restantes, _, muestras_almacenadas = state
        return (len(igneas_restantes) + len(sed_restantes)) == 0 and muestras_almacenadas == 0

    def heuristic(self, state):
        #desempaquetamos
        posicion_rover, _, igneas_restantes, sed_restantes, _, muestras_almacenadas = state
        fila, columna = posicion_rover

        muestras_restantes_totales = igneas_restantes + sed_restantes

        #su no quedan muestras, es muestras almacenadas * 1
        if len(muestras_restantes_totales) == 0:
            return muestras_almacenadas
        
        #distancia manhattan -> investiguen
        #calculamos distancia minima a la muestra más cercana
        distancia_minima = min(abs(fila - muestra[0]) + abs(columna - muestra[1]) for muestra in muestras_restantes_totales)
        
        #bounding box -> investiguen
        #separamos en filas y columnas
        filas_muestras = [muestra[0] for muestra in muestras_restantes_totales]
        columnas_muestras = [muestra[1] for muestra in muestras_restantes_totales]
        #calculamos la distancia entre el más lejano y el más cercano
        distancia_filas = max(filas_muestras) - min(filas_muestras)
        distancia_columnas = max(columnas_muestras) - min(columnas_muestras)
        #con los limites definidos podemos sacar 
        distancia_maxima = distancia_filas + distancia_columnas

        #costo usando sobremarcha
        costo_moverse = (distancia_minima + distancia_maxima + 1) // 2
        # el razomiento es que la distancia mínima es la muestra más cercana, entonces si o si tiene que acercarse a la muestra más cercana,
        # despues se le suma la distancia máxima, que es la distancia más larga posible de recorrer pasando por todas las muestras que están dentro de la boundng box
        # se suma 1 para que en casos impares no se quede corto

        #costo de recolectar y depositar faltantes
        costo_recolectar = 2 * len(muestras_restantes_totales)
        costo_depositar = len(muestras_restantes_totales)

        #costo de depositar almacenadas
        costo_depositar_almacenadas = muestras_almacenadas
        
        return costo_moverse + costo_recolectar + costo_depositar + costo_depositar_almacenadas


def planear_rover(
    rover_inicio,
    bateria_inicial,
    zonas_sombra,
    muestras_igneas,
    muestras_sedimentarias,
):
    estado_inicial = (
        rover_inicio,
        bateria_inicial,
        tuple(muestras_igneas),
        tuple(muestras_sedimentarias),
        "ninguno", #taladro
        0, #muestras almacenadas
    )

    problema = RoverProblem(estado_inicial, tuple(zonas_sombra))
    #viewer = WebViewer() # BaseViewer() para consola. IMPORTANTE: DESACTIVAR AL ENTREGAR
    resultado = astar(problema, graph_search=True) #, viewer=viewer)
    acciones = [accion for accion, estado in resultado.path() if accion is not None] #(problema.actions(estado_inicial))
    
    return acciones

if __name__ == "__main__":
    acciones = planear_rover()
    print(acciones)