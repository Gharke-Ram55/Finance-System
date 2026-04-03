"""
Management command: seed_data

Creates demo users, categories, and realistic transaction records
so the project works out of the box with meaningful data.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   (wipes existing data first)
"""

import random
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from transactions.models import Category, Transaction

User = get_user_model()


CATEGORIES = [
    ('Salary', 'income'),
    ('Freelance', 'income'),
    ('Investments', 'income'),
    ('Consulting', 'income'),
    ('Rent', 'expense'),
    ('Groceries', 'expense'),
    ('Utilities', 'expense'),
    ('Transport', 'expense'),
    ('Healthcare', 'expense'),
    ('Dining Out', 'expense'),
    ('Entertainment', 'expense'),
    ('Software & Tools', 'expense'),
    ('Marketing', 'expense'),
    ('Office Supplies', 'expense'),
]

INCOME_NOTES = [
    'Monthly salary credit',
    'Client project payment',
    'Quarterly dividend',
    'Freelance website project',
    'Consulting retainer fee',
    'Software license revenue',
    'Annual bonus received',
    'Invoice #1042 cleared',
]

EXPENSE_NOTES = [
    'Monthly office rent',
    'Weekly grocery run',
    'Electricity bill',
    'Metro pass renewal',
    'Doctor consultation',
    'Team lunch',
    'Netflix subscription',
    'AWS hosting charges',
    'Google Workspace plan',
    'Stationery and printing',
    'Fuel reimbursement',
    'Pharmacies',
    'Uber rides this week',
]


class Command(BaseCommand):
    help = 'Seeds the database with demo users, categories, and transactions.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing transactions and categories before seeding.',
        )

    def handle(self, *args, **options):
        if options['clear']:
            Transaction.objects.all().delete()
            Category.objects.all().delete()
            self.stdout.write('Cleared existing data.')

        self._create_users()
        categories = self._create_categories()
        self._create_transactions(categories)

        self.stdout.write(self.style.SUCCESS(
            '\nSeed complete. Login with:\n'
            '  admin   / admin123\n'
            '  analyst / analyst123\n'
            '  viewer  / viewer123\n'
        ))

    def _create_users(self):
        accounts = [
            ('admin', 'admin123', 'admin', 'Arjun', 'Mehta', 'arjun@zorvyn.io'),
            ('analyst', 'analyst123', 'analyst', 'Priya', 'Sharma', 'priya@zorvyn.io'),
            ('viewer', 'viewer123', 'viewer', 'Rahul', 'Verma', 'rahul@zorvyn.io'),
        ]
        for username, password, role, first, last, email in accounts:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username,
                    password=password,
                    role=role,
                    first_name=first,
                    last_name=last,
                    email=email,
                )
                self.stdout.write(f'  Created user: {username} ({role})')
            else:
                self.stdout.write(f'  User already exists: {username}')

    def _create_categories(self):
        created = []
        for name, type_hint in CATEGORIES:
            cat, _ = Category.objects.get_or_create(
                name=name,
                defaults={'type_hint': type_hint}
            )
            created.append(cat)
        self.stdout.write(f'  Categories ready: {len(created)}')
        return created

    def _create_transactions(self, categories):
        admin_user = User.objects.get(username='admin')

        income_cats = [c for c in categories if c.type_hint == 'income']
        expense_cats = [c for c in categories if c.type_hint == 'expense']

        today = date.today()
        transactions = []

        # Generate 8 months of data
        for month_offset in range(8):
            base_date = (today.replace(day=1) - timedelta(days=30 * month_offset))

            # 1–2 income entries per month
            for _ in range(random.randint(1, 2)):
                tx_date = base_date + timedelta(days=random.randint(1, 25))
                if tx_date > today:
                    tx_date = today
                transactions.append(Transaction(
                    amount=Decimal(str(random.randint(40000, 120000))),
                    transaction_type='income',
                    category=random.choice(income_cats),
                    date=tx_date,
                    notes=random.choice(INCOME_NOTES),
                    created_by=admin_user,
                ))

            # 6–12 expense entries per month
            for _ in range(random.randint(6, 12)):
                tx_date = base_date + timedelta(days=random.randint(1, 27))
                if tx_date > today:
                    tx_date = today
                transactions.append(Transaction(
                    amount=Decimal(str(round(random.uniform(500, 18000), 2))),
                    transaction_type='expense',
                    category=random.choice(expense_cats),
                    date=tx_date,
                    notes=random.choice(EXPENSE_NOTES),
                    created_by=admin_user,
                ))

        Transaction.objects.bulk_create(transactions)
        self.stdout.write(f'  Transactions created: {len(transactions)}')
