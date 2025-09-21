import pandas as pd

def check_dataset_quality():
    """Check the quality of the advanced dataset."""
    
    print("🔍 CHECKING ADVANCED DATASET QUALITY")
    print("=" * 50)
    
    # Load the advanced dataset
    df = pd.read_csv('data/training/dataset/advanced_dataset_5000.csv')
    
    print(f"Total records: {len(df)}")
    print(f"Unique messages: {df['log_message'].nunique()}")
    print(f"Uniqueness: {(df['log_message'].nunique() / len(df) * 100):.1f}%")
    
    # Check for duplicates
    duplicates = df.duplicated().sum()
    print(f"Exact duplicates: {duplicates}")
    
    message_duplicates = df.duplicated(subset=['log_message']).sum()
    print(f"Message duplicates: {message_duplicates}")
    
    print("\nLabel distribution:")
    for label, count in df['target_label'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {label}: {count} ({pct:.1f}%)")
    
    print("\nComplexity distribution:")
    for complexity, count in df['complexity'].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {complexity}: {count} ({pct:.1f}%)")
    
    # Check for ModernHR examples
    modernhr_examples = df[df['log_message'].str.contains('ModernHR|HRSystem', case=False, na=False)]
    print(f"\nHR System examples: {len(modernhr_examples)}")
    if len(modernhr_examples) > 0:
        print("HR examples by label:")
        for label, count in modernhr_examples['target_label'].value_counts().items():
            print(f"  {label}: {count}")
    
    # Check balance across labels
    label_counts = df['target_label'].value_counts()
    min_count = label_counts.min()
    max_count = label_counts.max()
    balance_ratio = min_count / max_count
    
    print(f"\nDataset balance:")
    print(f"  Min label count: {min_count}")
    print(f"  Max label count: {max_count}")
    print(f"  Balance ratio: {balance_ratio:.2f} (1.0 = perfect balance)")
    
    # Overall quality assessment
    print(f"\n✅ QUALITY ASSESSMENT:")
    print(f"   Uniqueness: {'✅ Excellent' if df['log_message'].nunique() / len(df) > 0.95 else '⚠️ Needs improvement'}")
    print(f"   Balance: {'✅ Good' if balance_ratio > 0.7 else '⚠️ Imbalanced'}")
    print(f"   Size: {'✅ Adequate' if len(df) > 3000 else '⚠️ Too small'}")
    print(f"   HR Coverage: {'✅ Good' if len(modernhr_examples) > 10 else '⚠️ Limited'}")
    
    return df

if __name__ == "__main__":
    dataset = check_dataset_quality()