"""
Módulo de Programação Dinâmica - Problema da Mochila 0/1 (Knapsack)
Disciplina: Projeto de Algoritmos (PA)

Aplicação: Carregamento do Veículo.
Cada tipo de transporte do entregador suporta um peso máximo de carga (W).
Cada pedido i possui um peso w_i e um valor v_i. O objetivo é escolher o
subconjunto de pedidos que cabe no veículo e que maximiza o valor total.
"""

from typing import Any, Dict, List, Optional

# Capacidade máxima de carga (kg) por tipo de transporte
VEHICLE_CAPACITY_KG = {
    "walk": 3.0,
    "bike": 8.0,
    "moto": 20.0,
    "car": 150.0,
}

# A PD trabalha com pesos inteiros: 1 unidade = 0,1 kg (100 g)
UNITS_PER_KG = 10


def kg_to_units(weight_kg: float) -> int:
    """Converte um peso em kg para unidades inteiras de 100 g."""
    return int(round(weight_kg * UNITS_PER_KG))


def prepare_items(orders: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Transforma os pedidos em itens da mochila:
      - id:     identificador do pedido
      - weight: peso w_i em unidades inteiras
      - value:  valor v_i do pedido (totalPrice)
    """
    items = []
    for order in orders:
        items.append({
            "id": order["id"],
            "weight": kg_to_units(float(order.get("weightKg") or 0.0)),
            "value": float(order.get("totalPrice") or 0.0),
        })
    return items


def build_knapsack_table(items: List[Dict[str, Any]], capacity: int) -> List[List[float]]:
    """
    Monta a tabela da Programação Dinâmica (bottom-up).

    OPT(i, w) = maior valor usando apenas os i primeiros pedidos com capacidade w.

    Recorrência:
      OPT(0, w) = 0
      OPT(i, w) = OPT(i-1, w)                                   se w_i > w
      OPT(i, w) = max(OPT(i-1, w), v_i + OPT(i-1, w - w_i))     caso contrário

    Complexidade: O(n * W) de tempo e espaço.
    """
    n = len(items)
    opt = [[0.0] * (capacity + 1) for _ in range(n + 1)]

    for i in range(1, n + 1):
        weight = items[i - 1]["weight"]
        value = items[i - 1]["value"]
        for w in range(capacity + 1):
            if weight > w:
                opt[i][w] = opt[i - 1][w]
            else:
                opt[i][w] = max(opt[i - 1][w], value + opt[i - 1][w - weight])

    return opt


def find_selected_items(
    items: List[Dict[str, Any]],
    opt: List[List[float]],
    capacity: int
) -> List[Dict[str, Any]]:
    """
    Traceback: percorre a tabela de trás para frente para descobrir quais pedidos
    entraram na solução ótima.

    Se OPT(i, w) == OPT(i-1, w), o pedido i não foi escolhido.
    Caso contrário, ele foi escolhido e a capacidade restante passa a ser w - w_i.

    Complexidade: O(n).
    """
    selected = []
    w = capacity
    for i in range(len(items), 0, -1):
        if opt[i][w] != opt[i - 1][w]:
            selected.append(items[i - 1])
            w -= items[i - 1]["weight"]
    selected.reverse()
    return selected


def print_knapsack_log(
    items: List[Dict[str, Any]],
    opt: List[List[float]],
    capacity: int,
    selected: List[Dict[str, Any]],
    transport: Optional[str],
    max_columns: int = 8
) -> None:
    """
    Imprime no terminal o passo a passo didático da PD:
    os itens, uma amostra da tabela OPT(i, w) e a decisão do traceback para cada pedido.
    """
    print("\n------ MOCHILA 0/1 - CARREGAMENTO DO VEICULO (PROGRAMACAO DINAMICA) ------")
    print(f"Transporte: {transport} | Capacidade: {capacity / UNITS_PER_KG:.1f} kg ({capacity} unidades de 100 g)")
    print(f"Pedidos analisados: {len(items)} | Tabela OPT: {len(items) + 1} x {capacity + 1}")
    for item in items:
        print(f"  Pedido #{item['id']}: peso = {item['weight'] / UNITS_PER_KG:.1f} kg | valor = R$ {item['value']:.2f}")

    # Amostra de colunas igualmente espaçadas (a tabela completa pode ter milhares de colunas)
    step = max(1, capacity // (max_columns - 1)) if max_columns > 1 else capacity
    columns = sorted(set(list(range(0, capacity + 1, step)) + [capacity]))
    print("--------------------------------------------------------------------------")
    print("Tabela OPT(i, w) [amostra de colunas, w em kg]:")
    print("i \\ w     " + "".join(f"{w / UNITS_PER_KG:>10.1f}" for w in columns))
    for i in range(len(items) + 1):
        label = "vazio" if i == 0 else f"#{items[i - 1]['id']}"
        print(f"{i:<2} {label:<7}" + "".join(f"{opt[i][w]:>10.2f}" for w in columns))

    print("--------------------------------------------------------------------------")
    print("Traceback (de OPT(n, W) ate OPT(0, w)):")
    selected_ids = {item["id"] for item in selected}
    w = capacity
    for i in range(len(items), 0, -1):
        item = items[i - 1]
        if item["id"] in selected_ids:
            print(f"  [ESCOLHIDO] Pedido #{item['id']}: OPT({i}, {w}) = {opt[i][w]:.2f} != OPT({i - 1}, {w}) -> w = {w - item['weight']}")
            w -= item["weight"]
        else:
            print(f"  [DESCARTADO] Pedido #{item['id']}: OPT({i}, {w}) = OPT({i - 1}, {w}) = {opt[i][w]:.2f}")

    used = sum(item["weight"] for item in selected)
    print("--------------------------------------------------------------------------")
    print(f"Pedidos carregados: {[f'#{item["id"]}' for item in selected]}")
    print(f"Peso utilizado: {used / UNITS_PER_KG:.1f} kg de {capacity / UNITS_PER_KG:.1f} kg")
    print(f"Valor total: R$ {opt[len(items)][capacity]:.2f}")
    print("--------------------------------------------------------------------------\n")


def run_knapsack(
    orders: List[Dict[str, Any]],
    transport: Optional[str] = None,
    capacity_kg: Optional[float] = None,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Executa o carregamento ótimo do veículo.
    A capacidade vem do tipo de transporte ou pode ser informada diretamente (capacity_kg).
    """
    if capacity_kg is None:
        if transport not in VEHICLE_CAPACITY_KG:
            raise ValueError("Tipo de transporte inválido. Use 'walk', 'bike', 'moto' ou 'car'.")
        capacity_kg = VEHICLE_CAPACITY_KG[transport]

    if capacity_kg <= 0:
        raise ValueError("A capacidade do veículo deve ser maior que zero.")

    order_ids = [order["id"] for order in orders]
    if len(set(order_ids)) != len(order_ids):
        raise ValueError("O lote contém IDs de pedidos duplicados.")

    items = prepare_items(orders)
    for item in items:
        if item["weight"] < 0 or item["value"] < 0:
            raise ValueError(f"O pedido #{item['id']} possui peso ou valor negativo.")

    capacity = kg_to_units(capacity_kg)
    if capacity == 0:
        raise ValueError("A capacidade mínima do veículo é de 0,1 kg.")
    opt =build_knapsack_table(items, capacity)
    selected = find_selected_items(items, opt, capacity)
    if verbose:
        print_knapsack_log(items, opt, capacity, selected, transport)

    selected_ids = [item["id"] for item in selected]
    used_units = sum(item["weight"] for item in selected)
    oversized_ids = [item["id"] for item in items if item["weight"] > capacity]
    left_out_ids = [
        item["id"] for item in items
        if item["id"] not in selected_ids and item["id"] not in oversized_ids
    ]

    return {
        "transport": transport,
        "capacityKg": capacity_kg,
        "selectedOrderIds": selected_ids,
        "leftOutOrderIds": left_out_ids,
        "oversizedOrderIds": oversized_ids,
        "totalValue": round(opt[len(items)][capacity], 2),
        "totalWeightKg": round(used_units / UNITS_PER_KG, 1),
        "usedCapacityPercent": round(100 * used_units / capacity, 1),
        "tableSize": {"rows": len(items) + 1, "columns": capacity + 1},
    }
