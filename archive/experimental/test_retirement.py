#!/usr/bin/env python3
"""
Test the retirement message classification
"""

from src.processors.processor_regex import classify_with_regex

def test_retirement_message():
    print("🔍 Testing Retirement Message Classification")
    print("=" * 50)
    
    msg = "The 'ReportGenerator' module will be retired in version 4.0. Please migrate to the 'AdvancedAnalyticsSuite' by Dec 2025"
    
    print("Message:")
    print(f"  {msg}")
    print()
    
    # Test regex
    regex_result = classify_with_regex('LegacyCRM', msg)
    print(f"Regex result: {regex_result}")
    
    # Check what keywords are present
    keywords = {
        'retire': 'retire' in msg.lower(),
        'version': 'version' in msg.lower(),
        'migrate': 'migrate' in msg.lower(),
        'deprecated': 'deprecat' in msg.lower(),
        'obsolete': 'obsolete' in msg.lower(),
        'will be removed': 'will.*be.*removed' in msg.lower(),
        'no longer supported': 'no.*longer.*supported' in msg.lower()
    }
    
    print("\nKeyword analysis:")
    for keyword, present in keywords.items():
        status = "✅" if present else "❌"
        print(f"  {status} {keyword}")
    
    print(f"\nExpected: deprecation_warning")
    print(f"Actual: {regex_result}")
    print(f"Status: {'✅' if regex_result == 'deprecation_warning' else '❌'}")

if __name__ == "__main__":
    test_retirement_message()