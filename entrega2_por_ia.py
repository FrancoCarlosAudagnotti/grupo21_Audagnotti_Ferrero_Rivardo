from simpleai.search import Csp, backtrack, HIGHEST_DEGREE_VARIABLE, FORWARD_CHECKING

def build_camp(camp_size, habs, generators, labs, deposits, airlocks, craters):
    rows, cols = camp_size

    # Si hay laboratorios pero ningún depósito al que conectarse, es imposible.
    if labs > 0 and deposits == 0:
        return None

    # 1. Definición de Variables
    # Asignamos un identificador único a cada instancia de cada tipo de módulo.
    hab_vars = [f"hab_{i}" for i in range(habs)]
    gen_vars = [f"gen_{i}" for i in range(generators)]
    lab_vars = [f"lab_{i}" for i in range(labs)]
    dep_vars = [f"dep_{i}" for i in range(deposits)]
    air_vars = [f"air_{i}" for i in range(airlocks)]

    variables = hab_vars + gen_vars + lab_vars + dep_vars + air_vars

    # Si no hay módulos por ubicar, retornamos una lista vacía.
    if not variables:
        return []

    # 2. Pre-cálculo de celdas para los dominios
    all_cells = [(r, c) for r in range(rows) for c in range(cols)]
    craters_set = set(craters)
    
    # Restricción 2: Ningún módulo en cráteres [cite: 10]
    valid_cells = [cell for cell in all_cells if cell not in craters_set]
    
    # Restricción 3: Esclusas en el borde [cite: 11]
    edge_cells = [(r, c) for r, c in valid_cells if r == 0 or r == rows - 1 or c == 0 or c == cols - 1]
    
    # Restricción 4: Habitacionales al interior [cite: 12]
    interior_cells = [(r, c) for r, c in valid_cells if 0 < r < rows - 1 and 0 < c < cols - 1]

    # 3. Definición de Dominios
    domains = {}
    for v in variables:
        if v.startswith("hab"):
            domains[v] = interior_cells
        elif v.startswith("air"):
            domains[v] = edge_cells
        else:
            domains[v] = valid_cells

    constraints = []

    # Función auxiliar para adyacencia ortogonal [cite: 17]
    def is_adjacent(pos1, pos2):
        return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1]) == 1

    # Restricción 1: Sin superposición (todas las variables deben tener posiciones distintas)
    def all_diff(variables, values):
        return values[0] != values[1]

    for i in range(len(variables)):
        for j in range(i + 1, len(variables)):
            constraints.append(((variables[i], variables[j]), all_diff))

    # Restricción 5 y 6: Generador aislado de Habitacionales y de otros Generadores [cite: 14]
    def not_adjacent(variables, values):
        return not is_adjacent(values[0], values[1])

    for g in gen_vars:
        for h in hab_vars:
            constraints.append(((g, h), not_adjacent))

    for i in range(len(gen_vars)):
        for j in range(i + 1, len(gen_vars)):
            constraints.append(((gen_vars[i], gen_vars[j]), not_adjacent))

    # Restricción 7: Cada laboratorio adyacente a al menos un depósito [cite: 15]
    def lab_dep_adj(variables, values):
        lab_pos = values[0]
        dep_positions = values[1:]
        for dep_pos in dep_positions:
            if is_adjacent(lab_pos, dep_pos):
                return True
        return False

    if dep_vars:
        for l in lab_vars:
            # Evaluamos el lab junto con todos los depósitos disponibles
            constraints.append(([l] + dep_vars, lab_dep_adj))

    # Restricción 8: Ruta de evacuación para habitacionales [cite: 16]
    def hab_evac(variables, values):
        hab_pos = values[0]
        other_positions = set(values[1:])
        r, c = hab_pos
        adjacents = [(r-1, c), (r+1, c), (r, c-1), (r, c+1)]
        
        for adj in adjacents:
            ar, ac = adj
            if 0 <= ar < rows and 0 <= ac < cols:
                # La celda debe estar libre de cráteres y de otros módulos [cite: 16]
                if adj not in craters_set and adj not in other_positions:
                    return True
        return False

    for h in hab_vars:
        # Evaluamos el habitacional junto con todas las demás variables
        other_vars = [v for v in variables if v != h]
        constraints.append(([h] + other_vars, hab_evac))

    # Optimización Crítica: Rompimiento de simetrías (Symmetry Breaking)
    # Evita que el motor evalúe intercambios inútiles (ej: intercambiar de lugar hab_0 y hab_1)
    def sym_break(variables, values):
        return (values[0][0] * cols + values[0][1]) < (values[1][0] * cols + values[1][1])

    for group in [hab_vars, gen_vars, lab_vars, dep_vars, air_vars]:
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                constraints.append(((group[i], group[j]), sym_break))

    # 4. Resolución del CSP
    problem = Csp(variables, domains, constraints)
    
    # Forward checking y heurística de variables agilizan drásticamente la búsqueda
    result = backtrack(problem, variable_heuristic=HIGHEST_DEGREE_VARIABLE, inference=FORWARD_CHECKING)

    if result:
        # Formatear la salida requerida: lista de tuplas (tipo, fila, columna) [cite: 25]
        return [(v.split('_')[0], pos[0], pos[1]) for v, pos in result.items()]
    
    return None