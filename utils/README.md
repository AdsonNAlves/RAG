
# 📦 utils Directory

This directory contains scripts used to **create database tables** and **test data ingestion and transformation pipelines** related to vegetation indexes and agronomic insights in the context of remote sensing data.

---

## 📁 Structure

### 🔧 `create/`

Contains scripts for creating PostgreSQL tables programmatically using `psycopg2`. Each script corresponds to a specific vegetation index or insight type.

#### Scripts:
- `create_gndvi.py` / `create_gndvi_insights.py`
- `create_ndvi.py` / `create_ndvi_insights.py`
- `create_ndwi.py` / `create_ndwi_insights.py`
- `create_osavi.py` / `create_osavi_fenologico.py` / `create_osavi_insights.py`
- `create_recl.py` / `create_recl_insights.py`
- `create_savi.py` / `create_savi_insights.py`

Each script:
- Connects to PostgreSQL
- Creates a table (if not exists)
- Defines columns relevant to agronomic interpretation, sensor data ranges, or recommendations

---

### ✅ `tests/`

Test suite for the `create/` scripts and their output. Ensures the correct execution of table creation and that data is handled properly.

#### Scripts:
- `test_<index>.py` → Validates table creation
- `test_<index>_insights.py` → Validates data model and expected behaviors

These tests can be executed using `pytest` or `unittest`.

---

## ⚙️ Dependencies

Make sure the following Python libraries are installed:

```bash
pip install psycopg2
```

## 🚀 Usage

To create all tables, run the respective script inside `create/`. Example:

```bash
python create_ndvi.py
```

To run all tests:

```bash
pytest application/utils/tests/
```

Or using:

```bash
python -m unittest discover -s application/utils/tests/
```

---

## 🗃️ Database Configuration

Connection details (host, port, user, password, database) should be adjusted in each script or set via environment variables.

Example default:
```python
host="localhost"
port="5433"
database="app_db"
user="admin"
password="admin"
```

---

## 🧩 Vegetation Indexes Included

- NDVI – Normalized Difference Vegetation Index
- NDWI – Normalized Difference Water Index
- GNDVI – Green NDVI
- OSAVI – Optimized Soil-Adjusted Vegetation Index
- SAVI – Soil-Adjusted Vegetation Index
- RECL – Relative Chlorophyll Level

---

## ✍️ Notes

- Each script is modular and can be extended to include insert or update logic.
- The structure is optimized for scalability and integration with FastAPI-based backends.

---

## 👨‍🔬 Maintainer

Adson Nogueira Alves
