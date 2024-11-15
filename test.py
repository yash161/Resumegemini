import requests
import json

# Set your API key here
api_key = 'AIzaSyA4H3Rgyv_ycJYntgPa1y9BhzGGBKN8dNg'

# Define the endpoint URL
url = f'https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}'

# Define the payload
payload = {
    "contents": [
        {
            "parts": [
                {
                    "text": "Please help me edit my resume to emphasize concise presentation and niche-appropriate language. Target the specific pain points of prospective companies."
                }
            ]
        }
    ]
}

# Set the headers
headers = {
    'Content-Type': 'application/json'
}

# Make the POST request
response = requests.post(url, headers=headers, data=json.dumps(payload))

# Check the response
if response.status_code == 200:
    print("Response:", response.json())
else:
    print("Error:", response.status_code, response.text)
