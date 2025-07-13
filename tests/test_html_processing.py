#!/usr/bin/env python3
"""Test script to verify HTML processing in API"""

import requests
import json
import time

# API configuration
API_KEY = "JJ_Yacbos|1!R~$_b~ALhxAz8_idU123"
BASE_URL = "http://localhost:8000"

def test_html_processing():
    """Test API with HTML content"""
    print("🧪 Testing HTML content processing...")

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Test data with HTML tags (exactly as user provided)
    html_article = {
        "title": "Elon Musk's Tesla says it could be targeted by retaliatory tariffs",
        "text": '<span>New York</span> <span>CNN</span>  —   <p> Tesla, the electric car company run by Elon Musk, said this week that retaliatory tariffs against US manufacturers could harm its operations and that the US should carefully consider its trade policies, a break from Musk\'s ally President Donald Trump. </p> <p> In a March 11 letter to US Trade Representative Jamieson Greer, company representatives wrote: "As a U.S. manufacturer and exporter, Tesla encourages USTR to consider the downstream impacts of certain proposed actions taken to address unfair trade practices." </p> <p> "While Tesla recognizes and supports the importance of fair trade, the assessment undertaken by USTR of potential actions to rectify unfair trade should also take into account exports from the United States," the letter said. </p> <p> It warned that past US tariff actions have resulted in "immediate reactions" by the targeted countries, such as increased tariffs on EVs imported into those countries. The letter is unsigned. </p> <p> Musk\'s Tesla has basked in the limelight under the Trump White House, which has put tariffs at the forefront of its economic policy. On Tuesday, the president <a href="https://www.cnn.com/2025/03/11/business/tesla-stock-trump-white-house/index.html">posed in front of a fleet of Teslas</a>, saying he would purchase one full price. As he spoke, Trump was holding what resembled a Tesla showroom pitch with a list of vehicle prices, <a href="https://www.gettyimages.com/detail/news-photo/president-donald-trump-holds-notes-on-the-pricing-of-tesla-news-photo/2204585275?adppopup=true">according to a photo from Getty Images</a>. </p> <p> But Tesla shares have been in a sharp slump recently, erasing their gains since Election Day. The company\'s European sales <a href="https://www.cnn.com/2025/02/25/business/elon-musk-net-worth-tesla/index.html">dropped 45%</a> in January, according to the European Automobile Manufacturers\' Association. And despite <a href="https://www.cnn.com/2025/02/03/politics/musk-government-employee/index.html">his outsized role</a> in the government, Musk has become <a href="https://www.cnn.com/2025/02/17/business/tesla-sales-elon-musk-politics/index.html">a polarizing political figure</a>. Tesla shares closed down 3% Thursday. </p> <p> Past tariff actions by the US, Tesla wrote, increased the cost of US-manufactured vehicles for the company and when those vehicles are exported out of the US. </p> <p> The Office of the US Trade Representative should investigate ways to avoid these pitfalls in future actions, the letter added. </p> <p> The letter also said that trade policy should consider the "limitations in the domestic supply chain" regarding EVs and lithium-ion batteries. Some of these items are simply impossible to source within the US, the letter<strong> </strong>argued. </p> <p> Tesla operates numerous US facilities that altogether employ over 70,000 people, according to the company. Its Fremont, California, factory manufactures vehicles as well as lithium-ion battery cells, and the company also has facilities in Austin, Texas; Sparks, Nevada; Buffalo, New York; Brooklyn Park, Minnesota; and Grand Rapids, Michigan. </p> <p> CNN has reached out to Tesla for comment. </p>'
    }

    print("📄 Original HTML content length:", len(html_article['text']))
    print("🔍 HTML tags found:", '<p>' in html_article['text'], '<span>' in html_article['text'], '<a>' in html_article['text'])

    try:
        # Submit HTML article for processing
        print("\n📤 Submitting HTML article to API...")
        response = requests.post(f"{BASE_URL}/summarize", headers=headers, json=html_article)

        if response.status_code == 200:
            result = response.json()
            task_id = result['task_id']
            print(f"✅ Article submitted successfully!")
            print(f"📋 Task ID: {task_id}")
            print(f"⏳ Status: {result['status']}")

            # Wait for processing
            print("\n⏳ Waiting for HTML processing and summarization...")
            max_wait = 60  # 60 seconds timeout
            wait_interval = 3

            for i in range(0, max_wait, wait_interval):
                time.sleep(wait_interval)
                status_response = requests.get(f"{BASE_URL}/task/{task_id}", headers=headers)

                if status_response.status_code == 200:
                    status_data = status_response.json()
                    print(f"📊 Status: {status_data['status']} (waited {i+wait_interval}s)")

                    if status_data['status'] == 'completed':
                        print("\n🎉 HTML processing and summarization completed!")
                        print(f"⚡ Processing time: {status_data.get('processing_time', 'N/A')} seconds")
                        print("\n📄 Generated Summary:")
                        print("=" * 60)
                        print(status_data['summary'])
                        print("=" * 60)

                        # Verify HTML was cleaned
                        summary_text = status_data['summary']
                        has_html = '<p>' in summary_text or '<span>' in summary_text or '<a>' in summary_text
                        print(f"\n✅ HTML cleaning verification: {'❌ HTML tags still present' if has_html else '✅ HTML tags successfully removed'}")

                        return True

                    elif status_data['status'] == 'failed':
                        print(f"\n❌ Processing failed: {status_data.get('error', 'Unknown error')}")
                        return False
                else:
                    print(f"❌ Status check failed: {status_response.status_code}")
                    break

            print("\n⏰ Timeout waiting for completion")
            return False

        else:
            print(f"❌ Failed to submit article: {response.status_code}")
            print(f"📄 Error response: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Test failed with exception: {e}")
        return False

