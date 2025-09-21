import pandas as pd

# Load the enhanced dataset
df = pd.read_csv('data/training/dataset/enhanced_synthetic_logs.csv')

print(f"Dataset size: {len(df)}")
print(f"\nCategory distribution:")
print(df['target_label'].value_counts())

print(f"\nSamples per category:")
for cat in df['target_label'].unique():
    count = len(df[df['target_label'] == cat])
    print(f"{cat}: {count} samples")

print(f"\nComplexity distribution:")
if 'complexity' in df.columns:
    print(df['complexity'].value_counts())

# Check for data quality indicators
print(f"\nData quality check:")
print(f"Unique log messages: {df['log_message'].nunique()}")
print(f"Average message length: {df['log_message'].str.len().mean():.1f} characters")
print(f"Min message length: {df['log_message'].str.len().min()}")
print(f"Max message length: {df['log_message'].str.len().max()}")