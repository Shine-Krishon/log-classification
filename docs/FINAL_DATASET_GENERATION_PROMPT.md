# OPTIMIZED LOG CLASSIFICATION DATASET GENERATION PROMPT

## EXECUTIVE SUMMARY
Generate a high-quality synthetic dataset of 20,000 business log messages for training a production-ready BERT classification system. This dataset will power a hybrid classification pipeline (Regex → BERT → LLM) where BERT needs to handle 60-70% of logs accurately, achieving 85-90% overall accuracy.

## DATASET REQUIREMENTS

### Target Size: 20,000 total samples
- **system_notification**: 4,000 samples
- **workflow_error**: 4,000 samples  
- **user_action**: 4,000 samples
- **deprecation_warning**: 4,000 samples
- **unclassified**: 4,000 samples

### Output Format
CSV file with columns: `log_message,target_label,complexity`

### Complexity Distribution (for hybrid system optimization):
- **regex** (40%): Simple, pattern-based logs catchable by regex rules
- **bert** (50%): Medium complexity requiring semantic understanding
- **llm** (10%): Complex, ambiguous logs requiring advanced reasoning

## CATEGORY DEFINITIONS & REAL-WORLD EXAMPLES

### 1. system_notification (4,000 samples)
**Definition**: Automated system events, health checks, successful operations, status updates
**Characteristics**: Informational, system-generated, operational status
**Business Context**: System monitoring, health checks, successful processes

**Example Patterns**:
```
"Application started successfully on port 8080"
"Database connection pool initialized with 20 connections"
"Scheduled backup completed successfully at 2024-09-14 02:00:00"
"Memory usage: 75% of available heap (6.2GB/8GB)"
"Configuration file config.yaml reloaded successfully"
"Cache cleared: 1,250 entries removed, 45MB freed"
"SSL certificate renewed for domain api.company.com"
"Load balancer health check passed - all 5 nodes healthy"
"ETL pipeline completed: 12,450 records processed in 4.2 minutes"
"API endpoint /v2/users responding normally (avg 145ms)"
```

### 2. workflow_error (4,000 samples)
**Definition**: Business process failures, validation errors, operational issues that impact business functions
**Characteristics**: Process failures, business logic errors, system malfunctions
**Business Context**: Order processing, payment failures, data validation, service disruptions

**Example Patterns**:
```
"Payment processing failed: insufficient funds for order #12345"
"Document validation failed: missing required field 'customer_id'"
"Database connection timeout after 30 seconds"
"API rate limit exceeded for client xyz-corp (150 requests/minute)"
"File upload failed: document.pdf exceeds 10MB limit"
"Email delivery failed: invalid recipient address user@invalid-domain"
"Credit card authorization declined: card expired"
"Data import failed: duplicate record found in line 1247"
"Service timeout: user authentication service unreachable"
"Queue processing failed: message format validation error"
```

### 3. user_action (4,000 samples)
**Definition**: User-initiated activities, authentication events, user interactions with the system
**Characteristics**: Human-triggered events, user behavior tracking, account management
**Business Context**: User sessions, profile management, user-driven operations

**Example Patterns**:
```
"User john.doe@company.com logged in from IP 192.168.1.100"
"Password changed successfully for user ID 12847"
"User admin created new project 'Q4-Analytics-Dashboard'"
"File upload completed: quarterly-report.pdf (2.3MB) by user alice.smith"
"Profile updated: user 78934 changed email from old@domain.com to new@domain.com"
"Two-factor authentication enabled for user account manager.ops"
"User session expired after 30 minutes of inactivity for user temp.user"
"Account locked: 5 failed login attempts for user suspicious.actor"
"Document shared: contract-v2.pdf shared with team-leads@company.com"
"User preferences updated: notification settings changed to email-only"
```

### 4. deprecation_warning (4,000 samples)
**Definition**: Warnings about deprecated features, legacy system alerts, upcoming changes
**Characteristics**: Future-breaking changes, outdated practices, migration notices
**Business Context**: API deprecations, legacy system warnings, upgrade notifications

**Example Patterns**:
```
"API endpoint /v1/users is deprecated, migrate to /v2/users by Dec 2024"
"Legacy authentication module will be sunset in Q2 2025"
"Configuration option 'legacy_mode=true' will be removed in version 3.0"
"Database driver mysql-connector-5.x is deprecated, upgrade to 8.x"
"SSL protocol TLSv1.1 is deprecated, upgrade to TLSv1.3 before Jan 2025"
"Method calculateTax() deprecated since v2.1, use TaxCalculationService instead"
"Report format XML will be discontinued, migrate to JSON by March 2025"
"Legacy email template system deprecated, use new template engine"
"Old file storage API deprecated: migrate to cloud storage service"
"Internet Explorer support ending Dec 2024, update browser requirements"
```

### 5. unclassified (4,000 samples)
**Definition**: Ambiguous messages, generic status updates, messages that don't clearly fit other categories
**Characteristics**: Vague context, multi-purpose messages, unclear business impact
**Business Context**: Generic events, unclear status messages, catch-all scenarios

