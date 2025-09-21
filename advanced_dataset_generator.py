"""
Advanced Dataset Generator for Log Classification
================================================

This script generates a high-quality, diverse dataset using strategic templates
and variations to create realistic business log messages that will significantly
improve model accuracy while avoiding massive dataset sizes.

Key strategies:
1. Template-based generation with realistic business contexts
2. Domain-specific patterns from real enterprise systems
3. Balanced distribution across all categories
4. Complexity-aware generation (regex/bert/llm appropriate)
5. Edge case coverage for robust classification
"""

import pandas as pd
import numpy as np
import random
import itertools
from datetime import datetime, timedelta
import re

class AdvancedLogDatasetGenerator:
    def __init__(self):
        self.generated_messages = set()  # Track uniqueness
        self.timestamp_base = datetime(2024, 1, 1)
        
        # Business systems and their realistic operations
        self.business_systems = {
            'HR': ['ModernHR', 'HRSystem', 'TalentManager', 'PayrollPro', 'WorkforceOne'],
            'Finance': ['BillingSystem', 'FinanceCore', 'AccountingPro', 'PaymentGateway', 'TaxManager'],
            'CRM': ['SalesforceAPI', 'CRMSystem', 'CustomerPortal', 'LeadManager', 'SupportDesk'],
            'ERP': ['SAPConnector', 'ERPSystem', 'InventoryManager', 'ProcurementAPI', 'SupplyChain'],
            'Infrastructure': ['DatabaseSystem', 'FileSystem', 'BackupService', 'MonitoringSystem', 'LoadBalancer'],
            'Security': ['SecurityCenter', 'FirewallManager', 'VPNGateway', 'AuthService', 'ComplianceBot'],
            'Analytics': ['AnalyticsEngine', 'DataWarehouse', 'ReportingAPI', 'MLPipeline', 'BusinessIntel'],
            'DevOps': ['JenkinsCI', 'DockerRegistry', 'KubernetesAPI', 'GitLabRunner', 'DeploymentBot']
        }
        
        # Employee and business identifiers for realism
        self.identifiers = {
            'employee_ids': [f'EMP{i:04d}' for i in range(1000, 9999, 47)],
            'customer_ids': [f'CUST{i:05d}' for i in range(10000, 99999, 123)],
            'transaction_ids': [f'TXN{i:08d}' for i in range(10000000, 99999999, 12347)],
            'order_ids': [f'ORD{i:06d}' for i in range(100000, 999999, 789)],
            'ticket_ids': [f'TKT{i:05d}' for i in range(10000, 99999, 234)],
            'project_ids': [f'PRJ{i:04d}' for i in range(1000, 9999, 67)],
            'invoice_ids': [f'INV{i:06d}' for i in range(100000, 999999, 456)]
        }
        
        # Business-realistic data values
        self.business_values = {
            'currencies': ['USD', 'EUR', 'GBP', 'CAD', 'AUD'],
            'amounts': [f'{amt:.2f}' for amt in [19.99, 49.99, 99.99, 149.99, 299.99, 499.99, 999.99, 1299.99, 2499.99]],
            'departments': ['Engineering', 'Marketing', 'Sales', 'HR', 'Finance', 'Operations', 'Legal', 'Support'],
            'locations': ['New York', 'London', 'Tokyo', 'Singapore', 'Sydney', 'Toronto', 'Dublin', 'Mumbai'],
            'products': ['Enterprise Suite', 'Professional Plan', 'Premium Service', 'Basic Package', 'Advanced Analytics'],
            'file_types': ['PDF', 'XLSX', 'CSV', 'JSON', 'XML', 'ZIP', 'DOC', 'PPT'],
            'error_codes': ['ERR_001', 'ERR_404', 'ERR_500', 'ERR_503', 'ERR_AUTH', 'ERR_TIMEOUT', 'ERR_LIMIT']
        }

    def generate_timestamp(self):
        """Generate realistic timestamps within business hours."""
        days_offset = random.randint(0, 365)
        hour = random.choice([8, 9, 10, 11, 13, 14, 15, 16, 17])  # Business hours
        minute = random.randint(0, 59)
        timestamp = self.timestamp_base + timedelta(days=days_offset, hours=hour, minutes=minute)
        return timestamp.strftime('%Y-%m-%d %H:%M:%S')

    def get_random_identifier(self, id_type):
        """Get a random business identifier."""
        return random.choice(self.identifiers[id_type])

    def get_random_value(self, value_type):
        """Get a random business value."""
        return random.choice(self.business_values[value_type])

    def generate_user_action_messages(self, count=500):
        """Generate realistic user action messages."""
        templates = [
            # HR Operations
            "Employee {emp_id} onboarding workflow completed successfully",
            "Payroll processing initiated for {dept} department ({count} employees)",
            "Performance review submitted for employee {emp_id}",
            "Leave request approved for {emp_id} from {start_date} to {end_date}",
            "Benefits enrollment completed for employee {emp_id}",
            "Training module '{course}' completed by {emp_id}",
            "Employee profile updated for {emp_id} - contact information",
            "Salary adjustment processed for {emp_id} - promotion to {title}",
            "Time tracking entry submitted by {emp_id} for project {proj_id}",
            "Employee directory synchronization completed",
            
            # Financial Operations  
            "Invoice {inv_id} generated for customer {cust_id} - amount {amount} {currency}",
            "Payment {txn_id} processed successfully - {amount} {currency}",
            "Refund initiated for transaction {txn_id} - amount {amount} {currency}",
            "Subscription renewal processed for customer {cust_id}",
            "Purchase order {order_id} approved by {emp_id}",
            "Expense report submitted by {emp_id} - total {amount} {currency}",
            "Budget allocation updated for {dept} department",
            "Tax calculation completed for invoice {inv_id}",
            "Payment method updated for customer {cust_id}",
            "Billing cycle completed for {count} customers",
            
            # CRM Operations
            "Lead {lead_id} converted to opportunity by {emp_id}",
            "Customer {cust_id} profile updated - contact preferences",
            "Support ticket {ticket_id} created for customer {cust_id}",
            "Sales opportunity {opp_id} marked as won - value {amount} {currency}",
            "Customer survey response recorded for {cust_id}",
            "Email campaign '{campaign}' sent to {count} recipients",
            "Customer meeting scheduled with {cust_id} for {date}",
            "Quote {quote_id} generated for customer {cust_id}",
            "Contract {contract_id} signed by customer {cust_id}",
            "Customer feedback submitted for order {order_id}",
            
            # File Operations
            "Document '{filename}.{ext}' uploaded by {emp_id}",
            "File sharing permissions updated for '{filename}.{ext}'",
            "Bulk file import completed - {count} files processed",
            "Document '{filename}.{ext}' downloaded by {emp_id}",
            "Folder structure reorganized by {emp_id}",
            "File version '{filename}.{ext}' created by {emp_id}",
            "Document collaboration session started for '{filename}.{ext}'",
            "File backup initiated for {emp_id}'s documents",
            "Document template '{template}' created by {emp_id}",
            "File retention policy applied to {count} documents"
        ]
        
        messages = []
        for _ in range(count):
            template = random.choice(templates)
            
            # Fill template with realistic data
            message = template.format(
                emp_id=self.get_random_identifier('employee_ids'),
                cust_id=self.get_random_identifier('customer_ids'),
                txn_id=self.get_random_identifier('transaction_ids'),
                order_id=self.get_random_identifier('order_ids'),
                ticket_id=self.get_random_identifier('ticket_ids'),
                proj_id=self.get_random_identifier('project_ids'),
                inv_id=self.get_random_identifier('invoice_ids'),
                amount=self.get_random_value('amounts'),
                currency=self.get_random_value('currencies'),
                dept=self.get_random_value('departments'),
                count=random.randint(5, 500),
                start_date=datetime.now().strftime('%Y-%m-%d'),
                end_date=(datetime.now() + timedelta(days=random.randint(1, 30))).strftime('%Y-%m-%d'),
                course=random.choice(['Security Awareness', 'Leadership Skills', 'Technical Training', 'Compliance Update']),
                title=random.choice(['Senior Developer', 'Team Lead', 'Manager', 'Director']),
                filename=random.choice(['report', 'presentation', 'document', 'analysis', 'proposal']),
                ext=self.get_random_value('file_types').lower(),
                template=random.choice(['Invoice Template', 'Report Template', 'Contract Template']),
                campaign=random.choice(['Monthly Newsletter', 'Product Update', 'Special Offer']),
                date=datetime.now().strftime('%Y-%m-%d'),
                lead_id=f'LEAD{random.randint(1000, 9999)}',
                opp_id=f'OPP{random.randint(1000, 9999)}',
                quote_id=f'QUO{random.randint(1000, 9999)}',
                contract_id=f'CON{random.randint(1000, 9999)}'
            )
            
            if message not in self.generated_messages:
                self.generated_messages.add(message)
                
                # Determine appropriate source system
                if any(keyword in message.lower() for keyword in ['employee', 'payroll', 'hr', 'benefits', 'training']):
                    source = random.choice(self.business_systems['HR'])
                elif any(keyword in message.lower() for keyword in ['invoice', 'payment', 'billing', 'financial']):
                    source = random.choice(self.business_systems['Finance'])
                elif any(keyword in message.lower() for keyword in ['customer', 'lead', 'support', 'crm']):
                    source = random.choice(self.business_systems['CRM'])
                elif any(keyword in message.lower() for keyword in ['file', 'document', 'folder']):
                    source = random.choice(self.business_systems['Infrastructure'])
                else:
                    source = random.choice(self.business_systems['ERP'])
                
                messages.append({
                    'timestamp': self.generate_timestamp(),
                    'source': source,
                    'log_message': message,
                    'target_label': 'user_action',
                    'complexity': 'bert'
                })
        
        return messages

    def generate_system_notification_messages(self, count=400):
        """Generate realistic system notification messages."""
        templates = [
            # Infrastructure notifications
            "Database backup completed successfully - {size}GB archived",
            "System health check passed - all services operational",
            "Load balancer configuration updated - {count} servers",
            "SSL certificate renewed for domain {domain}",
            "Disk space optimization completed - {size}GB freed",
            "Network connectivity test passed - latency {latency}ms",
            "Cache refresh completed - {count} entries updated",
            "Log rotation completed - {count} files archived",
            "System restart completed - uptime reset",
            "Performance monitoring baseline updated",
            
            # Business process notifications
            "Daily report generation completed - {count} reports generated",
            "Email service status: operational - {count} messages sent",
            "Backup verification successful - {count} files verified",
            "Data synchronization completed between {system1} and {system2}",
            "Scheduled maintenance window completed",
            "Service discovery updated - {count} services registered",
            "Configuration deployment successful across {count} instances",
            "Health monitoring alerts configured for {service}",
            "Resource utilization report generated",
            "Automated cleanup process completed",
            
            # Analytics and reporting
            "ETL pipeline execution completed - {count} records processed",
            "Data warehouse refresh completed successfully",
            "Business intelligence report published",
            "Real-time dashboard metrics updated",
            "Data quality validation passed - {score}% accuracy",
            "Machine learning model training initiated",
            "Analytics cache warming completed",
            "Report distribution completed - {count} recipients",
            "Data archival process completed",
            "Query performance optimization applied"
        ]
        
        messages = []
        for _ in range(count):
            template = random.choice(templates)
            
            message = template.format(
                size=random.randint(1, 500),
                count=random.randint(10, 1000),
                domain=random.choice(['api.company.com', 'portal.company.com', 'app.company.com']),
                latency=random.randint(10, 100),
                system1=random.choice(['CRM', 'ERP', 'HR', 'Finance']),
                system2=random.choice(['DataWarehouse', 'Analytics', 'Reporting']),
                service=random.choice(['PaymentAPI', 'UserService', 'NotificationService']),
                score=random.randint(85, 99)
            )
            
            if message not in self.generated_messages:
                self.generated_messages.add(message)
                
                # Assign appropriate source
                if any(keyword in message.lower() for keyword in ['database', 'backup', 'disk', 'network']):
                    source = random.choice(self.business_systems['Infrastructure'])
                elif any(keyword in message.lower() for keyword in ['etl', 'analytics', 'report', 'data']):
                    source = random.choice(self.business_systems['Analytics'])
                else:
                    source = random.choice(self.business_systems['DevOps'])
                
                messages.append({
                    'timestamp': self.generate_timestamp(),
                    'source': source,
                    'log_message': message,
                    'target_label': 'system_notification',
                    'complexity': random.choice(['regex', 'bert'])
                })
        
        return messages

    def generate_workflow_error_messages(self, count=400):
        """Generate realistic workflow error messages."""
        templates = [
            # Technical errors
            "Database connection timeout after {timeout}s - retrying",
            "API request failed with status code {code} - {endpoint}",
            "File upload failed - file size exceeds {limit}MB limit",
            "Payment processing failed - insufficient funds for {amount} {currency}",
            "Email delivery failed to {email} - invalid address",
            "Authentication failed for user {user_id} - invalid credentials",
            "Service timeout occurred - {service} did not respond within {timeout}s",
            "Memory allocation failed - insufficient resources for process {process_id}",
            "Network connection lost to {host} - attempting reconnection",
            "Validation failed for field '{field}' - required value missing",
            
            # Business process errors
            "Invoice generation failed for customer {cust_id} - missing billing address",
            "Payroll calculation error for employee {emp_id} - invalid tax rate",
            "Order processing failed - inventory insufficient for item {item_id}",
            "Report generation failed - data source {source} unavailable",
            "Backup process interrupted - disk space insufficient",
            "Synchronization failed between {system1} and {system2} - version conflict",
            "Workflow approval timeout - no response from {approver} after {hours} hours",
            "Data migration failed - schema validation error in table {table}",
            "Integration error with {system} - API key expired",
            "Batch processing failed - {count} records could not be processed",
            
            # User-related errors
            "Session expired for user {user_id} - login required",
            "Access denied for user {user_id} - insufficient permissions for {resource}",
            "Profile update failed for user {user_id} - duplicate email address",
            "Password reset failed for {email} - account not found",
            "Two-factor authentication failed for user {user_id} - invalid code",
            "File access denied - user {user_id} lacks read permission for {filename}",
            "Upload quota exceeded for user {user_id} - {usage}MB of {limit}MB used",
            "Account lockout triggered for user {user_id} - {attempts} failed login attempts",
            "Subscription expired for user {user_id} - renewal required",
            "Feature access denied - user {user_id} plan does not include {feature}"
        ]
        
        messages = []
        for _ in range(count):
            template = random.choice(templates)
            
            message = template.format(
                timeout=random.randint(30, 300),
                code=random.choice([400, 401, 403, 404, 500, 502, 503, 504]),
                endpoint=random.choice(['/api/users', '/api/payments', '/api/orders', '/api/reports']),
                limit=random.choice([10, 25, 50, 100]),
                amount=self.get_random_value('amounts'),
                currency=self.get_random_value('currencies'),
                email=f'user{random.randint(1, 999)}@company.com',
                user_id=self.get_random_identifier('employee_ids'),
                cust_id=self.get_random_identifier('customer_ids'),
                emp_id=self.get_random_identifier('employee_ids'),
                service=random.choice(['PaymentAPI', 'EmailService', 'AuthService']),
                process_id=f'PID{random.randint(1000, 9999)}',
                host=random.choice(['db-server-01', 'api-gateway', 'cache-server']),
                field=random.choice(['email', 'phone', 'address', 'amount']),
                item_id=f'ITEM{random.randint(1000, 9999)}',
                source=random.choice(['Database', 'API', 'FileSystem']),
                system1=random.choice(['CRM', 'ERP', 'HR']),
                system2=random.choice(['Analytics', 'Reporting', 'Billing']),
                approver=f'manager{random.randint(1, 20)}',
                hours=random.randint(24, 72),
                table=random.choice(['users', 'orders', 'payments', 'products']),
                system=random.choice(['Salesforce', 'SAP', 'Office365']),
                count=random.randint(5, 500),
                resource=random.choice(['financial_data', 'customer_info', 'reports']),
                filename=f'document_{random.randint(1, 999)}.pdf',
                usage=random.randint(80, 95),
                attempts=random.randint(3, 10),
                feature=random.choice(['Advanced Analytics', 'API Access', 'Premium Support'])
            )
            
            if message not in self.generated_messages:
                self.generated_messages.add(message)
                
                # Assign appropriate source
                if any(keyword in message.lower() for keyword in ['database', 'connection', 'server']):
                    source = random.choice(self.business_systems['Infrastructure'])
                elif any(keyword in message.lower() for keyword in ['payment', 'invoice', 'billing']):
                    source = random.choice(self.business_systems['Finance'])
                elif any(keyword in message.lower() for keyword in ['user', 'authentication', 'login']):
                    source = random.choice(self.business_systems['Security'])
                else:
                    source = random.choice(list(self.business_systems.values())[random.randint(0, len(self.business_systems)-1)])
                
                messages.append({
                    'timestamp': self.generate_timestamp(),
                    'source': source,
                    'log_message': message,
                    'target_label': 'workflow_error',
                    'complexity': 'bert'
                })
        
        return messages

    def generate_security_alert_messages(self, count=150):
        """Generate realistic security alert messages."""
        templates = [
            # Authentication threats
            "Multiple failed login attempts detected for user {user_id} from IP {ip}",
            "Brute force attack detected on endpoint {endpoint} - {attempts} attempts in {minutes} minutes",
            "Suspicious login location detected for user {user_id} - {location}",
            "Password policy violation - user {user_id} attempted weak password",
            "Account lockout triggered for user {user_id} - security threshold exceeded",
            "Privileged account access outside business hours - user {user_id} at {time}",
            "Two-factor authentication bypass attempt detected for user {user_id}",
            "Session hijacking attempt detected - invalid session token for user {user_id}",
            "Credential stuffing attack detected from IP range {ip_range}",
            "Unauthorized API key usage detected - key {key_id}",
            
            # Data access threats
            "Unauthorized access attempt to sensitive data - table {table}",
            "Data exfiltration alert - large data download by user {user_id}",
            "SQL injection attempt detected on endpoint {endpoint}",
            "Unauthorized file access attempt - {filename} by user {user_id}",
            "Privilege escalation attempt detected for user {user_id}",
            "Cross-site scripting attempt blocked on {url}",
            "Unauthorized database query execution by user {user_id}",
            "Sensitive data exposure risk - unencrypted transmission detected",
            "Data modification alert - bulk changes by user {user_id} in {table}",
            "Unauthorized backup access attempt from IP {ip}",
            
            # Network and system threats
            "Malware signature detected in file upload - {filename}",
            "DDoS attack detected - {requests} requests per second from {ip_range}",
            "Port scanning activity detected from IP {ip}",
            "Firewall rule violation - blocked connection from {ip} to {port}",
            "Intrusion detection alert - suspicious network traffic pattern",
            "Virus scan found {count} infected files in system",
            "Unauthorized network access attempt from MAC address {mac}",
            "Suspicious outbound connection to {domain} - potential data leak",
            "System file modification detected - {filename} changed unexpectedly",
            "Rootkit detection alert - system integrity compromised"
        ]
        
        messages = []
        for _ in range(count):
            template = random.choice(templates)
            
            message = template.format(
                user_id=self.get_random_identifier('employee_ids'),
                ip=f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
                endpoint=random.choice(['/admin', '/api/users', '/login', '/data/export']),
                attempts=random.randint(5, 50),
                minutes=random.randint(1, 30),
                location=self.get_random_value('locations'),
                time=f"{random.randint(0,23):02d}:{random.randint(0,59):02d}",
                ip_range=f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.0/24",
                key_id=f"KEY_{random.randint(1000,9999)}",
                table=random.choice(['users', 'customers', 'financial_data', 'employee_records']),
                filename=f"suspicious_file_{random.randint(1,999)}.{random.choice(['exe', 'pdf', 'zip'])}",
                url=random.choice(['company.com/admin', 'portal.company.com', 'api.company.com']),
                requests=random.randint(1000, 10000),
                port=random.choice([22, 80, 443, 3389, 5432]),
                domain=random.choice(['suspicious-site.com', 'malware-domain.net', 'phishing-site.org']),
                mac=f"{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}:{random.randint(10,99):02x}",
                count=random.randint(1, 20)
            )
            
            if message not in self.generated_messages:
                self.generated_messages.add(message)
                
                messages.append({
                    'timestamp': self.generate_timestamp(),
                    'source': random.choice(self.business_systems['Security']),
                    'log_message': message,
                    'target_label': 'security_alert',
                    'complexity': 'bert'
                })
        
        return messages

    def generate_deprecation_warning_messages(self, count=350):
        """Generate realistic deprecation warning messages."""
        templates = [
            # API deprecations
            "API version {version} will be deprecated on {date} - migrate to version {new_version}",
            "Deprecated method '{method}' used in {service} - use '{new_method}' instead",
            "Legacy authentication endpoint deprecated - switch to OAuth 2.0 by {date}",
            "REST API endpoint '{endpoint}' deprecated - use GraphQL equivalent",
            "Deprecated parameter '{param}' in API call - will be removed in version {version}",
            "Legacy SSL protocol TLS 1.0 deprecated - upgrade to TLS 1.2+ by {date}",
            "Deprecated database driver version {version} - update to {new_version}",
            "Legacy payment gateway deprecated - migrate to new provider by {date}",
            "Deprecated encryption algorithm MD5 - switch to SHA-256",
            "Legacy file format {format} support ending {date}",
            
            # Software deprecations
            "Internet Explorer support ending by {date} - update browser requirements",
            "Legacy Java version {version} deprecated - upgrade to Java {new_version}",
            "Deprecated Python 2.7 support - migrate to Python 3.8+ by {date}",
            "Legacy .NET Framework {version} deprecated - upgrade to .NET Core",
            "Deprecated Node.js version {version} - update to version {new_version}",
            "Legacy database MySQL {version} deprecated - upgrade to {new_version}",
            "Deprecated operating system support - {os} end of life {date}",
            "Legacy email client support ending - {client} deprecated {date}",
            "Deprecated mobile app version {version} - users must update",
            "Legacy report format deprecated - {format} support ending {date}",
            
            # Feature deprecations
            "Feature '{feature}' deprecated in favor of '{new_feature}'",
            "Legacy workflow engine deprecated - migrate processes by {date}",
            "Deprecated user interface theme - update to modern theme",
            "Legacy notification system deprecated - switch to new system by {date}",
            "Deprecated batch processing method - use streaming API instead",
            "Legacy search functionality deprecated - upgrade to enhanced search",
            "Deprecated file sharing method - migrate to secure sharing by {date}",
            "Legacy backup system deprecated - transition to cloud backup",
            "Deprecated integration method - use webhook integration instead",
            "Legacy dashboard deprecated - migrate to new analytics platform"
        ]
        
        messages = []
        for _ in range(count):
            template = random.choice(templates)
            
            future_date = (datetime.now() + timedelta(days=random.randint(30, 365))).strftime('%Y-%m-%d')
            
            message = template.format(
                version=f"v{random.randint(1,3)}.{random.randint(0,9)}",
                new_version=f"v{random.randint(2,4)}.{random.randint(0,9)}",
                date=future_date,
                method=random.choice(['getUserData()', 'processPayment()', 'sendEmail()', 'validateInput()']),
                new_method=random.choice(['getUserDataV2()', 'processSecurePayment()', 'sendSecureEmail()', 'validateInputV2()']),
                service=random.choice(['UserService', 'PaymentAPI', 'EmailService', 'ValidationService']),
                endpoint=random.choice(['/api/v1/users', '/api/v1/payments', '/api/v1/orders']),
                param=random.choice(['user_id', 'legacy_format', 'old_method', 'deprecated_field']),
                format=random.choice(['CSV v1.0', 'XML 1.0', 'Legacy PDF', 'Old Excel']),
                os=random.choice(['Windows 7', 'Ubuntu 16.04', 'CentOS 7', 'macOS 10.14']),
                client=random.choice(['Outlook 2010', 'Thunderbird 52', 'Apple Mail 11']),
                feature=random.choice(['Legacy Dashboard', 'Old Report Builder', 'Classic UI', 'Legacy Search']),
                new_feature=random.choice(['Modern Dashboard', 'New Report Builder', 'Modern UI', 'Enhanced Search'])
            )
            
            if message not in self.generated_messages:
                self.generated_messages.add(message)
                
                # Assign appropriate source
                source_options = list(self.business_systems.values())
                source = random.choice(source_options[random.randint(0, len(source_options)-1)])
                
                messages.append({
                    'timestamp': self.generate_timestamp(),
                    'source': source,
                    'log_message': message,
                    'target_label': 'deprecation_warning',
                    'complexity': random.choice(['regex', 'bert'])
                })
        
        return messages

    def generate_unclassified_messages(self, count=300):
        """Generate realistic unclassified messages that are genuinely ambiguous."""
        templates = [
            # Ambiguous system messages
            "Process {process_id} completed with status {status}",
            "Service {service} returned unexpected result: {result}",
            "Operation {operation} finished - duration {duration}ms",
            "Event {event_id} triggered in module {module}",
            "Resource {resource} state changed to {state}",
            "Handler {handler} processed {count} items",
            "Batch job {job_id} completed with warnings",
            "Queue {queue_name} processing rate: {rate} items/sec",
            "Cache hit ratio for {service}: {ratio}%",
            "Metrics collected for period {period}",
            
            # Cryptic technical messages
            "Buffer overflow condition detected in module {module}",
            "Memory fragmentation level: {level}% in heap {heap_id}",
            "Thread pool utilization: {utilization}% ({active}/{total} threads)",
            "Garbage collection triggered - {collected}MB freed",
            "Index rebuild completed for {table} - {time}ms elapsed",
            "Connection pool statistics: {active}/{max} connections active",
            "Lock contention detected on resource {resource} - {wait_time}ms wait",
            "Checkpoint operation completed - {pages} pages written",
            "Recovery process initiated for transaction log {log_id}",
            "Cluster node {node_id} status: {status}",
            
            # Business context unclear
            "Transaction {txn_id} marked for review",
            "Workflow {workflow_id} suspended pending approval",
            "Data consistency check revealed {anomalies} anomalies",
            "Business rule {rule_id} evaluation: {rule_result}",
            "Customer {cust_id} interaction logged with score {score}",
            "Inventory adjustment made for SKU {sku} - quantity {qty}",
            "Compliance check {check_id} resulted in status {status}",
            "Asset {asset_id} lifecycle status updated to {status}",
            "Contract {contract_id} milestone {milestone} reached",
            "Project {project_id} phase {phase} initiated"
        ]
        
        messages = []
        for _ in range(count):
            template = random.choice(templates)
            
            message = template.format(
                process_id=f"PRC{random.randint(1000, 9999)}",
                status=random.choice(['SUCCESS', 'WARNING', 'PARTIAL', 'UNKNOWN']),
                service=random.choice(['DataProcessor', 'EventHandler', 'TaskManager', 'ResourceController']),
                result=random.choice(['PARTIAL_DATA', 'TIMEOUT_REACHED', 'CONDITION_MET', 'THRESHOLD_EXCEEDED']),
                operation=random.choice(['SYNC', 'MERGE', 'VALIDATE', 'TRANSFORM', 'AGGREGATE']),
                duration=random.randint(100, 5000),
                event_id=f"EVT{random.randint(10000, 99999)}",
                module=random.choice(['CoreEngine', 'DataLayer', 'BusinessLogic', 'IntegrationHub']),
                resource=random.choice(['CPU_POOL', 'MEMORY_BANK', 'STORAGE_TIER', 'NETWORK_PIPE']),
                state=random.choice(['ACTIVE', 'IDLE', 'SUSPENDED', 'TRANSITIONING']),
                handler=random.choice(['MessageHandler', 'EventProcessor', 'DataTransformer']),
                count=random.randint(1, 1000),
                job_id=f"JOB{random.randint(100000, 999999)}",
                queue_name=random.choice(['high_priority', 'background_tasks', 'data_processing']),
                rate=random.randint(10, 1000),
                ratio=random.randint(60, 95),
                period=random.choice(['hourly', 'daily', 'weekly']),
                level=random.randint(20, 80),
                heap_id=f"HEAP{random.randint(1, 10)}",
                utilization=random.randint(30, 90),
                active=random.randint(10, 50),
                total=random.randint(50, 100),
                collected=random.randint(10, 500),
                table=random.choice(['user_data', 'transaction_log', 'audit_trail']),
                time=random.randint(1000, 30000),
                max=random.randint(50, 200),
                wait_time=random.randint(100, 2000),
                pages=random.randint(1000, 10000),
                log_id=f"LOG{random.randint(1000, 9999)}",
                node_id=f"NODE{random.randint(1, 20)}",
                txn_id=self.get_random_identifier('transaction_ids'),
                workflow_id=f"WF{random.randint(1000, 9999)}",
                anomalies=random.randint(0, 10),
                rule_id=f"RULE{random.randint(100, 999)}",
                rule_result=random.choice(['PASS', 'FAIL', 'CONDITIONAL', 'REVIEW']),
                cust_id=self.get_random_identifier('customer_ids'),
                score=random.randint(1, 100),
                sku=f"SKU{random.randint(100000, 999999)}",
                qty=random.randint(1, 1000),
                check_id=f"CHK{random.randint(1000, 9999)}",
                asset_id=f"AST{random.randint(1000, 9999)}",
                contract_id=f"CON{random.randint(1000, 9999)}",
                milestone=random.randint(1, 10),
                project_id=self.get_random_identifier('project_ids'),
                phase=random.choice(['PLANNING', 'EXECUTION', 'TESTING', 'DEPLOYMENT'])
            )
            
            if message not in self.generated_messages:
                self.generated_messages.add(message)
                
                # Random source assignment for ambiguous messages
                all_sources = []
                for sources in self.business_systems.values():
                    all_sources.extend(sources)
                
                messages.append({
                    'timestamp': self.generate_timestamp(),
                    'source': random.choice(all_sources),
                    'log_message': message,
                    'target_label': 'unclassified',
                    'complexity': 'llm'  # These require advanced reasoning
                })
        
        return messages

    def generate_advanced_dataset(self, total_size=3000):
        """Generate a comprehensive, balanced dataset."""
        print(f"🚀 GENERATING ADVANCED DATASET ({total_size} entries)")
        print("=" * 60)
        
        # Calculate balanced distribution
        per_category = total_size // 5
        remainder = total_size % 5
        
        distribution = {
            'user_action': per_category + (1 if remainder > 0 else 0),
            'system_notification': per_category + (1 if remainder > 1 else 0),
            'workflow_error': per_category + (1 if remainder > 2 else 0),
            'security_alert': per_category + (1 if remainder > 3 else 0),
            'deprecation_warning': per_category + (1 if remainder > 4 else 0),
            'unclassified': per_category
        }
        
        print("Target distribution:")
        for label, count in distribution.items():
            print(f"  {label}: {count}")
        
        # Generate each category
        all_messages = []
        
        print("\nGenerating categories:")
        
        print("  📝 User actions...")
        all_messages.extend(self.generate_user_action_messages(distribution['user_action']))
        
        print("  📢 System notifications...")
        all_messages.extend(self.generate_system_notification_messages(distribution['system_notification']))
        
        print("  ⚠️  Workflow errors...")
        all_messages.extend(self.generate_workflow_error_messages(distribution['workflow_error']))
        
        print("  🚨 Security alerts...")
        all_messages.extend(self.generate_security_alert_messages(distribution['security_alert']))
        
        print("  📅 Deprecation warnings...")
        all_messages.extend(self.generate_deprecation_warning_messages(distribution['deprecation_warning']))
        
        print("  ❓ Unclassified messages...")
        all_messages.extend(self.generate_unclassified_messages(distribution['unclassified']))
        
        # Convert to DataFrame
        df = pd.DataFrame(all_messages)
        
        # Shuffle the dataset
        df = df.sample(frac=1, random_state=42).reset_index(drop=True)
        
        print(f"\n✅ Generated {len(df)} unique, high-quality messages")
        print(f"📊 Final distribution:")
        for label, count in df['target_label'].value_counts().items():
            pct = (count / len(df)) * 100
            print(f"  {label}: {count} ({pct:.1f}%)")
        
        return df

