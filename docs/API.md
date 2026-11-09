# API Outline

The FastAPI application currently provides HTML workflows. The endpoints below describe the intended API evolution.

## Implemented routes

- `GET /` — dashboard, with optional `q` and `status` filters.
- `GET /loads/new` — load enquiry form.
- `POST /loads` — create a load.
- `GET /loads/{id}` — load detail and offer list.
- `POST /loads/{id}/status` — update load status.
- `POST /loads/{id}/bids` — record a transporter offer.
- `GET /transporters` — transporter directory.
- `POST /transporters` — create transporter.
- `GET /health` — health check.

## Planned JSON API

- `GET/POST /api/v1/loads`
- `GET/PATCH /api/v1/loads/{id}`
- `GET/POST /api/v1/loads/{id}/bids`
- `GET/POST /api/v1/transporters`
- `GET/POST /api/v1/trips`
- `GET/POST /api/v1/transactions`
- `GET /api/v1/reports/receivables`
- `GET /api/v1/reports/payables`

All planned API routes must require authentication, validate permissions, paginate collection responses, and avoid exposing private business data to unauthorized users.
