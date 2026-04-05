"""
warehouse system (noliktava)

features:
- UI to manage products (create/edit/delete)
- API endpoints required by lecturer:
  1) GET /api/products -> all products as json
  2) GET /api/products/{id}/stock -> current stock for a single product as json
"""

from __future__ import annotations

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

from .db import (
    init_db,
    seed_if_empty,
    list_products,
    get_product,
    create_product,
    update_product,
    delete_product,
)

app = FastAPI(title="warehouse system")
templates = Jinja2Templates(directory=str(__import__("pathlib").Path(__file__).parent / "templates"))


@app.on_event("startup")
def on_startup() -> None:
    init_db()
    seed_if_empty()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# ---------------------------
# api endpoints (json)
# ---------------------------

@app.get("/api/products")
def api_all_products() -> JSONResponse:
    """
    returns all products (including stock) in json.
    lecturer requirement: "par visiem produktiem"
    """
    return JSONResponse(content=list_products())


@app.get("/api/products/{product_id}/stock")
def api_product_stock(product_id: int) -> JSONResponse:
    """
    returns only a single product's current stock in json.
    lecturer requirement: "viena produkta atlikumu"
    """
    p = get_product(product_id)
    if not p:
        raise HTTPException(status_code=404, detail="product not found")
    return JSONResponse(content={"id": p["id"], "stock": p["stock"]})


# ---------------------------
# ui routes (html)
# ---------------------------

@app.get("/", response_class=HTMLResponse)
@app.get("/products", response_class=HTMLResponse)
def ui_products(request: Request) -> HTMLResponse:
    products = list_products()
    return templates.TemplateResponse(
        "products.html", {"request": request, "products": products}
    )


@app.get("/products/create", response_class=HTMLResponse)
def ui_create_form(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "mode": "create", "product": None, "error": None},
    )


@app.post("/products/create")
def ui_create_submit(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
):
    # basic validation to avoid empty values
    if not name.strip():
        return templates.TemplateResponse(
            "product_form.html",
            {"request": request, "mode": "create", "product": None, "error": "Product name cannot be empty"},
        )
    create_product(name.strip(), description.strip(), float(price), int(stock))
    return RedirectResponse(url="/products", status_code=303)


@app.get("/products/{product_id}/edit", response_class=HTMLResponse)
def ui_edit_form(request: Request, product_id: int) -> HTMLResponse:
    product = get_product(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="product not found")
    return templates.TemplateResponse(
        "product_form.html",
        {"request": request, "mode": "edit", "product": product, "error": None},
    )


@app.post("/products/{product_id}/edit")
def ui_edit_submit(
    product_id: int,
    name: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    stock: int = Form(...),
):
    ok = update_product(product_id, name.strip(), description.strip(), float(price), int(stock))
    if not ok:
        raise HTTPException(status_code=404, detail="product not found")
    return RedirectResponse(url="/products", status_code=303)


@app.post("/products/{product_id}/delete")
def ui_delete(product_id: int):
    delete_product(product_id)
    return RedirectResponse(url="/products", status_code=303)