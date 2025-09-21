"""
Comprehensive test suite for the enhanced log classification system.
Tests the 20K model performance, edge cases, and system robustness.
"""
import unittest
import time
import random
import pandas as pd
import numpy as np
from pathlib import Path
import sys
import os

# Add the current directory to the path for imports
sys.path.append('.')

# Import our enhanced processor
from processor_bert_enhanced import (
    classify_with_bert, 
    classify_batch, 
    get_model_info,
    get_model_performance_stats,
    load_model
)

class TestLogClassificationSystem(unittest.TestCase):
    """Comprehensive test suite for the log classification system."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures once for all tests."""
        print("\n" + "="*60)
        print("ENHANCED LOG CLASSIFICATION SYSTEM TEST SUITE")
        print("="*60)
        
        # Load model once for all tests
        cls.model_loaded = load_model()
        cls.model_info = get_model_info()
        
        print(f"Model loaded: {cls.model_loaded}")
        print(f"Model path: {cls.model_info.get('model_path', 'None')}")
        print(f"Model type: {cls.model_info.get('model_type', 'Unknown')}")
        
        if 'classes' in cls.model_info:
            print(f"Classes: {cls.model_info['classes']}")
    
    def test_model_loading(self):
        """Test that the model loads successfully."""
        self.assertTrue(self.model_loaded, "Model should load successfully")
        self.assertIsNotNone(self.model_info['model_path'], "Model path should be set")
        self.assertTrue(self.model_info['model_loaded'], "Model should be marked as loaded")
    
    def test_basic_classification(self):
        """Test basic classification functionality."""
        test_cases = [
            ("User login failed: invalid password", "workflow_error"),
            ("Database connection established", "system_notification"), 
            ("API endpoint deprecated", "deprecation_warning"),
            ("File uploaded successfully", "user_action"),
            ("Random gibberish xyz123", None)  # Should be unclassified or handled gracefully
        ]
        
        print("\n--- Basic Classification Tests ---")
        for message, expected_category in test_cases:
            result = classify_with_bert(message)
            print(f"{result:<20} | {message}")
            
            self.assertIsInstance(result, str, f"Result should be string for: {message}")
            self.assertNotEqual(result, "", f"Result should not be empty for: {message}")
            
            # For specific expected categories, verify they match
            if expected_category:
                self.assertEqual(result, expected_category, 
                               f"Expected {expected_category} for: {message}")
    
    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        edge_cases = [
            "",  # Empty string
            " ",  # Whitespace only
            "a",  # Single character
            "A" * 1000,  # Very long string
            "123456789",  # Numbers only
            "!!!@@@###",  # Special characters only
            "Mixed 123 !@# content",  # Mixed content
            "SQL injection attempt: DROP TABLE users; --",  # Security-related
            "🚀 Emoji test message 🔥",  # Unicode/emoji
            "\n\t Log with newlines and tabs \r\n",  # Whitespace characters
        ]
        
        print("\n--- Edge Case Tests ---")
        for message in edge_cases:
            result = classify_with_bert(message)
            display_msg = repr(message)[:50] + "..." if len(repr(message)) > 50 else repr(message)
            print(f"{result:<20} | {display_msg}")
            
            self.assertIsInstance(result, str, f"Should return string for edge case: {repr(message)}")
    
    def test_batch_classification(self):
        """Test batch classification performance and correctness."""
        messages = [
            "User authentication successful",
            "Database query timeout",
            "API rate limit exceeded", 
            "Cache invalidation completed",
            "Payment processing failed",
            "SSL certificate renewal",
            "Memory usage warning",
            "Disk space low alert",
            "Network connection lost",
            "Service startup complete"
        ]
        
        print("\n--- Batch Classification Test ---")
        start_time = time.time()
        results = classify_batch(messages)
        batch_time = time.time() - start_time
        
        print(f"Batch of {len(messages)} messages classified in {batch_time:.3f} seconds")
        print(f"Throughput: {len(messages)/batch_time:.1f} messages/second")
        
        self.assertEqual(len(results), len(messages), "Should return same number of results")
        
        for msg, result in zip(messages, results):
            print(f"{result:<20} | {msg}")
            self.assertIsInstance(result, str, f"Each result should be string")
    
    def test_performance_requirements(self):
        """Test that classification meets performance requirements."""
        message = "User login failed: authentication timeout"
        
        # Single classification performance
        times = []
        for _ in range(100):
            start = time.time()
            classify_with_bert(message)
            times.append(time.time() - start)
        
        avg_time = np.mean(times)
        p95_time = np.percentile(times, 95)
        
        print(f"\n--- Performance Test Results ---")
        print(f"Average classification time: {avg_time*1000:.2f}ms")
        print(f"95th percentile time: {p95_time*1000:.2f}ms")
        print(f"Throughput: {1/avg_time:.1f} classifications/second")
        
        # Performance requirements
        self.assertLess(avg_time, 1.0, "Average classification should be under 1 second")
        self.assertLess(p95_time, 2.0, "95th percentile should be under 2 seconds")
    
    def test_consistency(self):
        """Test that the same input gives consistent results."""
        message = "Database connection failed after timeout"
        
        results = []
        for _ in range(10):
            result = classify_with_bert(message)
            results.append(result)
        
        print(f"\n--- Consistency Test ---")
        print(f"Message: {message}")
        print(f"Results: {set(results)}")
        
        # All results should be the same
        self.assertEqual(len(set(results)), 1, "Same input should give consistent results")
    
    def test_real_world_samples(self):
        """Test with realistic log samples from different systems."""
        real_world_logs = [
            # Web server logs
            "127.0.0.1 - - [25/Dec/2023:10:00:01 +0000] GET /api/users/123 HTTP/1.1 200 1234",
            "nginx: [error] connect() failed (111: Connection refused) while connecting to upstream",
            
            # Application logs  
            "INFO 2023-12-25 10:00:01 UserService - User johndoe logged in successfully",
            "ERROR 2023-12-25 10:01:15 PaymentService - Credit card validation failed for transaction 98765",
            "WARN 2023-12-25 10:02:30 CacheService - Redis connection pool exhausted, creating new connections",
            
            # System logs
            "Dec 25 10:00:01 server01 kernel: Out of memory: Kill process 1234 (java) score 856 or sacrifice child",
            "systemd[1]: Started Apache HTTP Server",
            "cron[1234]: (root) CMD (/usr/bin/backup.sh)",
            
            # Database logs
            "2023-12-25 10:00:01 [ERROR] [MY-000067] [Server] Unknown table 'test.users'",
            "2023-12-25 10:01:00 [Note] [MY-000000] [Server] /usr/sbin/mysqld: ready for connections",
            
            # Security logs
            "Dec 25 10:00:01 server01 sshd[1234]: Failed password for invalid user admin from 192.168.1.100",
            "Intrusion attempt detected from IP 10.0.0.1 - multiple failed login attempts",
            
            # Deprecation warnings
            "DEPRECATED: Function mysql_query() is deprecated as of PHP 5.5.0. Use MySQLi or PDO instead",
            "Warning: API version v1 will be sunset on 2024-01-01. Please migrate to v2",
        ]
        
        print(f"\n--- Real-World Samples Test ---")
        print(f"Testing {len(real_world_logs)} realistic log samples...")
        
        results = {}
        for log in real_world_logs:
            result = classify_with_bert(log)
            category = results.get(result, 0)
            results[result] = category + 1
            
            # Show first 100 chars of log
            display_log = log[:100] + "..." if len(log) > 100 else log
            print(f"{result:<20} | {display_log}")
        
        print(f"\nClassification distribution:")
        for category, count in sorted(results.items()):
            percentage = (count / len(real_world_logs)) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        # Should classify all messages (no None results)
        self.assertNotIn(None, results.keys(), "All messages should be classified")
    
    def test_model_information(self):
        """Test model information retrieval."""
        info = get_model_info()
        
        print(f"\n--- Model Information ---")
        for key, value in info.items():
            if isinstance(value, list) and len(value) > 5:
                print(f"{key}: {len(value)} items")
            else:
                print(f"{key}: {value}")
        
        # Required information should be present
        self.assertIn('model_loaded', info, "Should have model_loaded status")
        self.assertIn('model_path', info, "Should have model_path")
        
        if info['model_loaded']:
            self.assertIsNotNone(info['model_path'], "Model path should not be None if loaded")
    
    def test_stress_test(self):
        """Stress test with high volume of classifications."""
        print(f"\n--- Stress Test ---")
        
        # Generate random log-like messages
        templates = [
            "User {user} logged in from IP {ip}",
            "Database query failed: {error}",
            "API request to {endpoint} returned {status}",
            "Memory usage at {percent}% on server {server}",
            "Payment {payment_id} processed for amount ${amount}",
            "SSL certificate for {domain} expires in {days} days",
            "File {filename} uploaded by user {user}",
            "Cache miss for key {key} in region {region}",
            "Network timeout connecting to {host}:{port}",
            "Service {service} restarted after {downtime} minutes"
        ]
        
        # Generate 1000 random messages
        messages = []
        for _ in range(1000):
            template = random.choice(templates)
            message = template.format(
                user=f"user{random.randint(1,1000)}",
                ip=f"192.168.{random.randint(1,255)}.{random.randint(1,255)}",
                error=random.choice(["timeout", "connection failed", "syntax error"]),
                endpoint=f"/api/v{random.randint(1,3)}/endpoint{random.randint(1,100)}",
                status=random.choice([200, 404, 500, 503]),
                percent=random.randint(1,100),
                server=f"server{random.randint(1,10)}",
                payment_id=f"pay_{random.randint(10000,99999)}",
                amount=random.randint(10,1000),
                domain=f"example{random.randint(1,100)}.com",
                days=random.randint(1,365),
                filename=f"file{random.randint(1,1000)}.txt",
                key=f"cache_key_{random.randint(1,10000)}",
                region=f"region_{random.randint(1,5)}",
                host=f"host{random.randint(1,50)}.example.com",
                port=random.choice([80, 443, 8080, 3306, 5432]),
                service=f"service{random.randint(1,20)}",
                downtime=random.randint(1,60)
            )
            messages.append(message)
        
        # Classify all messages
        start_time = time.time()
        results = classify_batch(messages)
        total_time = time.time() - start_time
        
        print(f"Classified {len(messages)} messages in {total_time:.2f} seconds")
        print(f"Throughput: {len(messages)/total_time:.1f} messages/second")
        
        # Verify results
        self.assertEqual(len(results), len(messages), "Should classify all messages")
        
        # Check distribution
        distribution = {}
        for result in results:
            distribution[result] = distribution.get(result, 0) + 1
        
        print(f"Classification distribution:")
        for category, count in sorted(distribution.items()):
            percentage = (count / len(results)) * 100
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        # Performance assertion
        self.assertLess(total_time, 60, "Should complete stress test within 60 seconds")

def run_comprehensive_tests():
    """Run all tests and generate a comprehensive report."""
    print("Starting comprehensive test suite...")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestLogClassificationSystem)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFailures:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback}")
    
    if result.errors:
        print(f"\nErrors:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback}")
    
    # Model info summary
    model_info = get_model_info()
    print(f"\nModel Information:")
    print(f"  Model path: {model_info.get('model_path', 'Unknown')}")
    print(f"  Model type: {model_info.get('model_type', 'Unknown')}")
    print(f"  Available models: {len(model_info.get('available_models', []))}")
    
    return result.wasSuccessful()

if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)