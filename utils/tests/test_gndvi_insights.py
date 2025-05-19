from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Optional

app = FastAPI()

DB_CONFIG = {
    "host": "localhost",
    "port": 5433,
    "database": "app_db",
    "user": "admin",
    "password": "admin"
}

TABLE = "gndvi_insights"

def conectar():
    return psycopg2.connect(**DB_CONFIG)

class InsightRegistro(BaseModel):
    faixa_tendencia: str
    interpretacao: str
    acoes_recomendadas: str

class InsightUpdate(BaseModel):
    faixa_tendencia: Optional[str] = None
    interpretacao: Optional[str] = None
    acoes_recomendadas: Optional[str] = None

@app.post("/insights/")
def criar_insight(dados: InsightRegistro):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            INSERT INTO {TABLE} (faixa_tendencia, interpretacao, acoes_recomendadas)
            VALUES (%s, %s, %s)
        """, (dados.faixa_tendencia, dados.interpretacao, dados.acoes_recomendadas))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Insight criado com sucesso"}

@app.get("/insights/")
def listar_insights():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {TABLE}")
    resultados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    return [dict(zip(colunas, linha)) for linha in resultados]

@app.put("/insights/{registro_id}")
def atualizar_insight(registro_id: int, dados: InsightUpdate):
    campos = []
    valores = []

    for campo, valor in dados.dict(exclude_unset=True).items():
        campos.append(f"{campo} = %s")
        valores.append(valor)

    if not campos:
        raise HTTPException(status_code=400, detail="Nenhum campo para atualizar")

    valores.append(registro_id)
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            UPDATE {TABLE} SET {', '.join(campos)} WHERE id = %s
        """, valores)
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()

    return {"mensagem": "Insight atualizado com sucesso"}

@app.delete("/insights/{registro_id}")
def deletar_insight(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {TABLE} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Insight deletado com sucesso"}
