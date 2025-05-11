import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer
from tqdm import tqdm

# Load test data
df_test = pd.read_csv("test.csv")

# Tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Define same subtype labels as during training
subtype_labels = ['severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat', 'sexual_explicit']

# Dataset
class TestDataset(Dataset):
    def __init__(self, df):
        self.texts = df['comment_text'].tolist()

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = tokenizer(self.texts[idx], padding='max_length', truncation=True, max_length=128, return_tensors='pt')
        return {
            'input_ids': enc['input_ids'].squeeze(),
            'attention_mask': enc['attention_mask'].squeeze()
        }

# Load model
class ToxicityClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        from transformers import BertModel
        self.bert = BertModel.from_pretrained("bert-base-uncased")
        self.tox_head = nn.Linear(768, 1)
        self.subtype_head = nn.Linear(768, len(subtype_labels))

    def forward(self, input_ids, attention_mask):
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask).pooler_output
        toxicity_score = torch.sigmoid(self.tox_head(out)).squeeze(1)
        subtype_pred = torch.sigmoid(self.subtype_head(out))
        return toxicity_score, subtype_pred

# Setup
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ToxicityClassifier().to(device)
model.load_state_dict(torch.load("toxicity.pth", map_location=device))
model.eval()

# DataLoader
test_loader = DataLoader(TestDataset(df_test), batch_size=32)

# Run inference
tox_scores = []
subtype_outputs = []

with torch.no_grad():
    for batch in tqdm(test_loader, desc="Running Inference"):
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        tox_pred, subtype_pred = model(input_ids, attention_mask)

        tox_scores.extend(tox_pred.cpu().tolist())
        subtype_outputs.extend(subtype_pred.cpu().tolist())

# Create output DataFrame
output_df = pd.DataFrame({
    "comment_text": df_test['comment_text'],
    "toxicity_score": tox_scores,
})

# Add subtype predictions
for i, label in enumerate(subtype_labels):
    output_df[label] = [row[i] for row in subtype_outputs]

# Apply thresholds to get "labels"
output_df["toxicity_label"] = output_df["toxicity_score"].apply(lambda x: "Inappropriate" if x >= 0.5 else "Appropriate")
output_df["subtypes"] = output_df[subtype_labels].apply(lambda row: [label for i, label in enumerate(subtype_labels) if row[i] >= 0.5], axis=1)

# Save
output_df.to_csv("inference_results.csv", index=False)
print("✅ Inference completed. Results saved to inference_results.csv")
