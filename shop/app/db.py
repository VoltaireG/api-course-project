"""
shop db layer (sqlite)

shop keeps its own database. products are imported from warehouse API and stored locally.
stock can be refreshed per-product using warehouse stock endpoint.

this matches lecturer requirement:
- shop can delete all products
- shop can import all products from warehouse api
- shop can refresh a single product's stock using warehouse api
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "shop.db"


def get_conn() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = get_conn()
    try:
        conn.execute(
            """
            create table if not exists products (
                id integer primary key,   -- same id as warehouse to simplify mapping
                name text not null,
                description text not null,
                price real not null,
                stock integer not null
            );
            """
        )
        conn.commit()
    finally:
        conn.close()


def list_products() -> List[Dict[str, Any]]:
    conn = get_conn()
    try:
        rows = conn.execute(
            "select id, name, description, price, stock from products order by id;"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def get_product(product_id: int) -> Optional[Dict[str, Any]]:
    conn = get_conn()
    try:
        row = conn.execute(
            "select id, name, description, price, stock from products where id = ?;",
            (product_id,),
        ).fetchone()
        return dict(row) if row else None
    finally:
        conn.close()


def delete_all_products() -> None:
    conn = get_conn()
    try:
        conn.execute("delete from products;")
        conn.commit()
    finally:
        conn.close()


def upsert_product(p: Dict[str, Any]) -> None:
    """
    inserts product if not exists, otherwise updates it.
    """
    conn = get_conn()
    try:
        conn.execute(
            """
            insert into products (id, name, description, price, stock)
            values (?, ?, ?, ?, ?)
            on conflict(id) do update set
                name = excluded.name,
                description = excluded.description,
                price = excluded.price,
                stock = excluded.stock;
            """,
            (int(p["id"]), p["name"], p["description"], float(p["price"]), int(p["stock"])),
        )
        conn.commit()
    finally:
        conn.close()


def update_stock(product_id: int, stock: int) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute(
            "update products set stock = ? where id = ?;",
            (int(stock), int(product_id)),
        )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()