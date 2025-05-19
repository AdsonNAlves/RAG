# pip install fastapi uvicorn psycopg2-binary 
# uvicorn gndvi:app --reload
# Interface Swagger: http://localhost:8000/docs
# JSON OpenAPI: http://localhost:8000/openapi.json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Optional

table = 'gndvi_interpretation'
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

class GNDVIRegistro(BaseModel):
    faixa_gndvi: str
    interpretacao: str
    indicativos: List[str]

class GNDVIUpdate(BaseModel):
    faixa_gndvi: Optional[str] = None
    interpretacao: Optional[str] = None
    indicativos: Optional[List[str]] = None

@app.post("/gndvi/")
def criar_gndvi(dados: GNDVIRegistro):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            INSERT INTO {table} (faixa_gndvi, interpretacao, indicativos)
            VALUES (%s, %s, %s)
        """, (dados.faixa_gndvi, dados.interpretacao, dados.indicativos))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro GNDVI criado com sucesso"}

@app.get("/gndvi/")
def listar_gndvi():
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

@app.put("/gndvi/{registro_id}")
def atualizar_gndvi(registro_id: int, dados: GNDVIUpdate):
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
    return {"mensagem": "Registro GNDVI atualizado com sucesso"}

@app.delete("/gndvi/{registro_id}")
def deletar_gndvi(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro GNDVI deletado com sucesso"}
