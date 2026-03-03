import requests
import time

class BitcraftAPI:
    def __init__(self, user_agent="BitJita (translator-app)"):
        self.base_url = "https://bitjita.com/api"
        self.headers = {
            "User-Agent": user_agent,
            "x-app-identifier": user_agent
        }
        self.last_timestamp = None

    def get_messages(self, limit=20):
        params = {"limit": limit}
        if self.last_timestamp:
            params["since"] = self.last_timestamp

        try:
            response = requests.get(f"{self.base_url}/chat", params=params, headers=self.headers)
            response.raise_for_status()
            data = response.json()
            
            messages = data.get("messages", [])
            if messages:
                # Update last_timestamp from the newest message (first in list)
                self.last_timestamp = messages[0].get("timestamp")
            
            return messages
        except Exception as e:
            print(f"Error fetching messages: {e}")
            return []

if __name__ == "__main__":
    api = BitcraftAPI()
    print("Fetching initial messages...")
    msgs = api.get_messages(limit=5)
    for m in msgs:
        print(f"[{m.get('timestamp')}] {m.get('username')}: {m.get('text')}")
