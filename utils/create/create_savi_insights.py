import psycopg2
from psycopg2 import OperationalError, Error

def get_connection(host, port, database, user, password):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        print("Conexão com o PostgreSQL estabelecida com sucesso.")
        return conn
    except OperationalError as e:
        raise RuntimeError(f"Erro ao conectar no PostgreSQL: {e}")

def create_table(conn):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS savi_insights (
        id SERIAL PRIMARY KEY,
        padrao_tendencia TEXT NOT NULL,
        significado_agronomico TEXT NOT NULL,
        acoes_possiveis TEXT NOT NULL
    );
    """
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(create_table_sql)
                print("Tabela 'savi_insights' criada com sucesso.")
    except Error as e:
        raise RuntimeError(f"Erro ao criar a tabela: {e}")

def main():
    try:
        conn = get_connection(
            host="localhost",
            port="5433",
            database="app_db",
            user="admin",
            password="admin"
        )
        create_table(conn)
    except Exception as e:
        print(f"Erro geral: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    main()
