import pandas as pd
from datetime import datetime

# Load the dataset, Original Kaggle train.csv
df = pd.read_csv("train.csv")

# Filter rows with target > 0
df = df[df['target'] > 0]

# Convert created_date to a uniform datetime format
df['created_date'] = pd.to_datetime(df['created_date'], errors='coerce')

# Drop rows with invalid date format
df = df.dropna(subset=['created_date'])

# Sort by created_date
df = df.sort_values(by='created_date')

# Keep only necessary columns
required_columns = [
    'comment_text', 'target', 'severe_toxicity', 'obscene', 'identity_attack', 
    'insult', 'threat', 'sexual_explicit', 'created_date'
]
df = df[required_columns]

# Split the data: 90% train, 10% validation
train_size = int(0.9 * len(df))
train_df = df.iloc[:train_size]
val_df = df.iloc[train_size:]

# Save to CSV
train_df.to_csv("training.csv", index=False)
val_df.to_csv("validation.csv", index=False)

print(f"✅ Preprocessing complete! Training samples: {len(train_df)}, Validation samples: {len(val_df)}")
