import requests

url = "http://20.244.56.144/evaluation-service/register"
payload = {
  "accessCode": "<ACCESS_CODE>",
  "email": "<YOUR_EMAIL>",
  "name": "<YOUR_NAME>",
  "mobileNo": "<YOUR_10_DIGIT_MOBILE>",
  "githubUsername": "<YOUR_GITHUB_USERNAME>",  
  "rollNo": "<YOUR_ROLL_NO>",
  # "companyName": "<YOUR_COMPANY>"
}

r = requests.post(url, json=payload, timeout=15)
print(r.status_code, r.text)
data = r.json()
print("clientId:", data.get("clientId") or data.get("clientID"))
print("clientSecret:", data.get("clientSecret"))
print("token:", data.get("access_token") or data.get("token"))