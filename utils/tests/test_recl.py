# pip install fastapi uvicorn psycopg2-binary
# uvicorn api_recl:app --reload
# Interface Swagger: http://localhost:8000/docs

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List

table = 'recl_interpretation'
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

class RECLRegistro(BaseModel):
    faixa_recl: str
    cor_mapa: str
    interpretacao_agronomica: str

@app.post("/recl/")
def criar_recl(dados: List[RECLRegistro]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for item in dados:
            cur.execute(f"""
                INSERT INTO {table} (faixa_recl, cor_mapa, interpretacao_agronomica)
                VALUES (%s, %s, %s)
            """, (item.faixa_recl, item.cor_mapa, item.interpretacao_agronomica))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registros RECL criados com sucesso"}

@app.get("/recl/")
def listar_recl():
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

@app.put("/recl/{registro_id}")
def atualizar_recl(registro_id: int, dados: RECLRegistro):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            UPDATE {table} SET faixa_recl=%s, cor_mapa=%s, interpretacao_agronomica=%s
            WHERE id = %s
        """, (dados.faixa_recl, dados.cor_mapa, dados.interpretacao_agronomica, registro_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro RECL atualizado com sucesso"}

@app.delete("/recl/{registro_id}")
def deletar_recl(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro RECL deletado com sucesso"}
