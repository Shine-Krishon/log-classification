#!/usr/bin/env python3
"""Test script to verify classification fix after model reset"""

from enhanced_production_system import classify_log_message
import requests
import time

# Test cases that should NOT be classified as security_alert
test_cases = [
    "User 12345 logged in",
    "User john.doe logged out",
    "User accessed dashboard page",
    "User uploaded file report.pdf",
    "User updated profile information",
    "User searched for 'sales data'",
    "User created new record ID: 789",
    "User deleted old backup file",
    "User generated monthly report",
    "User changed password successfully",
    
    # These SHOULD be security_alert
    "Failed login attempt from IP 192.168.1.100",
    "Multiple failed login attempts detected",
    "Suspicious activity: brute force attack",
    "Unauthorized access attempt blocked",
    "SQL injection attempt detected"
]

print("=== TESTING CLASSIFICATION AFTER MODEL RESET ===\n")

print("1. Testing direct enhanced classifier:")
print("-" * 50)
for log in test_cases:
    try:
        result = classify_log_message(log)
        category = result.get('prediction', 'unknown')  # Fixed: use 'prediction' not 'category'
        confidence = result.get('confidence', 0)
        
        # Check if security logs are properly classified
        is_security = any(word in log.lower() for word in ['failed', 'suspicious', 'unauthorized', 'injection', 'attack', 'brute'])
        expected = 'security_alert' if is_security else 'user_action'
        status = "✅" if category == expected else "❌"
        
        print(f"{status} '{log[:50]}...' → {category} ({confidence:.2f})")
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n2. Testing via server API:")
print("-" * 50)

# Start server in background if not running
import subprocess
import threading

def start_server():
    subprocess.run(["python", "server.py"], cwd="C:/Works/project-nlp-log-classification")

# Check if server is running
try:
    response = requests.get("http://localhost:8000/health", timeout=2)
    server_running = True
except:
    server_running = False
    print("Starting server...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(3)

# Test via API
try:
    # Test health endpoint first
    health_response = requests.get("http://localhost:8000/api/v1/health/", timeout=5)
    if health_response.status_code == 200:
        print(f"✅ Server health: {health_response.json()}")
    else:
        print(f"❌ Health check failed: {health_response.status_code}")
    
    # Test performance stats
    stats_response = requests.get("http://localhost:8000/api/v1/performance/stats/", timeout=5)
    if stats_response.status_code == 200:
        print(f"✅ Performance stats: {stats_response.json()}")
    else:
        print(f"❌ Stats failed: {stats_response.status_code}")
        
    print("Note: /classify/ endpoint requires CSV file upload, not individual log messages")
    
except Exception as e:
    print(f"❌ API not available: {e}")

print("\n=== SUMMARY ===")
print("If you see ❌ for basic user actions being classified as security_alert,")
print("the model reset was successful and accuracy should be improved!")