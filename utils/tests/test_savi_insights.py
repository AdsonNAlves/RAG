from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List

table = 'savi_insights'
banco = 'app_db'

app = FastAPI()

def conectar():
    return psycopg2.connect(
        host="localhost",
        port=5433,
        database=banco,
        user="admin",
        password="admin"
    )

class SAVIInsight(BaseModel):
    padrao_tendencia: str
    significado_agronomico: str
    acoes_possiveis: str

@app.post("/savi-insights/")
def criar_savi_insights(dados: List[SAVIInsight]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for item in dados:
            cur.execute(f"""
                INSERT INTO {table} (padrao_tendencia, significado_agronomico, acoes_possiveis)
                VALUES (%s, %s, %s)
            """, (item.padrao_tendencia, item.significado_agronomico, item.acoes_possiveis))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registros SAVI Insights criados com sucesso"}

@app.get("/savi-insights/")
def listar_savi_insights():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    resultados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    registros = []
    for linha in resultados:
        registro = dict(zip(colunas, linha))
        registros.append(registro)
    return registros

@app.put("/savi-insights/{registro_id}")
def atualizar_savi_insight(registro_id: int, dados: SAVIInsight):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            UPDATE {table}
            SET padrao_tendencia=%s, significado_agronomico=%s, acoes_possiveis=%s
            WHERE id = %s
        """, (dados.padrao_tendencia, dados.significado_agronomico, dados.acoes_possiveis, registro_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro SAVI Insight atualizado com sucesso"}

@app.delete("/savi-insights/{registro_id}")
def deletar_savi_insight(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro SAVI Insight deletado com sucesso"}
