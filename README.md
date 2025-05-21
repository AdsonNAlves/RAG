# 🤖 Multimodal AI Infrastructure with Podman Compose + Gradio

Este projeto define uma infraestrutura de IA multimodal baseada em contêineres usando **Podman Compose**. Ele integra componentes para ingestão, processamento e recuperação aumentada por geração (**RAG**) com interface via **Gradio**. Tudo está isolado em containers via Podman Compose: postgres, milvus, minio, etcd, ollama, spark, e rag_app.
O serviço rag_app é construído a partir de um Dockerfile e roda o script rag.py.

---

## 📦 Serviços Incluídos

| Serviço      | Função                             | Porta (Host) | Volume Persistente      |
|--------------|------------------------------------|--------------|--------------------------|
| PostgreSQL   | Banco de dados relacional          | 5433         | `pg_data`                |
| MinIO        | Armazenamento de objetos           | 9000/9001    | `minio_data`             |
| Milvus       | Banco de dados vetorial            | 19530/9091   | `milvus_data`            |
| Spark        | Processamento distribuído          | 8080/7077    | -                        |
| Ollama       | Execução de LLMs como `phi4-mini`  | 11434        | `ollama_data`            |
| RAG App      | Pipeline RAG com LLM + Gradio UI   | 7860         | Código local             |

---

## 🚀 Primeiros Passos

### Pré-requisitos

- [`podman`](https://podman.io/)
- [`podman-compose`](https://github.com/containers/podman-compose)
- Internet para baixar imagens e modelos

### Subir ambiente:

```bash
make up
```

> Isso inicia todos os serviços definidos em `podman-compose.yml`.

---

## 🧠 RAG Pipeline com Gradio

A aplicação principal (`rag.py`) executa o pipeline RAG completo:

- Pré-processamento com **Spark**
- Embedding com **Ollama**
- Indexação com **Milvus**
- Consulta com recuperação vetorial
- Interface com **Gradio**

Acesse a interface em:

```bash
http://localhost:7860
```

### Comandos úteis

```bash
make logs      # Ver logs do rag-app
make exec      # Entrar no container rag_app
make restart   # Reiniciar ambiente
```

---

## 🔍 Serviços Detalhados

### PostgreSQL

- 📦 `postgres:15`
- Usuário: `admin` • Senha: `admin` • Banco: `app_db`
- Porta: `5433`
- Volume: `pg_data`

```bash
psql -h localhost -p 5433 -U admin app_db
```

---

### MinIO

- 📦 `quay.io/minio/minio`
- Acesso: `minioadmin:minioadmin`
- Console: [http://localhost:9001](http://localhost:9001)
- API: [http://localhost:9000](http://localhost:9000)
- Bucket padrão: `milvus-bucket`

---

### Milvus

- 📦 `milvusdb/milvus:v2.3.9`
- Porta gRPC: `19530`
- Porta HTTP: `9091`
- Volume: `milvus_data`

```python
from pymilvus import connections
connections.connect(host="localhost", port="19530")
```

---

### Spark

- 📦 `bitnami/spark:3.5`
- UI: [http://localhost:8080](http://localhost:8080)

Usado para UDFs de chunking, embeddings e pré-processamento.

---

### Ollama

- 📦 `ollama/ollama`
- Porta: `11434`
- Volume: `ollama_data`

Executar modelo manualmente:

```bash
podman exec -it ollama ollama run phi4-mini
```

Testar via API:

```bash
curl -s http://localhost:11434/api/generate \
  -d '{"model":"phi4-mini","prompt":"Qual o seu propósito?"}' \
  | jq -r '.response'
```

---

## 📁 Makefile

```makefile
.PHONY: up down logs exec restart dev prod

up:           # Subir ambiente dev
	podman-compose -f podman-compose.yml up -d --build

down:         # Parar serviços dev
	podman-compose -f podman-compose.yml down

logs:         # Logs do rag-app
	podman-compose -f podman-compose.yml logs -f rag-app

exec:         # Acessar container rag_app
	podman exec -it rag_app bash

restart:      # Reiniciar ambiente
	make down && make up

dev:          # Alias para make up
	make up

prod:         # Futuro ambiente prod
	podman-compose -f podma-prod.yml up -d --build
```

---

## 💾 Volumes

| Serviço     | Volume        | Caminho no container           |
|-------------|---------------|--------------------------------|
| PostgreSQL  | `pg_data`     | `/var/lib/postgresql/data`    |
| MinIO       | `minio_data`  | `/data`                       |
| Milvus      | `milvus_data` | `/var/lib/milvus`             |
| Ollama      | `ollama_data` | `/root/.ollama`               |

---

## 🧠 Arquitetura

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
                   │  - Limpeza       │              │
                   │  - Chunking      │              │
                   │  - Embedding UDF │              │
                   └─────┬────────────┘              │
                         │                           │
                   ┌─────▼────────────┐              │
                   │     Milvus       │ ◄────────────┘
                   └─────┬────────────┘
                         │
                   ┌─────▼────────────┐
                   │     Ollama       │ ◄── Gradio UI
                   └──────────────────┘
```

---

## ✅ Próximos Passos

- [ ] Versão de produção com `podma-prod.yml`
- [ ] Adicionar workers Spark (escala horizontal)
- [ ] API REST ou GraphQL para queries
- [ ] Monitoramento com Grafana + Prometheus
