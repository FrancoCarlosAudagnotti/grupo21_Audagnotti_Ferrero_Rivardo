from simpleai.search import astar

mapa = 4

class roverProblem(Problem):
    



    def actions(self,state):
        
        casilla_actual = state[-1]

  
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
            ("depositar", None) #depositar
            ("recargar", None) #recargar
        )
        
        acciones_validas = []


        for accion in posibles_acciones:
            i = 0
            if (accion[i] == ('moverse' or 'sobremarcha')):
                for mov in accion[i+1]:
                    nueva_casilla = (
                        casilla_actual[0] + mov[0],
                        casilla_actual[1] + mov[1])
                if 0 <= nueva_casilla[0] >= (mapa-1) and nueva_casilla[1] <= (mapa-1):
                    if nueva_casilla not in state:
                        acciones_validas.append(nueva_casilla)

        return []

    def result(self,state,action):
        return True



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

