from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List

table = 'savi_interpretation'
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

class SAVIInterpretation(BaseModel):
    faixa_valores: str
    cor_visual: str
    interpretacao_agronomica: str

@app.post("/savi-interpretation/")
def criar_savi_interpretation(dados: List[SAVIInterpretation]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for item in dados:
            cur.execute(f"""
                INSERT INTO {table} (faixa_valores, cor_visual, interpretacao_agronomica)
                VALUES (%s, %s, %s)
            """, (item.faixa_valores, item.cor_visual, item.interpretacao_agronomica))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registros SAVI criados com sucesso"}

@app.get("/savi-interpretation/")
def listar_savi_interpretation():
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

@app.put("/savi-interpretation/{registro_id}")
def atualizar_savi_interpretation(registro_id: int, dados: SAVIInterpretation):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            UPDATE {table}
            SET faixa_valores=%s, cor_visual=%s, interpretacao_agronomica=%s
            WHERE id = %s
        """, (dados.faixa_valores, dados.cor_visual, dados.interpretacao_agronomica, registro_id))
        conn.commit()
        if cur.rowcount == 0:
            raise HTTPException(status_code=404, detail="Registro não encontrado")
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro SAVI atualizado com sucesso"}

@app.delete("/savi-interpretation/{registro_id}")
def deletar_savi_interpretation(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro SAVI deletado com sucesso"}
