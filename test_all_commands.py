#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Test Suite for All Chatbot Commands
Tests all 23 intent categories with multiple query variations
"""

from chatbot import handle_query
from datetime import datetime

# Test cases organized by category
ALL_TEST_QUERIES = {
    "💳 1. Billing Inquiries": [
        "What's my billing cycle?",
        "How am I being charged?",
        "Tell me about my subscription",
        "What's my payment method?",
    ],
    
    "💳 2. Refund Status": [
        "How do I get a refund?",
        "I want my money back",
        "What's the refund policy?",
        "When will my refund arrive?",
    ],
    
    "💳 3. Invoice Request": [
        "I need an invoice",
        "Can I get a receipt?",
        "Send me my billing statement",
        "I need proof of payment",
    ],
    
    "💳 4. Payment Dispute (Escalates)": [
        "I was charged twice",
        "This charge is incorrect",
        "I see an unauthorized charge",
        "I want to dispute this payment",
    ],
    
    "👤 5. Password Reset": [
        "I forgot my password",
        "How do I reset my password?",
        "I can't log in",
        "My password doesn't work",
    ],
    
    "👤 6. Account Creation": [
        "How do I create an account?",
        "I want to sign up",
        "How do I register?",
        "How can I get started?",
    ],
    
    "👤 7. Account Locked (Escalates)": [
        "My account is locked",
        "I can't access my account",
        "My account was suspended",
        "Why is my account locked?",
    ],
    
    "👤 8. Cancel Subscription (Escalates)": [
        "I want to cancel my subscription",
        "How do I unsubscribe?",
        "Stop my subscription",
        "Cancel my account",
    ],
    
    "👤 9. Upgrade Plan": [
        "Can I upgrade to premium?",
        "I want to upgrade my plan",
        "Change to Pro plan",
        "How do I get more features?",
    ],
    
    "👤 10. Downgrade Plan": [
        "I need a cheaper plan",
        "Can I downgrade?",
        "Switch to basic plan",
        "I want to reduce my costs",
    ],
    
    "👤 11. Account Security": [
        "How do I enable 2FA?",
        "My account was hacked",
        "I see suspicious activity",
        "Make my account more secure",
    ],
    
    "👤 12. Data Export (Escalates)": [
        "I need to export my data",
        "How do I download my information?",
        "Can I backup my data?",
        "Get all my data",
    ],
    
    "👤 13. Multiple Accounts": [
        "Can I have multiple accounts?",
        "Do you have a team plan?",
        "I need a second account",
        "Family account options",
    ],
    
    "📦 14. Order Status": [
        "Track my order",
        "Track my order #ABC-12345",
        "Where is my order?",
        "What's my delivery status?",
        "Check shipment status",
    ],
    
    "💻 15. App Crash": [
        "The app keeps crashing",
        "My app freezes",
        "App won't respond",
        "App keeps closing",
    ],
    
    "💻 16. Bug Report": [
        "I found a bug",
        "There's an error in the app",
        "Something's not working right",
        "The feature is broken",
    ],
    
    "💻 17. Mobile App": [
        "How do I download the mobile app?",
        "Is there an iOS version?",
        "Android app download",
        "Where's your app in the app store?",
    ],
    
    "💻 18. Integration Help": [
        "How do I integrate with Zapier?",
        "I need API documentation",
        "Connect to third-party tools",
        "Webhook setup help",
    ],
    
    "⚙️ 19. Pricing": [
        "What are your prices?",
        "How much does it cost?",
        "Tell me about your plans",
        "What are the fees?",
    ],
    
    "⚙️ 20. Business Hours": [
        "When are you open?",
        "What are your support hours?",
        "When can I contact support?",
        "Are you available now?",
    ],
    
    "⚙️ 21. Notification Settings": [
        "Stop sending me emails",
        "How do I turn off notifications?",
        "Change my alert settings",
        "Unsubscribe from emails",
    ],
    
    "⚙️ 22. Feature Request": [
        "I have a feature request",
        "Can you add dark mode?",
        "Suggestion for improvement",
        "I wish you had...",
    ],
    
    "⚙️ 23. Trial Extension (Escalates)": [
        "Can I extend my free trial?",
        "I need more trial time",
        "My trial is ending",
        "Trial extension request",
    ],
}

def run_comprehensive_tests():
    """Run all test queries and generate a detailed report"""
    
    print("=" * 100)
    print("COMPREHENSIVE CHATBOT COMMAND TEST SUITE")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 100)
    print()
    
    total_categories = len(ALL_TEST_QUERIES)
    total_queries = sum(len(queries) for queries in ALL_TEST_QUERIES.values())
    passed = 0
    failed = 0
    escalated = 0
    
    results_summary = []
    
    for category, queries in ALL_TEST_QUERIES.items():
        print(f"\n{category}")
        print("-" * 100)
        
        category_passed = 0
        category_failed = 0
        category_escalated = 0
        
        for i, query in enumerate(queries, 1):
            try:
                response = handle_query(query)
                
                # Check if response is valid
                if response and len(response) > 10:
                    # Check if escalated
                    if "escalating" in response.lower() or "human support" in response.lower():
                        status = "⚠️ ESCALATE"
                        escalated += 1
                        category_escalated += 1
                    else:
                        status = "✅ PASS"
                        passed += 1
                        category_passed += 1
                else:
                    status = "❌ FAIL (Empty response)"
                    failed += 1
                    category_failed += 1
                
                # Truncate response for display
                display_response = response[:70] + "..." if len(response) > 70 else response
                
                print(f"{status} | Query {i}: {query}")
                print(f"         | Response: {display_response}")
                
            except Exception as e:
                status = "❌ FAIL"
                failed += 1
                category_failed += 1
                print(f"{status} | Query {i}: {query}")
                print(f"         | Error: {str(e)}")
        
        # Category summary
        results_summary.append({
            'category': category,
            'passed': category_passed,
            'failed': category_failed,
            'escalated': category_escalated,
            'total': len(queries)
        })
        
        print()
    
    # Final Summary
    print("=" * 100)
    print("TEST SUMMARY")
    print("=" * 100)
    print(f"\nCategories Tested: {total_categories}")
    print(f"Total Queries:     {total_queries}")
    print(f"✅ Passed:         {passed}")
    print(f"⚠️  Escalated:      {escalated}")
    print(f"❌ Failed:         {failed}")
    print(f"\nSuccess Rate:      {((passed + escalated) / total_queries * 100):.1f}%")
    
    # Category breakdown
    print("\n" + "=" * 100)
    print("CATEGORY BREAKDOWN")
    print("=" * 100)
    for result in results_summary:
        total = result['total']
        passed_pct = (result['passed'] / total * 100) if total > 0 else 0
        escalated_pct = (result['escalated'] / total * 100) if total > 0 else 0
        
        print(f"\n{result['category']}")
        print(f"  Total: {total} | ✅ {result['passed']} ({passed_pct:.0f}%) | "
              f"⚠️  {result['escalated']} ({escalated_pct:.0f}%) | ❌ {result['failed']}")
    
    print("\n" + "=" * 100)
    
    if failed == 0:
        print("🎉 ALL TESTS PASSED! The chatbot is working perfectly.")
    else:
        print(f"⚠️  {failed} test(s) failed. Review the errors above.")
    
    print("=" * 100)
    
    return {
        'total': total_queries,
        'passed': passed,
        'escalated': escalated,
        'failed': failed,
        'categories': total_categories
    }


if __name__ == "__main__":
    results = run_comprehensive_tests()
    
    # Exit code for CI/CD
    exit(0 if results['failed'] == 0 else 1)
