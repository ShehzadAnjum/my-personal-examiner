"""
Test exam generation API endpoint
"""

import requests
import json

def test_exam_api():
    """Test the exam generation API endpoint"""
    url = "http://localhost:8001/api/exams"

    payload = {
        "subject_code": "9708",
        "exam_type": "PRACTICE",
        "question_count": 5,
        "strategy": "balanced"
    }

    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    print(f"🔍 Testing POST {url}")
    print(f"📦 Payload: {json.dumps(payload, indent=2)}\n")

    try:
        response = requests.post(url, json=payload, headers=headers)

        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response Headers:")
        for key, value in response.headers.items():
            print(f"   {key}: {value}")

        print(f"\n📝 Response Body:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)

        if response.status_code == 201:
            print("\n✅ Exam generated successfully!")
        else:
            print(f"\n❌ Error: {response.status_code}")

    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")

if __name__ == "__main__":
    test_exam_api()
