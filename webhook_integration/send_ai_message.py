import requests
import json

url = "https://graph.facebook.com/v22.0/me/messages"

payload = json.dumps({
  "messaging_type": "MESSAGE_TAG",
  "tag": "ACCOUNT_UPDATE",
  "recipient": {
    "id": 26796838439922692
  },
  "message": {
    "text": "test facebook"
  }
})
headers = {
  'Content-Type': 'application/json',
  'Authorization': 'Bearer EAAK0ZCfTww3YBQzv90ZCcTeB4leiZBXGeGxZAAIU1KbDyh1wGv7JPfE29WAdyTq9uT2jJZBxZAQV4wVPguPlkyMLHHDSkSGYqTbZB7jWTGPJbzb2FU7qSEASbdlmogFZB1jkMNZCJLKvz8kRefDtDWhUrOi4NtZAKNaEkhZBtUd5ziA5pZCZCLf8n3tP5nEuY4zCtaKSLY6VZBt7Jq'
}

response = requests.request("POST", url, headers=headers, data=payload)

print(response.text)
