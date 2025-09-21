import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample
import re
import random

def fine_tune_dataset():
    """
    Fine-tune the dataset to improve quality and balance
    """
    print("=== Loading Dataset ===")
    df = pd.read_csv('logs_chunk1.csv')
    print(f"Original dataset size: {len(df)}")
    
    # 1. Remove duplicates while keeping one copy
    print("\n=== Removing Duplicates ===")
    print(f"Duplicates before: {df.duplicated().sum()}")
    df_unique = df.drop_duplicates()
    print(f"Dataset size after removing duplicates: {len(df_unique)}")
    
    # 2. Create expanded dataset with variations
    print("\n=== Creating Message Variations ===")
    
    def create_variations(message, complexity, category):
        variations = [message]
        
        # Generate variations based on complexity
        if complexity == 'regex':
            # Simple pattern substitutions
            variations.extend([
                message.replace('user', 'client').replace('User', 'Client'),
                message.replace('failed', 'unsuccessful').replace('error', 'issue'),
                message.replace('successfully', 'completed').replace('started', 'initiated')
            ])
        
        elif complexity == 'bert':
            # More complex semantic variations
            substitutions = {
                'administrator': 'admin',
                'configuration': 'config',
                'application': 'app',
                'database': 'db',
                'connection': 'conn',
                'authentication': 'auth',
                'authorization': 'authz',
                'performance': 'perf'
            }
            for old, new in substitutions.items():
                if old in message.lower():
                    variations.append(message.replace(old, new).replace(old.title(), new.title()))
        
        elif complexity == 'llm':
            # Semantic paraphrasing
            paraphrases = {
                'deprecated': 'obsolete',
                'warning': 'alert',
                'method': 'function',
                'instead': 'alternatively',
                'failed': 'was unsuccessful',
                'successful': 'completed successfully'
            }
            for old, new in paraphrases.items():
                if old in message.lower():
                    variations.append(message.replace(old, new).replace(old.title(), new.title()))
        
        # Remove duplicates and original
        variations = list(set(variations))
        if len(variations) > 3:
            variations = variations[:3]  # Limit variations
        
        return variations
    
    # Generate expanded dataset
    expanded_data = []
    for _, row in df_unique.iterrows():
        variations = create_variations(row['log_message'], row['complexity'], row['target_label'])
        for variation in variations:
            expanded_data.append({
                'log_message': variation,
                'target_label': row['target_label'],
                'complexity': row['complexity']
            })
    
    df_expanded = pd.DataFrame(expanded_data)
    print(f"Expanded dataset size: {len(df_expanded)}")
    
    # 3. Balance complexity distribution
    print("\n=== Balancing Complexity Distribution ===")
    
    # Current distribution
    complexity_counts = df_expanded['complexity'].value_counts()
    print("Current complexity distribution:")
    print(complexity_counts)
    
    # Target: more balanced distribution
    target_size = min(complexity_counts) * 1.5  # Use 1.5x the smallest group
    target_size = int(target_size)
    
    balanced_data = []
    for complexity in df_expanded['complexity'].unique():
        complexity_data = df_expanded[df_expanded['complexity'] == complexity]
        
        if len(complexity_data) > target_size:
            # Downsample
            complexity_data = resample(complexity_data, n_samples=target_size, random_state=42)
        elif len(complexity_data) < target_size:
            # Upsample
            complexity_data = resample(complexity_data, n_samples=target_size, random_state=42, replace=True)
        
        balanced_data.append(complexity_data)
    
    df_balanced = pd.concat(balanced_data, ignore_index=True)
    print(f"Balanced dataset size: {len(df_balanced)}")
    print("New complexity distribution:")
    print(df_balanced['complexity'].value_counts())
    
    # 4. Add synthetic high-quality examples
    print("\n=== Adding Synthetic Examples ===")
    
    synthetic_examples = {
        'system_notification': [
            ('Service mesh deployment completed: 127 pods scheduled across 3 nodes', 'llm'),
            ('Database connection pool exhausted: max 50 connections reached', 'bert'),
            ('Memory usage: 1.2GB allocated, GC triggered', 'regex'),
            ('API rate limit exceeded: 1000 requests per minute', 'bert'),
            ('SSL certificate expires in 30 days: auto-renewal scheduled', 'llm')
        ],
        'workflow_error': [
            ('Kubernetes pod eviction: node pressure memory threshold exceeded', 'llm'),
            ('Payment gateway timeout: transaction rollback initiated', 'bert'),
            ('Data validation error: schema mismatch in field user_id', 'bert'),
            ('Circuit breaker opened: downstream service unresponsive', 'llm'),
            ('File upload failed: size exceeds 10MB limit', 'regex')
        ],
        'user_action': [
            ('OAuth2 token refresh: session extended for user sarah.connor', 'bert'),
            ('Profile picture updated: 2.1MB JPEG uploaded', 'regex'),
            ('Password policy violation: minimum 12 characters required', 'bert'),
            ('Multi-factor authentication bypass attempted: security alert', 'llm'),
            ('Account lockout triggered: 5 failed login attempts', 'regex')
        ],
        'deprecation_warning': [
            ('Legacy API endpoint /v1/users deprecated: migrate to /v2/users by Q4', 'llm'),
            ('Function getUserById() marked deprecated: use UserService.findById()', 'bert'),
            ('XML configuration support ending: switch to YAML format', 'bert'),
            ('Python 3.8 support dropped: upgrade to 3.9+ required', 'llm'),
            ('HTTP/1.1 deprecated: HTTP/2 mandatory from next release', 'llm')
        ],
        'unclassified': [
            ('Anomalous network traffic detected: investigating pattern', 'llm'),
            ('Unexpected process termination: PID 12345 exit code 139', 'bert'),
            ('Custom event handler triggered: processing queue depth 47', 'bert'),
            ('Legacy module loaded: compatibility mode activated', 'bert'),
            ('Unknown error state: manual intervention required', 'regex')
        ]
    }
    
    synthetic_data = []
    for category, examples in synthetic_examples.items():
        for message, complexity in examples:
            synthetic_data.append({
                'log_message': message,
                'target_label': category,
                'complexity': complexity
            })
    
    df_synthetic = pd.DataFrame(synthetic_data)
    df_final = pd.concat([df_balanced, df_synthetic], ignore_index=True)
    
    print(f"Final dataset size: {len(df_final)}")
    
    # 5. Final statistics
    print("\n=== Final Dataset Statistics ===")
    print("Category distribution:")
    print(df_final['target_label'].value_counts())
    print("\nComplexity distribution:")
    print(df_final['complexity'].value_counts())
    
    # Check uniqueness
    unique_messages = df_final['log_message'].nunique()
    print(f"\nUnique messages: {unique_messages}")
    print(f"Uniqueness ratio: {unique_messages/len(df_final)*100:.1f}%")
    
    # Message length statistics
    df_final['message_length'] = df_final['log_message'].str.len()
    print(f"\nMessage length stats:")
    print(f"Average: {df_final['message_length'].mean():.1f}")
    print(f"Median: {df_final['message_length'].median():.1f}")
    print(f"Range: {df_final['message_length'].min()} - {df_final['message_length'].max()}")
    
    # 6. Split into train/validation/test sets
    print("\n=== Creating Train/Validation/Test Splits ===")
    
    # Stratified split to maintain class balance
    train_data, temp_data = train_test_split(
        df_final, test_size=0.3, random_state=42, 
        stratify=df_final[['target_label', 'complexity']]
    )
    
    val_data, test_data = train_test_split(
        temp_data, test_size=0.5, random_state=42,
        stratify=temp_data[['target_label', 'complexity']]
    )
    
    print(f"Train set: {len(train_data)} samples ({len(train_data)/len(df_final)*100:.1f}%)")
    print(f"Validation set: {len(val_data)} samples ({len(val_data)/len(df_final)*100:.1f}%)")
    print(f"Test set: {len(test_data)} samples ({len(test_data)/len(df_final)*100:.1f}%)")
    
    # 7. Save improved datasets
    print("\n=== Saving Improved Datasets ===")
    df_final.to_csv('logs_chunk1_improved.csv', index=False)
    train_data.to_csv('train_set.csv', index=False)
    val_data.to_csv('validation_set.csv', index=False)
    test_data.to_csv('test_set.csv', index=False)
    
    print("Files saved:")
    print("- logs_chunk1_improved.csv (complete improved dataset)")
    print("- train_set.csv (training data)")
    print("- validation_set.csv (validation data)")  
    print("- test_set.csv (test data)")
    
    return df_final, train_data, val_data, test_data

if __name__ == "__main__":
    df_final, train_data, val_data, test_data = fine_tune_dataset()