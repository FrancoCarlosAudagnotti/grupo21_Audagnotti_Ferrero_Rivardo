from simpleai.search import astar, SearchProblem

class RoverProblem(SearchProblem):

    def __init__(self, initial_state, zonas_sombra):
        super().__init__(initial_state)
        self.zonas_sombra = zonas_sombra

    def actions(self, state):
        posibles_acciones = (
            #accion, valor
            #los desplazamientos son en fila, columna
            ("moverse",(1,0)), #derecha
            ("moverse",(0,1)), #arriba
            ("moverse",(-1,0)), #izquierda
            ("moverse",(0,-1)), #abajo
            ("sobremarcha",(2,0)), #derecha
            ("sobremarcha",(0,2)), #ariba
            ("sobremarcha",(-2,0)), #izquierda
            ("sobremarcha",(0,-2)), #abajo
            ("equipar","termico"), #taladro térmico
            ("equipar","percusion"), #taladro de percusion
            ("recolectar","ignea"), #muestra ignea
            ("recolectar","sedimentaria"),#muestra sedimentaria
            ("depositar", None), #depositar
            ("recargar", None) #recargar
        )
        #desempaquetamos todos los valores del estado
        posicion_rover, bateria_actual, igneas_restantes, sed_restantes, taladro_equipado, muestras_alamacenadas = state
        acciones_validas = []
        
        for accion, valor in posibles_acciones:
            if bateria_actual > 1:               
                if (accion == 'moverse'):
                    mover_fila, mover_columna = valor
                    rover_fila, rover_columna = posicion_rover
                    #definimos la nueva casilla (virtual) a la que se moveria el rover
                    nueva_casilla = (rover_fila + mover_fila, rover_columna + mover_columna)
                    acciones_validas.append((accion, nueva_casilla))
                # ---------------------
                elif(accion == 'equipar'):
                    #si el rover esta en una casilla con muestra ignea y el valor de la accion es termico, se puede equipar
                    if posicion_rover in igneas_restantes and taladro_equipado != 'termico':
                        acciones_validas.append((accion, valor))
                    #si el rover esta en una casilla con muestra sedimentaria y el valor de la accion es percusion, se puede equipar
                    elif posicion_rover in sed_restantes and taladro_equipado != 'percusion':
                        acciones_validas.append((accion, valor))
                # ---------------------
                elif(accion == 'depositar'):
                    #si tiene 2 muestras o quedan muestras impares, puede depositar
                    if muestras_alamacenadas == 2 or (len(igneas_restantes) + len(sed_restantes)) < 2:
                        acciones_validas.append((accion, valor))
            #-----------------------
            if bateria_actual > 3:
                if(accion == 'recolectar'):
                    #si el rover esta en una casilla con muestra ignea, tiene el taladro termico equipado y el valor de la accion es ignea, se puede recolectar
                    if valor == 'ignea' and posicion_rover in igneas_restantes and taladro_equipado == 'termico':
                        acciones_validas.append((accion, valor))
                    #si el rover esta en una casilla con muestra sedimentaria, tiene el taladro de percusion equipado y el valor de la accion es sedimentaria, se puede recolectar
                    elif valor == 'sedimentaria' and posicion_rover in sed_restantes and taladro_equipado == 'percusion':
                        acciones_validas.append((accion, valor))
            #-----------------------
            if bateria_actual > 4:   
                if (accion == 'sobremarcha'):
                    #llamamos funcion de movimiento
                    mover_fila, mover_columna = valor
                    rover_fila, rover_columna = posicion_rover
                    #definimos la nueva casilla (virtual) a la que se moveria el rover
                    nueva_casilla = (rover_fila + mover_fila, rover_columna + mover_columna)
                    acciones_validas.append((accion, nueva_casilla))
            #caso puede recargar siempre que tenga menos de 20
            if bateria_actual < 20:
                if(accion == 'recargar'):
                    #si el rover esta en una zona de sombra y su bateria es menor a la inicial, se puede recargar
                    if posicion_rover not in self.zonas_sombra and bateria_actual < self.bateria_inicial:
                        acciones_validas.append((accion, valor))
            
            #caso puede recargar solo cuandoe es menor o igual a 10 DEMOSTRAR
            #elif bateria_actual <= 10:
            #    if(accion == 'recargar'):
            #       #si el rover esta en una zona de sombra y su bateria es menor a la inicial, se puede recargar
            #        if posicion_rover not in self.zonas_sombra and bateria_actual < self.bateria_inicial:
            #            acciones_validas.append((accion, valor))
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
                muestras_igneas = list(igneas_restantes)
                muestras_igneas.remove(posicion_rover)
                muestras_igneas = tuple((igneas_restantes))
            else:
                muestras_sedimentarias = list(sed_restantes)
                muestras_sedimentarias.remove(posicion_rover)
                muestras_sedimentarias = tuple((sed_restantes))
            muestras_alamacenadas += 1
            bateria_actual -= 3
        #batería -4
        if accion == 'sobremarcha':
            posicion_rover = valor
            bateria_actual -= 4
        #batería +10 caso <20
        if accion == 'recargar':
            bateria_actual += 10
            if bateria_actual > 20:
                bateria_actual = 20
        #batería +10 caso <=10
        #if accion == 'recargar':
        #    bateria_actual += 10
        return (posicion_rover, bateria_actual, igneas_restantes, sed_restantes, taladro_equipado, muestras_alamacenadas)

    def cost(self,state,action, state2):
        costo = 0
        accion, _ = action
        muestras_almacenadas = state[5]

        if accion == 'moverse':
            costo = 1
        elif accion == 'equipar':
            costo = 3
        elif accion == 'depositar':
            if muestras_almacenadas == 2:
                costo = 2
            else:
                costo = 1
        #-----------------------
        elif accion == 'recolectar':
            costo = 2
        #-----------------------
        elif accion == 'sobremarcha':
            costo = 1
        #-----------------------
        elif accion == 'recargar':
            costo = 4
        return costo

    def is_goal(self, state):
        #desempaquetamos estado
        posicion_rover, bateria_actual, igneas_restantes, sed_restantes, taladro_equipado, muestras_alamacenadas = state
        if len(igneas_restantes) == 0 and len(sed_restantes) == 0 and muestras_alamacenadas == 0 and bateria_actual > 0:
            return True
        return False

    def heuristic(self, state):
        posicion, _, igneas, sedimentarias, _, _ = state
        x, y = posicion

        muestras = igneas + sedimentarias
        restantes = len(muestras)

        if restantes == 0:
            return 0

        # distancia a la muestra más cercana
        dist_min = min(abs(x-mx) + abs(y-my) for mx, my in muestras)

        # costo mínimo de movimiento usando sobremarcha
        movimiento_min = (dist_min + 1) // 2

        # si hay solo una muestra
        if restantes == 1:
            return movimiento_min + 3  # moverse, recolectar + depositar

        # si hay varias muestras
        xd = [m[0] for m in muestras]
        yd = [m[1] for m in muestras]

        dispersion_muestras = (max(xd) - min(xd)) + (max(yd) - min(yd))

        costo_recolectar = 2 * restantes
        costo_depositar = restantes

        return movimiento_min + dispersion_muestras + costo_recolectar + costo_depositar


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
        "ninguno", #Taladro
        0, #Muestras almacenadas
    )

    problema = RoverProblem(estado_inicial, tuple(zonas_sombra))
    #viewer = WebViewer() # BaseViewer() para consola. IMPORTANTE: DESACTIVAR AL ENTREGAR
    resultado = astar(problema, graph_search=True) #, viewer=viewer)
    acciones = [accion for accion, estado in resultado.path() if accion is not None] #(problema.actions(estado_inicial))
    
    return acciones

if __name__ == "__main__":
    # Formato coordenadas: (fila, columna)
    acciones = planear_rover(
        # rover_inicio=(0, 0),
        # bateria_inicial=20,
        # zonas_sombra=[(0, 1), (0, 2)],
        # #muestras_igneas=None,
        # #muestras_sedimentarias=None,
        # muestras_igneas=[(1, 1), (1, 2)],
        # muestras_sedimentarias=[(2, 3)],
    )

    print(acciones)