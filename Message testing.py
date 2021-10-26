
import requests
resp = requests.post('https://textbelt.com/text', {
  'phone': '+917415579827',
  'message': 'Hello world',
  'key': 'textbelt',
})
print(resp.json())
