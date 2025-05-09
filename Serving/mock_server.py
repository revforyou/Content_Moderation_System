from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Input(BaseModel):
    text: str

@app.post("/predict")
def predict(input: Input):
    return {"prediction": "not_toxic", "confidence": 0.87}
