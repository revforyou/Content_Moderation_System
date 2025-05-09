import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertModel
from torch.optim import AdamW
from tqdm import tqdm
import argparse
import os

# ========== Constants ==========
SUBTYPE_LABELS = ['severe_toxicity', 'obscene', 'identity_attack', 'insult', 'threat', 'sexual_explicit']
MAX_LEN = 128
BATCH_SIZE = 32
LR = 2e-5
EPOCHS = 3
MODEL_NAME = 'bert-base-uncased'
SAVE_PATH = 'toxicity.pth'


# ========== Dataset ==========
class ToxicityDataset(Dataset):
    def __init__(self, df, tokenizer):
        self.texts = df['comment_text'].tolist()
        self.targets = df['toxic'].tolist()
        self.labels = df[SUBTYPE_LABELS].values
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        enc = self.tokenizer(
            self.texts[idx],
            padding='max_length',
            truncation=True,
            max_length=MAX_LEN,
            return_tensors='pt'
        )
        return {
            'input_ids': enc['input_ids'].squeeze(),
            'attention_mask': enc['attention_mask'].squeeze(),
            'toxicity': torch.tensor(self.targets[idx], dtype=torch.float),
            'labels': torch.tensor(self.labels[idx], dtype=torch.float)
        }


# ========== Model ==========
class ToxicityClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.bert = BertModel.from_pretrained(MODEL_NAME)
        self.tox_head = nn.Linear(768, 1)
        self.subtype_head = nn.Linear(768, len(SUBTYPE_LABELS))

    def forward(self, input_ids, attention_mask):
        out = self.bert(input_ids=input_ids, attention_mask=attention_mask).pooler_output
        tox_score = torch.sigmoid(self.tox_head(out)).squeeze(1)
        subtype_pred = torch.sigmoid(self.subtype_head(out))
        return tox_score, subtype_pred


# ========== Train Function ==========
def train(args):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    # Load and preprocess data
    df = pd.read_csv(args.data_path)
    df['toxic'] = (df['target'] >= 0.5).astype(int)
    df[SUBTYPE_LABELS] = (df[SUBTYPE_LABELS] >= 0.5).astype(int)

    tokenizer = BertTokenizer.from_pretrained(MODEL_NAME)
    dataset = ToxicityDataset(df, tokenizer)
    dataloader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    model = ToxicityClassifier().to(device)
    optimizer = AdamW(model.parameters(), lr=LR)
    bce_loss = nn.BCELoss()

    for epoch in range(EPOCHS):
        model.train()
        total_loss, correct, total = 0, 0, 0

        loop = tqdm(dataloader, desc=f"Epoch {epoch+1}")
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

            loop.set_postfix({
                "loss": f"{loss.item():.3f}",
                "acc": f"{100*correct/total:.2f}%",
                "step": step
            })

        print(f"✅ Epoch {epoch+1} | Accuracy: {100*correct/total:.2f}% | Avg Loss: {total_loss/len(dataloader):.4f}")
        torch.save(model.state_dict(), os.path.join(args.output_dir, SAVE_PATH))


# ========== Entry Point ==========
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_path', type=str, default="train_clean.csv", help="Path to training CSV file")
    parser.add_argument('--output_dir', type=str, default=".", help="Directory to save model")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    train(args)
