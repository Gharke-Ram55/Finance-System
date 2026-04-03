from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth
from decimal import Decimal
from datetime import date, timedelta

from .models import Transaction, Category


def get_filtered_transactions(filters: dict):
    """
    Apply filters to the Transaction queryset and return results.
    Centralizing filter logic here keeps views thin.
    """
    qs = Transaction.objects.select_related('category', 'created_by')

    tx_type = filters.get('transaction_type')
    if tx_type in ['income', 'expense']:
        qs = qs.filter(transaction_type=tx_type)

    category = filters.get('category')
    if category:
        qs = qs.filter(category=category)

    date_from = filters.get('date_from')
    if date_from:
        qs = qs.filter(date__gte=date_from)

    date_to = filters.get('date_to')
    if date_to:
        qs = qs.filter(date__lte=date_to)

    search = filters.get('search', '').strip()
    if search:
        qs = qs.filter(notes__icontains=search)

    sort = filters.get('sort', '-date')
    allowed_sorts = ['-date', 'date', '-amount', 'amount']
    if sort not in allowed_sorts:
        sort = '-date'
    qs = qs.order_by(sort)

    return qs


def compute_summary(queryset=None):
    """
    Returns total income, total expenses, and net balance
    from a given queryset (or all transactions if none given).
    """
    if queryset is None:
        queryset = Transaction.objects.all()

    totals = queryset.aggregate(
        total_income=Sum('amount', filter=Q(transaction_type='income')),
        total_expense=Sum('amount', filter=Q(transaction_type='expense')),
    )

    income = totals['total_income'] or Decimal('0.00')
    expense = totals['total_expense'] or Decimal('0.00')
    balance = income - expense

    return {
        'total_income': income,
        'total_expense': expense,
        'balance': balance,
    }


def get_category_breakdown(transaction_type=None):
    """
    Returns per-category totals, optionally filtered by income or expense.
    """
    qs = Transaction.objects.all()
    if transaction_type:
        qs = qs.filter(transaction_type=transaction_type)

    breakdown = (
        qs.values('category__name')
        .annotate(total=Sum('amount'), count=Count('id'))
        .order_by('-total')
    )
    return list(breakdown)


def get_monthly_totals(months=6):
    """
    Returns income and expense totals grouped by month for the last N months.
    Uses proper month arithmetic instead of approximating with timedelta days.
    """
    today = date.today()

    # Step back exactly N months without the 30-days-per-month approximation bug
    cutoff_month = today.month - months
    cutoff_year = today.year
    while cutoff_month <= 0:
        cutoff_month += 12
        cutoff_year -= 1
    cutoff = date(cutoff_year, cutoff_month, 1)

    rows = (
        Transaction.objects.filter(date__gte=cutoff)
        .annotate(month=TruncMonth('date'))
        .values('month', 'transaction_type')
        .annotate(total=Sum('amount'))
        .order_by('month')
    )

    monthly = {}
    for row in rows:
        # Guard against None — can happen on empty or malformed data
        if not row['month']:
            continue
        key = row['month'].strftime('%b %Y')
        if key not in monthly:
            monthly[key] = {'income': 0, 'expense': 0}
        tx_type = row['transaction_type']
        if tx_type in ('income', 'expense'):
            monthly[key][tx_type] = float(row['total'] or 0)

    return monthly


def get_recent_transactions(limit=10):
    return Transaction.objects.select_related('category').order_by('-date', '-created_at')[:limit]


def get_dashboard_stats():
    """
    Aggregates everything needed by the main dashboard in one place.
    """
    all_tx = Transaction.objects.all()
    summary = compute_summary(all_tx)

    today = date.today()
    this_month_qs = all_tx.filter(date__year=today.year, date__month=today.month)
    this_month = compute_summary(this_month_qs)

    recent = get_recent_transactions(8)
    monthly = get_monthly_totals(6)
    cat_expense = get_category_breakdown('expense')[:5]

    return {
        'summary': summary,
        'this_month': this_month,
        'recent_transactions': recent,
        'monthly_data': monthly,
        'top_expense_categories': cat_expense,
        'total_transactions': all_tx.count(),
    }
