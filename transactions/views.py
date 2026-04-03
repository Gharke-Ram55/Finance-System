from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
import csv
import json
from decimal import Decimal

from .models import Transaction, Category
from .forms import TransactionForm, TransactionFilterForm, CategoryForm
from .services import (
    get_filtered_transactions,
    compute_summary,
    get_dashboard_stats,
    get_category_breakdown,
    get_monthly_totals,
)
from users.decorators import admin_required, analyst_required


class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


@login_required
def dashboard(request):
    try:
        stats = get_dashboard_stats()
    except Exception:
        # If anything goes wrong building stats (e.g. empty DB edge cases),
        # return safe defaults so the page still loads
        stats = {
            'summary': {'total_income': Decimal('0'), 'total_expense': Decimal('0'), 'balance': Decimal('0')},
            'this_month': {'total_income': Decimal('0'), 'total_expense': Decimal('0'), 'balance': Decimal('0')},
            'recent_transactions': [],
            'monthly_data': {},
            'top_expense_categories': [],
            'total_transactions': 0,
        }

    monthly = stats['monthly_data']
    labels = list(monthly.keys())
    income_data = [monthly[k].get('income', 0) for k in labels]
    expense_data = [monthly[k].get('expense', 0) for k in labels]

    context = {
        'stats': stats,
        'chart_labels': json.dumps(labels),
        'chart_income': json.dumps(income_data),
        'chart_expense': json.dumps(expense_data),
    }
    return render(request, 'transactions/dashboard.html', context)


@login_required
def transaction_list(request):
    filter_form = TransactionFilterForm(request.GET or None)
    filters = {}

    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    transactions = get_filtered_transactions(filters)
    summary = compute_summary(transactions)

    paginator = Paginator(transactions, 15)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'filter_form': filter_form,
        'summary': summary,
        'total_count': transactions.count(),
    }
    return render(request, 'transactions/transaction_list.html', context)


@login_required
@admin_required
def transaction_create(request):
    form = TransactionForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            tx = form.save(commit=False)
            tx.created_by = request.user
            tx.save()
            messages.success(request, f'Transaction of ₹{tx.amount} recorded successfully.')
            return redirect('transaction_list')
        else:
            messages.error(request, 'Please fix the errors below.')

    context = {'form': form, 'action': 'Add New'}
    return render(request, 'transactions/transaction_form.html', context)


@login_required
@admin_required
def transaction_edit(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    form = TransactionForm(request.POST or None, instance=tx)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Transaction updated.')
            return redirect('transaction_list')

    context = {'form': form, 'action': 'Edit', 'transaction': tx}
    return render(request, 'transactions/transaction_form.html', context)


@login_required
@admin_required
def transaction_delete(request, pk):
    tx = get_object_or_404(Transaction, pk=pk)
    if request.method == 'POST':
        amount = tx.amount
        tx.delete()
        messages.success(request, f'Transaction of ₹{amount} deleted.')
        return redirect('transaction_list')
    return render(request, 'transactions/transaction_confirm_delete.html', {'transaction': tx})


@login_required
def transaction_detail(request, pk):
    tx = get_object_or_404(Transaction.objects.select_related('category', 'created_by'), pk=pk)
    return render(request, 'transactions/transaction_detail.html', {'transaction': tx})


@login_required
@analyst_required
def export_csv(request):
    filter_form = TransactionFilterForm(request.GET or None)
    filters = {}
    if filter_form.is_valid():
        filters = filter_form.cleaned_data

    transactions = get_filtered_transactions(filters)

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transactions.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Date', 'Type', 'Category', 'Amount (INR)', 'Notes', 'Created By'])
    for tx in transactions:
        writer.writerow([
            tx.pk,
            tx.date,
            tx.transaction_type,
            tx.category.name if tx.category else '',
            tx.amount,
            tx.notes,
            tx.created_by.username if tx.created_by else '',
        ])

    return response


@login_required
@admin_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'transactions/category_list.html', {'categories': categories})


@login_required
@admin_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Category created.')
        return redirect('category_list')
    return render(request, 'transactions/category_form.html', {'form': form, 'action': 'Create'})


@login_required
@admin_required
def category_delete(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    if request.method == 'POST':
        cat.delete()
        messages.success(request, f'Category "{cat.name}" deleted.')
        return redirect('category_list')
    return render(request, 'transactions/category_confirm_delete.html', {'category': cat})
