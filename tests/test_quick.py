#!/usr/bin/env python3
"""
Quick test runner for critical components.
"""
import unittest
import sys
import time

def test_regex_processor():
    """Test regex processor quickly."""
    print("Testing Regex Processor...")
    from processor_regex import classify_with_regex
    
    test_cases = [
        ("ERROR: Database failed", "workflow_error"),
        ("INFO: User logged in", "user_action"),  # Fixed expectation
    ]
    
    passed = 0
    for log_msg, expected in test_cases:
        result = classify_with_regex("TestApp", log_msg)
        if result == expected:
            passed += 1
            print(f"  ✅ {log_msg[:30]}... -> {result}")
        else:
            print(f"  ❌ {log_msg[:30]}... -> {result} (expected {expected})")
    
    print(f"  Regex Tests: {passed}/{len(test_cases)} passed")
    return passed == len(test_cases)

def test_cache_system():
    """Test cache system quickly."""
    print("Testing Cache System...")
    from cache_manager import InMemoryCache, get_cache_stats
    
    cache = InMemoryCache(max_size=10, default_ttl=60)
    
    # Test basic operations
    cache.set("test1", "value1")
    result = cache.get("test1")
    
    if result == "value1":
        print("  ✅ Cache set/get working")
        
        # Test stats
        stats = get_cache_stats()
        if isinstance(stats, dict):
            print("  ✅ Cache stats working")
            return True
        else:
            print("  ❌ Cache stats failed")
    else:
        print("  ❌ Cache set/get failed")
    
    return False

def test_performance_monitor():
    """Test performance monitoring quickly."""
    print("Testing Performance Monitor...")
    from performance_monitor_simple import monitor_performance, performance_monitor
    
    @monitor_performance()
    def test_func(x):
        return x * 2
    
    # Call the function
    result = test_func(5)
    
    if result == 10:
        print("  ✅ Performance decorator working")
        
        # Check stats
        stats = performance_monitor.get_stats()
        if stats.get('total_functions_monitored', 0) > 0:
            print("  ✅ Performance stats working")
            return True
        else:
            print("  ❌ Performance stats failed")
    else:
        print("  ❌ Performance decorator failed")
    
    return False

def test_classification_service():
    """Test classification service quickly."""
    print("Testing Classification Service...")
    from classification_service import classification_service
    
    try:
        result = classification_service.classify_logs([("TestApp", "ERROR: Test message")])
        
        if isinstance(result, list) and len(result) > 0:
            print("  ✅ Classification service working")
            return True
        else:
            print("  ❌ Classification service returned invalid result")
    except Exception as e:
        print(f"  ❌ Classification service failed: {e}")
    
    return False

def test_config_system():
    """Test configuration system quickly."""
    print("Testing Configuration...")
    from config import config
    from constants import HTTP_STATUS, ERROR_MESSAGES
    
    checks = [
        (hasattr(config, 'max_file_size_mb'), "Config max_file_size_mb"),
        (isinstance(HTTP_STATUS, dict), "HTTP_STATUS constants"),
        (isinstance(ERROR_MESSAGES, dict), "ERROR_MESSAGES constants"),
    ]
    
    passed = 0
    for check, name in checks:
        if check:
            print(f"  ✅ {name}")
            passed += 1
        else:
            print(f"  ❌ {name}")
    
    return passed == len(checks)

def run_quick_tests():
    """Run all quick tests."""
    print("=== Quick Test Suite ===\n")
    
    tests = [
        ("Regex Processor", test_regex_processor),
        ("Cache System", test_cache_system),
        ("Performance Monitor", test_performance_monitor),
        ("Classification Service", test_classification_service),
        ("Configuration", test_config_system),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            start_time = time.time()
            success = test_func()
            duration = time.time() - start_time
            results.append((test_name, success, duration))
            print(f"  Time: {duration:.3f}s")
        except Exception as e:
            print(f"  ❌ {test_name} crashed: {e}")
            results.append((test_name, False, 0))
        
        print()
    
    # Summary
    print("=== Test Results Summary ===")
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for test_name, success, duration in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name} ({duration:.3f}s)")
    
    print(f"\nOverall: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
    
    if passed == total:
        print("🎉 All critical tests passed!")
        return True
    else:
        print("⚠️  Some tests failed - review above")
        return False

if __name__ == "__main__":
    success = run_quick_tests()
    sys.exit(0 if success else 1)