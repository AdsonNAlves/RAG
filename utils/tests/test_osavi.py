# pip install fastapi uvicorn psycopg2-binary 
# uvicorn osavi:app --reload
# Interface Swagger: http://localhost:8000/docs
# JSON OpenAPI: http://localhost:8000/openapi.json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Optional

table = 'osavi_interpretation'
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

class OSAVIRegistro(BaseModel):
    faixa_osavi: str
    cor_imagem: str
    interpretacao_agronomica: str

class OSAVIUpdate(BaseModel):
    faixa_osavi: Optional[str] = None
    cor_imagem: Optional[str] = None
    interpretacao_agronomica: Optional[str] = None

@app.post("/osavi/")
def criar_osavi(lista_dados: List[OSAVIRegistro]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for dados in lista_dados:
            cur.execute(f"""
                INSERT INTO {table} (faixa_osavi, cor_imagem, interpretacao_agronomica)
                VALUES (%s, %s, %s)
            """, (dados.faixa_osavi, dados.cor_imagem, dados.interpretacao_agronomica))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": f"{len(lista_dados)} registro(s) OSAVI criado(s) com sucesso"}
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



