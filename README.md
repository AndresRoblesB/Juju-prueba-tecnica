# ETL-TEST

Pipeline ETL para procesamiento de datos de órdenes, productos y usuarios.

## 📋 Requisitos Previos

- Python 3.11 o superior (Se realizó con 3.14, este sería el recomendado)
- pip (gestor de paquetes de Python)

## 🚀 Instalación y Configuración (Windows sin Docker)

### 1. Clonar el repositorio

```bash
git clone https://github.com/AndresRoblesB/Juju-prueba-tecnica.git
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

### 3. Activar el entorno virtual

```bash
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 💻 Uso

### Ejecutar el pipeline ETL

El pipeline acepta un parámetro de fecha opcional en formato `YYYY-MM-DD` para filtrar las órdenes desde esa fecha.

#### Opción 1: Con fecha específica

```bash
python -m src.etl_job 2025-08-20
```

#### Opción 2: Sin parámetros (usa fecha por defecto)

```bash
python -m src.etl_job
```

### Resultado

El pipeline ejecutará las siguientes etapas:

1. **Extracción**: Lee datos de `sample_data/` y los mueve a `output/raw/`
   - `raw_orders.parquet`
   - `raw_products.parquet`
   - `raw_users.parquet`

2. **Transformación**: Procesa los datos y genera archivos curados en `output/curated/`
   - Datos procesados y limpios listos para análisis

## 📁 Estructura del Proyecto

```
JUJU-PRUEBA-TECNICA/
├── .venv/                  # Entorno virtual (no incluido en git)
├── docs/                   # Documentación
├── output/                 # Datos procesados
│   ├── raw/               # Datos extraídos
│   └── curated/           # Datos transformados
├── sample_data/           # Datos de ejemplo
├── sql/                   # Scripts SQL (No se usó en este caso)
├── src/                   # Código fuente
│   ├── api_client.py     # Cliente para extracción de datos
│   ├── db.py             # Funciones de base de datos (No se usó en este caso)
│   ├── etl_job.py        # Pipeline principal
│   └── transforms.py     # Transformaciones de datos
├── tests/                 # Tests unitarios
├── requirements.txt       # Dependencias del proyecto
└── README.md             # Este archivo
```

## 🧪 Ejecutar Tests

```bash
pytest tests/test_transforms.py
```

## 📦 Dependencias Principales

- **pandas** (2.3.3): Manipulación y análisis de datos
- **pyarrow** (22.0.0): Lectura/escritura de archivos Parquet
- **pytest** (9.0.2): Framework de testing

## 🔧 Desactivar el entorno virtual

Cuando termines de trabajar:

```bash
deactivate
```

## 📝 Notas

- Los archivos de salida se generan en formato Parquet para optimizar el almacenamiento y la velocidad de lectura
- Asegúrate de tener el entorno virtual activado antes de ejecutar el pipeline

## 🐳 Docker (Opcional)

Si prefieres usar Docker, consulta el archivo `docker-compose.yml` en el repositorio y corre los siguientes comandos

```bash
docker compose build
```

```bash
docker compose run --rm etl python -m src.etl_job 2025-08-20
```


.

---

**Proyecto JUJU-PRUEBA-TECNICA** | Procesamiento eficiente de datos
