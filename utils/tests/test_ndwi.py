from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List

table = 'ndwi_interpretation'
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

class NDWIInterpretation(BaseModel):
    faixa_ndwi: str
    cor_tipica: str
    interpretacao: str

@app.post("/ndwi/")
def criar_ndwi_interpretacoes(dados: List[NDWIInterpretation]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for item in dados:
            cur.execute(f"""
                INSERT INTO {table} (faixa_ndwi, cor_tipica, interpretacao)
                VALUES (%s, %s, %s)
            """, (item.faixa_ndwi, item.cor_tipica, item.interpretacao))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registros NDWI criados com sucesso"}

@app.get("/ndwi/")
def listar_ndwi_interpretacoes():
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

@app.put("/ndwi/{registro_id}")
def atualizar_ndwi_interpretacao(registro_id: int, dados: NDWIInterpretation):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            UPDATE {table}
            SET faixa_ndwi=%s, cor_tipica=%s, interpretacao=%s
            WHERE id = %s
        """, (dados.faixa_ndwi, dados.cor_tipica, dados.interpretacao, registro_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro NDWI atualizado com sucesso"}

@app.delete("/ndwi/{registro_id}")
def deletar_ndwi_interpretacao(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro NDWI deletado com sucesso"}
