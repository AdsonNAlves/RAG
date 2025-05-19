# Multimodal AI Infrastructure with Podman Compose

Defines a development environment using Podman Compose to orchestrate the following services:

- PostgreSQL (relational database)
- Milvus (vector database)
- MinIO (object storage, used by Milvus)
- Apache Spark (distributed processing engine)
- Ollama (lightweight LLM runtime supporting phi4-mini and other models)

All services are containerized and connected via an internal network, with persistent volumes configured for data storage.

---

## 🚀 Getting Started

### Prerequisites

- Podman and podman-compose installed on your system
- At least 8 GB RAM recommended
- Internet connection to pull base images and download models

### Start All Services

In the directory with your podman-compose.yaml file:

```bash
podman-compose -f podman-compose.yml up -d
```

All containers will start in detached mode.

---

## 🧱 Services Overview

### 1. PostgreSQL

- 📦 Image: postgres:15
- 🛠 Environment:
  - User: admin
  - Password: admin
  - DB: app_db
- 📂 Volume: pg_data → /var/lib/postgresql/data
- 📡 Port: 5432

Use with any PostgreSQL client:

```bash
psql -h localhost -p 5433 -U admin postgres
```

---

### 2. MinIO

- 📦 Image: quay.io/minio/minio
- 🛠 Credentials:
  - Access Key: minioadmin
  - Secret Key: minioadmin
- 📂 Volume: minio_data → /data
- 🌐 Console: http://localhost:9001
- 📡 API: http://localhost:9000

Default bucket used by Milvus: milvus-bucket

---

### 3. Milvus

- 📦 Image: milvusdb/milvus:v2.3.9
- 🛠 Configured with external:
  - etcd
  - MinIO
  - PostgreSQL
- 📂 Volume: milvus_data → /var/lib/milvus
- 📡 Ports:
  - 19530 (gRPC)
  - 9091 (HTTP)

You can use pymilvus to interact with it:

```python
from pymilvus import connections
connections.connect(host='localhost', port='19530')
```

---

### 4. Apache Spark

- 📦 Image: bitnami/spark:3.5
- 📡 Ports:
  - 8080 (Web UI)
  - 7077 (Cluster port)

Configured as Spark master. Workers can be added later.

Web UI: http://localhost:8080

---

### 5. Ollama with phi4-mini

- 📦 Image: ollama/ollama
- 📂 Volume: ollama_data → /root/.ollama
- 📡 Port: 11434

Start or run models inside the container:

```bash
podman exec -it ollama ollama run phi4-mini
```

You can interact with Ollama via its HTTP API:

```bash
curl -s http://localhost:11434/api/generate \
  -d '{
    "model": "phi4-mini",
    "prompt": "Qual o seu propósito?"
  }' \
  | jq -r 'select(.response) | .response' | tr -d '\n'; echo
```

ℹ️ If phi4-mini is not yet officially available, use phi3 or llama3 instead:

```bash
ollama run phi3
```

---

## 💾 Data Persistence

Each service uses a Podman volume for persistence:

| Service    | Volume Name   | Path Inside Container              |
|------------|---------------|------------------------------------|
| PostgreSQL | pg_data       | /var/lib/postgresql/data           |
| Milvus     | milvus_data   | /var/lib/milvus                    |
| MinIO      | minio_data    | /data                              |
| Ollama     | ollama_data   | /root/.ollama                      |

You can inspect volumes via:

```bash
podman volume ls
podman volume inspect <volume_name>
```

---

## 🧹 Shut Down and Cleanup

To stop all services:

```bash
podman-compose -f podman-compose.yml down
```

To remove all volumes (careful!):

```bash
podman volume rm pg_data milvus_data minio_data ollama_data
```

## Architecture Diagram
```
                  ┌────────────┐
                  │ PostgreSQL │
                  └─────┬──────┘
                        │
                  ┌─────▼──────┐
                  │   MinIO    │
                  └─────┬──────┘
                        │
                  ┌─────▼────────────┐
                  │     Spark        │ ◄────────────┐
                  │  - Leitura       │              │
                  │  - Limpeza       │              │
                  │  - Chunking      │              │
                  │  - Embedding UDF │              │
                  └─────┬────────────┘              │
                        │                           │
                  ┌─────▼────────────┐              │
                  │     Milvus       │ ◄────────────┘
                  └──────────────────┘
```
Can be automated via Airflow or REST scripts.

---

<!-- ## 🧠 Next Steps

- Add Spark workers and job submission support
- Connect your LLM-based module to Milvus and PostgreSQL
- Build custom REST or WebSocket APIs for inference and vector search -->