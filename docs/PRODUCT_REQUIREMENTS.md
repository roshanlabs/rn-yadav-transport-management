# Product Requirements — RN YADAV TRAILER SERVICE

## 1. Product objective

Create a simple operations system for a transport business where enquiries currently arrive by phone and are coordinated manually. The system should make load details, transporter options, vehicle assignments, trip progress, and payment commitments visible in one place.

## 2. Users and access

- **Owner / administrator:** full access to enquiries, rates, transporter contacts, assignments, financial records, and reports.
- **Operations staff:** create and update enquiries, contact transporters, record offers, and update trip progress.
- **Read-only / network user (future):** view approved public load or vehicle information without seeing private customer or payment data.

Authentication and role-based permissions are required before a multi-user or public deployment.

## 3. Core workflows

### Load enquiry
Capture a unique reference, caller/customer name and phone, pickup and delivery locations, material, required vehicle type, approximate weight, expected loading date, customer rate, payment terms, and notes.

### Transporter sourcing
Search the contact directory by name, phone, base location, and vehicle type. Record each offer against the relevant load, including quoted rate, vehicle number, availability, and notes. Compare offers before assigning a transporter.

### Assignment and trip
Record selected transporter, driver and vehicle details, agreed rate, advance, planned pickup, actual loading, dispatch, delivery confirmation, proof-of-delivery reference, and exceptions.

### Payment follow-up
Track customer amount due, transporter payable, advance paid/received, balance, due date, payment status, and transaction references. Financial entries must be auditable.

## 4. Load lifecycle

Suggested statuses: OPEN → QUOTING → ASSIGNED → IN_TRANSIT → DELIVERED. CANCELLED may be used from applicable stages. Store status history in production rather than only the current status.

## 5. MVP scope

Included in the starter:
- Manual load enquiry entry and list/search/filter.
- Transporter contact directory.
- Multiple transporter offers per load.
- Basic status updates and load detail page.
- SQLite persistence for local development.

Not yet included:
- User login and multi-user access.
- Trip/vehicle/driver master records.
- Proof-of-delivery and document uploads.
- Customer and transporter ledgers.
- Invoicing, GST, accounting integrations, and payment reconciliation.
- Public load board, bidding by external users, notifications, and mobile app.
- Production hosting, backups, monitoring, and audit trails.

## 6. Non-functional requirements

- Protect phone numbers, negotiated rates, and financial information.
- Validate all input on the server.
- Use role-based access and HTTPS.
- Keep audit history for changes to rates, assignments, and payments.
- Back up the database and uploaded documents.
- Provide CSV export and operational reports in a later release.

## 7. Success measures

- Every new enquiry is registered with a unique reference.
- Staff can find a load by reference, caller, or route.
- Offers can be compared before assignment.
- Operations can identify open, assigned, in-transit, and delivered loads.
- Outstanding customer receivables and transporter payables can be reconciled in the finance phase.
