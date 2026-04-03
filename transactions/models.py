from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from users.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type_hint = models.CharField(
        max_length=10,
        choices=[('income', 'Income'), ('expense', 'Expense'), ('both', 'Both')],
        default='both'
    )
    icon = models.CharField(max_length=50, default='circle')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']


class Transaction(models.Model):
    TYPE_INCOME = 'income'
    TYPE_EXPENSE = 'expense'

    TYPE_CHOICES = [
        (TYPE_INCOME, 'Income'),
        (TYPE_EXPENSE, 'Expense'),
    ]

    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    transaction_type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    date = models.DateField()
    notes = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.transaction_type.capitalize()} ₹{self.amount} on {self.date}"

    @property
    def is_income(self):
        return self.transaction_type == self.TYPE_INCOME

    @property
    def is_expense(self):
        return self.transaction_type == self.TYPE_EXPENSE

    class Meta:
        db_table = 'transactions'
        ordering = ['-date', '-created_at']
