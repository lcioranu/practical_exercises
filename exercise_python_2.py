"""Revenue aggregation exercise for optimization discussions.

This module contains an intentionally non-optimized implementation that computes
total revenue per customer from a list of orders. It is designed to be refactored
during interviews to improve time complexity and code clarity.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict


@dataclass
class Order:
    order_id: str
    customer_id: str
    amount: float


class OrderRepository(ABC):
    @abstractmethod
    def get_orders(self) -> List[Order]:
        pass


class InMemoryOrderRepository(OrderRepository):
    def __init__(self, orders: List[Order]):
        self._orders = orders

    def get_orders(self) -> List[Order]:
        return self._orders


class RevenueService:
    def __init__(self, repo: OrderRepository):
        self.repo = repo

    def revenue_by_customer(self) -> Dict[str, float]:
        orders = self.repo.get_orders()

        unique_customers = []
        for o in orders:
            if o.customer_id not in unique_customers:  # O(n)
                unique_customers.append(o.customer_id)

        result = {}
        for customer_id in unique_customers:
            total = 0.0
            for o in orders:
                if o.customer_id == customer_id:
                    total += o.amount
            result[customer_id] = total

        return result


if __name__ == "__main__":
    orders = [
        Order("1", "c1", 120.0),
        Order("2", "c2", 50.0),
        Order("3", "c1", 30.0),
        Order("4", "c3", 200.0),
        Order("5", "c2", 70.0),
    ]

    service = RevenueService(InMemoryOrderRepository(orders))
    print(service.revenue_by_customer())
