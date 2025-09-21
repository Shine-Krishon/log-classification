#!/usr/bin/env python3
"""
Direct test of LLM response to debug the issue
"""

from src.processors.processor_llm import get_groq_client
from src.core.config import config

def test_llm_response():
    print("🔍 Testing Raw LLM Response")
    print("=" * 50)
    
    client = get_groq_client()
    if not client:
        print("❌ Groq client not available")
        return
    
    test_logs = [
        ("LegacyCRM", "Case escalation for ticket ID 7324 failed because the assigned support agent is no longer active")
    ]
    
    # Create prompt similar to the actual implementation
    batch_prompt = """Classify each log message into exactly one category: user_action, system_notification, workflow_error, deprecation_warning, or unclassified.

Log messages:
"""
    
    for i, (source, log_message) in enumerate(test_logs, 1):
        batch_prompt += f"{i}. [{source}] {log_message}\n"
    
    batch_prompt += f"""\nRespond with ONLY a numbered list of exactly {len(test_logs)} classifications (no explanations or thinking):
1. category_name
2. category_name
... (continue for all {len(test_logs)} logs)

Valid categories ONLY: user_action, system_notification, workflow_error, deprecation_warning, security_alert, unclassified

Example response format:
1. workflow_error
2. user_action
3. system_notification"""
    
    print("Prompt:")
    print(batch_prompt)
    print("\n" + "="*50)
    
    # Make API call
    try:
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
            max_tokens=200,
        )
        
        response_content = response.choices[0].message.content.strip()
        print("Raw Response:")
        print(response_content)
        print("\n" + "="*50)
        
        # Test parsing
        import re
        response_content = re.sub(r'<think>.*?</think>', '', response_content, flags=re.DOTALL)
        response_content = response_content.strip()
        
        lines = [line.strip() for line in response_content.split('\n') if line.strip()]
        print("Parsed Lines:")
        for i, line in enumerate(lines):
            print(f"  {i}: '{line}'")
        
        classifications = []
        valid_classifications = {'user_action', 'system_notification', 'workflow_error', 'deprecation_warning', 'security_alert', 'unclassified'}
        
        for line in lines:
            line_clean = line.strip()
            line_clean = re.sub(r'^\d+\.\s*', '', line_clean)
            line_clean = line_clean.strip()
            
            print(f"Processing: '{line_clean}'")
            
            if line_clean in valid_classifications:
                classifications.append(line_clean)
                print(f"  ✅ Valid: {line_clean}")
            else:
                print(f"  ❌ Invalid, trying keywords...")
                if 'fail' in line_clean.lower() or 'error' in line_clean.lower():
                    classifications.append("workflow_error")
                    print(f"  ✅ Keyword match: workflow_error")
                else:
                    classifications.append("unclassified")
                    print(f"  ❌ No match: unclassified")
        
        print(f"\nFinal classifications: {classifications}")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_llm_response()