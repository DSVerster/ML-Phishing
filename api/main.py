from pathlib import Path

import numpy as np
import tensorflow as tf
from fastapi import FastAPI
from lime.lime_text import LimeTextExplainer
from pydantic import BaseModel

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "phishing_model.keras"
model = tf.keras.models.load_model(MODEL_PATH)

explainer = LimeTextExplainer(class_names=["Legit", "Phishing"])

app = FastAPI(title="Phishing Email Detector API")


class EmailRequest(BaseModel):
    text: str


def predict_proba(texts):
    probs = model(tf.constant([[t] for t in texts]), training=False).numpy().ravel()
    return np.column_stack([1 - probs, probs])


@app.get("/")
def home():
    return {"status": "API is running"}


@app.post("/predict")
def predict(email: EmailRequest):
    prob = float(predict_proba([email.text])[0][1])
    label = "phishing" if prob >= 0.5 else "legit"
    return {"label": label, "phishing_probability": round(prob, 4)}


@app.post("/explain")
def explain(email: EmailRequest):
    exp = explainer.explain_instance(email.text, predict_proba, num_features=8, num_samples=500)
    words = [{"word": word, "weight": round(float(weight), 4)} for word, weight in exp.as_list()]
    return {"words": words}