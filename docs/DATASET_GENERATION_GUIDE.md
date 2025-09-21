# 20,000 SAMPLE DATASET GENERATION GUIDE

## 🎯 OPTIMIZED APPROACH: 20,000 High-Quality Samples

### Quick Strategy Options:

#### **Option 1: Single Generation (RECOMMENDED)**
- **Target**: 20,000 samples in one go
- **Time**: 2-4 hours
- **Success Rate**: High (most LLMs can handle this)
- **Effort**: Low

#### **Option 2: Batch Generation (if single fails)**
- **Target**: 4 batches of 5,000 samples each
- **Time**: 4-6 hours total
- **Success Rate**: Very High
- **Effort**: Medium

## 📋 BATCH GENERATION INSTRUCTIONS (if needed)

### Batch 1: Generate 5,000 samples
```
Categories: 1,000 each of system_notification, workflow_error, user_action, deprecation_warning, unclassified
Focus: Core business scenarios, clear examples
```

### Batch 2: Generate 5,000 samples
```
Categories: 1,000 each (same distribution)
Focus: E-commerce and SaaS scenarios
```

### Batch 3: Generate 5,000 samples
```
Categories: 1,000 each (same distribution)
Focus: Enterprise and financial services
```

### Batch 4: Generate 5,000 samples
```
Categories: 1,000 each (same distribution)
Focus: DevOps and technical operations
```

## 🔧 COMBINING BATCHES (if using batch approach)

### Step 1: Validate Each Batch
```python
import pandas as pd

# Check each batch
for i in range(1, 5):
    df = pd.read_csv(f'batch_{i}.csv')
    print(f"Batch {i}: {len(df)} samples")
    print(df['target_label'].value_counts())
    print(f"Unique messages: {df['log_message'].nunique()}")
    print()
```

### Step 2: Combine and Deduplicate
```python
# Combine all batches
all_batches = []
for i in range(1, 5):
    df = pd.read_csv(f'batch_{i}.csv')
    all_batches.append(df)

# Combine
final_dataset = pd.concat(all_batches, ignore_index=True)

# Remove duplicates
final_dataset = final_dataset.drop_duplicates(subset=['log_message'])

# Shuffle
final_dataset = final_dataset.sample(frac=1).reset_index(drop=True)

# Save
final_dataset.to_csv('enhanced_synthetic_logs_20k.csv', index=False)

print(f"Final dataset: {len(final_dataset)} samples")
print(final_dataset['target_label'].value_counts())
```

## ✅ EXPECTED RESULTS WITH 20,000 SAMPLES

### Performance Improvements:
- **Current Accuracy**: ~59%
- **Expected Accuracy**: 85-90%
- **BERT Coverage**: 60-70% (vs current 20%)
- **LLM Usage**: 15-25% (vs current 40%)

### System Benefits:
- **Faster Response Times**: More BERT, less LLM
- **Lower Costs**: Reduced LLM API calls
- **Better Accuracy**: Comprehensive training data
- **Edge Case Handling**: Unclassified category

## 🚀 NEXT STEPS AFTER GENERATION

1. **Save Dataset**: `enhanced_synthetic_logs_20k.csv`
2. **Train Model**: Use `train_enhanced_model.py`
3. **Test Performance**: Against medium test files
4. **Validate Results**: Check accuracy improvements
5. **Deploy**: If satisfied, or expand if needed

## 📊 SUCCESS METRICS TO WATCH

### Training Metrics:
- **Dataset size**: 20,000 samples
- **Category balance**: 4,000 each
- **Uniqueness**: >95%
- **Training time**: 1-2 hours

### Performance Metrics:
- **Overall accuracy**: 85-90%
- **BERT precision/recall**: >90% per category
- **Response time**: <3 seconds maintained
- **Edge case handling**: Robust unclassified detection

## 💡 EXPANSION PLAN (if needed later)

If 20,000 samples achieve 85-87% accuracy but you want 90%+:

1. **Generate 20,000 more samples** (same prompt)
2. **Focus on difficult cases** that current model misses
3. **Add domain-specific patterns** based on your logs
4. **Retrain with 40,000 total samples**

The 20,000 sample approach gives you immediate, significant improvements with the option to expand based on actual performance testing!