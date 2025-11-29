# Proyecto 06 — Pipeline de Datos para Trading Algorítmico (Mercado)

Estructura general del proyecto

project/

│

├── docker-compose.yml

├── .env.example

├── feature-builder/

│     ├── Dockerfile

│     └── build_features.py 

│
├── notebooks/

│     └── 01_ingesta_prices_raw.ipynb 

			└── 02_build_features_prototipo.ipynb
			
			└── 03_verificacion.ipynb
			
  │
  
└── requirements.txt

1. Cómo levantar el entorno con Docker Compose

Primero hay que asegurarse de tener un archivo .env en la raíz del proyecto 
Luego se ejecuta lo siguiente:

    docker compose build
    
    docker compose pull
    
    docker compose up -d

Servicios disponibles
| Servicio             | URL                                                                      | Descripción                         |
| -------------------- | ------------------------------------------------------------------------ | ----------------------------------- |
| **Jupyter Notebook** | [http://localhost:8888/lab](http://localhost:8888/lab)                   | Ingesta y análisis de datos         |
| **pgAdmin**          | [http://localhost:5050/login?next=/](http://localhost:5050/login?next=/) | UI para explorar PostgreSQL         |
| **Postgres**         | `docker exec -it postgres bash`                                          | Acceso a la base de datos vía shell |


2. Comandos de ingesta a RAW (desde Jupyter Notebook)

La ingesta de datos de mercado se realiza corriendo el notebook:
notebooks/01_ingesta_prices_raw.ipynb

Este notebook:

  -Lee las variables de ambiente
  
  -Descarga precios diarios OHLCV vía Yahoo Finance
  
  -Estandariza columnas
  
  -Inserta en raw.prices_daily
  
  -Imprime conteos y fechas mín/máx

Hay que asegurarse de tener configurado en en el .env:

    TICKERS=AAPL,MSFT,TSLA
    
    START_DATE=2019-01-01
    
    END_DATE=2025-01-01



3. Comando para construir la tabla analytics.daily_features

Esto lo hace el servicio feature-builder, ejecutando el script CLI build_features.py.

Construir las features para un ticker (sobrescribir):

docker compose run feature-builder --mode full --ticker AAPL --overwrite true

Para los otros tickers:

docker compose run feature-builder --mode full --ticker MSFT --overwrite false

docker compose run feature-builder --mode full --ticker TSLA --overwrite false

Cada ejecución:

  -Lee datos desde raw.prices_daily
  
  -Calcula features de mercado
  
  -Inserta (o sobrescribe) en analytics.daily_features
  
  -Muestra logs:
  
    -filas procesadas
    
    -fecha mínima
    
    -fecha máxima

4. Explicación breve de las columnas principales de analytics.daily_features
La tabla analytics.daily_features es una "One Big Table" donde cada fila representa:
  1 día bursátil para 1 activo

Identificación del día
| Columna                        | Descripción                            |
| ------------------------------ | -------------------------------------- |
| `date`                         | Fecha del dato                         |
| `ticker`                       | Símbolo del activo (AAPL, MSFT, TSLA…) |
| `year`, `month`, `day_of_week` | Componentes de fecha para ML           |

Datos del mercado
| Columna                        | Descripción                    |
| ------------------------------ | ------------------------------ |
| `open`, `close`, `high`, `low` | Precios diarios estándar       |
| `volume`                       | Volumen negociado ese día      |
| `adj_close`                    | Precio ajustado (viene de RAW) |

Features derivadas
| Feature             | Fórmula                        | Interpretación          |
| ------------------- | ------------------------------ | ----------------------- |
| `return_close_open` | `(close - open) / open`        | Retorno intradía        |
| `return_prev_close` | `close / close_lag1 - 1`       | Retorno vs día anterior |
| `volatility_5d`     | `std(retornos últimos 5 días)` | Volatilidad reciente    |

Metadatos
| Columna           | Descripción                                |
| ----------------- | ------------------------------------------ |
| `run_id`          | Identificador de la ejecución del pipeline |
| `ingested_at_utc` | Timestamp de creación de las features      |


5. Reproducibilidad
Para reconstruir el proyecto desde cero:
  docker compose down -v
  docker compose build
  docker compose up -d

Luego:
  Ejecutar el notebook 01_ingesta_prices_raw.ipynb
  Ejecutar el feature-builder para cada ticker
