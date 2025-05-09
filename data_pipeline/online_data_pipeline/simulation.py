import pandas as pd
import time
import requests
import random


DATA_PATH = "/mnt/object/production.csv"


API_URL = "http://localhost:8000/predict" 


DRY_RUN = True 


MIN_DELAY = 1
MAX_DELAY = 3

def simulate_stream():
    print(f"Reading production data from {DATA_PATH}")
    df = pd.read_csv(DATA_PATH)

    print(f"Total comments to stream: {len(df)}")

    for idx, row in df.iterrows():
        text = row.get("comment_text") or row.get("clean_text")
        if not isinstance(text, str):
            continue

        payload = {"text": text}

        if DRY_RUN:
            print(f"[DRY RUN] Would send: {payload}")
        else:
            try:
                response = requests.post(API_URL, json=payload)
                print(f"Sent comment {idx+1}/{len(df)} — Status: {response.status_code}")
            except Exception as e:
                print(f"Error sending comment {idx+1}: {e}")

        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY)) 

if __name__ == "__main__":
    simulate_stream()
