# RN YADAV TRAILER SERVICE — Transport Management

A small, mobile-friendly starter app for managing transport load enquiries, transporter contacts, and quotations. Built with Python, FastAPI, Jinja2, and SQLite.

## Current features

- Dashboard with load counts, search, and status filtering.
- Manual load enquiry creation with a generated reference.
- Load detail page with customer, route, vehicle, weight, payment terms, and notes.
- Multiple transporter offers against each load.
- Basic load status updates.
- Transporter contact directory.
- SQLite database created automatically on first startup.

## Run locally

Requires Python 3.10 or newer.

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# macOS / Linux:
# source .venv/bin/activate

pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000.

## Data storage

By default, SQLite data is stored in `data/transport.db`. Set `DATABASE_PATH` or `DATA_DIR` to use a different location. The database and runtime data are excluded from Git.

## Important before real business use

This is an MVP starter, not a production-ready system. It currently has no login or role permissions. Do not expose it publicly or enter real customer, driver, or payment information until authentication, access controls, HTTPS, backups, audit logs, and a privacy review are implemented.

## Project documents

- [Product requirements](docs/PRODUCT_REQUIREMENTS.md)
- [Database design](docs/DATABASE.md)
- [API outline](docs/API.md)
- [Roadmap](docs/ROADMAP.md)

## License

MIT. See [LICENSE](LICENSE).
