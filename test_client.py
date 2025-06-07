import requests

api_key = "12550dba-a2ef-4606-81a7-78c4dc21b69a"

try:
    response = requests.get("http://127.0.0.1:5000/quote", headers={
        "x-api-key": api_key
    })

    if response.status_code == 200:
        print("✅ Quote Response:", response.json())
    else:
        print("❌ Error:", response.status_code, response.text)
except Exception as e:
    print("⚠️ Error occurred:", e)