**Example Patterns**:
```
"Process completed"
"Status: OK"
"Event triggered"
"Operation finished"
"Task done"
"Update available"
"Service ready"
"Request processed"
"Action completed successfully"
"Maintenance window scheduled"
"Performance baseline updated"
"Threshold exceeded"
"Alert cleared"
"Module loaded"
"Connection established"
```

## ADVANCED GENERATION GUIDELINES

### Diversity Requirements:
1. **Realistic Business Scenarios**: E-commerce, SaaS, enterprise applications, financial services
2. **Varied Log Formats**: 
   - Structured: `[2024-09-14 15:30:22] INFO: User login successful`
   - Semi-structured: `User john.doe logged in from 192.168.1.100 at 15:30:22`
   - Free-form: `Login successful for user john.doe`

3. **Technical Authenticity**:
   - **User identifiers**: john.doe, alice.smith, admin, user123, manager.ops, temp.user
   - **IP addresses**: Mix internal (192.168.x.x, 10.x.x.x) and external (203.0.113.x)
   - **File names**: report.pdf, config.yaml, data.csv, image.jpg, backup.zip
   - **Error codes**: HTTP (200, 404, 500), custom (ERR001, FAIL_AUTH, TIMEOUT_001)
   - **Quantities**: File sizes (2.3MB, 150KB), percentages (75%, 95.7%), counts (1,250 records)
   - **Durations**: 4.2 minutes, 30 seconds, 2.5 hours
   - **Versions**: v2.1, 3.0, API v1/v2

### Business Context Patterns:
1. **E-commerce**: Orders, payments, inventory, shipping, customer accounts
2. **SaaS Applications**: Subscriptions, billing, user management, feature usage
3. **Enterprise Systems**: HR, finance, analytics, reporting, compliance
4. **DevOps**: Deployments, monitoring, infrastructure, CI/CD pipelines

### Technical Patterns Include:
1. **Database Operations**: Connections, queries, transactions, backups
2. **API Activities**: Requests, responses, rate limiting, authentication
3. **File Operations**: Uploads, downloads, processing, storage
4. **Network Events**: Connections, timeouts, security, monitoring
5. **System Performance**: Memory, CPU, disk usage, response times

### Quality Standards:
1. **Uniqueness**: >95% unique messages (avoid repetitive patterns)
2. **Realistic Length**: 25-120 characters per message (typical log message range)
3. **Business Relevance**: Each log should represent realistic business application scenarios
4. **Proper Categorization**: Clear assignment to target categories based on business impact

### Complexity Assignment Logic:
- **regex (40%)**: Simple patterns with clear keywords
  - "User {username} logged in"
  - "Backup completed successfully"
  - "Configuration file loaded"
  
- **bert (50%)**: Semantic understanding required
  - "Payment authorization declined due to insufficient account balance"
  - "Document validation failed: missing customer identification data"
  - "Service degradation detected in authentication module"
  
- **llm (10%)**: Complex reasoning or ambiguous context
  - "Process completed with unexpected results requiring manual review"
  - "Event triggered by external system with unclear status"
  - "Operation finished but validation pending"

## SPECIAL CONSIDERATIONS

### Handle Edge Cases Naturally:
- **Empty/minimal logs**: "OK", "Done", "Ready"
- **Technical data**: JSON snippets, SQL fragments, file paths
- **International content**: Unicode characters, different languages
- **Special characters**: Symbols, punctuation, escape sequences
- **Long messages**: Verbose error descriptions, detailed status reports

### Avoid Common Pitfalls:
1. **No template repetition**: Each message should feel organically different
2. **Realistic errors**: Use actual business failure scenarios, not generic "error occurred"
3. **Proper timestamps**: Use realistic business hours and dates
4. **Consistent naming**: User IDs, file names, and domains should feel authentic

## OUTPUT FORMAT EXAMPLE:
```csv
log_message,target_label,complexity
"Application server started successfully on port 8080",system_notification,regex
"Payment processing failed for order #12345: credit card declined",workflow_error,bert
"User alice.smith updated profile settings",user_action,regex
"API endpoint /v1/auth deprecated - migrate to /v2/auth by Q1 2025",deprecation_warning,bert
"Process completed with status: pending review",unclassified,llm
```

## VALIDATION REQUIREMENTS:
- [ ] Total count: exactly 20,000 samples
- [ ] Category distribution: 4,000 samples each
- [ ] Complexity distribution: ~40% regex, ~50% bert, ~10% llm
- [ ] Uniqueness ratio: >95% unique messages
- [ ] Message length: 25-120 characters average
- [ ] Business authenticity: Realistic enterprise scenarios
- [ ] Proper CSV formatting with escaped quotes/commas

## SUCCESS METRICS:
This dataset should enable:
- **85-90% classification accuracy** on business logs
- **BERT handling 60-70%** of logs (reducing LLM dependency)
- **Robust edge case handling** through unclassified category
- **Production-ready performance** for enterprise deployment

Generate exactly 20,000 unique, realistic business log messages that will train an excellent log classification system capable of handling real-world enterprise logging scenarios with high accuracy and robustness.