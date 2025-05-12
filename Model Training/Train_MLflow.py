import pandas as pd
import time
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
from torch.optim import AdamW
from tqdm import tqdm
import mlflow
import mlflow.pytorch

# Set up MLflow experiment
mlflow.set_experiment("toxicity_classification")

# Load and filter dataset
df = pd.read_csv("train.csv", nrows=100000)
df['toxic'] = (df['target'] >= 0.5).astype(int)
subtype_labels = ['severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat', 'sexual_explicit']
df[subtype_labels] = (df[subtype_labels] >= 0.5).astype(int)

# Load tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Define the custom dataset class
class ToxicityDataset(Dataset):
    def __init__(self, df):
        self.texts = df['comment_text'].tolist()
        self.targets = df['toxic'].tolist()
        self.labels = df[subtype_labels].values

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = tokenizer(self.texts[idx], padding='max_length', truncation=True, max_length=128, return_tensors='pt')
        return {
            'input_ids': enc['input_ids'].squeeze(),
            'attention_mask': enc['attention_mask'].squeeze(),
            'toxicity': torch.tensor(self.targets[idx], dtype=torch.float),
            'labels': torch.tensor(self.labels[idx], dtype=torch.float)
        }

# Define the model
class ToxicityClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert = BertModel.from_pretrained("bert-base-uncased")
        self.tox_head = nn.Linear(768, 1)
        self.subtype_head = nn.Linear(768, len(subtype_labels))

    def forward(self, input_ids, attention_mask):
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask).pooler_output
        toxicity_score = torch.sigmoid(self.tox_head(out)).squeeze(1)
        subtype_pred = torch.sigmoid(self.subtype_head(out))
        return toxicity_score, subtype_pred

# Set up device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ToxicityClassifier().to(device)
optimizer = AdamW(model.parameters(), lr=2e-5)
bce_loss = nn.BCELoss()
train_loader = DataLoader(ToxicityDataset(df), batch_size=32, shuffle=True)

# Start MLflow run
with mlflow.start_run():
    mlflow.log_param("batch_size", 64)
    mlflow.log_param("epochs", 1)
    mlflow.log_param("learning_rate", 2e-5)

    start_time = time.time()
    torch.cuda.reset_peak_memory_stats()

    for epoch in range(1):
        model.train()
        total_loss, correct, total = 0, 0, 0
        loop = tqdm(train_loader, desc=f"Epoch {epoch+1}")

        for step, batch in enumerate(loop):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            toxicity = batch['toxicity'].to(device)
            labels = batch['labels'].to(device)

            optimizer.zero_grad()
            tox_pred, subtype_pred = model(input_ids, attention_mask)

            loss_tox = bce_loss(tox_pred, toxicity)
            loss_subtype = bce_loss(subtype_pred, labels)
            loss = loss_tox + loss_subtype
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            preds = (tox_pred >= 0.5).float()
            correct += (preds == toxicity).sum().item()
            total += toxicity.size(0)

        avg_loss = total_loss / len(train_loader)
        accuracy = 100 * correct / total
        mlflow.log_metric("train_loss", avg_loss)
        mlflow.log_metric("train_accuracy", accuracy)

        print(f"✅ Epoch {epoch+1} | Accuracy: {accuracy:.2f}% | Loss: {avg_loss:.4f}")
        torch.save(model.state_dict(), "toxicity.pth")

    end_time = time.time()
    training_time = end_time - start_time
    mlflow.log_metric("training_time_sec", training_time)

    if device.type == "cuda":
        peak_mem_MB = torch.cuda.max_memory_allocated(device) / (1024 ** 2)
        mlflow.log_metric("peak_gpu_mem_MB", peak_mem_MB)

    mlflow.pytorch.log_model(model, "Toxicity")
