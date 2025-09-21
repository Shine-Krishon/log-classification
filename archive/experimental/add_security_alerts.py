#!/usr/bin/env python3
"""
Script to add security alert entries to the log classification dataset.
This script will replace some existing workflow_error entries with security_alert entries
to create a balanced dataset with around 500 security alerts.
"""

import pandas as pd
import re
import random

def main():
    # Read the current dataset
    df = pd.read_csv('logs_chunk1.csv')
    
    print("Original distribution:")
    print(df['target_label'].value_counts())
    
    # Define various security alert log messages
    security_alerts = [
        # Authentication & Access Control
        "Failed login attempt for user admin from IP {ip}",
        "Multiple failed login attempts detected for user {user}",
        "Unauthorized access attempt detected from IP {ip}",
        "Account lockout triggered after 5 failed login attempts",
        "Privileged user login from unusual location: {location}",
        "Session hijacking attempt detected for user {user}",
        "Invalid authentication token detected from IP {ip}",
        "Brute force attack detected against user {user}",
        "Password policy violation: weak password detected",
        "Suspicious login pattern detected for user {user}",
        
        # Network Security
        "Blocked IP {ip} after detecting brute force attack",
        "DDoS attack detected from multiple IPs",
        "Port scan detected from IP {ip}",
        "Firewall blocked suspicious traffic from {ip}",
        "Network intrusion attempt from IP {ip}",
        "Malicious traffic pattern detected",
        "Unusual network activity from internal IP {ip}",
        "VPN connection from blacklisted IP {ip}",
        "Network flooding detected from {ip}",
        "Suspicious outbound connection to {ip}",
        
        # Application Security
        "SQL injection attempt detected in user input",
        "Cross-site scripting attempt detected in request",
        "Buffer overflow attempt detected",
        "Command injection attempt blocked",
        "Path traversal attack detected",
        "File inclusion vulnerability exploited",
        "CSRF attack attempt detected",
        "XML external entity attack blocked",
        "Deserialization attack attempt detected",
        "LDAP injection attempt blocked",
        
        # Data Security
        "Potential data exfiltration detected: large file download",
        "Sensitive data access from unauthorized location",
        "Unusual data export activity detected",
        "Unauthorized database access attempt",
        "Data breach indicator: mass data access",
        "Suspicious file access pattern detected",
        "Encrypted file decryption attempt failed",
        "Database privilege escalation attempt",
        "Sensitive table access without authorization",
        "Data masking policy violation detected",
        
        # Malware & Threats
        "Malicious file upload detected: virus signature found",
        "Ransomware activity detected on system",
        "Trojan horse detected in uploaded file",
        "Phishing attempt detected in email content",
        "Spyware behavior detected on endpoint",
        "Botnet communication detected",
        "Malware sandbox escape attempt",
        "Rootkit activity detected on system",
        "Keylogger activity detected",
        "Cryptocurrency miner detected",
        
        # System Security
        "Suspicious activity: User privilege escalation attempt detected",
        "Unauthorized system configuration change",
        "Critical system file modification detected",
        "Suspicious process execution detected",
        "System integrity check failed",
        "Unauthorized service installation attempt",
        "Registry modification attack detected",
        "Kernel-level attack attempt blocked",
        "Memory corruption attack detected",
        "Sandbox breakout attempt detected",
        
        # Insider Threats
        "Employee accessing sensitive data outside work hours",
        "Unusual file deletion pattern detected",
        "Mass email forwarding to external addresses",
        "Suspicious USB device activity detected",
        "Unauthorized software installation attempt",
        "Data copying to unauthorized storage detected",
        "Suspicious remote access session",
        "Off-hours database access from employee account",
        "Bulk user account creation detected",
        "Administrative privilege abuse detected",
        
        # Advanced Threats
        "Advanced persistent threat indicators detected",
        "Zero-day exploit attempt blocked by IDS",
        "Supply chain attack: compromised software detected",
        "Container escape attempt detected",
        "Machine learning model poisoning attempt",
        "IoT device compromise: unusual communication pattern",
        "Sandbox evasion technique detected in attachment",
        "Critical system file tampering detected",
        "Deepfake content detected in video upload",
        "AI-powered social engineering attempt detected",
        "Biometric spoofing attempt detected",
        "Voice phishing (vishing) call detected",
        "Smart contract exploit attempt on blockchain",
        "Edge computing security violation detected",
        "Federated learning model compromise detected"
    ]
    
    # IP addresses for placeholders
    suspicious_ips = [
        "192.168.1.100", "10.0.0.5", "203.0.113.42", "198.51.100.15",
        "172.16.0.50", "10.10.10.10", "192.168.0.200", "203.0.113.100",
        "198.51.100.200", "172.16.255.1", "10.0.0.100", "192.168.1.50",
        "203.0.113.10", "198.51.100.50", "172.16.0.100", "192.168.1.200",
        "10.0.0.200", "172.16.1.1", "203.0.113.50", "198.51.100.100"
    ]
    
    # Usernames for placeholders
    usernames = [
        "admin", "root", "administrator", "guest", "user1", "test",
        "service_account", "backup_user", "operator", "support",
        "webadmin", "dbadmin", "sysadmin", "testuser", "demo"
    ]
    
    # Locations for placeholders
    locations = [
        "Unknown Country", "Tor Network", "China", "Russia", "Nigeria",
        "Romania", "Brazil", "North Korea", "Iran", "Anonymous Proxy",
        "Dark Web", "Suspicious Region", "Blacklisted Country"
    ]
    
    # Complexity levels
    complexities = ["regex", "bert", "llm"]
    
    # Count current security alerts
    current_security_count = len(df[df['target_label'] == 'security_alert'])
    target_security_count = 500
    needed_alerts = target_security_count - current_security_count
    
    print(f"Current security alerts: {current_security_count}")
    print(f"Target security alerts: {target_security_count}")
    print(f"Need to add: {needed_alerts}")
    
    if needed_alerts <= 0:
        print("Already have enough security alerts!")
        return
    
    # Find workflow_error entries that contain "Service timeout: authentication unreachable"
    auth_timeout_mask = (df['target_label'] == 'workflow_error') & \
                       (df['log_message'].str.contains('Service timeout: authentication unreachable', na=False))
    
    auth_timeout_indices = df[auth_timeout_mask].index.tolist()
    print(f"Found {len(auth_timeout_indices)} authentication timeout entries to potentially replace")
    
    # Find other workflow_error entries as backup
    other_workflow_mask = (df['target_label'] == 'workflow_error') & \
                         (~df['log_message'].str.contains('Service timeout: authentication unreachable', na=False))
    
    other_workflow_indices = df[other_workflow_mask].index.tolist()
    print(f"Found {len(other_workflow_indices)} other workflow_error entries available")
    
    # Combine indices to replace
    indices_to_replace = auth_timeout_indices + other_workflow_indices[:max(0, needed_alerts - len(auth_timeout_indices))]
    
    # Limit to the number we actually need
    indices_to_replace = indices_to_replace[:needed_alerts]
    
    print(f"Will replace {len(indices_to_replace)} entries with security alerts")
    
    # Replace entries with security alerts
    for i, idx in enumerate(indices_to_replace):
        # Choose a random security alert template
        alert_template = random.choice(security_alerts)
        
        # Fill in placeholders
        alert_message = alert_template
        if "{ip}" in alert_message:
            alert_message = alert_message.replace("{ip}", random.choice(suspicious_ips))
        if "{user}" in alert_message:
            alert_message = alert_message.replace("{user}", random.choice(usernames))
        if "{location}" in alert_message:
            alert_message = alert_message.replace("{location}", random.choice(locations))
        
        # Choose random complexity
        complexity = random.choice(complexities)
        
        # Update the dataframe
        df.at[idx, 'log_message'] = alert_message
        df.at[idx, 'target_label'] = 'security_alert'
        df.at[idx, 'complexity'] = complexity
        
        if (i + 1) % 50 == 0:
            print(f"Processed {i + 1}/{len(indices_to_replace)} entries...")
    
    print("Final distribution:")
    print(df['target_label'].value_counts())
    
    # Save the updated dataset
    df.to_csv('logs_chunk1.csv', index=False)
    print("Dataset updated successfully!")
    
    # Verify the result
    print("\nVerifying the changes...")
    df_verify = pd.read_csv('logs_chunk1.csv')
    print("Verified distribution:")
    print(df_verify['target_label'].value_counts())

if __name__ == "__main__":
    main()