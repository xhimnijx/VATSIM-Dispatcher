import requests

url = "https://api.vatsim.net/v2/atc/online"

payload={}
headers = {
  'Accept': 'application/json'
}

response = requests.request("GET", url, headers=headers, data=payload)

with open('heatmap generator/current_vatsim_data.json', 'w') as file:
    file.write(response.text)
