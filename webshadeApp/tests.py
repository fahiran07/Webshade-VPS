import requests
url = f"http://82.29.162.97/set-status-online/?connect-id=2094839"
response = requests.post(url)
response_data = response.json()
print(response_data)