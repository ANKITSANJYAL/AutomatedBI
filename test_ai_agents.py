#!/usr/bin/env python3
"""
Test script to check what the AI agents are actually returning
"""

import requests
import json
import sys

# Test file upload and see what we get back
def test_upload():
    url = "http://localhost:5001/api/upload"
    
    # Upload the test CSV file
    with open("test_data.csv", "rb") as f:
        files = {"file": ("test_data.csv", f, "text/csv")}
        response = requests.post(url, files=files)
    
    print("=== UPLOAD RESPONSE ===")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        dataset_id = response.json().get("dataset_id")
        if dataset_id:
            test_analysis_results(dataset_id)
    
    return response.json()

def test_analysis_results(dataset_id):
    """Test what the analysis endpoint returns"""
    url = f"http://localhost:5001/api/analysis/{dataset_id}"
    response = requests.get(url)
    
    print("\n=== ANALYSIS RESULTS ===")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Response Keys: {list(data.keys())}")
        
        # Check if we have domain analysis
        if 'domain_analysis' in data:
            print(f"Domain Analysis: {json.dumps(data['domain_analysis'], indent=2)}")
        
        # Check dashboard design
        if 'dashboard_design' in data:
            print(f"Dashboard Design: {json.dumps(data['dashboard_design'], indent=2)}")
            
        # Check data quality
        if 'data_quality' in data:
            print(f"Data Quality Keys: {list(data['data_quality'].keys()) if data['data_quality'] else 'None'}")
            
    else:
        print(f"Error: {response.text}")

def test_dashboard_endpoint(dataset_id):
    """Test the dashboard endpoint specifically"""
    url = f"http://localhost:5001/api/dashboard/{dataset_id}"
    response = requests.get(url)
    
    print("\n=== DASHBOARD ENDPOINT ===")
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Dashboard Data: {json.dumps(data, indent=2)}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    try:
        result = test_upload()
        if "dataset_id" in result:
            test_dashboard_endpoint(result["dataset_id"])
    except Exception as e:
        print(f"Error: {e}")
