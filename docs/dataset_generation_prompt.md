# Log Classification Dataset Generation Prompt

## Task Overview
Generate a comprehensive synthetic dataset for training a BERT-based log classification system. The dataset should contain realistic business application log messages across 5 categories with high diversity and quality.

## Dataset Requirements

### Target Size: 40,000 total samples
- **system_notification**: 8,000 samples
- **workflow_error**: 8,000 samples  
- **user_action**: 8,000 samples
- **deprecation_warning**: 8,000 samples
- **unclassified**: 8,000 samples

### Output Format
CSV file with columns: `log_message,target_label,complexity`

### Complexity Distribution (for hybrid classification system):
- **regex** (40%): Simple, pattern-based logs that can be caught by regex rules
- **bert** (50%): Medium complexity requiring semantic understanding
- **llm** (10%): Complex, ambiguous logs requiring advanced reasoning

## Category Definitions & Examples

### 1. system_notification (6,000 samples)
**Purpose**: System status, health checks, startup/shutdown events, configuration changes
**Characteristics**: Informational, automated system events
**Examples**:
- "Application started successfully on port 8080"
- "Database connection pool initialized with 20 connections"
- "Configuration file config.yaml reloaded"
- "Scheduled backup completed successfully"
- "Memory usage: 75% of available heap"

### 2. workflow_error (6,000 samples)
**Purpose**: Business process failures, validation errors, workflow interruptions
**Characteristics**: Process-specific failures that impact business operations
**Examples**:
- "Payment processing failed: insufficient funds for order #12345"
- "Document validation failed: missing required field 'customer_id'"
- "Workflow timeout: approval process exceeded 24 hour limit"
- "Data import failed: duplicate record found in line 1247"
- "API rate limit exceeded for client xyz-corp"

### 3. user_action (6,000 samples)
**Purpose**: User interactions, authentication, user-initiated operations
**Characteristics**: Human-triggered events and user behavior tracking
**Examples**:
- "User john.doe logged in from IP 192.168.1.100"
- "Password changed for user alice.smith"
- "File upload completed: document.pdf (2.3MB)"
- "User admin created new project 'Q4-Analytics'"
- "Profile updated for user ID 98765"

### 4. deprecation_warning (4,000 samples)
**Purpose**: Deprecated API usage, outdated configurations, legacy system warnings
**Characteristics**: Warnings about future breaking changes or outdated practices
**Examples**:
- "API endpoint /v1/users is deprecated, use /v2/users instead"
- "Configuration option 'legacy_mode' will be removed in version 3.0"
- "Method calculateTax() is deprecated since version 2.1"
- "Database driver mysql-connector-5.x is deprecated"
- "SSL protocol TLSv1.1 is deprecated, upgrade to TLSv1.3"

### 5. unclassified (3,000 samples)
**Purpose**: Logs that don't fit clear categories, ambiguous or mixed-purpose messages
**Characteristics**: Edge cases, unclear context, or multi-purpose logs
**Examples**:
- "Process completed"
- "Status: OK"
- "Event triggered"
- "External service response received"
- "Timer expired"

## Generation Guidelines

### Diversity Requirements:
1. **Vary log formats**: Structured, semi-structured, and free-form messages
2. **Include timestamps**: Different formats (ISO, Unix, custom)
3. **Use realistic data**: 
   - User IDs: john.doe, alice.smith, admin, user123, etc.
   - IP addresses: Mix of internal (192.168.x.x, 10.x.x.x) and external
   - File names: document.pdf, report.xlsx, config.yaml, etc.
   - Error codes: HTTP status codes, custom error codes (ERR001, FAIL_AUTH, etc.)
   - Quantities: File sizes, counts, percentages, durations

### Technical Patterns:
1. **Include common log patterns**:
   - HTTP request/response logs
   - Database operation logs
   - File system operations
   - Network events
   - Security events
   - Performance metrics

2. **Vary complexity levels**:
   - **Simple regex patterns**: Clear keywords, consistent format
   - **BERT-suitable**: Semantic meaning, context-dependent
   - **LLM-required**: Ambiguous, requires reasoning, complex context

### Quality Requirements:
1. **Minimize duplication**: Ensure high uniqueness ratio (>90%)
2. **Realistic length**: 20-100 characters per log message
3. **Proper categorization**: Each log should clearly belong to its assigned category
4. **Business context**: Use realistic business scenarios (e-commerce, SaaS, enterprise)

## Example Output Format:
```csv
log_message,target_label,complexity
"Application server started on port 8080",system_notification,regex
"User authentication failed for john.doe from IP 203.0.113.15",user_action,bert
"Payment gateway timeout during transaction processing",workflow_error,bert
"Legacy API endpoint /v1/auth will be deprecated in Q2 2026",deprecation_warning,bert
"Operation completed with status 200",unclassified,llm
```

## Instructions for LLM:
1. Generate exactly 40,000 unique log messages following the distribution above
2. Ensure each message is realistic and would actually appear in business application logs  
3. Maintain high diversity - avoid repetitive patterns
4. Assign appropriate complexity levels based on how easily each log could be classified
5. Use proper CSV escaping for any messages containing commas or quotes
6. Focus on practical, real-world scenarios that a business application would encounter

## Validation Checklist:
- [ ] Total count: 40,000 samples
- [ ] Category distribution matches requirements
- [ ] Complexity distribution: ~40% regex, ~50% bert, ~10% llm
- [ ] High uniqueness ratio (>90% unique messages)
- [ ] Realistic business log patterns
- [ ] Proper CSV formatting