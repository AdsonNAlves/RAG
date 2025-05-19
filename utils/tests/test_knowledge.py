# pip install fastapi uvicorn psycopg2-binary 
# uvicorn test:app --reload
# Interface Swagger: http://localhost:8000/docs
# JSON OpenAPI: http://localhost:8000/openapi.json

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import datetime
import psycopg2

table = 'knowledge_base1'
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

class Registro(BaseModel):
    date: datetime.date
    area: str
    name: str
    feature: str
    data_type: str
    insights: str | None = None
    recommendation: str | None = None
    responsible: str | None = None

class RegistroUpdate(BaseModel):
    date: datetime.date | None = None
    area: str | None = None
    name: str | None = None
    feature: str | None = None
    data_type: str | None = None
    insights: str | None = None
    recommendation: str | None = None
    responsible: str | None = None

@app.post("/kb/")
def criar_registro(dados: Registro):
    conn = conectar()
    cur = conn.cursor()
    try:
        cur.execute(f"""
            INSERT INTO {table} (date, area, name, feature, data_type, insights, recommendation, responsible)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (dados.date, dados.area, dados.name, dados.feature, dados.data_type,
              dados.insights, dados.recommendation, dados.responsible))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": "Registro criado com sucesso"}

@app.get("/kb/")
def listar_registros():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    resultados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(colunas, linha)) for linha in resultados]

@app.put("/kb/{registro_id}")
def atualizar_registro(registro_id: int, dados: RegistroUpdate):
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
    return {"mensagem": "Registro atualizado com sucesso"}

@app.delete("/kb/{registro_id}")
def deletar_registro(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro deletado com sucesso"}
