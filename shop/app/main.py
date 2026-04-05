"""
shop system (internetveikals)

features:
- product list page (public)
- admin panel:
  - delete all local products
  - import all products from warehouse api and store in shop db
  - refresh stock per product by calling warehouse stock endpoint
"""

from __future__ import annotations

import os
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .db import init_db, list_products, delete_all_products, upsert_product, update_stock, get_product
from .warehouse_client import WarehouseClient

app = FastAPI(title="shop system")
templates = Jinja2Templates(directory=str(__import__("pathlib").Path(__file__).parent / "templates"))


def get_warehouse_base_url() -> str:
    """
    configure warehouse url using environment variable.

    for local run:
    - WAREHOUSE_BASE_URL=http://localhost:8001

    for docker-compose:
    - WAREHOUSE_BASE_URL=http://warehouse:8000  (service name)
    """
    url = os.getenv("WAREHOUSE_BASE_URL", "http://localhost:8001")
    return url


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "warehouse_base_url": get_warehouse_base_url()}


@app.get("/", response_class=HTMLResponse)
@app.get("/products", response_class=HTMLResponse)
def ui_products(request: Request) -> HTMLResponse:
    products = list_products()
    return templates.TemplateResponse(
        "products.html",
        {"request": request, "products": products, "warehouse_base_url": get_warehouse_base_url(), "message": None},
    )


@app.get("/admin", response_class=HTMLResponse)
def ui_admin(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "admin.html",
        {"request": request, "warehouse_base_url": get_warehouse_base_url(), "message": None},
    )


@app.post("/admin/delete-all")
def admin_delete_all() -> RedirectResponse:
    delete_all_products()
    return RedirectResponse(url="/admin?msg=deleted", status_code=303)


@app.post("/admin/import")
async def admin_import() -> RedirectResponse:
    client = WarehouseClient(get_warehouse_base_url())
    ok, msg, products = await client.get_all_products()
    if not ok:
        # show message in admin page via query parameter
        return RedirectResponse(url=f"/admin?msg=import_failed&detail={msg}", status_code=303)

    # store all products in shop db (upsert)
    for p in products:
        # minimal schema validation to avoid runtime errors
        required = {"id", "name", "description", "price", "stock"}
        if not required.issubset(set(p.keys())):
            return RedirectResponse(url="/admin?msg=import_failed&detail=invalid_product_format", status_code=303)
        upsert_product(p)

    return RedirectResponse(url=f"/admin?msg=import_ok&count={len(products)}", status_code=303)


@app.post("/admin/products/{product_id}/refresh-stock")
async def admin_refresh_stock(product_id: int) -> RedirectResponse:
    # shop can only refresh stock for a product it has locally
    local = get_product(product_id)
    if not local:
        raise HTTPException(status_code=404, detail="product not found in shop db")

    client = WarehouseClient(get_warehouse_base_url())
    ok, msg, stock = await client.get_stock(product_id)
    if not ok or stock is None:
        return RedirectResponse(url=f"/products?msg=stock_failed&id={product_id}&detail={msg}", status_code=303)

    success = update_stock(product_id, stock)
    if not success:
        return RedirectResponse(url=f"/products?msg=stock_failed&id={product_id}&detail=failed_to_update_db", status_code=303)
    return RedirectResponse(url=f"/products?msg=stock_ok&id={product_id}&stock={stock}", status_code=303)