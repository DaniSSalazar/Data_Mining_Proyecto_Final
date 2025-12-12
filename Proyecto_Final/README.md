# Descripción General

Este proyecto desarrolla un modelo de Machine Learning capaz de predecir si la acción de Tesla Inc. (TSLA) cerrará al con un incremento o disminución en el precio, utilizando únicamente información disponible al inicio del día (lags, indicadores técnicos y variables derivadas).

Además, se implementa una API REST para servir predicciones en tiempo real y una simulación financiera que evalúa el impacto económico de estas predicciones mediante una estrategia simple de inversión durante el año 2025.

## 1. Entrenamiento del Modelo

El entrenamiento se realiza en el notebook:
`ml_trading_classifier.ipynb` (está dividido por secciones y específicamente las secciones 7 8, y 9 hacen referencia directa a esto, pues secciones anteriores preparan los conjuntos par entrenamiento validación, y test)

El flujo del notebook incluye:

### Análisis Exploratorio (EDA)
* **Balance de clases** para `target_up`
* **Distribución de retornos diarios**
* **Correlaciones** entre variables de mercado

### Ingeniería de Características
Incluye variables del tipo:

* **Lags** (retornos, volumen, rangos, volatilidad)
* **Indicadores técnicos** (SMA, EMA, RSI, MACD, Bollinger Bands) 
* **Momentum y estructuras de volatilidad**
* **Variables categóricas de fecha** (día de la semana, mes)

> **Nota:** Estas transformaciones se diseñan para evitar *data leakage* y respetar la causalidad temporal.

### División Temporal del Dataset

Se utiliza un split estrictamente cronológico:

| Conjunto | Período | Objetivo |
| :--- | :--- | :--- |
| **Train** | 2015–2021 | Ajuste inicial |
| **Validation** | 2022–2024 | Selección de modelo |
| **Test** | 2025 | Evaluación final (para simulación) |

### Comparación de Modelos

Se entrenan al menos **7 algoritmos**:

* Regresión Logística
* LinearSVC
* Árbol de Decisión
* Random Forest
* Gradient Boosting
* LightGBM
* Catboost

Cada modelo se evalúa con:

* Accuracy
* Precision
* Recall
* F1 Score
* ROC–AUC 
* Matriz de confusión

### Selección y Exportación del Modelo Ganador

El modelo seleccionado se entrena utilizando **Train + Validation** y se exporta como un pipeline completo:

joblib.dump(pipeline_final, "model/best_model.pkl")

Este pipeline contiene:

* Transformaciones (imputación, escalado, one-hot)

* Ingeniería de características

* Modelo final

## 2. Guardado del Modelo
Dentro del notebook hay una sección llamada "Exportar Modelo" en donde se corre el código para generar el archivo:

`model/best_model.pkl`

el cual contiene:

* **Preprocesamiento**
* **Transformaciones** numéricas y categóricas
* **Modelo entrenado**

Este formato garantiza **reproducibilidad**, evita fugas de datos (*data leakage*) y es **compatible con la API**. Sin embargo, para que funcione con esta en el entorno local se debe guardar el archivo en /model/best_model.pkl.

## 3. Despliegue de la API (FastAPI + Docker)

Para levantar únicamente el servicio de inferencia:

docker compose up --build model-api

Para levantar todos los servicios del proyecto:

docker compose up --build

Una vez desplegada, la API está disponible en:

http://localhost:8000

Documentación Swagger: http://localhost:8000/docs

## 4. Uso del Endpoint `/predict`

El modelo requiere un vector completo de *features*, consistente con el entrenamiento.

### Ejemplo de Solicitud:

curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "open": 248.93,
    "high_lag1": 6427.93,
    "low_lag1": 402.54,
    "range_lag1": 0.0599,
    "volume": 9710700,
    "volume_lag1": 76825100,
    "volume_lag2": 64941000,
    "volume_ma5_lag1": 1000,
    "volume_rel": 0.72,
    "return_prev_close_lag1": 0.0123,
    "return_prev_close_lag2": -0.0021,
    "return_close_open_lag1": 0.0041,
    "volatility_5d_lag1": 0.025,
    "volatility_5d_lag2": 0.028,
    "sma_5": 410.22,
    "ema_5": 423.70,
    "momentum_5": -0.064,
    "rsi_14": 50.56,
    "macd": 23.83,
    "macd_signal": 32.66,
    "boll_position": -0.21,
    "dist_max_5": -0.12,
    "dist_min_5": 0.00,
    "day_of_week": 3,
    "month": 1
  }'

Respuesta:

JSON

{ "prediction": 1 }

Interpretación:

* 1 → se espera que TSLA cierre al alza

* 0 → se espera que cierre a la baja
