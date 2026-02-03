# nlu.py
import re
from typing import Dict, Any, Tuple, Optional

try:
    import spacy
    _nlp = spacy.load("en_core_web_sm")
except Exception:
    _nlp = None  # Fallback to regex-only

INTENT_PATTERNS = {
    'billing_inquiry': [
        r'\bbill(ing)?\b', r'\binvoice\b', r'\bcharge(d|s)?\b', r'\bbilled\b',
        r'\bpayment method\b', r'\bsubscription\b'
    ],
    'refund_status': [
        r'\brefund\b', r'\bmoney back\b', r'\breversal\b', r'\breimburs\w*\b'
    ],
    'password_reset': [
        r'\bforgot (my )?password\b', r'\breset password\b', r'\bcan\'?t log ?in\b',
        r'\bpassword (not )?work\w*\b'
    ],
    'app_crash': [
        r'\b(crash|freez(e|ing))\b', r'\bapp (stops|hangs)\b', r'\bnot (working|responding)\b',
        r'\bforce clos\w*\b', r'\bkeeps closing\b'
    ],
    'order_status': [
        r'\btrack(ing)?\b', r'\border status\b', r'\bdelivery\b', r'\bwhere.*order\b',
        r'\bshipment\b', r'\bshipping status\b'
    ],
    'business_hours': [
        r'\bhours\b', r'\bwhen.*open\b', r'\bsupport time\b', r'\bavailable\b',
        r'\bcontact.*time\b', r'\bwhen can.*reach\b'
    ],
    'pricing': [
        r'\bpric(e|es|ing)\b', r'\bplan(s)?\b', r'\bcost(s)?\b', r'\bhow much\b',
        r'\bfee(s)?\b', r'\bsubscription cost\b'
    ],
    'account_locked': [
        r'\blocked\b', r'\baccount locked\b', r'\bcannot login\b', r'\baccount suspended\b',
        r'\baccess denied\b', r'\bsuspended account\b'
    ],
    'payment_dispute': [
        r'\bdispute\b', r'\bincorrect charge\b', r'\bdouble charged\b', r'\bwrong amount\b',
        r'\bunauthorized charge\b', r'\bchargeback\b'
    ],
    'cancel_subscription': [
        r'\bcancel\b', r'\bunsubscribe\b', r'\bstop (billing|subscription)\b',
        r'\bend (my )?subscription\b', r'\bdelete.*account\b'
    ],
    'upgrade_plan': [
        r'\bupgrade\b', r'\bchange plan\b', r'\bhigher tier\b', r'\bpremium\b',
        r'\bbetter plan\b', r'\bswitch.*plan\b'
    ],
    'downgrade_plan': [
        r'\bdowngrade\b', r'\blower plan\b', r'\bbasic plan\b', r'\breduce.*cost\b',
        r'\bcheaper plan\b'
    ],
    'account_creation': [
        r'\bcreate account\b', r'\bsign up\b', r'\bregister\b', r'\bnew account\b',
        r'\bhow.*join\b', r'\bget started\b'
    ],
    'data_export': [
        r'\bexport.*data\b', r'\bdownload.*data\b', r'\bget.*data\b', r'\bdata export\b',
        r'\bcopy.*information\b', r'\bbackup.*data\b'
    ],
    'feature_request': [
        r'\bfeature\b', r'\bsuggestion\b', r'\bwish list\b', r'\bcan you add\b',
        r'\bnew feature\b', r'\bwould be nice\b'
    ],
    'integration_help': [
        r'\bintegrat(e|ion)\b', r'\bapi\b', r'\bconnect\b', r'\bwebhook\b',
        r'\bthird[- ]?party\b', r'\blink.*account\b'
    ],
    'bug_report': [
        r'\bbug\b', r'\berror\b', r'\bissue\b', r'\bproblem\b', r'\bglitch\b',
        r'\bnot working (correctly|properly)\b', r'\bsomething.*wrong\b'
    ],
    'account_security': [
        r'\bsecurity\b', r'\b2fa\b', r'\btwo[- ]?factor\b', r'\bhacked\b',
        r'\bunauthorized access\b', r'\bsuspicious activity\b', r'\bsecure.*account\b'
    ],
    'mobile_app': [
        r'\bmobile app\b', r'\bphone app\b', r'\bios\b', r'\bandroid\b',
        r'\bdownload app\b', r'\bapp store\b', r'\bplay store\b'
    ],
    'notification_settings': [
        r'\bnotification(s)?\b', r'\bemail alert(s)?\b', r'\bstop.*emails\b',
        r'\bturn off.*notifications\b', r'\balert settings\b', r'\bunsubscribe.*emails\b'
    ],
    'invoice_request': [
        r'\binvoice\b', r'\breceipt\b', r'\bproof.*payment\b', r'\bbilling statement\b',
        r'\bpayment confirmation\b', r'\btax.*document\b'
    ],
    'trial_extension': [
        r'\bextend.*trial\b', r'\btrial extension\b', r'\bmore time\b', r'\btrial.*end\w*\b',
        r'\bfree trial\b', r'\btrial.*expir\w*\b'
    ],
    'multiple_accounts': [
        r'\bmultiple account(s)?\b', r'\bmore than one\b', r'\bsecond account\b',
        r'\bteam account\b', r'\bshared account\b', r'\bfamily plan\b'
    ],
}

ENTITY_PATTERNS = {
    'order_id': r'\border\s*#?\s*([A-Z0-9\-]{6,})\b',
    'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',
}

def extract_entities(text: str) -> Dict[str, Any]:
    entities = {}
    # Regex entities
    for name, pat in ENTITY_PATTERNS.items():
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            entities[name] = m.group(1) if m.groups() else m.group(0)
    # Optional spaCy entities
    if _nlp:
        doc = _nlp(text)
        for ent in doc.ents:
            if ent.label_ in ('DATE', 'TIME', 'MONEY'):
                entities.setdefault(ent.label_.lower(), []).append(ent.text)
    return entities

def match_intent(text: str) -> Tuple[Optional[str], float]:
    text_norm = text.lower().strip()
    scores = {}
    for intent, patterns in INTENT_PATTERNS.items():
        score = 0.0
        for p in patterns:
            if re.search(p, text_norm):
                score += 0.5  # weight per hit (increased from 0.4)
        # Bonus if intent name appears as a word (rare, but helpful)
        if intent in text_norm:
            score += 0.3  # increased bonus
        scores[intent] = min(score, 1.0)
    # Pick best intent if any score > 0
    best_intent = max(scores, key=scores.get) if scores else None
    best_score = scores.get(best_intent, 0.0) if best_intent else 0.0
    if best_score < 0.2:
        return None, 0.0
    return best_intent, best_score
