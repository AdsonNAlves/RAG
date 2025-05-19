# pip install fastapi uvicorn psycopg2-binary 
# uvicorn ndvi:app --reload
# Interface Swagger: http://localhost:8000/docs
# JSON OpenAPI: http://localhost:8000/openapi.json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Optional

table = 'ndvi_interpretation'
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

class NDVIRegistro(BaseModel):
    faixa_ndvi: str
    vigor_vegetativo: str
    indicativos: List[str]  # armazenado como string separada por quebra de linha no banco
    recomendacao: str 

class NDVIUpdate(BaseModel):
    faixa_ndvi: Optional[str] = None
    vigor_vegetativo: Optional[str] = None
    indicativos: Optional[List[str]] = None
    recomendacao: Optional[str] = None

@app.post("/ndvi/")
def criar_ndvi(dados: NDVIRegistro):
    conn = conectar()
    cur = conn.cursor()
    try:
        indicativos_str = "\n".join(dados.indicativos)
        cur.execute(f"""
            INSERT INTO {table} (faixa_ndvi, vigor_vegetativo, indicativos, recomendacao)
            VALUES (%s, %s, %s,%s)
        """, (dados.faixa_ndvi, dados.vigor_vegetativo, indicativos_str))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro NDVI criado com sucesso"}

@app.get("/ndvi/")
def listar_ndvi():
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
        registro["indicativos"] = registro["indicativos"].split("\n") if registro["indicativos"] else []
        registros.append(registro)
    return registros

@app.put("/ndvi/{registro_id}")
def atualizar_ndvi(registro_id: int, dados: NDVIUpdate):
    campos = []
    valores = []

    for campo, valor in dados.dict(exclude_unset=True).items():
        if campo == "indicativos" and valor is not None:
            valor = "\n".join(valor)
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
    return {"mensagem": "Registro NDVI atualizado com sucesso"}

@app.delete("/ndvi/{registro_id}")
def deletar_ndvi(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro NDVI deletado com sucesso"}
