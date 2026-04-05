"""
warehouse db layer (sqlite)

this module handles:
- database connection
- schema creation
- CRUD operations for products

additional note:
- warehouse is the "source of truth" for product data and stock
- shop imports products and refreshes stock through warehouse API
"""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any, Dict, List, Optional

DB_PATH = Path(__file__).resolve().parent.parent / "warehouse.db"


def get_conn() -> sqlite3.Connection:
    """
    returns a sqlite connection with row factory enabled for dict-like access.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """
    creates tables if they do not exist.
    """
    conn = get_conn()
    try:
        conn.execute(
            """
            create table if not exists products (
                id integer primary key autoincrement,
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


def seed_if_empty() -> None:
    """
    inserts sample products if database is empty.
    useful for demo without manual data entry.
    """
    conn = get_conn()
    try:
        row = conn.execute("select count(*) as cnt from products;").fetchone()
        if row["cnt"] == 0:
            conn.executemany(
                """
                insert into products (name, description, price, stock)
                values (?, ?, ?, ?);
                """,
                [
                    ("coffee mug", "300 ml ceramic mug", 7.99, 25),
                    ("t-shirt", "size m, black", 19.90, 8),
                    ("usb-c cable", "1 m braided cable", 6.50, 40),
                    ("notebook", "a5 dotted, 120 pages", 4.20, 12),
                ],
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


def create_product(name: str, description: str, price: float, stock: int) -> int:
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            insert into products (name, description, price, stock)
            values (?, ?, ?, ?);
            """,
            (name, description, price, stock),
        )
        conn.commit()
        return int(cur.lastrowid)
    finally:
        conn.close()


def update_product(
    product_id: int, name: str, description: str, price: float, stock: int
) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute(
            """
            update products
            set name = ?, description = ?, price = ?, stock = ?
            where id = ?;
            """,
            (name, description, price, stock, product_id),
        )
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()


def delete_product(product_id: int) -> bool:
    conn = get_conn()
    try:
        cur = conn.execute("delete from products where id = ?;", (product_id,))
        conn.commit()
        return cur.rowcount == 1
    finally:
        conn.close()
