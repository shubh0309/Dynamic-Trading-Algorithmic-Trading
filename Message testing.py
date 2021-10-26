
import requests
resp = requests.post('https://textbelt.com/text', {
  'phone': '+919792836413',
  'message': 'Hello world',
  'key': 'textbelt',
})
print(resp.json())