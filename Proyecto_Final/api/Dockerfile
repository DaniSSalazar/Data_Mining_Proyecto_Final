FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Copiar el modelo desde el contexto actual (api/)
COPY best_model.pkl /app/model/best_model.pkl

EXPOSE 8000

CMD ["python", "app.py"]

