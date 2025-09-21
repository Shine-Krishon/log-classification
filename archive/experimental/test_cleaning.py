#!/usr/bin/env python3
"""
Debug the actual cleaning process
"""

import re

def test_cleaning():
    # Simulate the actual response we're getting
    response_content = """<think>
Okay, so I need to classify this log message into one of the given categories. The log message is: "[LegacyCRM] Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active (test 1726286957)'"""
    
    print("Original response:")
    print(f"'{response_content}'")
    print(f"Length: {len(response_content)}")
    print()
    
    # Apply the NEW cleaning logic
    original_content = response_content
    
    # First, remove complete thinking blocks
    response_content = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL)
    
    print("After removing complete thinking blocks:")
    print(f"'{response_content}'")
    print(f"Length: {len(response_content.strip())}")
    print()
    
    # If no complete blocks were removed but we still have <think>, remove incomplete blocks
    if '<think>' in response_content:
        print("✅ Found incomplete thinking block, removing everything after <think>")
        response_content = re.sub(r'<think>.*', '', response_content, flags=re.DOTALL)
        print(f"After removing incomplete block: '{response_content}'")
        print(f"Length: {len(response_content.strip())}")
        print()
    
    # Check condition
    if len(response_content.strip()) < 10:
        print("✅ Condition met: Response is short, extracting from thinking")
        thinking_content = original_content.lower()
        
        if ('fail' in thinking_content or 'error' in thinking_content) and ('case' in thinking_content or 'escalation' in thinking_content):
            extracted = "1. workflow_error"
            print(f"✅ Extracted: {extracted}")
        else:
            extracted = "1. unclassified"
            print(f"❌ No match: {extracted}")
    else:
        print("❌ Condition NOT met: Response still has content")
        print("Continuing with normal processing...")

if __name__ == "__main__":
    test_cleaning()