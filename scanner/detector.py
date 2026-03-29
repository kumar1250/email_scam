import re
import json
from urllib.parse import urlparse


SCAM_KEYWORDS = {
    'urgent': 3.0,
    'congratulations': 2.5,
    'winner': 2.5,
    'lottery': 3.0,
    'prize': 2.5,
    'free money': 3.5,
    'claim now': 3.0,
    'act now': 2.8,
    'limited time': 2.0,
    'verify your account': 3.0,
    'click here': 2.0,
    'update your information': 2.8,
    'suspended': 2.5,
    'unusual activity': 2.5,
    'confirm your identity': 2.8,
    'inheritance': 3.0,
    'beneficiary': 2.8,
    'million dollars': 3.5,
    'wire transfer': 3.0,
    'bank account': 2.0,
    'social security': 2.8,
    'password expired': 3.0,
    'account locked': 2.8,
    'dear friend': 2.0,
    'dear customer': 1.5,
    'nigerian prince': 4.0,
    'million pounds': 3.5,
    'advance fee': 3.5,
    'confidential': 1.5,
    'undisclosed': 2.0,
    'secret': 1.5,
    'investment opportunity': 2.5,
    'risk free': 2.5,
    'guaranteed': 2.0,
    'no cost': 2.0,
    'credit card': 1.5,
    'ssn': 3.0,
    'tax refund': 2.8,
    'irs': 2.0,
    'bitcoin': 2.0,
    'cryptocurrency': 1.8,
    'gift card': 2.8,
    'western union': 3.0,
    'moneygram': 3.0,
    'suspended account': 3.0,
    'verify now': 2.8,
    'expires soon': 2.2,
    'warning': 1.5,
    'alert': 1.5,
    'immediate action': 3.0,
    'you have been selected': 2.8,
}

SAFE_DOMAINS = [
    'google.com', 'gmail.com', 'microsoft.com', 'outlook.com',
    'apple.com', 'amazon.com', 'paypal.com', 'github.com',
    'linkedin.com', 'twitter.com', 'facebook.com', 'instagram.com',
    'yahoo.com', 'hotmail.com', 'live.com', 'netflix.com',
]

SUSPICIOUS_TLDS = ['.xyz', '.tk', '.ml', '.ga', '.cf', '.gq', '.bit', '.top', '.click']

PHISHING_PATTERNS = [
    r'paypa1', r'g00gle', r'micros0ft', r'amaz0n', r'app1e',
    r'secure.*login', r'login.*secure', r'account.*verify',
    r'verify.*account', r'update.*credential',
]


def extract_urls(text):
    url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
    return re.findall(url_pattern, text, re.IGNORECASE)


def analyze_urls(urls):
    suspicious = []
    reasons = []
    score = 0.0

    for url in urls:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        path = parsed.path.lower()
        is_suspicious = False

        for tld in SUSPICIOUS_TLDS:
            if domain.endswith(tld):
                suspicious.append(url)
                reasons.append(f"Suspicious domain extension ({tld}): {domain}")
                score += 2.5
                is_suspicious = True
                break

        for pattern in PHISHING_PATTERNS:
            if re.search(pattern, domain + path, re.IGNORECASE):
                if url not in suspicious:
                    suspicious.append(url)
                reasons.append(f"Phishing pattern detected in URL: {domain}")
                score += 3.0
                is_suspicious = True
                break

        if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', domain):
            suspicious.append(url)
            reasons.append(f"URL uses IP address instead of domain name: {domain}")
            score += 2.5
            is_suspicious = True

        if len(domain) > 50:
            if url not in suspicious:
                suspicious.append(url)
            reasons.append(f"Unusually long domain name: {domain[:50]}...")
            score += 1.5
            is_suspicious = True

        known_brand = None
        for brand in ['paypal', 'google', 'microsoft', 'apple', 'amazon', 'ebay', 'bank']:
            if brand in domain:
                for safe in SAFE_DOMAINS:
                    if domain == safe or domain.endswith('.' + safe):
                        known_brand = None
                        break
                    known_brand = brand
                break

        if known_brand:
            if url not in suspicious:
                suspicious.append(url)
            reasons.append(f"Possible brand impersonation of '{known_brand}': {domain}")
            score += 3.5
            is_suspicious = True

    return suspicious, reasons, score


