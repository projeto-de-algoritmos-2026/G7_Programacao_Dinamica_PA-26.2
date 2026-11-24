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
