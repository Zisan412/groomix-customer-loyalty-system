# Groomix Backend

Phase 2 backend APIs for the Groomix customer loyalty system. This project uses
Django 5.2, Django REST Framework, JWT authentication, and SQLite for local
development. PostgreSQL and frontend integration are intentionally deferred.

## Local setup (Windows PowerShell)

From the repository root:

```powershell
Set-Location .\backend
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The API is available at `http://127.0.0.1:8000/api/` and Django Admin at
`http://127.0.0.1:8000/admin/`. Use `Ctrl+C` to stop the server. If PowerShell
blocks virtual-environment activation, use the Python executable directly:
`.venv\Scripts\python.exe manage.py runserver`.

Edit `.env` for local settings. It is ignored by Git; `.env.example` contains
placeholders only. The default database is `backend/db.sqlite3`. Never deploy
with `DEBUG=True` or the development-only fallback secret key.

Factory Admins are created through `createsuperuser` or Django Admin, not public
registration. Public registration always creates a Wholesaler.

## Authentication

Send the access token on protected API requests:

```http
Authorization: Bearer <access-token>
```

Tokens expire after 30 minutes; refresh tokens expire after one day and are
rotated/blacklisted on refresh.

| Method | Endpoint | Purpose |
| --- | --- | --- |
| POST | `/api/auth/register/` | Register a wholesaler |
| POST | `/api/auth/login/` | Login with `email` and `password`; returns access/refresh tokens and user |
| POST | `/api/auth/refresh/` | Refresh an access token using `refresh` |
| POST | `/api/auth/logout/` | Blacklist a refresh token using `refresh` |
| GET, PATCH, PUT | `/api/auth/me/` | View or update the signed-in user's profile |

The profile endpoint does not allow users to change their role or approval
state. API errors use DRF's standard JSON responses and validation details.
List endpoints are paginated (20 items by default); supported search and
ordering fields are described below where relevant.

## API endpoints

All paths below are relative to `/api`. Protected endpoints require a JWT.

### Categories and products

| Method | Endpoint | Access |
| --- | --- | --- |
| GET, POST | `/categories/` | Authenticated read; Factory Admin create |
| GET, PUT, PATCH, DELETE | `/categories/{id}/` | Authenticated read; Factory Admin edit/deactivate |
| GET, POST | `/products/` | Authenticated read; Factory Admin create |
| GET, PUT, PATCH, DELETE | `/products/{id}/` | Authenticated read; Factory Admin edit/deactivate |

Product listing accepts `?category={id}`, `?search={text}`, and ordering by
`name`, `selling_price`, or `created_at`. Products record wholesale selling
price, manufacturing cost, units per box, and stock/reserved box counts.
Wholesalers see active products and categories only.

### Orders

| Method | Endpoint | Access |
| --- | --- | --- |
| GET, POST | `/orders/` | Wholesalers create and view their orders; Admin views all |
| GET | `/orders/{id}/` | Owner or Factory Admin |
| POST | `/orders/{id}/approve/` | Factory Admin |
| POST | `/orders/{id}/reject/` | Factory Admin |
| POST | `/orders/{id}/set_status/` | Factory Admin; JSON body includes `status` |
| POST | `/orders/{id}/cancel/` | Owning Wholesaler |

Order creation takes product IDs, quantities in boxes, and a payment mode
(`ADVANCE` or `CREDIT`); prices and totals are calculated from current server
data. Optional `redeem_points` and `notes` may be included. Order lines retain
product, price, cost, box-size, and quantity snapshots.

Admin status progression is validated. Approval reserves stock. Dispatch
removes the reserved quantity from stock. Approved, undispatched cancellation
releases reserved stock; dispatched orders cannot be cancelled and should use
the returns process. Rejection closes a pending order as `CANCELLED` because
the order status set does not include a separate rejected status.

### Payments

| Method | Endpoint | Access |
| --- | --- | --- |
| GET, POST | `/payments/` | Wholesalers submit and view their payments; Admin views all |
| GET | `/payments/{id}/` | Owner or Factory Admin |
| POST | `/payments/{id}/verify/` | Factory Admin |

Wholesalers submit payment records for approved orders. A submitted amount is
pending and does not change paid balances until an Admin verifies it. The
verification request includes `verified: true|false`; an Admin may provide a
`verified_amount` no greater than the submitted amount. No payment gateway is
connected.

### Credit

