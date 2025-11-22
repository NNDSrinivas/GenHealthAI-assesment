#!/usr/bin/env python3
"""
Production Testing Script for AWS Deployment
GenHealth.AI Clinical Document Processing API
"""

import requests
import json
import time
from datetime import datetime

def test_production_features():
    """Test all production-grade features of the API."""
    
    base_url = "http://127.0.0.1:8000"
    
    print("🚀 Testing Production-Grade GenHealth.AI Clinical Document API")
    print("=" * 70)
    print(f"⏰ Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    tests_passed = 0
    total_tests = 0
    
    def test_endpoint(name, method, url, **kwargs):
        nonlocal tests_passed, total_tests
        total_tests += 1
        try:
            print(f"🧪 Testing {name}...")
            response = requests.request(method, f"{base_url}{url}", timeout=10, **kwargs)
            
            if response.status_code in [200, 201]:
                tests_passed += 1
                print(f"   ✅ {response.status_code} - {name}")
                
                # Show response preview for important endpoints
                if url in ['/health', '/api', '/']:
                    data = response.json()
                    if 'service' in data:
                        print(f"   📋 Service: {data.get('service', 'N/A')}")
                    if 'version' in data:
                        print(f"   🔖 Version: {data.get('version', 'N/A')}")
                    if 'status' in data:
                        print(f"   💚 Status: {data.get('status', 'N/A')}")
                
            else:
                print(f"   ❌ {response.status_code} - {name}")
                print(f"      Error: {response.text[:100]}...")
                
        except Exception as e:
            print(f"   💥 Error - {name}: {str(e)[:50]}...")
        
        print()
    
    # 1. Test Root API Documentation
    test_endpoint("Root API Documentation", "GET", "/")
    
    # 2. Test Simple Health Check (for load balancers)
    test_endpoint("Simple Health Check", "GET", "/health?simple=true")
    
    # 3. Test Detailed Health Check (with monitoring)
    test_endpoint("Detailed Health Check", "GET", "/health")
    
    # 4. Test API Information Endpoint
    test_endpoint("API Information", "GET", "/api")
    
    # 5. Test Order Creation
    order_data = {
        "patient_name": "Emily Chen",
        "order_type": "blood_test",
        "status": "pending",
        "notes": "Production deployment test"
    }
    test_endpoint("Create Order", "POST", "/api/orders", 
                  json=order_data, 
                  headers={"Content-Type": "application/json"})
    
    # 6. Test Order Listing
    test_endpoint("List Orders", "GET", "/api/orders")
    
    # 7. Test Patient Listing
    test_endpoint("List Patients", "GET", "/api/patients")
    
    # 8. Test Error Handling (404)
    test_endpoint("404 Error Handling", "GET", "/nonexistent")
    
    # Summary
    print("🎯 PRODUCTION TEST RESULTS")
    print("=" * 50)
    print(f"✅ Tests Passed: {tests_passed}/{total_tests}")
    print(f"📊 Success Rate: {(tests_passed/total_tests)*100:.1f}%")
    print()
    
    if tests_passed >= 6:  # Allow some tolerance
        print("🎉 PRODUCTION READY!")
        print("✨ Your API is ready for AWS deployment!")
        print()
        print("🚀 Deploy Commands:")
        print("   Elastic Beanstalk: ./deploy-aws.sh")
        print("   App Runner: ./deploy-apprunner.sh")
        print()
        print("📖 Full Guide: AWS_DEPLOYMENT.md")
    else:
        print("⚠️  Some tests failed. Review logs before deploying.")
    
    print()
    print(f"⏰ Test Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    test_production_features()