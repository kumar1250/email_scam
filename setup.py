#!/usr/bin/env python
"""
Run this once after setting up the project to:
- Apply migrations
- Create demo admin and user accounts
- Seed initial scam keywords
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_scam_detector.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth.models import User
from accounts.models import UserProfile
from scanner.models import ScamKeyword

print("✅  Applying migrations...")
from django.core.management import call_command
call_command('migrate', verbosity=0)

# Create admin
if not User.objects.filter(username='admin').exists():
    admin = User.objects.create_superuser('admin', 'admin@shieldmail.com', 'admin123')
    admin.first_name = 'Admin'
    admin.last_name = 'User'
    admin.save()
    UserProfile.objects.create(user=admin)
    print("✅  Admin created  →  username: admin  /  password: admin123")
else:
    print("ℹ️   Admin already exists")

# Create demo user
if not User.objects.filter(username='user').exists():
    demo = User.objects.create_user('user', 'user@example.com', 'user123')
    demo.first_name = 'Demo'
    demo.last_name = 'User'
    demo.save()
    UserProfile.objects.create(user=demo)
    print("✅  Demo user created  →  username: user  /  password: user123")
else:
    print("ℹ️   Demo user already exists")

# Seed keywords
SEED_KEYWORDS = [
    ('click here immediately', 3.0, 'urgent'),
    ('you have won', 3.5, 'financial'),
    ('bank account details', 3.0, 'financial'),
    ('send money', 2.8, 'financial'),
    ('100% free', 2.5, 'financial'),
    ('no obligation', 2.0, 'financial'),
    ('cash prize', 3.0, 'financial'),
    ('verify your email', 2.5, 'phishing'),
    ('confirm your details', 2.5, 'phishing'),
    ('your account will be closed', 3.0, 'phishing'),
    ('dear account holder', 2.5, 'social'),
    ('exclusive offer', 2.0, 'social'),
    ('act immediately', 3.0, 'urgent'),
    ('final notice', 2.8, 'urgent'),
    ('double your money', 3.5, 'financial'),
]

created = 0
for kw, weight, cat in SEED_KEYWORDS:
    _, c = ScamKeyword.objects.get_or_create(keyword=kw, defaults={'weight': weight, 'category': cat})
    if c:
        created += 1

print(f"✅  Seeded {created} new scam keywords")
print("\n🚀  Setup complete! Run:  python manage.py runserver")
