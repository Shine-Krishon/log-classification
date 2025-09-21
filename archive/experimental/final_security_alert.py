#!/usr/bin/env python3
"""
Script to add one final security alert to reach 100 total
"""

import pandas as pd

# Read the current dataset
df = pd.read_csv('logs_chunk1.csv')

# Find one more authentication timeout entry
auth_timeout_indices = df[df['log_message'] == 'Service timeout: authentication unreachable'].index.tolist()

if len(auth_timeout_indices) > 0:
    # Replace one more with a security alert
    idx = auth_timeout_indices[0]
    df.loc[idx, 'log_message'] = 'Advanced persistent threat (APT) activity detected'
    df.loc[idx, 'target_label'] = 'security_alert'
    df.loc[idx, 'complexity'] = 'llm'
    
    # Save the updated dataset
    df.to_csv('logs_chunk1.csv', index=False)
    
    print("Added final security alert")
else:
    print("No more authentication timeout entries available")

# Show the final counts
print("\nFinal target label counts:")
print(df['target_label'].value_counts())