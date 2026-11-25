"""
Módulo de Programação Dinâmica - Problema da Mochila 0/1 (Knapsack)
Disciplina: Projeto de Algoritmos (PA)

Aplicação: Carregamento do Veículo.
Cada tipo de transporte do entregador suporta um peso máximo de carga (W).
Cada pedido i possui um peso w_i e um valor v_i. O objetivo é escolher o
subconjunto de pedidos que cabe no veículo e que maximiza o valor total.
"""

from typing import Any, Dict, List

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
