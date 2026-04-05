"""
warehouse api client for shop

this file is the key for lecturer: it shows how shop communicates with warehouse via http API.

required warehouse endpoints:
- GET {WAREHOUSE_BASE_URL}/api/products
- GET {WAREHOUSE_BASE_URL}/api/products/{id}/stock
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

import httpx


class WarehouseClient:
    def __init__(self, base_url: str, timeout_s: float = 5.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_s = timeout_s

    async def get_all_products(self) -> Tuple[bool, str, List[Dict[str, Any]]]:
        """
        returns (ok, message, products)
        """
        url = f"{self.base_url}/api/products"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                r = await client.get(url)
            if r.status_code != 200:
                return False, f"warehouse returned {r.status_code}", []
            data = r.json()
            if not isinstance(data, list):
                return False, "invalid response format (expected list)", []
            return True, "ok", data
        except Exception as e:
            return False, f"warehouse request failed: {e}", []

    async def get_stock(self, product_id: int) -> Tuple[bool, str, int | None]:
        """
        returns (ok, message, stock)
        """
        url = f"{self.base_url}/api/products/{product_id}/stock"
        try:
            async with httpx.AsyncClient(timeout=self.timeout_s) as client:
                r = await client.get(url)
            if r.status_code == 404:
                return False, "product not found in warehouse", None
            if r.status_code != 200:
                return False, f"warehouse returned {r.status_code}", None
            data = r.json()
            if "stock" not in data:
                return False, "invalid response format (missing stock)", None
            return True, "ok", int(data["stock"])
        except Exception as e:
            return False, f"warehouse request failed: {e}", None