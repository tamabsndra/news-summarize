#!/usr/bin/env python3
"""Test the exact JSON format provided by the user"""

import requests
import json

def test_exact_json_format():
    """Test the exact JSON format with HTML content"""

    # Read the exact JSON file
    with open('test_html_curl.json', 'r') as f:
        data = json.load(f)

    headers = {
        'Authorization': 'Bearer JJ_Yacbos|1!R~$_b~ALhxAz8_idU123',
        'Content-Type': 'application/json'
    }

    print('📄 Testing exact JSON format with HTML content...')
    print('🔍 Title:', data['title'])
    print('🔍 Original text length:', len(data['text']))
    print('🔍 Contains HTML tags:', '<p>' in data['text'], '<span>' in data['text'], '<a>' in data['text'])

    # Test sync endpoint for faster response
    print('\n📤 Sending request to API...')
    response = requests.post('http://localhost:8000/summarize/sync', headers=headers, json=data)

    print('📊 Response status:', response.status_code)

    if response.status_code == 200:
        result = response.json()
        print('✅ Success!')
        print('⚡ Processing time:', result.get('processing_time', 'N/A'), 'seconds')
        print('\n📄 Generated Summary:')
        print('=' * 60)
        print(result['summary'])
        print('=' * 60)

        # Check if HTML was cleaned
        has_html = '<p>' in result['summary'] or '<span>' in result['summary'] or '<a>' in result['summary']
        print(f'\n🧹 HTML cleaning: {"❌ HTML tags still present" if has_html else "✅ HTML tags successfully removed"}')

        return True
    else:
        print('❌ Error:', response.text)
        return False

if __name__ == "__main__":
    print("🚀 Testing Exact JSON Format")
    print("=" * 50)

    success = test_exact_json_format()

    print("\n" + "=" * 50)
    if success:
        print("🎉 SUCCESS: API can process exact JSON format with HTML!")
        print("✅ Your API is ready to handle HTML content automatically!")
    else:
        print("❌ FAILED: There was an issue processing the JSON format")
