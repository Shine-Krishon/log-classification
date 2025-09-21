#!/usr/bin/env python3
"""
Test with fresh LLM call (no cache)
"""

import logging
import time
from src.processors.processor_llm import get_groq_client
from src.core.config import config

# Set up verbose logging
logging.basicConfig(level=logging.INFO)

def test_fresh_llm():
    print("🔍 Testing Fresh LLM Call (No Cache)")
    print("=" * 50)
    
    client = get_groq_client()
    if not client:
        print("❌ Groq client not available")
        return
    
    # Add timestamp to avoid cache
    test_logs = [
        ("LegacyCRM", f"Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active (test {int(time.time())})")
    ]
    
    # Create prompt
    batch_prompt = """Classify each log message into exactly one category: user_action, system_notification, workflow_error, deprecation_warning, or unclassified.

Log messages:
"""
    
    for i, (source, log_message) in enumerate(test_logs, 1):
        batch_prompt += f"{i}. [{source}] {log_message}\n"
    
    batch_prompt += f"""\nRespond with ONLY a numbered list of exactly {len(test_logs)} classifications (no explanations or thinking):
1. category_name
... (continue for all {len(test_logs)} logs)

Valid categories ONLY: user_action, system_notification, workflow_error, deprecation_warning, security_alert, unclassified

Example response format:
1. workflow_error"""
    
    # Make API call
    response = client.chat.completions.create(
        model=config.llm_model_name,
        messages=[
            {
                "role": "system", 
                "content": "You are a precise log classifier. Output ONLY a numbered list with one category per line. No explanations, no thinking text, just the numbered classifications."
            },
            {
                "role": "user", 
                "content": batch_prompt
            }
        ],
        temperature=0.1,
        max_tokens=50,  # Very limited to force concise response
    )
    
    response_content = response.choices[0].message.content.strip()
    print("Raw Response:")
    print(f"'{response_content}'")
    print()
    
    # Test our new parsing logic
    import re
    
    original_content = response_content
    
    # First, remove complete thinking blocks
    response_content = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL)
    
    # If response is now empty or very short, the thinking block was incomplete
    if len(response_content.strip()) < 10:
        print("⚠️ Response mostly thinking text, extracting from original content")
        thinking_content = original_content.lower()
        
        if 'workflow_error' in thinking_content and ('fail' in thinking_content or 'error' in thinking_content):
            response_content = "1. workflow_error"
            print("✅ Extracted: workflow_error")
        else:
            response_content = "1. unclassified"
            print("❌ No clear classification found")
    else:
        print("✅ Good response, proceeding normally")
    
    print(f"Final response: '{response_content}'")
    
    # Parse final result
    lines = [line.strip() for line in response_content.split('\n') if line.strip()]
    if lines:
        line_clean = re.sub(r'^\d+\.\s*', '', lines[0])
        print(f"Final classification: {line_clean}")
    else:
        print("❌ No classification extracted")

if __name__ == "__main__":
    test_fresh_llm()