import os
import psycopg2

DATABASE_URL = os.environ.get("notas")

def get_db():
    return psycopg2.connect(DATABASE_URL)
