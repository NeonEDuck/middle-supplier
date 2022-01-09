import psycopg2
import os

HOST=os.getenv('HOST')
PORT=5432
USER=os.getenv('USER')
PASSWORD=os.getenv('PASSWORD')
DATABASE=os.getenv('DATABASE')

def query(sql_string: str, args: list|dict|tuple = None):
    results=[]
    with psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    ) as conn:
        with conn.cursor() as cur:
            cur.execute(sql_string, args)
            try:
                results = cur.fetchall()
                print(results)
            except:
                pass
        conn.commit()
    return results

def connect():
    return psycopg2.connect(
        host=HOST,
        port=PORT,
        user=USER,
        password=PASSWORD,
        database=DATABASE
    )