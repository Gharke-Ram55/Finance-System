from django.contrib import admin
from .models import Transaction, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'type_hint', 'icon']
    search_fields = ['name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'transaction_type', 'amount', 'category', 'created_by', 'created_at']
    list_filter = ['transaction_type', 'category', 'date']
    search_fields = ['notes']
    date_hierarchy = 'date'
