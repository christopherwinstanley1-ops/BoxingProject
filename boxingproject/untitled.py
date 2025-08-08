import requests
import pandas as pd

# 🔐 Replace this with your actual API key
API_KEY = "89c61046d8ed0ccf9ebfa3996ef443cc"

# 📡 API endpoint and parameters
url = "https://api.the-odds-api.com/v4/sports/boxing_boxing/odds"
params = {
    "apiKey": API_KEY,
    "regions": "us,uk,eu",       # Betting regions
    "markets": "h2h",            # "head-to-head" odds
    "oddsFormat": "decimal"      # You can also use 'american' or 'fractional'
}

# 🚀 Send the GET request
response = requests.get(url, params=params)

# 📦 Convert response to JSON
if response.status_code == 200:
    data = response.json()
    print(f"Received {len(data)} events.")
else:
    print("Error:", response.status_code, response.text)