def analyze_sender(sender):
    if not sender:
        return [], 0.0

    reasons = []
    score = 0.0

    free_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'live.com']
    legitimate_senders = ['paypal.com', 'amazon.com', 'apple.com', 'microsoft.com', 'google.com']

    email_match = re.search(r'[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}', sender)
    if email_match:
        email = email_match.group(0).lower()
        domain = email.split('@')[1]

        for legit in legitimate_senders:
            if legit.split('.')[0] in sender.lower() and legit not in domain:
                reasons.append(f"Sender claims to be from {legit.split('.')[0]} but uses different domain")
                score += 3.0
                break

        for pattern in PHISHING_PATTERNS:
            if re.search(pattern, email, re.IGNORECASE):
                reasons.append(f"Suspicious sender email pattern: {email}")
                score += 2.5
                break

        if re.search(r'\d{4,}', domain):
            reasons.append(f"Sender domain contains unusual numbers: {domain}")
            score += 1.5

    return reasons, score


def analyze_keywords(content):
    content_lower = content.lower()
    detected = []
    score = 0.0
    reasons = []

    try:
        from scanner.models import ScamKeyword
        db_keywords = ScamKeyword.objects.filter(is_active=True)
        keyword_dict = {kw.keyword.lower(): kw.weight for kw in db_keywords}
    except:
        keyword_dict = {}

    all_keywords = {**SCAM_KEYWORDS, **keyword_dict}

    for keyword, weight in all_keywords.items():
        if keyword.lower() in content_lower:
            detected.append(keyword)
            score += weight

    if detected:
        reasons.append(f"Found {len(detected)} suspicious keyword(s): {', '.join(detected[:5])}")

    if re.search(r'[A-Z\s]{20,}', content):
        score += 1.5
        reasons.append("Email contains excessive ALL CAPS text (pressure tactic)")

    exclamation_count = content.count('!')
    if exclamation_count > 5:
        score += min(exclamation_count * 0.2, 2.0)
        reasons.append(f"Excessive use of exclamation marks ({exclamation_count})")

    if re.search(r'\$[\d,]+|\d+ dollars|\d+ euros|\d+ pounds', content_lower):
        score += 1.5
        reasons.append("Mentions specific monetary amounts")

    if re.search(r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{1,2} (hours?|days?|minutes?) (remaining|left|only)', content_lower):
        score += 1.0
        reasons.append("Contains time pressure or deadline tactics")

    return detected, reasons, score


def calculate_result(total_score):
    if total_score >= 8.0:
        confidence = min(95, 60 + (total_score - 8) * 2)
        return 'SCAM', round(confidence, 1)
    elif total_score >= 4.0:
        confidence = min(85, 40 + (total_score - 4) * 5)
        return 'SUSPICIOUS', round(confidence, 1)
    else:
        safe_confidence = max(75, 99 - total_score * 5)
        return 'SAFE', round(safe_confidence, 1)


def analyze_email(subject='', sender='', content=''):
    full_text = f"{subject} {sender} {content}"
    total_score = 0.0
    all_reasons = []
    all_suspicious_links = []
    all_detected_keywords = []

    urls = extract_urls(full_text)
    suspicious_links, url_reasons, url_score = analyze_urls(urls)
    all_suspicious_links.extend(suspicious_links)
    all_reasons.extend(url_reasons)
    total_score += url_score

    sender_reasons, sender_score = analyze_sender(sender)
    all_reasons.extend(sender_reasons)
    total_score += sender_score

    detected_keywords, kw_reasons, kw_score = analyze_keywords(full_text)
    all_detected_keywords.extend(detected_keywords)
    all_reasons.extend(kw_reasons)
    total_score += kw_score

    if not all_reasons:
        all_reasons.append("No significant scam indicators found")

    result, confidence = calculate_result(total_score)

    return {
        'result': result,
        'confidence_score': confidence,
        'reasons': all_reasons,
        'suspicious_links': all_suspicious_links,
        'detected_keywords': all_detected_keywords,
        'raw_score': round(total_score, 2),
    }
