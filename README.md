#  Proyecto 06 — Pipeline de Datos para Trading Algorítmico (Mercado)

Este proyecto implementa un pipeline de datos individual utilizando Docker Compose para la ingesta, transformación y verificación de datos de mercado (OHLCV) de tres activos específicos.

---

##  1. Cómo Levantar el Entorno con Docker Compose

Asegúrate de tener un archivo `.env` configurado en la raíz del proyecto antes de continuar.

Para construir, descargar e iniciar los servicios:

docker compose build
docker compose pull
docker compose up -d

Servicios

| Servicio             | URL                                                                      | Descripción                         |
| -------------------- | ------------------------------------------------------------------------ | ----------------------------------- |
| **Jupyter Notebook** | [http://localhost:8888/lab](http://localhost:8888/lab)                   | Ingesta y análisis de datos         |
| **pgAdmin**          | [http://localhost:5050/login?next=/](http://localhost:5050/login?next=/) | UI para explorar PostgreSQL         |
| **Postgres**         | `docker exec -it postgres bash`                                          | Acceso a la base de datos vía shell |


2. Comandos de Ingesta de Datos (RAW)
   
La ingesta inicial de datos OHLCV (Precios Diarios) se realiza a través de un Jupyter Notebook.

Notebook de Ingesta

Ejecutar el siguiente notebook para poblar la tabla raw.prices_daily:

notebooks/01_ingesta_prices_raw.ipynb

Funcionalidad del Notebook:

   -Lee las variables TICKERS, START_DATE, y END_DATE del entorno (.env).
   
   -Descarga datos OHLCV históricos desde Yahoo Finance utilizando yfinance.
   
   -Limpia, estandariza columnas e inserta los datos en la tabla raw.prices_daily de PostgreSQL.
   
   -Muestra logs detallados (filas descargadas, fechas min/máx por ticker, conteo de filas en Postgres).


3. Construcción de Features — feature-builder
   
La tabla de features (analytics.daily_features) se construye ejecutando un script CLI dentro del contenedor feature-builder, no en Jupyter.

Comando General

Utilizar el siguiente formato para procesar un activo

docker compose run feature-builder --mode full --ticker <TICKER> --overwrite true

Ejemplos para los 3 Activos

Se debe ejecutar este comando para cada uno de los activos (AAPL, MSFT, TSLA):

docker compose run feature-builder --mode full --ticker AAPL --overwrite true

docker compose run feature-builder --mode full --ticker MSFT --overwrite false

docker compose run feature-builder --mode full --ticker TSLA --overwrite false


Detalles de la Ejecución:

✔ Lee datos de precios desde raw.prices_daily.

✔ Calcula las features diarias (retornos, volatilidad, etc.).

✔ Sobrescribe la tabla de resultados: analytics.daily_features.

✔ Imprime logs del proceso (filas procesadas, fecha min/max).

4. Descripción de los Notebooks Incluidos
01_ingesta_prices_raw.ipynb

      -Objetivo: Poblar la tabla de datos crudos (raw.prices_daily).
      
      -Lectura de variables de entorno (os.getenv).
      
      -Descarga de datos y limpieza.
      
      -Inserción en Postgres usando SQLAlchemy.
      
      -Validación de fechas y conteos.

 02_build_features_prototipo.ipynb
 
      -Objetivo: Área de pruebas para el desarrollo de transformaciones antes de su codificación final en el script (build_features.py).
      
      -Carga manual de datos RAW para un solo ticker.
      
      -Pruebas de cálculos de features (retornos, volatilidad rolling).
      
      -Validación de estructura (shape y nulls).
      
      -Exportación temporal a analytics.daily_features.

03_verificacion.ipynb

      -Objetivo: Validar que el pipeline completo se haya ejecutado correctamente.
      
      -Verificaciones de conteos de filas (RAW vs ANALYTICS).
      
      -Revisión de fechas mínimas/máximas y días sin datos.
 
      
5. Explicación Breve de las Columnas de analytics.daily_features

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

6. Reproducibilidad

Para reconstruir el proyecto desde cero:

  docker compose down -v
  
  docker compose build
  
  docker compose up -d

Luego:

  Ejecutar el notebook 01_ingesta_prices_raw.ipynb
  
  Ejecutar el feature-builder para cada ticker

  Ejecutar Verificación (Notebook):

   Ejecutar 03_verificacion.ipynb
