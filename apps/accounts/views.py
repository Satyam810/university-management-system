"""Account views for authentication."""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.views.generic import CreateView, UpdateView, ListView
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import LoginForm, UserCreateForm, UserEditForm
from .models import User, Role
from .mixins import AdminRequiredMixin


class CustomLoginView(LoginView):
    """Custom login view with role-based redirect."""
    form_class = LoginForm
    template_name = 'accounts/login.html'

    def get_success_url(self):
        return reverse_lazy('core:home')


class CustomLogoutView(LogoutView):
    """Custom logout view."""
    next_page = 'accounts:login'


class UserCreateView(AdminRequiredMixin, CreateView):
    """Create new user (Admin only)."""
    model = User
    form_class = UserCreateForm
    template_name = 'accounts/user_form.html'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User created successfully.')
        return super().form_valid(form)


class UserListView(AdminRequiredMixin, ListView):
    """List all users - Admin only."""
    model = User
    template_name = 'accounts/user_list.html'
    context_object_name = 'users'
    paginate_by = 20

    def get_queryset(self):
        role = self.request.GET.get('role')
        qs = User.objects.all().order_by('-date_joined')
        if role:
            qs = qs.filter(role=role)
        return qs


class UserUpdateView(AdminRequiredMixin, UpdateView):
    """Edit user - Admin only."""
    model = User
    form_class = UserEditForm
    template_name = 'accounts/user_form.html'
    context_object_name = 'user_obj'
    success_url = reverse_lazy('accounts:user_list')

    def form_valid(self, form):
        messages.success(self.request, 'User updated successfully.')
        return super().form_valid(form)


@login_required
def user_delete(request, pk):
    """Delete user - Admin only."""
    if request.user.role != Role.ADMIN:
        return redirect('core:home')
    user = get_object_or_404(User, pk=pk)
    if user == request.user:
        messages.error(request, 'You cannot delete yourself.')
        return redirect('accounts:user_list')
    if user.is_superuser:
        messages.error(request, 'Cannot delete superuser.')
        return redirect('accounts:user_list')
    username = user.username
    user.delete()
    messages.success(request, f'User {username} has been deleted.')
    return redirect('accounts:user_list')
