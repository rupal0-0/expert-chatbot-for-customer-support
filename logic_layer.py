# logic_layer.py
from pyDatalog import pyDatalog

# Declare predicate and variable terms
pyDatalog.create_terms('intent, entity, response, policy, escalate, fallback')
pyDatalog.create_terms('I, E, Text, Confidence, Reason')
pyDatalog.create_terms('low_confidence, force_escalation')

# --- Knowledge base: responses ---
# Response(Text) is the answer string for a given intent; entity specialization is optional.

# Billing inquiries
+response('billing_inquiry', 'Your billing cycle is monthly. You can view invoices in the Billing section of your account.')
+response('refund_status', 'Refunds are processed within 5-7 business days after approval.')
+response('invoice_request', 'You can download invoices from Account Settings -> Billing -> Invoice History. Need a specific invoice? Share the date and I\'ll help locate it.')

# Technical issues
+response('password_reset', 'To reset your password, use "Forgot Password" on the login page. Check spam for the reset email.')
+response('app_crash', 'Please update to the latest app version. If it still crashes, share logs via Settings -> Diagnostics.')
+response('bug_report', 'Thanks for reporting! Please describe the issue in detail and share screenshots if possible. Our team will investigate within 24-48 hours.')

# Order tracking
+response('order_status', 'You can track your order in My Orders -> Track. Share your order ID if you need me to check.')

# General info
+response('business_hours', 'Our support hours are 9:00-18:00 IST, Monday to Friday.')
+response('pricing', 'We offer Basic, Pro, and Enterprise plans. Pricing details are on the Plans page in your dashboard.')

# Account management
+response('cancel_subscription', 'You can cancel anytime from Account Settings -> Subscription -> Cancel. You\'ll retain access until the end of your billing period.')
+response('upgrade_plan', 'Great! You can upgrade from Account Settings -> Subscription -> Change Plan. Upgrades are prorated.')
+response('downgrade_plan', 'You can downgrade from Account Settings -> Subscription -> Change Plan. Changes take effect at the next billing cycle.')
+response('account_creation', 'Sign up at our homepage! Click "Get Started" and follow the steps. The Basic plan includes a 14-day free trial.')
+response('multiple_accounts', 'You can create separate accounts for different uses. For team features, check out our Team Plan with shared workspaces.')

# Security & Privacy
+response('account_security', 'Enable 2FA in Account Settings -> Security for extra protection. Use a strong, unique password and review login activity regularly.')
+response('data_export', 'Export your data from Account Settings -> Privacy -> Download Data. You\'ll receive a link within 24 hours.')

# Features & Integration
+response('feature_request', 'We love hearing ideas! Submit feature requests at feedback.example.com or via the Feedback button in your dashboard.')
+response('integration_help', 'We integrate with 100+ tools. Check our Integration Directory or visit docs.example.com/integrations for setup guides.')
+response('mobile_app', 'Download our app from the App Store (iOS) or Google Play Store (Android). Search "YourApp Support".')
+response('notification_settings', 'Manage notifications in Account Settings -> Notifications. You can customize email, SMS, and push alerts.')

# Trial & Special requests
+response('trial_extension', 'Trial extensions are handled case-by-case. I\'m escalating to our support team who can review your request.')

# --- Policies ---
# Some intents require escalation under conditions (e.g., account locked).
# Use + to assert facts so pyDatalog registers them

# assert facts
+policy('force_escalation_required', 'account_locked')
+policy('force_escalation_required', 'payment_dispute')
+policy('force_escalation_required', 'trial_extension')
+policy('force_escalation_required', 'data_export')  # May need verification
+policy('force_escalation_required', 'cancel_subscription')  # Retention team handles

# Escalate on low confidence or forced policy triggers
# We express escalation conditions with helper rules.

low_confidence(Confidence) <= (Confidence < 0.4)  # lowered threshold to 0.4
force_escalation(I) <= policy('force_escalation_required', I)

# A case escalates if either low confidence OR forced escalation applies.
escalate(I, Confidence, Reason) <= (low_confidence(Confidence)) & (Reason == 'low_confidence')
escalate(I, Confidence, Reason) <= (force_escalation(I)) & (Reason == 'policy')

# Fallback when no response is defined
fallback(I) <= ~(response(I, Text))