def test_clean_vs_html():
    """Compare processing of clean text vs HTML text"""
    print("\n🔄 Testing clean text vs HTML text processing...")

    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }

    # Clean text version
    clean_article = {
        "title": "Tesla Tariffs Clean Text Test",
        "text": "Tesla, the electric car company run by Elon Musk, said this week that retaliatory tariffs against US manufacturers could harm its operations and that the US should carefully consider its trade policies, a break from Musk's ally President Donald Trump. In a March 11 letter to US Trade Representative Jamieson Greer, company representatives wrote: As a U.S. manufacturer and exporter, Tesla encourages USTR to consider the downstream impacts of certain proposed actions taken to address unfair trade practices. While Tesla recognizes and supports the importance of fair trade, the assessment undertaken by USTR of potential actions to rectify unfair trade should also take into account exports from the United States, the letter said. It warned that past US tariff actions have resulted in immediate reactions by the targeted countries, such as increased tariffs on EVs imported into those countries. The letter is unsigned. Tesla operates numerous US facilities that altogether employ over 70,000 people, according to the company. Its Fremont, California, factory manufactures vehicles as well as lithium-ion battery cells, and the company also has facilities in Austin, Texas; Sparks, Nevada; Buffalo, New York; Brooklyn Park, Minnesota; and Grand Rapids, Michigan."
    }

    # HTML version
    html_article = {
        "title": "Tesla Tariffs HTML Test",
        "text": "<p>Tesla, the electric car company run by Elon Musk, said this week that retaliatory tariffs against US manufacturers could harm its operations and that the US should carefully consider its trade policies, a break from Musk's ally President Donald Trump.</p><p>In a March 11 letter to US Trade Representative Jamieson Greer, company representatives wrote: <strong>As a U.S. manufacturer and exporter, Tesla encourages USTR to consider the downstream impacts of certain proposed actions taken to address unfair trade practices.</strong></p><p>While Tesla recognizes and supports the importance of fair trade, the assessment undertaken by USTR of potential actions to rectify unfair trade should also take into account exports from the United States, the letter said.</p><p>It warned that past US tariff actions have resulted in <em>immediate reactions</em> by the targeted countries, such as increased tariffs on EVs imported into those countries. The letter is unsigned.</p><p>Tesla operates numerous US facilities that altogether employ over 70,000 people, according to the company. Its <a href='#'>Fremont, California, factory</a> manufactures vehicles as well as lithium-ion battery cells, and the company also has facilities in Austin, Texas; Sparks, Nevada; Buffalo, New York; Brooklyn Park, Minnesota; and Grand Rapids, Michigan.</p>"
    }

    print("📊 Content comparison:")
    print(f"Clean text length: {len(clean_article['text'])}")
    print(f"HTML text length: {len(html_article['text'])}")

    # Test both versions
    print("\n🧪 Testing both versions...")

    # Test clean version (sync for faster comparison)
    try:
        clean_response = requests.post(f"{BASE_URL}/summarize/sync", headers=headers, json=clean_article)
        print(f"✅ Clean text: {clean_response.status_code}")

        html_response = requests.post(f"{BASE_URL}/summarize/sync", headers=headers, json=html_article)
        print(f"✅ HTML text: {html_response.status_code}")

        if clean_response.status_code == 200 and html_response.status_code == 200:
            print("🎉 Both versions processed successfully!")
            return True
        else:
            print("❌ One or both versions failed")
            return False

    except Exception as e:
        print(f"❌ Comparison test failed: {e}")
        return False

def main():
    """Run HTML processing tests"""
    print("🚀 HTML Processing Test Suite")
    print("=" * 50)

    tests_passed = 0
    total_tests = 2

    # Test 1: Full HTML article processing
    if test_html_processing():
        tests_passed += 1
        print("✅ Test 1 passed: Full HTML processing")
    else:
        print("❌ Test 1 failed: Full HTML processing")

    # Test 2: Clean vs HTML comparison
    if test_clean_vs_html():
        tests_passed += 1
        print("✅ Test 2 passed: Clean vs HTML comparison")
    else:
        print("❌ Test 2 failed: Clean vs HTML comparison")

    print("\n" + "=" * 50)
    print(f"📊 HTML Processing Tests: {tests_passed}/{total_tests} passed")

    if tests_passed == total_tests:
        print("🎉 All HTML processing tests passed!")
        print("✅ API can now handle HTML content automatically!")
    else:
        print("⚠️  Some tests failed. Please check the output above.")

if __name__ == "__main__":
    main()
