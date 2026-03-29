from django.db import models
from django.contrib.auth.models import User
import json


class ScamKeyword(models.Model):
    keyword = models.CharField(max_length=200, unique=True)
    weight = models.FloatField(default=1.0)
    category = models.CharField(max_length=100, default='general')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.keyword

    class Meta:
        ordering = ['-weight']


class EmailScan(models.Model):
    RESULT_CHOICES = [('SCAM', 'Scam'), ('SAFE', 'Safe'), ('SUSPICIOUS', 'Suspicious')]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='scans')
    subject = models.CharField(max_length=500, blank=True, null=True)
    sender = models.CharField(max_length=300, blank=True, null=True)
    email_content = models.TextField()
    result = models.CharField(max_length=20, choices=RESULT_CHOICES)
    confidence_score = models.FloatField(default=0.0)
    reasons = models.TextField(default='[]')  # JSON list
    suspicious_links = models.TextField(default='[]')  # JSON list
    detected_keywords = models.TextField(default='[]')  # JSON list
    scanned_at = models.DateTimeField(auto_now_add=True)
    file_name = models.CharField(max_length=255, blank=True, null=True)

    def get_reasons(self):
        try:
            return json.loads(self.reasons)
        except:
            return []

    def get_suspicious_links(self):
        try:
            return json.loads(self.suspicious_links)
        except:
            return []

    def get_detected_keywords(self):
        try:
            return json.loads(self.detected_keywords)
        except:
            return []

    def __str__(self):
        return f"{self.user.username} - {self.result} ({self.scanned_at.strftime('%Y-%m-%d')})"

    class Meta:
        ordering = ['-scanned_at']
