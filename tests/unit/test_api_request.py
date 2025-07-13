#!/usr/bin/env python3
"""Test script to verify API functionality"""

import requests
import json
import time
import os

# Read API key from environment
API_KEY = "JJ_Yacbos|1!R~$_b~ALhxAz8_idU123"
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"✅ Health Status: {response.status_code}")
        print(f"📊 Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_summarize_async():
    """Test async summarization"""
    print("\n📝 Testing async summarization...")

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        'title': 'Elon Musk Tesla Tariffs News',
        'text': '''New York CNN — Tesla, the electric car company run by Elon Musk, said this week that retaliatory tariffs against US manufacturers could harm its operations and that the US should carefully consider its trade policies, a break from Musk ally President Donald Trump. In a March 11 letter to US Trade Representative Jamieson Greer, company representatives wrote: As a U.S. manufacturer and exporter, Tesla encourages USTR to consider the downstream impacts of certain proposed actions taken to address unfair trade practices. While Tesla recognizes and supports the importance of fair trade, the assessment undertaken by USTR of potential actions to rectify unfair trade should also take into account exports from the United States, the letter said. It warned that past US tariff actions have resulted in immediate reactions by the targeted countries, such as increased tariffs on EVs imported into those countries. The letter is unsigned. Musk Tesla has basked in the limelight under the Trump White House, which has put tariffs at the forefront of its economic policy. On Tuesday, the president posed in front of a fleet of Teslas, saying he would purchase one full price. As he spoke, Trump was holding what resembled a Tesla showroom pitch with a list of vehicle prices. But Tesla shares have been in a sharp slump recently, erasing their gains since Election Day. The company European sales dropped 45% in January, according to the European Automobile Manufacturers Association. And despite his outsized role in the government, Musk has become a polarizing political figure. Tesla shares closed down 3% Thursday.'''
    }

    try:
        # Submit article for summarization
        response = requests.post(f"{BASE_URL}/summarize", headers=headers, json=data)
        print(f"✅ Submit Status: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"📋 Task ID: {task_id}")
            print(f"⏳ Status: {result['status']}")

            # Check task status
            print("\n⏳ Waiting for completion...")
            for i in range(30):  # Wait up to 30 seconds
                time.sleep(2)
                status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)
                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Status: {status_data['status']}")

                    if status_data['status'] == 'completed':
                        print("✅ Summarization completed!")
                        print(f"⚡ Processing time: {status_data.get('processing_time', 'N/A')} seconds")
                        print(f"📄 Summary:\n{status_data['summary']}")
                        return True
                    elif status_data['status'] == 'failed':
                        print(f"❌ Summarization failed: {status_data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    return False

            print("⏰ Timeout waiting for completion")
            return False
        else:
            print(f"❌ Submit failed: {response.status_code}")
            print(f"🔍 Error: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_authentication():
    """Test authentication"""
    print("\n🔐 Testing authentication...")

    # Test without API key
    response = requests.post(f"{BASE_URL}/summarize", json={'title': 'Test', 'text': 'Test content'})
    if response.status_code == 401:
        print("✅ Authentication required - working correctly")
    else:
        print(f"❌ Authentication test failed: {response.status_code}")
        return False

    # Test with invalid API key
    headers = {'Authorization': 'Bearer invalid-key'}
    response = requests.post(f"{BASE_URL}/summarize", headers=headers, json={'title': 'Test', 'text': 'Test content'})
    if response.status_code == 401:
        print("✅ Invalid API key rejected - working correctly")
        return True
    else:
        print(f"❌ Invalid API key test failed: {response.status_code}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting API Tests")
    print("=" * 50)

    success_count = 0
    total_tests = 3

    if test_health():
        success_count += 1

    if test_authentication():
        success_count += 1

    if test_summarize_async():
        success_count += 1

    print("\n" + "=" * 50)
    print(f"📊 Test Results: {success_count}/{total_tests} passed")

    if success_count == total_tests:
        print("🎉 All tests passed! API is working correctly!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
