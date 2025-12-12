from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import os

# ================================
# 1. Cargar el modelo final (pipeline)
# ================================
MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/best_model.pkl")

app = FastAPI()

model = joblib.load(MODEL_PATH)

# ================================
# 2. Lista DEFINITIVA de features usados por el modelo
# ================================
FEATURE_COLS = [
    "open",
    "high_lag1", "low_lag1",
    "range_lag1",

    "volume",
    "volume_lag1", "volume_lag2",
    "volume_ma5_lag1",
    "volume_rel",

    "return_prev_close_lag1",
    "return_prev_close_lag2",
    "return_close_open_lag1",

    "volatility_5d_lag1",
    "volatility_5d_lag2",

    "sma_5", "ema_5",
    "momentum_5",
    "rsi_14",

    "macd", "macd_signal",

    "boll_position",

    "dist_max_5", "dist_min_5",

    "day_of_week",
    "month"
]

# ================================
# 3. Esquema Pydantic con todos los features
# ================================
class InputFeatures(BaseModel):
    open: float
    high_lag1: float
    low_lag1: float
    range_lag1: float

    volume: float
    volume_lag1: float
    volume_lag2: float
    volume_ma5_lag1: float
    volume_rel: float

    return_prev_close_lag1: float
    return_prev_close_lag2: float
    return_close_open_lag1: float

    volatility_5d_lag1: float
    volatility_5d_lag2: float

    sma_5: float
    ema_5: float
    momentum_5: float
    rsi_14: float

    macd: float
    macd_signal: float

    boll_position: float

    dist_max_5: float
    dist_min_5: float

    day_of_week: int
    month: int


@app.get("/")
def root():
    return {"status": "API funcionando correctamente"}


# ================================
# 4. Endpoint de predicción
# ================================
@app.post("/predict")
def predict(features: InputFeatures):

    # Convertir el input de Pydantic en un DataFrame
    data_dict = features.dict()
    df = pd.DataFrame([data_dict])

    # Verificar columnas faltantes
    missing = [c for c in FEATURE_COLS if c not in df.columns]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Faltan columnas requeridas: {missing}"
        )

    # Predicción
    pred = model.predict(df)[0]

    return {"prediction": int(pred)}


# ================================
# 5. Para ejecución local
# ================================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
