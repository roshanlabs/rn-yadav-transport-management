# Database Design

The initial MVP currently implements `loads`, `transporters`, and `bids`. The following is the target relational design for later releases.

## Core tables

### loads
- id (PK), reference (unique), customer_id (FK, nullable during MVP transition)
- caller_name, caller_phone, origin, destination, material
- vehicle_type, weight_tonnes, customer_rate, payment_terms
- expected_loading_at, status, notes, created_at, updated_at

### customers
- id (PK), name, phone, email, billing_address, tax_identifier (optional), notes

### transporters
- id (PK), name, phone, base_location, notes, active, created_at

### transporter_vehicles
- id (PK), transporter_id (FK), registration_number (unique)
- vehicle_type, capacity_tonnes, permit_expiry, insurance_expiry, fitness_expiry, active

### drivers
- id (PK), transporter_id (FK, nullable), name, phone, licence_number
- licence_valid_until, notes

### bids
- id (PK), load_id (FK), transporter_id (FK, nullable for one-off contacts)
- quoted_rate, vehicle_id (FK, nullable), availability, notes, created_at

### trips
- id (PK), load_id (FK, unique for first MVP trip; change to one-to-many if split trips are needed)
- transporter_id (FK), vehicle_id (FK), driver_id (FK)
- agreed_rate, advance_amount, planned_pickup_at, loaded_at, dispatched_at, delivered_at
- proof_of_delivery_path, status, exception_notes

### financial_transactions
- id (PK), load_id (FK), trip_id (FK, nullable)
- party_type (CUSTOMER / TRANSPORTER), direction (RECEIVABLE / PAYABLE)
- amount, transaction_date, due_date, method, reference, status, notes

### users and audit_logs
- users: id, name, email, password_hash, role, active, created_at
- audit_logs: id, user_id, entity_type, entity_id, action, before_json, after_json, created_at

## Relationships

- One customer can have many loads.
- One load can have many bids.
- A transporter can own many vehicles and be associated with many drivers.
- One assigned load has one or more trips depending on operational needs.
- Each trip can have multiple financial transactions.
- User actions affecting sensitive business data should be logged.

## Privacy and integrity

Use foreign keys, unique constraints for references and vehicle registrations, decimal/numeric types for money in production, and explicit timezone handling. Do not expose customer phone numbers, rates, or payment details on a public load board.
