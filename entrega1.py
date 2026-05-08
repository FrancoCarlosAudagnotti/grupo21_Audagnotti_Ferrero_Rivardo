from simpleai.search import astar

mapa = 4

class roverProblem(Problem):
    



    def actions(self,state):
        
        casilla_actual = state[-1]
        muestras_igneas = state[3]
        muestras_sedimentarias = state[4]
        bateria = state[1]
        muestras_totales = len(muestras_igneas) + len(muestras_sedimentarias)
        deposito = 0
        sombras = state[2]

        posibles_acciones = ( 
            #Fila, Columna
            ("moverse",(1,0)), #Moverse derecha
            ("moverse",(0,1)), #Moverse arriba
            ("moverse",(-1,0)), #Moverse izquierda
            ("moverse",(0,-1)), #Moverse abajo
            ("sobremarcha",(2,0)), #Sobremarcha derecha
            ("sobremarcha",(0,2)), #Sobremarcha
            ("sobremarcha",(-2,0)), #Sobremarcha izquierda
            ("sobremarcha",(0,-2)), #Sobremarcha abajo
            ("equipar","termico"), #Equipar taladro térmico
            ("equipar","percusion"), #Equipar taladro de percusion
            ("recolectar","ignea"), #Recolectar ignea
            ("recolectar","sedimentaria"),#Recolectar sedimentaria
            ("depositar", None), #depositar
            ("recargar", None) #recargar
        )
        
        acciones_validas = []


        for accion in posibles_acciones:         
            if (accion[0] in ('moverse', 'sobremarcha')):
                for mov in accion[1]:
                    nueva_casilla = (
                        casilla_actual[0] + mov[0],
                        casilla_actual[1] + mov[1])
                if 0 <= nueva_casilla[0] >= (mapa-1) and nueva_casilla[1] <= (mapa-1):
                    if nueva_casilla not in state:
                        acciones_validas.append(accion)                  
            elif(accion[0] == 'equipar'):
                for muestra_ig in muestras_igneas:
                    if muestra_ig == casilla_actual: 
                        acciones_validas.append(posibles_acciones[8])

                for muestra_sed in muestras_sedimentarias:
                    if muestra_sed == casilla_actual: 
                        acciones_validas.append(posibles_acciones[9])
                        
            elif(accion[0] == 'recolectar'):
                for muestra_ig in muestras_igneas:
                    if muestra_ig == casilla_actual: 
                        acciones_validas.append(posibles_acciones[10])

                for muestra_sed in muestras_sedimentarias:
                    if muestra_sed == casilla_actual: 
                        acciones_validas.append(posibles_acciones[11])
            elif (accion[0] == 'depositar'):
                acciones_validas.append(accion)
            
            elif (accion[0] == 'recargar'):
                if (casilla_actual not in sombras):
                    acciones_validas.append(accion)                      
        return acciones_validas



    def result(self,state,action):
        nuevo_estado = state
        if action[0] == 'moverse':
            nuevo_estado[0] = (
                        nuevo_estado[0][0] + action[1][0],
                        nuevo_estado[0][1] + action[1][1])
        
        return nuevo_estado




    def heuristic(self,state):
        return 0
    

    def cost(self,state,action, state2):
        return f"{minutos},{segundos}"
    

    def is_soal(self,state):
        return True



if __name__ == "__main__":

    estado_ini = planear_rover(
    rover_inicio=(0, 0),
    bateria_inicial=20,
    zonas_sombra=[(0, 1), (0, 2)],
    muestras_igneas=[(1, 1), (1, 2)],
    muestras_sedimentarias=[(2, 3)],
)

