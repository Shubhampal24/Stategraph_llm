import psycopg
from psycopg import sql

db_url = "postgresql://postgres.gtaivhiuntamjeuinlal:pulsetrace%401234@aws-0-ap-south-1.pooler.supabase.com:5432/postgres"

try:
    conn = psycopg.connect(db_url, autocommit=True)
    cur = conn.cursor()
    print("Connected successfully!")
    
    cur.execute("SELECT version();")
    print("Version:", cur.fetchone()[0])
    
    for db in ['stateflow', 'stateflow_test']:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (db,))
        if not cur.fetchone():
            print(f"Creating {db}...")
            cur.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(db)))
            print(f"Created {db}")
        else:
            print(f"Database {db} already exists.")
            
    conn.close()
except Exception as e:
    print(f"Failed: {e}")
