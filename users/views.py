from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse

from .models import User
from .forms import LoginForm, UserCreateForm, UserEditForm
from .decorators import admin_required


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    form = LoginForm(data=request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')

    return render(request, 'users/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
@admin_required
def user_list(request):
    users = User.objects.all().order_by('-created_at')
    return render(request, 'users/user_list.html', {'users': users})


@login_required
@admin_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST':
        if form.is_valid():
            user = form.save()
            messages.success(request, f'User "{user.username}" created successfully.')
            return redirect('user_list')
        else:
            messages.error(request, 'Please correct the errors below.')

    return render(request, 'users/user_form.html', {'form': form, 'action': 'Create'})


@login_required
@admin_required
def user_edit(request, pk):
    user = get_object_or_404(User, pk=pk)
    form = UserEditForm(request.POST or None, instance=user)
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, f'User "{user.username}" updated.')
            return redirect('user_list')

    return render(request, 'users/user_form.html', {'form': form, 'action': 'Edit', 'edit_user': user})


@login_required
@admin_required
def user_delete(request, pk):
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        if user == request.user:
            messages.error(request, 'You cannot delete your own account.')
        else:
            username = user.username
            user.delete()
            messages.success(request, f'User "{username}" removed.')
        return redirect('user_list')

    return render(request, 'users/user_confirm_delete.html', {'target_user': user})


@login_required
def profile_view(request):
    return render(request, 'users/profile.html', {'profile_user': request.user})
