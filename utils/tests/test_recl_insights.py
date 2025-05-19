from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List

table = 'recl_insights'
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

class RECLInsight(BaseModel):
    faixa_tendencia: str
    interpretacao: str
    acoes_recomendadas: str

@app.post("/recl-insights/")
def criar_recl_insights(dados: List[RECLInsight]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for item in dados:
            cur.execute(f"""
                INSERT INTO {table} (faixa_tendencia, interpretacao, acoes_recomendadas)
                VALUES (%s, %s, %s)
            """, (item.faixa_tendencia, item.interpretacao, item.acoes_recomendadas))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registros RECL Insights criados com sucesso"}

@app.get("/recl-insights/")
def listar_recl_insights():
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

@app.put("/recl-insights/{registro_id}")
def atualizar_recl_insight(registro_id: int, dados: RECLInsight):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            UPDATE {table} SET faixa_tendencia=%s, interpretacao=%s, acoes_recomendadas=%s
            WHERE id = %s
        """, (dados.faixa_tendencia, dados.interpretacao, dados.acoes_recomendadas, registro_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro RECL Insight atualizado com sucesso"}

@app.delete("/recl-insights/{registro_id}")
def deletar_recl_insight(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro RECL Insight deletado com sucesso"}
