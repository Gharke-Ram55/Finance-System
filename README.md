# FinTrack — Python Finance Tracking System

A backend-first finance tracking system built with **Django 4.2**, **SQLite**, and a clean HTML/CSS/JS frontend. Designed for internal use at Zorvyn to manage, categorize, and analyze financial transactions across teams with role-based access control.

---

## What This Project Does

FinTrack lets teams log income and expense transactions, filter and search through records, and generate visual summaries of their financial activity — all from a single web interface. Role-based permissions ensure that not everyone can edit or delete records, while analysts get access to deeper insights and export tools.

The goal was to keep the architecture clean and honest: thin views, business logic in a service layer, models that reflect the actual domain, and a UI that feels like a real internal tool rather than a demo.

---

## Tech Stack

| Layer | Choice | Reason |
|---|---|---|
| Framework | Django 4.2 | Mature, batteries-included, great ORM |
| Database | SQLite | Zero config, perfect for this scale |
| Frontend | HTML + CSS + Vanilla JS | No build step, fast, readable |
| Charts | Chart.js (CDN) | Lightweight, no npm required |
| Fonts | DM Sans + DM Mono | Clean, professional feel |

---

## Project Structure

```
fintrack/
├── fintrack/               # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── transactions/           # Core app — records, categories, dashboard
│   ├── models.py           # Transaction and Category models
│   ├── views.py            # Dashboard, CRUD views, export
│   ├── forms.py            # Form classes with validation
│   ├── services.py         # Business logic (filtering, summaries, analytics)
│   ├── urls.py
│   └── management/
│       └── commands/
│           └── seed_data.py  # Demo data generator
│
├── users/                  # User management and auth
│   ├── models.py           # Custom User with role field
│   ├── views.py            # Login, logout, user CRUD
│   ├── forms.py            # Login, create, edit forms
│   ├── decorators.py       # @admin_required, @analyst_required
│   └── urls.py
│
├── analytics/              # Analytics views (Analyst+ only)
│   ├── views.py
│   └── urls.py
│
├── templates/              # All HTML templates
│   ├── base/base.html      # Main layout (sidebar, topbar)
│   ├── transactions/       # Dashboard, list, form, detail templates
│   ├── users/              # Login, user management templates
│   └── analytics/          # Analytics overview template
│
├── static/
│   ├── css/main.css        # All styles (dark fintech theme)
│   └── js/main.js          # Minimal utility JS
│
├── manage.py
└── requirements.txt
```

---

## Setup Instructions

### 1. Clone and create a virtual environment

```bash
git clone <repo-url>
cd fintrack
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Apply migrations

```bash
python manage.py migrate
```

### 4. Load demo data (recommended)

This creates 3 demo users and ~70 realistic transactions spread across 8 months.

```bash
python manage.py seed_data
```

To wipe and re-seed:

```bash
python manage.py seed_data --clear
```

### 5. Start the server

```bash
python manage.py runserver
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## Demo Accounts

| Username | Password | Role | What they can do |
|---|---|---|---|
| `admin` | `admin123` | Admin | Full access — create, edit, delete, manage users |
| `analyst` | `analyst123` | Analyst | View all records, analytics, filter, export CSV |
| `viewer` | `viewer123` | Viewer | View dashboard and transaction list only |

---

## Role-Based Access

Access control is enforced at the view level using custom decorators defined in `users/decorators.py`.

| Feature | Viewer | Analyst | Admin |
|---|---|---|---|
| View dashboard | ✓ | ✓ | ✓ |
| View transactions | ✓ | ✓ | ✓ |
| Filter and search | ✓ | ✓ | ✓ |
| Analytics page | ✗ | ✓ | ✓ |
| Export CSV | ✗ | ✓ | ✓ |
| Add transaction | ✗ | ✗ | ✓ |
| Edit / Delete | ✗ | ✗ | ✓ |
| Manage users | ✗ | ✗ | ✓ |
| Manage categories | ✗ | ✗ | ✓ |

---

## Key Features

**Financial Records**
- Create, view, edit, and delete income/expense transactions
- Each transaction stores: amount, type, category, date, notes, and the user who created it
- Paginated list view (15 per page) with real-time filtered summary cards

**Filtering and Search**
- Filter by transaction type, category, date range, and notes keyword
- Sort by date or amount in either direction
- Filtered summary (income / expense / balance) updates based on active filters

**Analytics**
- 12-month income vs expense line chart
- Category breakdowns shown as doughnut charts and horizontal bar charts
- Per-category totals with percentage bars
- Accessible to Analyst and Admin roles only

**CSV Export**
- Exports the currently filtered result set
- Includes all key fields: ID, date, type, category, amount, notes, created by
- Available to Analyst and Admin roles

**User Management**
- Admin can create, edit, and remove users
- Roles enforced via decorators — not just UI hints
- Profile page shows each user's access level clearly

---

## Design Decisions and Assumptions

**Service layer in `transactions/services.py`**
All aggregation logic (summaries, category breakdowns, monthly totals, filtering) lives in a dedicated service module. Views just call these functions and pass results to templates. This keeps views thin and the business logic easy to test independently.

**Currency**
The system uses Indian Rupees (₹) as the currency, matching Zorvyn's base location in Bengaluru. This is a display-only assumption — the underlying decimal storage is currency-agnostic.

**Date restriction**
Transactions cannot be dated in the future. This is validated at the form level and makes sense for an auditing context.

**No future dates, no negative amounts**
The form validator rejects future dates and enforces amount > 0. These are simple but important data integrity rules.

**SQLite**
Chosen for simplicity. Swapping to PostgreSQL only requires changing the `DATABASES` setting — the ORM code doesn't change.

**No external auth libraries**
Django's built-in `AbstractUser` and `AuthenticationForm` are used directly. The role field is a plain CharField with choices, which keeps the access model easy to reason about.

**Chart.js via CDN**
Loaded from jsDelivr CDN to avoid any npm/build step. The charts are rendered client-side using data injected as JSON from the view.

---

## Running the Django Admin

The built-in Django admin is also available for inspecting data directly.

```bash
python manage.py createsuperuser
# then visit http://127.0.0.1:8000/admin/
```

---

## Optional: Reset and re-seed

```bash
rm db.sqlite3
python manage.py migrate
python manage.py seed_data
```
