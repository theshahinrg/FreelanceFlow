# Freelancer CRM (Django)

Created by **TheShahinRG** — https://shahindev.com

Simple CRM for freelancers to keep track of clients, projects, invoices, and contact history.

## Tech stack
- Python 3.13
- Django 4.2
- SQLite (default; swap out in `config/settings.py` if needed)

## Getting started
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Generate migration files (whenever you change your models):
   ```bash
   python manage.py makemigrations
   ```
3. Run database migrations:
   ```bash
   python manage.py migrate
   ```
4. Create a superuser (for admin access):
   ```bash
   python manage.py createsuperuser
   ```
5. Start the dev server:
   ```bash
   python manage.py runserver
   ```
6. Log in at `/accounts/login/` and start adding clients, projects, and invoices. The Django admin is available at `/admin/`.

## Running tests
```bash
python manage.py test
```

## Features
- Django auth-protected CRUD for Clients, Projects, Invoices, and Contact Logs
- Client list with search and filters by name/company, email, and project status
- Client detail showing related projects, invoices, and contact history
- Project/invoice lists with simple status filters
- Admin customization with search, filters, and useful list displays

## Screenshots
- `screenshots/dashboard.png`
- `screenshots/client-detail.png`
- `screenshots/invoices.png`
