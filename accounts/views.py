from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import SignupForm, LoginForm, ProfileUpdateForm, PasswordChangeForm
from .models import UserProfile


def signup_view(request):
    if request.user.is_authenticated:
        return redirect('scanner:dashboard')
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Welcome, {user.first_name}! Account created successfully.')
            return redirect('scanner:dashboard')
        else:
            messages.error(request, 'Please fix the errors below.')
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        if request.user.is_staff:
            return redirect('admin_panel:dashboard')
        return redirect('scanner:dashboard')
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}!')
            if user.is_staff:
                return redirect('admin_panel:dashboard')
            return redirect('scanner:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')


@login_required
def profile_view(request):
    profile, _ = UserProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'update_profile':
            form = ProfileUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profile updated successfully!')
            else:
                messages.error(request, 'Error updating profile.')
            return redirect('accounts:profile')
        elif action == 'change_password':
            pwd_form = PasswordChangeForm(request.POST)
            if pwd_form.is_valid():
                if request.user.check_password(pwd_form.cleaned_data['old_password']):
                    request.user.set_password(pwd_form.cleaned_data['new_password1'])
                    request.user.save()
                    update_session_auth_hash(request, request.user)
                    messages.success(request, 'Password changed successfully!')
                else:
                    messages.error(request, 'Current password is incorrect.')
            else:
                for error in pwd_form.errors.values():
                    messages.error(request, error[0])
            return redirect('accounts:profile')

    from scanner.models import EmailScan
    scan_count = EmailScan.objects.filter(user=request.user).count()
    scam_count = EmailScan.objects.filter(user=request.user, result='SCAM').count()
    profile_form = ProfileUpdateForm(instance=request.user)
    pwd_form = PasswordChangeForm()
    return render(request, 'accounts/profile.html', {
        'profile': profile,
        'profile_form': profile_form,
        'pwd_form': pwd_form,
        'scan_count': scan_count,
        'scam_count': scam_count,
    })
