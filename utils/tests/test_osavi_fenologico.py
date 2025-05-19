from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from typing import List, Optional

table = 'osavi_fenologico'
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

class OSAVIFeno(BaseModel):
    estagio_fenologico: str
    faixa_osavi: str
    interpretacao: str
    aplicacoes_praticas: str

class OSAVIFenoUpdate(BaseModel):
    estagio_fenologico: Optional[str] = None
    faixa_osavi: Optional[str] = None
    interpretacao: Optional[str] = None
    aplicacoes_praticas: Optional[str] = None

@app.post("/osavi_feno/")
def criar_osavi_feno(lista: List[OSAVIFeno]):
    conn = conectar()
    cur = conn.cursor()
    try:
        for item in lista:
            cur.execute(f"""
                INSERT INTO {table} (estagio_fenologico, faixa_osavi, interpretacao, aplicacoes_praticas)
                VALUES (%s, %s, %s, %s)
            """, (item.estagio_fenologico, item.faixa_osavi, item.interpretacao, item.aplicacoes_praticas))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()
    return {"mensagem": f"{len(lista)} registro(s) criados com sucesso"}

@app.get("/osavi_feno/")
def listar_osavi_feno():
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM {table}")
    resultados = cur.fetchall()
    colunas = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return [dict(zip(colunas, linha)) for linha in resultados]

@app.put("/osavi_feno/{registro_id}")
def atualizar_osavi_feno(registro_id: int, dados: OSAVIFenoUpdate):
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

@app.delete("/osavi_feno/{registro_id}")
def deletar_osavi_feno(registro_id: int):
    conn = conectar()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id = %s", (registro_id,))
    conn.commit()
    if cur.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro não encontrado")
    cur.close()
    conn.close()
    return {"mensagem": "Registro deletado com sucesso"}