def main():
    """Generate advanced dataset for log classification."""
    
    generator = AdvancedLogDatasetGenerator()
    
    # Generate different sized datasets for testing
    sizes = [3000, 5000]  # Test with different sizes
    
    for size in sizes:
        print(f"\n🎯 CREATING {size}-ENTRY ADVANCED DATASET")
        print("=" * 70)
        
        df = generator.generate_advanced_dataset(size)
        
        # Save the dataset
        filename = f'data/training/dataset/advanced_dataset_{size}.csv'
        df.to_csv(filename, index=False)
        print(f"\n💾 Saved to: {filename}")
        
        # Show sample messages
        print(f"\n📋 Sample messages:")
        for i, (_, row) in enumerate(df.sample(5).iterrows(), 1):
            print(f"  {i}. [{row['target_label']}] {row['log_message'][:80]}...")
    
    print(f"\n🎉 ADVANCED DATASETS GENERATED SUCCESSFULLY!")
    print(f"These datasets use strategic template-based generation with:")
    print(f"  ✅ Realistic business contexts and identifiers")
    print(f"  ✅ Domain-specific terminology and operations")
    print(f"  ✅ Balanced complexity distribution")
    print(f"  ✅ Edge cases and ambiguous scenarios")
    print(f"  ✅ Enterprise-grade message patterns")

if __name__ == "__main__":
    main()