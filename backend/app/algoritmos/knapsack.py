"""
Módulo de Programação Dinâmica - Problema da Mochila 0/1 (Knapsack)
Disciplina: Projeto de Algoritmos (PA)

Aplicação: Carregamento do Veículo.
Cada tipo de transporte do entregador suporta um peso máximo de carga (W).
Cada pedido i possui um peso w_i e um valor v_i. O objetivo é escolher o
subconjunto de pedidos que cabe no veículo e que maximiza o valor total.
"""

# Capacidade máxima de carga (kg) por tipo de transporte
VEHICLE_CAPACITY_KG = {
    "walk": 3.0,
    "bike": 8.0,
    "moto": 20.0,
    "car": 150.0,
}
