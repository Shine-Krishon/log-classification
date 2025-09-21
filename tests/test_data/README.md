# Test Data Suite for Log Classification System

This directory contains comprehensive test datasets designed to validate and stress-test the log classification system across various scenarios and edge cases.

## Test Files Overview

### 📁 Test Data Location
All test CSV files are organized in: `tests/test_data/`

### 🧪 Test Files

#### 1. **small_test.csv** (10 records)
- **Purpose**: Quick functionality verification
- **Content**: Basic log entries from various sources
- **Use Case**: Smoke testing, basic validation
- **Classification Categories**: user_action, security, system_notification, error

#### 2. **medium_test.csv** (100 records)
- **Purpose**: Standard testing with diverse scenarios
- **Content**: Realistic log entries across all major source systems
- **Use Case**: Feature testing, performance baseline
- **Source Systems**: 10 different systems (ModernCRM, BillingSystem, etc.)

#### 3. **large_test.csv** (200+ records)
- **Purpose**: Comprehensive system testing
- **Content**: Extensive real-world scenarios with detailed log messages
- **Use Case**: Integration testing, accuracy validation
- **Categories**: All classification types with rich context

#### 4. **stress_test.csv** (1,000 records)
- **Purpose**: Performance and scalability testing
- **Content**: Randomly generated diverse log entries
- **Use Case**: Load testing, performance optimization
- **Features**: 
  - 22 different source systems
  - 5 classification categories
  - Realistic variability in message patterns

#### 5. **edge_cases_test.csv** (50+ records)
- **Purpose**: Boundary condition and error handling testing
- **Content**: Unusual, problematic, and edge case scenarios
- **Use Case**: Robustness testing, error handling validation
- **Special Cases**:
  - Empty messages and sources
  - Unicode and special characters
  - Very long messages
  - JSON/XML/SQL embedded in logs
  - Control characters and escape sequences
  - Multiple languages and emojis

#### 6. **original_test.csv** (10 records)
- **Purpose**: Original test data for regression testing
- **Content**: The initial test dataset from project development
- **Use Case**: Baseline comparison, regression validation

## 🎯 Testing Scenarios

### Performance Testing
```bash
# Test with different file sizes
Small:    10 records   (~1 KB)
Medium:   100 records  (~10 KB)
Large:    200+ records (~25 KB)
Stress:   1,000 records (~100 KB)
```

### Classification Categories Tested
1. **user_action**: Login/logout, profile changes, file uploads
2. **system_notification**: Backups, updates, maintenance
3. **error**: Failures, timeouts, exceptions
4. **performance**: Metrics, query times, optimization
5. **security**: Authentication, intrusion detection, access control

### Source System Coverage
- **Modern Systems**: ModernCRM, ModernHR, AnalyticsEngine
- **Legacy Systems**: LegacyCRM (special handling required)
- **Infrastructure**: WebServer, DatabaseSystem, SecuritySystem
- **Business Systems**: BillingSystem, PaymentGateway, InventorySystem
- **Communication**: EmailSystem, NotificationSystem
- **Monitoring**: MonitoringSystem, LoggingSystem

## 🚀 Usage Instructions

### Quick Test
```bash
# Upload small_test.csv to test basic functionality
curl -X POST "http://localhost:8000/classify/" \
  -F "file=@tests/test_data/small_test.csv"
```

### Performance Test
```bash
# Upload stress_test.csv to test system performance
curl -X POST "http://localhost:8000/classify/" \
  -F "file=@tests/test_data/stress_test.csv"
```

### Edge Case Validation
```bash
# Upload edge_cases_test.csv to test error handling
curl -X POST "http://localhost:8000/classify/" \
  -F "file=@tests/test_data/edge_cases_test.csv"
```

### Web Interface Testing
1. Start the server: `python main.py`
2. Open: http://localhost:8000
3. Upload test files through the web interface
4. Compare results across different file sizes

## 📊 Expected Results

### Classification Distribution (Approximate)
- **user_action**: 25-30%
- **system_notification**: 20-25%
- **error**: 15-20%
- **security**: 15-20%
- **performance**: 10-15%
- **unclassified**: <5%

### Performance Benchmarks
- **Small test**: <1 second processing
- **Medium test**: <5 seconds processing
- **Large test**: <15 seconds processing
- **Stress test**: <60 seconds processing

### Edge Case Handling
- **Empty records**: Should be handled gracefully
- **Unicode content**: Should be processed correctly
- **Large messages**: Should not cause crashes
- **Special characters**: Should be sanitized appropriately

## 🔧 Troubleshooting

### Common Issues
1. **File format errors**: Ensure CSV has proper headers (source, log_message)
2. **Encoding issues**: Files are UTF-8 encoded
3. **Performance degradation**: Check system resources during stress testing
4. **Classification accuracy**: Compare with manual classification samples

### Validation Steps
1. Check file upload success
2. Verify classification completion
3. Review performance metrics
4. Validate output format
5. Check for error logs

## 📈 Test Results Analysis

### Metrics to Monitor
- **Processing speed**: Records per second
- **Memory usage**: Peak and average consumption
- **Accuracy**: Manual validation sampling
- **Error rate**: Failed classifications
- **Response times**: API endpoint performance

### Success Criteria
- ✅ All test files process without errors
- ✅ Performance within acceptable limits
- ✅ Edge cases handled gracefully
- ✅ Classification accuracy >85%
- ✅ No memory leaks or crashes

---

**Note**: These test files provide comprehensive coverage for validating the log classification system's functionality, performance, and robustness across various real-world scenarios.