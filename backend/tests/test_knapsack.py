"""Testes do Problema da Mochila 0/1 (Carregamento do Veículo)."""

from itertools import combinations
import random
import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.algoritmos.knapsack import VEHICLE_CAPACITY_KG, run_knapsack
from app.routes.algoritmos import router


def brute_force_best_value(orders, capacity_kg):
    """Testa todos os subconjuntos (2^n) e devolve o maior valor que cabe no veículo."""
    best = 0.0
    for size in range(len(orders) + 1):
        for subset in combinations(orders, size):
            weight = sum(round(order["weightKg"] * 10) for order in subset)
            if weight <= round(capacity_kg * 10):
                best = max(best, sum(order["totalPrice"] for order in subset))
    return round(best, 2)


class KnapsackTests(unittest.TestCase):
    def setUp(self):
        self.demo_orders = [
            {"id": 101, "weightKg": 1.2, "totalPrice": 499.90},
            {"id": 102, "weightKg": 1.1, "totalPrice": 650.00},
            {"id": 103, "weightKg": 0.5, "totalPrice": 1899.00},
            {"id": 104, "weightKg": 0.9, "totalPrice": 249.90},
            {"id": 105, "weightKg": 22.0, "totalPrice": 1250.00},
        ]

    def test_demo_orders_walk(self):
        result = run_knapsack(self.demo_orders, "walk", verbose=False)
        self.assertEqual(result["selectedOrderIds"], [101, 102, 103])
        self.assertEqual(result["leftOutOrderIds"], [104])
        self.assertEqual(result["oversizedOrderIds"], [105])
        self.assertAlmostEqual(result["totalValue"], 3048.90)
        self.assertAlmostEqual(result["totalWeightKg"], 2.8)

    def test_car_loads_everything(self):
        result = run_knapsack(self.demo_orders, "car", verbose=False)
        self.assertEqual(result["selectedOrderIds"], [101, 102, 103, 104, 105])
        self.assertEqual(result["leftOutOrderIds"], [])

    def test_greedy_by_value_is_not_optimal(self):
        # Pegar o pedido mais caro primeiro (guloso) daria 100; a PD encontra 120.
        orders = [
            {"id": 1, "weightKg": 3.0, "totalPrice": 100.0},
            {"id": 2, "weightKg": 2.0, "totalPrice": 60.0},
            {"id": 3, "weightKg": 2.0, "totalPrice": 60.0},
        ]
        result = run_knapsack(orders, capacity_kg=4.0, verbose=False)
        self.assertEqual(result["selectedOrderIds"], [2, 3])
        self.assertAlmostEqual(result["totalValue"], 120.0)

    def test_matches_brute_force_on_random_batches(self):
        rng = random.Random(42)
        for _ in range(200):
            orders = [
                {
                    "id": order_id,
                    "weightKg": round(rng.uniform(0.1, 6.0), 1),
                    "totalPrice": round(rng.uniform(10, 2000), 2),
                }
                for order_id in range(rng.randint(0, 8))
            ]
            capacity_kg = rng.choice(list(VEHICLE_CAPACITY_KG.values())[:3])
            result = run_knapsack(orders, capacity_kg=capacity_kg, verbose=False)
            self.assertAlmostEqual(result["totalValue"], brute_force_best_value(orders, capacity_kg), places=2)

            chosen = [order for order in orders if order["id"] in result["selectedOrderIds"]]
            self.assertLessEqual(sum(round(o["weightKg"] * 10) for o in chosen), round(capacity_kg * 10))
            self.assertAlmostEqual(sum(o["totalPrice"] for o in chosen), result["totalValue"], places=2)

    def test_empty_batch(self):
        result = run_knapsack([], "moto", verbose=False)
        self.assertEqual(result["selectedOrderIds"], [])
        self.assertEqual(result["totalValue"], 0.0)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            run_knapsack(self.demo_orders, "aviao", verbose=False)
        with self.assertRaises(ValueError):
            run_knapsack(self.demo_orders, capacity_kg=0, verbose=False)
        with self.assertRaises(ValueError):
            run_knapsack(self.demo_orders, capacity_kg=0.04, verbose=False)
        with self.assertRaises(ValueError):
            run_knapsack(self.demo_orders + [self.demo_orders[0]], "car", verbose=False)
        with self.assertRaises(ValueError):
            run_knapsack([{"id": 1, "weightKg": -1, "totalPrice": 10}], "car", verbose=False)


class KnapsackEndpointTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(router)
        self.client = TestClient(app)
        self.orders = [
            {"id": 1, "weightKg": 1.2, "totalPrice": 10.0},
            {"id": 2, "weightKg": 2.5, "totalPrice": 30.0},
        ]

    def test_endpoint_returns_selected_orders(self):
        response = self.client.post("/api/load/knapsack", json={"orders": self.orders, "transport": "walk"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["selectedOrderIds"], [2])

    def test_endpoint_rejects_missing_or_invalid_transport(self):
        self.assertEqual(self.client.post("/api/load/knapsack", json={"orders": self.orders}).status_code, 422)
        self.assertEqual(
            self.client.post("/api/load/knapsack", json={"orders": self.orders, "transport": "aviao"}).status_code,
            422,
        )


if __name__ == "__main__":
    unittest.main()
