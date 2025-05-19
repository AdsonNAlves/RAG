# pip install fastapi uvicorn psycopg2-binary
# uvicorn osavi_insights_api:app --reload
# http://localhost:8000/docs

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import psycopg2

table = 'osavi_insights'
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

class OSAVIInsight(BaseModel):
    faixa_tendencia: str
    interpretacao: str
    acoes_recomendadas: str

class OSAVIUpdate(BaseModel):
    faixa_tendencia: Optional[str] = None
    interpretacao: Optional[str] = None
    acoes_recomendadas: Optional[str] = None

@app.post("/osavi/")
def criar_osavi_lote(dados: List[OSAVIInsight]):
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
    return {"mensagem": "Registros OSAVI criados com sucesso"}

@app.get("/osavi/")
def listar_osavi():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    resultados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    registros = [dict(zip(colunas, linha)) for linha in resultados]
    return registros

@app.put("/osavi/{registro_id}")
def atualizar_osavi(registro_id: int, dados: OSAVIUpdate):
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
        cur.execute(f"UPDATE {table} SET {', '.join(campos)} WHERE id = %s", valores)
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro OSAVI atualizado com sucesso"}

@app.delete("/osavi/{registro_id}")
def deletar_osavi(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro OSAVI deletado com sucesso"}
