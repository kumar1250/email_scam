import json
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import EmailScan, ScamKeyword
from .detector import analyze_email
from .forms import EmailScanForm


@login_required
def dashboard(request):
    scans = EmailScan.objects.filter(user=request.user)
    total = scans.count()
    scam_count = scans.filter(result='SCAM').count()
    safe_count = scans.filter(result='SAFE').count()
    suspicious_count = scans.filter(result='SUSPICIOUS').count()
    recent_scans = scans[:10]

    monthly_data = {}
    for scan in scans:
        key = scan.scanned_at.strftime('%b %Y')
        if key not in monthly_data:
            monthly_data[key] = {'scam': 0, 'safe': 0, 'suspicious': 0}
        monthly_data[key][scan.result.lower()] += 1

    context = {
        'total': total,
        'scam_count': scam_count,
        'safe_count': safe_count,
        'suspicious_count': suspicious_count,
        'recent_scans': recent_scans,
        'monthly_data': json.dumps(monthly_data),
        'form': EmailScanForm(),
    }
    return render(request, 'scanner/dashboard.html', context)


@login_required
def scan_email(request):
    if request.method == 'POST':
        subject = request.POST.get('subject', '')
        sender = request.POST.get('sender', '')
        content = request.POST.get('content', '')
        file_name = None

        uploaded_file = request.FILES.get('email_file')
        if uploaded_file:
            file_name = uploaded_file.name
            try:
                content = uploaded_file.read().decode('utf-8', errors='ignore')
            except Exception as e:
                return JsonResponse({'error': f'Could not read file: {str(e)}'}, status=400)

        if not content.strip():
            return JsonResponse({'error': 'Email content is required.'}, status=400)

        analysis = analyze_email(subject=subject, sender=sender, content=content)

        scan = EmailScan.objects.create(
            user=request.user,
            subject=subject,
            sender=sender,
            email_content=content[:5000],
            result=analysis['result'],
            confidence_score=analysis['confidence_score'],
            reasons=json.dumps(analysis['reasons']),
            suspicious_links=json.dumps(analysis['suspicious_links']),
            detected_keywords=json.dumps(analysis['detected_keywords']),
            file_name=file_name,
        )

        return JsonResponse({
            'scan_id': scan.id,
            'result': analysis['result'],
            'confidence_score': analysis['confidence_score'],
            'reasons': analysis['reasons'],
            'suspicious_links': analysis['suspicious_links'],
            'detected_keywords': analysis['detected_keywords'],
            'raw_score': analysis['raw_score'],
        })
    return JsonResponse({'error': 'POST required'}, status=405)


@login_required
def history(request):
    scans = EmailScan.objects.filter(user=request.user)
    paginator = Paginator(scans, 15)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'scanner/history.html', {'page_obj': page_obj})


@login_required
def scan_detail(request, scan_id):
    scan = get_object_or_404(EmailScan, id=scan_id, user=request.user)
    return render(request, 'scanner/scan_detail.html', {'scan': scan})


@login_required
@require_POST
def delete_scan(request, scan_id):
    scan = get_object_or_404(EmailScan, id=scan_id, user=request.user)
    scan.delete()
    messages.success(request, 'Scan record deleted.')
    return redirect('scanner:history')


@login_required
@require_POST
def delete_all_history(request):
    EmailScan.objects.filter(user=request.user).delete()
    messages.success(request, 'All scan history deleted.')
    return redirect('scanner:history')


@login_required
def export_history_csv(request):
    scans = EmailScan.objects.filter(user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="scan_history.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Subject', 'Sender', 'Result', 'Confidence', 'Scanned At'])
    for scan in scans:
        writer.writerow([
            scan.id,
            scan.subject or 'N/A',
            scan.sender or 'N/A',
            scan.result,
            f"{scan.confidence_score}%",
            scan.scanned_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response
