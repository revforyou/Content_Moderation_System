import pandas as pd
import time
import requests
import random

DATA_PATH = "/mnt/object/production.csv"

API_URL = "http://localhost:8000/predict"

MIN_DELAY = 1
MAX_DELAY = 3

def main():
    print("📦 Loading production data...")
    df = pd.read_csv(DATA_PATH)
    total = len(df)

    for i, row in df.iterrows():
        comment = row["comment_text"]

        payload = {"text": comment}
        try:
            response = requests.post(API_URL, json=payload)
            result = response.json()

            print(f"✅ Sent [{i+1}/{total}]:", payload["text"][:60], "→", result)
        except Exception as e:
            print(f"❌ Error on row {i+1}: {e}")

        time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))

    print("✅ Simulation complete.")

if __name__ == "__main__":
    main()
