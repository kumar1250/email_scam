# 🛡️ ShieldMail — Email Scam Detection System

A full-stack Django web application for detecting email scams with role-based authentication, an AI-style rule-based detection engine, admin dashboard, analytics, and a polished modern UI.

---

## 🚀 Quick Start

### 1. Prerequisites
- Python 3.10 or higher
- pip

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. One-command setup (migrations + demo accounts + seed data)
```bash
python setup.py
```

### 4. Run the server
```bash
python manage.py runserver
```

### 5. Open in browser
```
http://127.0.0.1:8000/
```

---

## 🔑 Demo Credentials

| Role  | Username | Password |
|-------|----------|----------|
| Admin | `admin`  | `admin123` |
| User  | `user`   | `user123`  |

---

## 📁 Project Structure

```
email_scam_detector/
├── email_scam_detector/     # Django project settings & URLs
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                # Auth: signup, login, logout, profile
│   ├── models.py            # UserProfile model
│   ├── views.py
│   ├── forms.py
│   └── urls.py
│
├── scanner/                 # Core scanning app
│   ├── models.py            # EmailScan, ScamKeyword models
│   ├── views.py             # Dashboard, scan, history, detail
│   ├── detector.py          # 🔍 Scam detection engine
│   ├── forms.py
│   └── urls.py
│
├── admin_panel/             # Admin dashboard app
│   ├── views.py             # Stats, user mgmt, keywords, export
│   └── urls.py
│
├── templates/               # All HTML templates
│   ├── base.html            # Sidebar + topbar layout
│   ├── accounts/
│   │   ├── login.html
│   │   ├── signup.html
│   │   └── profile.html
│   ├── scanner/
│   │   ├── dashboard.html   # Main scan UI + charts
│   │   ├── history.html
│   │   └── scan_detail.html
│   └── admin_panel/
│       ├── dashboard.html   # Analytics + charts
│       ├── users.html
│       ├── scans.html
│       └── keywords.html
│
├── static/
│   ├── css/main.css         # Complete design system (dark mode)
│   └── js/main.js           # Theme toggle, animations, toasts
│
├── setup.py                 # DB init + demo data seeder
├── manage.py
└── requirements.txt
```

---

## ✨ Features

### User Features
- 🔐 Secure signup / login / logout with password hashing
- 📊 Personal dashboard with scan stats & charts
- 📧 Paste email text or upload `.txt` / `.eml` files
- 🔍 Instant scam analysis with confidence score
- 📋 Full scan history with pagination
- 🗑️ Delete individual or all history
- 📥 Export history as CSV
- 👤 Profile page — update name, email, password
- 🌙 Dark mode toggle (persisted in localStorage)

### Admin Features
- 👥 View and manage all users (activate/deactivate/delete)
- 📨 View all scans across all users with filters
- 📈 Analytics: bar chart, donut chart, top users
- 🏷️ Manage scam keyword dataset (add/toggle/delete)
- 📤 Export all scan data as CSV

### Detection Engine (`scanner/detector.py`)
- **Keyword scoring** — 50+ built-in scam keywords with weighted scoring
- **URL analysis** — detects suspicious TLDs, IP-based links, brand impersonation
- **Phishing patterns** — regex patterns for typosquatting (paypa1, g00gle, etc.)
- **Sender analysis** — detects mismatched domains, suspicious email patterns
- **Text analysis** — ALL CAPS detection, excessive exclamation marks, money amounts
- **Confidence score** — 0–99% probability derived from total weighted score
- **3-tier result** — SCAM / SUSPICIOUS / SAFE

---

## 🎨 UI Design
- Font: **Inter** (UI) + **Space Grotesk** (headings/numbers)
- Icons: **Font Awesome 6**
- Charts: **Chart.js 4**
- Full **dark mode** support via CSS variables
- Fully **responsive** (mobile sidebar toggle)
- Animated stat counters, scan result slide-in, pulse effects

---

## 🔒 Security
- Django CSRF protection on all forms and AJAX requests
- Password hashing via Django's PBKDF2 + SHA256
- `@login_required` + `@user_passes_test(admin_required)` decorators
- Input validation on all forms
- File upload restricted to `.txt` and `.eml`

---

## ☁️ Render.com Deployment
1. Create a new web service on Render:
   - Connect your GitHub repo
   - Environment: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn email_scam_detector.wsgi:application --bind 0.0.0.0:$PORT`
   - Add `render.yaml` and `Procfile` to repository (already present)

2. Set Render environment variables:
   - `DJANGO_SECRET_KEY` (a strong random secret)
   - `DJANGO_DEBUG=false`
   - `DJANGO_ALLOWED_HOSTS=*` (or your Render domain)
   - `DATABASE_URL` (optional: PostgreSQL add-on in Render)

3. (Optional but recommended) Add PostgreSQL service in Render, copy its DATABASE_URL to the web service.

4. Ensure migrations run (Render automatically does this if you add a release command in settings):
   - You can add in Render "Migration command": `python manage.py migrate`

5. Enable static files in production:
   - `STATIC_ROOT = BASE_DIR / 'staticfiles'` (already set)
   - `STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'`
   - `MIDDLEWARE` includes `whitenoise.middleware.WhiteNoiseMiddleware`

6. Deploy and verify in browser.

---

### Quick local test after install
```bash
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
" 
