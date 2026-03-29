import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import Count, Q
from scanner.models import EmailScan, ScamKeyword
from accounts.models import UserProfile


def admin_required(user):
    return user.is_authenticated and user.is_staff


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def dashboard(request):
    total_users = User.objects.filter(is_staff=False).count()
    total_scans = EmailScan.objects.count()
    scam_count = EmailScan.objects.filter(result='SCAM').count()
    safe_count = EmailScan.objects.filter(result='SAFE').count()
    suspicious_count = EmailScan.objects.filter(result='SUSPICIOUS').count()
    recent_scans = EmailScan.objects.select_related('user').order_by('-scanned_at')[:10]
    top_users = User.objects.filter(is_staff=False).annotate(
        scan_count=Count('scans')
    ).order_by('-scan_count')[:5]

    monthly = {}
    for scan in EmailScan.objects.all():
        key = scan.scanned_at.strftime('%b %Y')
        if key not in monthly:
            monthly[key] = {'scam': 0, 'safe': 0, 'suspicious': 0}
        monthly[key][scan.result.lower()] += 1

    context = {
        'total_users': total_users,
        'total_scans': total_scans,
        'scam_count': scam_count,
        'safe_count': safe_count,
        'suspicious_count': suspicious_count,
        'recent_scans': recent_scans,
        'top_users': top_users,
        'monthly_data': json.dumps(monthly),
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def users_list(request):
    query = request.GET.get('q', '')
    users = User.objects.filter(is_staff=False)
    if query:
        users = users.filter(Q(username__icontains=query) | Q(email__icontains=query))
    users = users.annotate(scan_count=Count('scans')).order_by('-date_joined')
    return render(request, 'admin_panel/users.html', {'users': users, 'query': query})


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def toggle_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_staff=False)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} has been {status}.')
    return redirect('admin_panel:users_list')


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id, is_staff=False)
    username = user.username
    user.delete()
    messages.success(request, f'User {username} deleted.')
    return redirect('admin_panel:users_list')


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def all_scans(request):
    result_filter = request.GET.get('result', '')
    scans = EmailScan.objects.select_related('user').all()
    if result_filter:
        scans = scans.filter(result=result_filter)
    return render(request, 'admin_panel/scans.html', {'scans': scans, 'result_filter': result_filter})


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def keywords(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            kw = request.POST.get('keyword', '').strip().lower()
            weight = float(request.POST.get('weight', 1.0))
            category = request.POST.get('category', 'general')
            if kw:
                obj, created = ScamKeyword.objects.get_or_create(keyword=kw, defaults={'weight': weight, 'category': category})
                if created:
                    messages.success(request, f'Keyword "{kw}" added.')
                else:
                    obj.weight = weight
                    obj.category = category
                    obj.save()
                    messages.info(request, f'Keyword "{kw}" updated.')
        elif action == 'delete':
            kid = request.POST.get('keyword_id')
            ScamKeyword.objects.filter(id=kid).delete()
            messages.success(request, 'Keyword deleted.')
        elif action == 'toggle':
            kid = request.POST.get('keyword_id')
            kw = get_object_or_404(ScamKeyword, id=kid)
            kw.is_active = not kw.is_active
            kw.save()
        return redirect('admin_panel:keywords')

    kw_list = ScamKeyword.objects.all().order_by('-weight')
    return render(request, 'admin_panel/keywords.html', {'keywords': kw_list})


@login_required
@user_passes_test(admin_required, login_url='/accounts/login/')
def export_csv(request):
    scans = EmailScan.objects.select_related('user').all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_scans_report.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'User', 'Subject', 'Sender', 'Result', 'Confidence', 'Scanned At'])
    for scan in scans:
        writer.writerow([
            scan.id, scan.user.username, scan.subject or 'N/A',
            scan.sender or 'N/A', scan.result,
            f"{scan.confidence_score}%", scan.scanned_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
