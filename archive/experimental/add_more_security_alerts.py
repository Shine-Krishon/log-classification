#!/usr/bin/env python3
"""
Script to add more security alert logs by replacing additional authentication timeout entries
"""

import pandas as pd
import random

# Read the current dataset
df = pd.read_csv('logs_chunk1.csv')

# Additional security alert messages
additional_security_messages = [
    "Multi-factor authentication bypass attempt detected",
    "Session token hijacking detected for user session",
    "Cross-site request forgery (CSRF) attack blocked",
    "Directory traversal attack attempt detected",
    "Command injection attempt in system call",
    "XML external entity (XXE) attack detected",
    "Server-side request forgery (SSRF) attempt blocked",
    "Local file inclusion (LFI) attack detected",
    "Remote file inclusion (RFI) attack blocked",
    "HTTP header injection attack detected",
    "NoSQL injection attempt detected in database query",
    "LDAP injection attack blocked",
    "Email header injection attempt detected",
    "Host header injection attack blocked",
    "Business logic flaw exploitation detected",
    "Race condition attack attempt detected",
    "Clickjacking attack blocked by security headers",
    "Open redirect vulnerability exploitation detected",
    "Server misconfiguration exploitation attempt",
    "Insecure direct object reference attack detected",
    "Privilege escalation attempt through API",
    "Authentication bypass through parameter pollution",
    "Deserialization attack detected in user input",
    "Template injection attack blocked",
    "Expression language injection detected",
    "Path traversal attack through file upload",
    "Weak random number generation exploitation",
    "Timing attack detected on authentication system",
    "Side-channel attack attempt detected",
    "Cache poisoning attack detected",
    "DNS cache poisoning attempt blocked",
    "ARP spoofing attack detected on network",
    "DHCP spoofing attack detected",
    "BGP hijacking attempt detected",
    "SSL strip attack detected and blocked",
    "Downgrade attack on TLS connection detected",
    "Heartbleed vulnerability exploitation attempt",
    "Shellshock exploit attempt detected",
    "EternalBlue exploit attempt blocked",
    "WannaCry ransomware signature detected"
]

# Complexity levels for security alerts
complexity_levels = ['regex', 'bert', 'llm']

# Find remaining authentication timeout entries
auth_timeout_indices = df[df['log_message'] == 'Service timeout: authentication unreachable'].index.tolist()

print(f"Found {len(auth_timeout_indices)} remaining authentication timeout entries")

# Replace 30 more of them with security alerts
replacements_to_make = min(30, len(auth_timeout_indices))
if replacements_to_make > 0:
    selected_indices = random.sample(auth_timeout_indices, replacements_to_make)

    print(f"Replacing {replacements_to_make} more entries with security alerts")

    for i, idx in enumerate(selected_indices):
        security_msg = additional_security_messages[i % len(additional_security_messages)]
        complexity = random.choice(complexity_levels)
        
        df.loc[idx, 'log_message'] = security_msg
        df.loc[idx, 'target_label'] = 'security_alert'
        df.loc[idx, 'complexity'] = complexity

    # Save the updated dataset
    df.to_csv('logs_chunk1.csv', index=False)

    print(f"\nReplaced {replacements_to_make} more authentication timeout entries with security alerts")
else:
    print("No more authentication timeout entries to replace")

# Show the updated counts
print("\nFinal target label counts:")
print(df['target_label'].value_counts())

# Show some examples of the security alerts we added
print("\nSample security alerts added:")
security_alerts = df[df['target_label'] == 'security_alert']['log_message'].unique()
for i, alert in enumerate(security_alerts[:10]):
    print(f"{i+1}. {alert}")
    
print(f"... and {len(security_alerts) - 10} more security alert types")