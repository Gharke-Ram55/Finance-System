from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
import json
from decimal import Decimal

from transactions.services import (
    get_category_breakdown,
    get_monthly_totals,
    compute_summary,
)
from transactions.models import Transaction
from users.decorators import analyst_required


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@login_required
@analyst_required
def analytics_overview(request):
    """
    Main analytics page. Shows category breakdowns, monthly trends,
    and income vs expense comparisons. Analyst and Admin only.
    """
    monthly = get_monthly_totals(12)
    expense_breakdown = get_category_breakdown('expense')
    income_breakdown = get_category_breakdown('income')
    overall = compute_summary()

    labels = list(monthly.keys())
    income_series = [monthly[k].get('income', 0) for k in labels]
    expense_series = [monthly[k].get('expense', 0) for k in labels]

    exp_cats = [r['category__name'] or 'Uncategorized' for r in expense_breakdown[:8]]
    exp_vals = [float(r['total']) for r in expense_breakdown[:8]]

    inc_cats = [r['category__name'] or 'Uncategorized' for r in income_breakdown[:8]]
    inc_vals = [float(r['total']) for r in income_breakdown[:8]]

    context = {
        'overall': overall,
        'monthly_labels': json.dumps(labels),
        'monthly_income': json.dumps(income_series),
        'monthly_expense': json.dumps(expense_series),
        'expense_cats': json.dumps(exp_cats),
        'expense_vals': json.dumps(exp_vals),
        'income_cats': json.dumps(inc_cats),
        'income_vals': json.dumps(inc_vals),
        'expense_breakdown': expense_breakdown[:8],
        'income_breakdown': income_breakdown[:8],
    }
    return render(request, 'analytics/overview.html', context)
