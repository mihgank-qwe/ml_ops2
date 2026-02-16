"""FastAPI-приложение для предсказания дефолта"""

from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI
from pydantic import BaseModel

# Загрузка модели при старте
project_root = Path(__file__).resolve().parents[2]
model_path = project_root / "models" / "credit_default_model.pkl"

app = FastAPI(title="Credit Default Prediction API")

if model_path.exists():
    model = joblib.load(model_path)
else:
    model = None


# Схема входных данных
class ClientData(BaseModel):
    """Признаки клиента для предсказания"""

    LIMIT_BAL: float
    SEX: int
    EDUCATION: int
    MARRIAGE: int
    AGE: int
    PAY_0: int
    PAY_2: int
    PAY_3: int
    PAY_4: int
    PAY_5: int
    PAY_6: int
    BILL_AMT1: float
    BILL_AMT2: float
    BILL_AMT3: float
    BILL_AMT4: float
    BILL_AMT5: float
    BILL_AMT6: float
    PAY_AMT1: float
    PAY_AMT2: float
    PAY_AMT3: float
    PAY_AMT4: float
    PAY_AMT5: float
    PAY_AMT6: float
    PAY_MEAN: float
    PAY_MAX: int
    PAY_MIN: int
    BILL_AMT_MEAN: float
    BILL_AMT_MAX: float
    PAY_AMT_MEAN: float
    PAY_AMT_SUM: float
    PAY_TO_BILL_RATIO: float


@app.post("/predict")
def predict(data: ClientData):
    """Предсказывает вероятность дефолта"""
    if model is None:
        return {"error": "Модель не загружена. Сначала обучите модель"}

    input_data = pd.DataFrame([data.model_dump()])
    prediction = model.predict(input_data)
    probability = model.predict_proba(input_data)[0][1]

    return {
        "default_prediction": int(prediction[0]),
        "default_probability": float(probability),
    }


@app.get("/")
def read_root():
    """Проверка работы API"""
    return {"message": "Credit Default Prediction API работает"}
