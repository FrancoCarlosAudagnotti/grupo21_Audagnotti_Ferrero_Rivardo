from simpleai.search import SearchProblem, astar

class RoverProblem(SearchProblem):
    def __init__(self, initial_state, zonas_sombra):
        super().__init__(initial_state)
        # Convertimos zonas de sombra a set para búsquedas rápidas (O(1))
        self.zonas_sombra = set(zonas_sombra)

    def actions(self, state):
        pos, bateria, taladro, carga, igneas, sedimentarias = state
        r, c = pos
        acciones_validas = []

        # 1. Moverse: Toma 1 minuto, consume 1 batería
        if bateria > 1:
            for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                acciones_validas.append(("moverse", (r + dr, c + dc)))

        # 2. Sobremarcha: Toma 1 minuto, consume 4 batería (2 celdas en línea recta)
        if bateria > 4:
            for dr, dc in [(0, 2), (0, -2), (2, 0), (-2, 0)]:
                acciones_validas.append(("sobremarcha", (r + dr, c + dc)))

        # 3. Equipar taladro: Toma 3 minutos, consume 1 batería
        if bateria > 1:
            if taladro != "termico" and igneas:
                acciones_validas.append(("equipar", "termico"))
            if taladro != "percusion" and sedimentarias:
                acciones_validas.append(("equipar", "percusion"))

        # 4. Perforar y recolectar: Toma 2 minutos, consume 3 batería
        if bateria > 3 and carga < 2:
            if pos in igneas and taladro == "termico":
                acciones_validas.append(("recolectar", "ignea"))
            if pos in sedimentarias and taladro == "percusion":
                acciones_validas.append(("recolectar", "sedimentaria"))

        # 5. Depositar cápsula: Toma 1 min/muestra, consume 1 batería
        if bateria > 1 and carga > 0:
            faltantes = len(igneas) + len(sedimentarias)
            # Solo deposita si tiene 2 muestras o si ya no quedan más por recolectar
            if carga == 2 or (carga > 0 and faltantes == 0):
                acciones_validas.append(("depositar", None))

        # 6. Desplegar paneles solares (recargar): Toma 4 minutos, restaura 10 (límite 20)
        # No consume batería, pero requiere no estar en zona de sombra
        if pos not in self.zonas_sombra and bateria < 20:
            acciones_validas.append(("recargar", None))

        return acciones_validas

    def result(self, state, action):
        pos, bateria, taladro, carga, igneas, sedimentarias = state
        tipo_accion, param = action

        # Copiamos los sets inmutables para modificarlos
        nuevas_igneas = set(igneas)
        nuevas_sedi = set(sedimentarias)

        if tipo_accion == "moverse":
            pos = param
            bateria -= 1
        elif tipo_accion == "sobremarcha":
            pos = param
            bateria -= 4
        elif tipo_accion == "equipar":
            taladro = param
            bateria -= 1
        elif tipo_accion == "recolectar":
            if param == "ignea":
                nuevas_igneas.remove(pos)
            else:
                nuevas_sedi.remove(pos)
            carga += 1
            bateria -= 3
        elif tipo_accion == "depositar":
            carga = 0
            bateria -= 1
        elif tipo_accion == "recargar":
            bateria = min(20, bateria + 10)

        return (pos, bateria, taladro, carga, frozenset(nuevas_igneas), frozenset(nuevas_sedi))

    def cost(self, state, action, state2):
        tipo_accion, _ = action
        carga_actual = state[3]

        if tipo_accion in ["moverse", "sobremarcha"]:
            return 1
        elif tipo_accion == "equipar":
            return 3
        elif tipo_accion == "recolectar":
            return 2
        elif tipo_accion == "depositar":
            return 1 * carga_actual  # 1 minuto por cada muestra entregada
        elif tipo_accion == "recargar":
            return 4
        return 0

    def is_goal(self, state):
        _, _, _, carga, igneas, sedimentarias = state
        # El objetivo es haber recolectado todas y tener la bodega vacía (ya depositadas)
        return len(igneas) == 0 and len(sedimentarias) == 0 and carga == 0

    def heuristic(self, state):
        _, _, _, carga, igneas, sedimentarias = state
        # Heurística admisible basada en tiempos mínimos inevitables
        # Recolectar cada muestra toma 2 minutos. Depositar toma 1 minuto por muestra.
        tiempo_recoleccion = (len(igneas) + len(sedimentarias)) * 2
        tiempo_deposito = (len(igneas) + len(sedimentarias) + carga) * 1
        return tiempo_recoleccion + tiempo_deposito


def planear_rover(
    rover_inicio=(0, 0),
    bateria_inicial=20,
    zonas_sombra=[(0, 1), (0, 2)],
    muestras_igneas=[(1, 1), (1, 2)],
    muestras_sedimentarias=[(2, 3)],
):
    # Estado inicial: (pos, batería, taladro, carga, igneas, sedimentarias)
    # Utilizamos frozenset para que las listas de muestras sean inmutables y el estado sea 'hashable'
    estado_inicial = (
        rover_inicio,
        bateria_inicial,
        None,
        0,
        frozenset(muestras_igneas),
        frozenset(muestras_sedimentarias)
    )

    problema = RoverProblem(estado_inicial, zonas_sombra)
    
    # Utilizamos A* ya que busca el costo mínimo (el menor tiempo posible)
    resultado = astar(problema)

    if resultado is None:
        return [] # No se encontró solución

    # Extraemos solo las acciones de la ruta resultante, omitiendo el estado inicial (que tiene accion None)
    acciones = [nodo[0] for nodo in resultado.path() if nodo[0] is not None]
    return acciones


if __name__ == "__main__":
    # Prueba del código usando el escenario por defecto
    acciones_optimas = planear_rover()
    
    print("Secuencia de acciones resultante:")
    for accion in acciones_optimas:
        print(f"  {accion}")