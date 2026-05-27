from simpleai.search import (
    CspProblem,
    LEAST_CONSTRAINING_VALUE,
    MOST_CONSTRAINED_VARIABLE,
    backtrack,
)
from itertools import combinations

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):

    #Variables: 'hab', 'gen', 'lab', 'dep', 'air'
    variables = []
    for i in range(habs):
        variables.append(f'hab_{i}')
    for i in range(generators):
        variables.append(f'gen_{i}')
    for i in range(labs):
        variables.append(f'lab_{i}')
    for i in range(deposits):
        variables.append(f'dep_{i}')
    for i in range(airlocks):
        variables.append(f'air_{i}')

    #Dominios: 
    #desempaquetamos en filas y columnas para iterar
    filas, columnas = camp_size
    
    # contemplan cráteres, no los agrega, evitamos restricción
    # para 'hab' solo interiores, evitamos restricción
    dominios_hab = []
    for fila in range(1, filas - 1):
        for columna in range(1, columnas - 1):
            if (fila, columna) not in craters:
                dominios_hab.append((fila, columna))
    
    # para 'air' solo límites, evitamos restricción
    dominios_air = []
    for fila in range(filas):
        for columna in range(columnas):
            if (fila == 0 or fila == filas - 1 or columna == 0 or columna == columnas - 1) and (fila, columna) not in craters:
                dominios_air.append((fila, columna))

    dominios = {}
    for variable in variables:
        if variable.startswith('hab'):
            dominios[variable] = dominios_hab.copy()
        elif variable.startswith('air'):
            dominios[variable] = dominios_air.copy()
        else:
            dominios[variable] = [(fila, columna) for fila in range(filas) for columna in range(columnas) if (fila, columna) not in craters]

    #Restricciones: 
    restricciones = []

    # Restriccion 1:
    # No pueden haber dos módulos en la misma celda
    def no_superponen(vars, values):
        return values[0] != values[1]

    # Restriccion 5:
    # Un generador no puede ser adyacente (estar a pegado) a un módulo habitacional
    def gen_hab_no_adyacentes(vars, values):
        #revisamos si gen y hab son adyacentes y viceversa
        if (vars[0].startswith('gen') and vars[1].startswith('hab')) or (vars[0].startswith('hab') and vars[1].startswith('gen')):
            (fila1, columna1), (fila2, columna2) = values
            #distancia manhattan, para no adyacencia otrogonal
            return abs(fila1 - fila2) + abs(columna1 - columna2) > 1
        return True #si la distancia es mayr a 1 significa que estan separados

    # Restriccion 6: ADYACENCIA ORTOGONAL, NO DIAGONAL
    # Dos generadores no pueden ser adyacentes (estar a pegado) entre sí
    def gen_gen_no_adyacentes(vars, values):
        #revisamos si 2 gen son adyacentes
        if vars[0].startswith('gen') and vars[1].startswith('gen'):
            (fila1, columna1), (fila2, columna2) = values
            #distancia manhattan, para no adyacencia otrogonal
            return abs(fila1 - fila2) + abs(columna1 - columna2) > 1
        return True #si la distancia es mayr a 1 significa que estan separados

    # Restriccion 7: ADYACENCIA ORTOGONAL, NO DIAGONAL
    # Cada laboratorio debe ser adyacente (estar a pegado) a al menos un depósito
    def lab_dep_adyacentes(vars, values):
        #obtenemos la posición de laboratorio, 
        pos_lab = values[0]
        #obtenemos las posiciones de los depósitos
        pos_depositos = values[1:]
        # revisamos si alguno de los depósitos es adyasente a un laboratorio
        for pos_dep in pos_depositos:
            #distancia manhattan, para adyacencia otrogonal
            if abs(pos_lab[0] - pos_dep[0]) + abs(pos_lab[1] - pos_dep[1]) == 1:
                return True # si encuentra uno ya basta para devolver true
        return False 

    # Restriccion 8: ADYACENCIA ORTOGONAL, NO DIAGONAL
    # Cada módulo habitacional debe tener al menos una celda adyacente (estar a pegado) libre (sin módulo ni cráter) 
    def hab_escape_adyacente(vars, values):
        #desempaquetamos la posición del módulo hab
        fila_hab, columna_hab = values[0]

        adyacentes_ortogonales = [
            (fila_hab + 1, columna_hab), 
            (fila_hab - 1, columna_hab), 
            (fila_hab, columna_hab + 1), 
            (fila_hab, columna_hab - 1)
        ]
        
        bloqueos = 0
        
        for pos in values[1:]: # para cada posición ocupada por otro módulo
            if pos in adyacentes_ortogonales: # si esa posición es adyacente al módulo hab
                bloqueos += 1

        return bloqueos < 4 # si hay menos de 4 bloqueos, significa que hay al menos una celda adyacente libre

    for var1, var2 in combinations(variables, 2):
        restricciones.append(((var1, var2), no_superponen))
        restricciones.append(((var1, var2), gen_hab_no_adyacentes))
        restricciones.append(((var1, var2), gen_gen_no_adyacentes))

    for var in variables:
        if var.startswith('lab'):
            restricciones.append(((var, *[v for v in variables if v.startswith('dep')]), lab_dep_adyacentes)) # garantizamos que las variables usadas sean (lab_x, dep_x,....)
        elif var.startswith('hab'):
            otras_variables = [v for v in variables if v != var] # obtenemos las otras variables para la restricción
            restricciones.append(((var, *otras_variables), hab_escape_adyacente)) # lo mismo que antes pero lo correspondiente para la restricción 8

    domino = CspProblem(variables, dominios, restricciones)
    solucion = backtrack(
        domino,
        variable_heuristic=MOST_CONSTRAINED_VARIABLE,
        value_heuristic=LEAST_CONSTRAINING_VALUE,
    )
    if solucion is None:
        return None

    # para devolver en el formato requerido les borramos el sufjo y nos quedamos con la base
    def tipo_base(tipo):
        if tipo.startswith("hab"):
            return "hab"
        if tipo.startswith("gen"):
            return "gen"
        if tipo.startswith("lab"):
            return "lab"
        if tipo.startswith("dep"):
            return "dep"
        if tipo.startswith("air"):
            return "air"

    resultado = []
    for tipo, (fila, columna) in solucion.items():
        resultado.append((tipo_base(tipo), fila, columna))
    return resultado
