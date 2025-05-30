# -*- coding: utf-8 -*-

from flask import Flask, request, render_template
import torch
import torch.nn as nn
from transformers import BertTokenizer, BertModel
import os

app = Flask(__name__)

# Define labels
subtype_labels = ['severe_toxicity','obscene', 'identity_attack','insult', 'threat', 'sexual_explicit']

# Load tokenizer
tokenizer = BertTokenizer.from_pretrained("bert-base-uncased")

# Model
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

# Load model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = ToxicityClassifier().to(device)
model.load_state_dict(torch.load("toxicity.pth", map_location=device))
model.eval()

@app.route("/", methods=["GET", "POST"])
def index():
    result = {}
    if request.method == "POST":
        comment = request.form["comment"]
        enc = tokenizer(comment, return_tensors="pt", padding='max_length', truncation=True, max_length=128)
        input_ids = enc["input_ids"].to(device)
        attention_mask = enc["attention_mask"].to(device)

        with torch.no_grad():
            tox_score, subtype_pred = model(input_ids, attention_mask)
            tox_score = tox_score.item()
            subtype_probs = subtype_pred[0].cpu().numpy().tolist()

        classification = "Inappropriate" if tox_score >= 0.5 else "Appropriate"
        subtype_results = [(label.title(), f"{100*p:.2f}%") for label, p in zip(subtype_labels, subtype_probs)]

        result = {
            "comment": comment,
            "toxicity": f"{tox_score * 100:.2f}%",
            "classification": classification,
            "subtypes": subtype_results,
            "conf_appropriate": f"{(1 - tox_score) * 100:.2f}",
            "conf_inappropriate": f"{tox_score * 100:.2f}",
        }

    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)

