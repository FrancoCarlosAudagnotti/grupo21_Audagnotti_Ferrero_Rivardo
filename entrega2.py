from simpleai.search import (
    CspProblem,
    LEAST_CONSTRAINING_VALUE,
    MOST_CONSTRAINED_VARIABLE,
    backtrack,
)
def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):

    #Variables: 'hab', 'gen', 'lab', 'desp', 'air'
    variables = []
    for i in range(habs):
        variables.append(f'hab_{i}')
    for i in range(generators):
        variables.append(f'gen_{i}')
    for i in range(labs):
        variables.append(f'lab_{i}')
    for i in range(deposits):
        variables.append(f'desp_{i}')
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
        if (vars[0].startswith('gen') and vars[1].startswith('hab')) or (vars[0].startswith('hab') and vars[1].startswith('gen')):
            (fila1, columna1), (fila2, columna2) = values
            #distancia manhattan, para no adyacencia otrogonal
            return abs(fila1 - fila2) + abs(columna1 - columna2) > 1
        return True

    # Restriccion 6: ADYACENCIA ORTOGONAL, NO DIAGONAL
    # Dos generadores no pueden ser adyacentes (estar a pegado) entre sí

    # Restriccion 7: ADYACENCIA ORTOGONAL, NO DIAGONAL
    # Cada laboratorio debe ser adyacente (estar a pegado) a al menos un depósito

    # Restriccion 8: ADYACENCIA ORTOGONAL, NO DIAGONAL
    # Cada módulo habitacional debe tener al menos una celda adyacente (estar a pegado) libre (sin módulo ni cráter) 

    pass



def resolver():
    domino = CspProblem(variables, dominios, restricciones)
    return backtrack(
        domino,
        variable_heuristic=MOST_CONSTRAINED_VARIABLE,
        value_heuristic=LEAST_CONSTRAINING_VALUE,
    )

def main():
    result = resolver()

    if result is None:
        print("No se encontró solución")
        return

    for variable in variables:
        print(result[variable])

if __name__ == "__main__":
    main()