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

```text
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