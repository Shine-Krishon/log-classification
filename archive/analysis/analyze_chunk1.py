import pandas as pd
import numpy as np
from collections import Counter

def analyze_dataset():
    # Read the dataset
    df = pd.read_csv('logs_chunk1.csv')
    
    print("=== Dataset Analysis ===")
    print(f"Total records: {len(df)}")
    print(f"Columns: {list(df.columns)}")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"Duplicate rows: {duplicates}")
    
    # Category distribution
    print("\n=== Category Distribution ===")
    category_counts = df['target_label'].value_counts()
    print(category_counts)
    print(f"Total categories: {len(category_counts)}")
    
    # Complexity distribution
    print("\n=== Complexity Distribution ===")
    complexity_counts = df['complexity'].value_counts()
    print(complexity_counts)
    
    # Cross-tabulation of category and complexity
    print("\n=== Category vs Complexity ===")
    crosstab = pd.crosstab(df['target_label'], df['complexity'])
    print(crosstab)
    
    # Check for missing values
    print("\n=== Missing Values ===")
    print(df.isnull().sum())
    
    # Message length distribution
    print("\n=== Message Length Analysis ===")
    df['message_length'] = df['log_message'].str.len()
    print(f"Average message length: {df['message_length'].mean():.1f}")
    print(f"Median message length: {df['message_length'].median():.1f}")
    print(f"Min message length: {df['message_length'].min()}")
    print(f"Max message length: {df['message_length'].max()}")
    
    # Sample messages by category
    print("\n=== Sample Messages by Category ===")
    for category in df['target_label'].unique():
        sample = df[df['target_label'] == category]['log_message'].iloc[0]
        print(f"{category}: {sample}")
    
    # Check for unique messages
    print("\n=== Uniqueness Analysis ===")
    unique_messages = df['log_message'].nunique()
    print(f"Unique messages: {unique_messages}")
    print(f"Uniqueness ratio: {unique_messages/len(df)*100:.1f}%")
    
    # Check template patterns
    print("\n=== Template Pattern Analysis ===")
    template_messages = df[df['log_message'].str.contains(r'\{.*\}', regex=True)]
    print(f"Messages with templates: {len(template_messages)}")
    print(f"Template ratio: {len(template_messages)/len(df)*100:.1f}%")
    
    return df

if __name__ == "__main__":
    df = analyze_dataset()