# api course project: internetveikals un noliktavas sistēma

šajā projektā ir izstrādātas divas atsevišķas sistēmas:

- noliktavas sistēma
- internetveikals

galvenais mērķis ir nodrošināt datu apmaiņu starp sistēmām, izmantojot API, nevis tiešu pieslēgšanos datubāzei.

## projekta ideja

noliktavas sistēma glabā produktu datus un nodrošina API servisus, caur kuriem internetveikals var:

- iegūt visus produktus
- iegūt konkrēta produkta aktuālo atlikumu

internetveikals glabā savu produktu kopiju savā datubāzē un atjaunina datus, izsaucot noliktavas sistēmas API.

## izmantotās tehnoloģijas

- Python
- FastAPI
- Jinja2
- SQLite
- Uvicorn

## projekta struktūra


api-course-project/
  README.md

  warehouse/
    requirements.txt
    app/
      main.py
      db.py
      templates/
        base.html
        products.html
        product_form.html

  shop/
    requirements.txt
    app/
      main.py
      db.py
      warehouse_client.py
      templates/
        base.html
        products.html
        admin.html

## noliktavas sistēmas API
- GET /api/products — atgriež visus produktus JSON formātā
- GET /api/products/{id}/stock — atgriež konkrēta produkta atlikumu

## datu apmaiņa starp sistēmām
internetveikals neizmanto tiešu piekļuvi noliktavas datubāzei.

datu apmaiņa notiek tikai caur HTTP API:
- GET /api/products
- GET /api/products/{id}/stock

API izsaukumi realizēti failā:
- shop/app/warehouse_client.py

## lokāla palaišana

### noliktavas sistēma
cd C:\api-course-project\warehouse
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001

### internetveikals
cd C:\api-course-project\shop
py -m venv .venv
.venv\Scripts\activate.bat
pip install -r requirements.txt
set WAREHOUSE_BASE_URL=http://localhost:8001
uvicorn app.main:app --reload --port 8002

## testēšanas scenārijs

### scenārijs 1: produktu importēšana
1. atvērt internetveikala produktu sarakstu
2. atvērt admin paneli
3. nospiest "delete all products"
4. nospiest "import all products from warehouse"
5. pārliecināties, ka produkti parādās

### scenārijs 2: atlikuma atjaunošana
1. noliktavas sistēmā mainīt produkta stock
2. internetveikalā nospiest "update stock"
3. pārliecināties, ka stock ir atjaunots

## online saites

### warehouse
- UI: https://warehouse-api-dz2p.onrender.com/products
- API (all products): https://warehouse-api-dz2p.onrender.com/api/products
- API (stock example): https://warehouse-api-dz2p.onrender.com/api/products/1/stock

### shop
- UI: https://shop-api-v34l.onrender.com/products
- admin panel: https://shop-api-v34l.onrender.com/admin

## secinājumi
projektā tika izstrādātas divas neatkarīgas sistēmas, kuras savstarpēji komunicē, izmantojot API. internetveikals neizmanto tiešu piekļuvi noliktavas datubāzei, bet iegūst un atjaunina datus tikai caur noliktavas sistēmas servisiem. tas demonstrē praktisku API izmantošanu datu apmaiņai starp sistēmām.
