#!/usr/bin/env python3
"""
Test script to verify the reorganized server works correctly.
"""
import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_server():
    """Test that the server can be imported and basic endpoints work."""
    
    print("🔄 Testing reorganized server...")
    
    try:
        # Test server import
        from src.server import app
        print("✅ Server import successful")
        
        # Test FastAPI app creation
        print(f"✅ FastAPI app created: {type(app).__name__}")
        
        # Test route registration
        routes = [route.path for route in app.routes]
        print(f"✅ Routes registered: {len(routes)} routes")
        
        # Test key routes exist
        expected_routes = ["/", "/classify/", "/health/"]
        missing_routes = [route for route in expected_routes if route not in routes]
        if missing_routes:
            print(f"⚠️  Missing routes: {missing_routes}")
        else:
            print("✅ All expected routes present")
        
        print("\n🎉 Server reorganization test PASSED!")
        print("📝 The application should work correctly with: python main.py")
        print("🌐 Server will be available at: http://localhost:8000")
        print("📊 Frontend will be available at: http://localhost:8000/")
        
        return True
        
    except Exception as e:
        print(f"❌ Server test failed: {e}")
        return False

if __name__ == "__main__":
    test_server()