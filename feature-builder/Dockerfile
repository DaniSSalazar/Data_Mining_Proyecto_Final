FROM python:3.10-slim

WORKDIR /app

COPY build_features.py .

RUN pip install psycopg2-binary pandas numpy sqlalchemy

ENTRYPOINT ["python", "build_features.py"]
