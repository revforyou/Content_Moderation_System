import pandas as pd
from sklearn.model_selection import train_test_split

df = pd.read_csv("train.csv", usecols=["comment_text", "target", "created_date"])
df["created_date"] = pd.to_datetime(df["created_date"], format='mixed')
df = df.sort_values("created_date")

split_index = int(len(df) * 0.9)
train_val = df.iloc[:split_index]
production = df.iloc[split_index:]

train, val = train_test_split(train_val, test_size=0.1111, random_state=42)

train.to_csv("train.csv", index=False)
val.to_csv("val.csv", index=False)
production.to_csv("production.csv", index=False)
