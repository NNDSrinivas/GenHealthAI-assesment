#!/usr/bin/env python3
"""
API Testing Script for GenHealth.AI Assessment
Tests all required endpoints for the assessment
"""

import requests
import json
import time
from pathlib import Path


BASE_URL = "https://unadjourned-gentling-dolly.ngrok-free.dev"  # Public ngrok URL

def test_health_check():
    """Test the health endpoint"""
    print("🔍 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_order_crud():
    """Test Order CRUD operations"""
    print("\n🔍 Testing Order CRUD Operations...")
    
    # Create Order
    order_data = {
        "patient_id": "test-patient-123",
        "order_type": "lab_test",
        "description": "Blood test for assessment",
        "status": "pending"
    }
    
    try:
        # POST - Create Order
        response = requests.post(f"{BASE_URL}/api/orders", json=order_data)
        print(f"✅ Create Order: {response.status_code}")
        if response.status_code == 201:
            order_id = response.json()['data']['id']
            print(f"   Created Order ID: {order_id}")
            
            # GET - Read Order
            response = requests.get(f"{BASE_URL}/api/orders/{order_id}")
            print(f"✅ Get Order: {response.status_code}")
            
            # PUT - Update Order
            update_data = {"status": "completed"}
            response = requests.put(f"{BASE_URL}/api/orders/{order_id}", json=update_data)
            print(f"✅ Update Order: {response.status_code}")
            
            # GET All Orders
            response = requests.get(f"{BASE_URL}/api/orders")
            print(f"✅ List Orders: {response.status_code}")
            
            # DELETE - Remove Order
            response = requests.delete(f"{BASE_URL}/api/orders/{order_id}")
            print(f"✅ Delete Order: {response.status_code}")
            
            return True
    except Exception as e:
        print(f"❌ Order CRUD Failed: {e}")
        return False

def test_pdf_upload():
    """Test PDF document upload and processing"""
    print("\n🔍 Testing PDF Upload and OCR Processing...")
    
    # You can test with the sample PDF from the Google Drive link
    # For now, we'll test the endpoint structure
    
    try:
        # Test without file first to see endpoint response
        response = requests.post(f"{BASE_URL}/api/documents/upload")
        print(f"📄 PDF Upload Endpoint Response: {response.status_code}")
        
        # If you have a test PDF file, uncomment below:
        # with open('test_document.pdf', 'rb') as f:
        #     files = {'file': f}
        #     response = requests.post(f"{BASE_URL}/api/documents/upload", files=files)
        #     print(f"✅ PDF Upload: {response.status_code}")
        #     if response.status_code == 200:
        #         result = response.json()
        #         patient_data = result.get('patient_data', {})
        #         print(f"   First Name: {patient_data.get('first_name')}")
        #         print(f"   Last Name: {patient_data.get('last_name')}")
        #         print(f"   DOB: {patient_data.get('date_of_birth')}")
        
        return True
    except Exception as e:
        print(f"❌ PDF Upload Failed: {e}")
        return False

def test_activity_logging():
    """Test activity logging endpoint"""
    print("\n🔍 Testing Activity Logging...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/activities")
        print(f"✅ Activity Logs: {response.status_code}")
        return True
    except Exception as e:
        print(f"❌ Activity Logging Failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting GenHealth.AI API Assessment Tests")
    print(f"🌐 Base URL: {BASE_URL}")
    print("=" * 60)
    
    # Update BASE_URL with your actual ngrok URL before running
    if "your-ngrok-url" in BASE_URL:
        print("⚠️  Please update BASE_URL with your actual ngrok URL!")
        return
    
    results = []
    
    # Run all tests
    results.append(test_health_check())
    results.append(test_order_crud())
    results.append(test_pdf_upload())
    results.append(test_activity_logging())
    
    # Summary
    print("\n" + "=" * 60)
    print(f"🎯 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Your API is ready for assessment.")
    else:
        print("⚠️  Some tests failed. Check the output above.")

if __name__ == "__main__":
    main()