| Method | Endpoint | Access |
| --- | --- | --- |
| GET, POST | `/credit/requests/` | Wholesaler creates/views own requests; Admin views all |
| POST | `/credit/requests/{id}/decide/` | Factory Admin |
| GET | `/credit/me/` | Wholesaler's approved facility |
| GET | `/credit/entries/` | Wholesaler sees own ledger; Admin sees all |

An approval decision sets the limit, payment term, and facility validity.
Facility validity is checked separately from each order's payment due date.
Credit orders reserve available credit on approval; verified payments and
approved returns update the balance and credit ledger.

### Loyalty

| Method | Endpoint | Access |
| --- | --- | --- |
| GET | `/loyalty/settings/` | Any authenticated user |
| PUT, PATCH | `/loyalty/settings/` | Factory Admin |
| GET | `/loyalty/me/` | Wholesaler's balance and paginated transactions |
| GET | `/loyalty/transactions/` | Own ledger; Admin can view all or filter by `?wholesaler={id}` |
| POST | `/loyalty/adjustments/` | Factory Admin |

Default settings are a 10% reward budget from eligible gross profit, 100 points
per rupee, 1,000 minimum redemption points, a 20% maximum checkout discount,
and 12-month expiry.

For each order line, gross profit is `(selling price - manufacturing cost) ×
boxes`, with negative line profit treated as zero for rewards. The checkout
discount is subtracted from eligible profit. The budget percentage is converted
to points using the configured points-per-rupee rate. Points are awarded once
only after delivery and full verified payment. The ledger records earned,
redeemed, expired, refunded, reversed, and admin-adjustment entries.

### Rewards Store

| Method | Endpoint | Access |
| --- | --- | --- |
| GET, POST | `/rewards/items/` | Authenticated browse; Factory Admin creates |
| GET, PUT, PATCH, DELETE | `/rewards/items/{id}/` | Factory Admin manage/deactivate |
| GET, POST | `/rewards/redemptions/` | Own requests; Admin views all; Wholesaler creates |
| POST | `/rewards/redemptions/{id}/approve/` | Factory Admin |
| POST | `/rewards/redemptions/{id}/reject/` | Factory Admin |
| POST | `/rewards/redemptions/{id}/dispatch/` | Factory Admin |
| POST | `/rewards/redemptions/{id}/deliver/` | Factory Admin |

Reward stock is separate from sales inventory. Requesting a reward reserves its
stock and points. Rejection releases the reserved reward stock and refunds the
points through the loyalty ledger.

### Returns

| Method | Endpoint | Access |
| --- | --- | --- |
| GET, POST | `/returns/` | Wholesaler creates/views own requests; Admin views all |
| GET | `/returns/{id}/` | Owner or Factory Admin |
| POST | `/returns/{id}/review/` | Factory Admin |
| POST | `/returns/{id}/inspect/` | Factory Admin |

Returns are limited to delivered orders and must be requested within seven
days. Requests identify order lines and quantities. Admin review and inspection
record the decision and inspection result. Accepted returns can restock goods,
adjust credit, create a pending manual-refund record, and reverse proportionate
earned points.

## Main business workflows

1. A wholesaler registers and logs in. A Factory Admin account is provisioned
   through Django's superuser/admin tools.
2. The wholesaler submits an order in boxes. The API looks up active products
   and calculates all prices, discounts, and totals itself.
3. Admin approval reserves inventory. Credit orders additionally require an
   active, valid facility with enough available credit.
4. Payment submissions remain pending until an Admin verifies them. Advance
   payment orders must be fully paid before processing.
5. Admin progresses an order through processing, dispatch, and delivery. A
   delivered, fully paid order can earn points once.
6. The wholesaler may spend available points on a future checkout discount or
   submit a Rewards Store redemption. Returns are reviewed and inspected
   separately, with applicable ledger reversals/refunds.

## Development checks

Run from `backend/` with the virtual environment active:

```powershell
python manage.py check
python manage.py makemigrations --check
python manage.py test
```

The tests use Django's temporary test database and do not require a separate
SQLite database setup.

## Scope and limitations

- SQLite is for development/testing only. PostgreSQL configuration and
  deployment hardening are deferred.
- Payment recording and verification are manual workflows, not payment
  processing. Refunds are recorded as pending manual refunds; no provider
  actually transfers money.
- There is no frontend integration, email delivery, background scheduler, or
  production deployment configuration in this phase.
- Loyalty expiry is applied when a wholesaler's balance is queried or points
  are spent, rather than by a scheduled background job.
- Credit eligibility criteria remain a manual Admin decision; configurable
  automated eligibility thresholds are not part of this phase.
