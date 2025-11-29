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
