from django import forms
from .models import Transaction, Category
import datetime


class TransactionForm(forms.ModelForm):
    date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'}),
        initial=datetime.date.today
    )

    class Meta:
        model = Transaction
        fields = ['amount', 'transaction_type', 'category', 'date', 'notes']
        widgets = {
            'amount': forms.NumberInput(attrs={
                'class': 'form-input',
                'placeholder': '0.00',
                'step': '0.01',
                'min': '0.01',
            }),
            'transaction_type': forms.Select(attrs={'class': 'form-input', 'id': 'id_transaction_type'}),
            'category': forms.Select(attrs={'class': 'form-input', 'id': 'id_category'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-input',
                'placeholder': 'Optional description or notes...',
                'rows': 3,
            }),
        }

    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount is not None and amount <= 0:
            raise forms.ValidationError("Amount must be greater than zero.")
        return amount

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date > datetime.date.today():
            raise forms.ValidationError("Transaction date cannot be in the future.")
        return date


class TransactionFilterForm(forms.Form):
    SORT_CHOICES = [
        ('-date', 'Date (Newest First)'),
        ('date', 'Date (Oldest First)'),
        ('-amount', 'Amount (High to Low)'),
        ('amount', 'Amount (Low to High)'),
    ]

    transaction_type = forms.ChoiceField(
        choices=[('', 'All Types'), ('income', 'Income'), ('expense', 'Expense')],
        required=False,
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label='All Categories',
        widget=forms.Select(attrs={'class': 'form-input'})
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'form-input', 'type': 'date'})
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Search notes...'})
    )
    sort = forms.ChoiceField(
        choices=SORT_CHOICES,
        required=False,
        initial='-date',
        widget=forms.Select(attrs={'class': 'form-input'})
    )

    def clean(self):
        cleaned = super().clean()
        date_from = cleaned.get('date_from')
        date_to = cleaned.get('date_to')
        if date_from and date_to and date_from > date_to:
            raise forms.ValidationError("Start date cannot be after end date.")
        return cleaned


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'type_hint', 'icon']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Category name'}),
            'type_hint': forms.Select(attrs={'class': 'form-input'}),
            'icon': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. shopping-bag'}),
        }
