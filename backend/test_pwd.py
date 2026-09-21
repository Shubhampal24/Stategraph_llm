import psycopg

passwords = ["pulsetrace@1234", "postgres", "admin", "password", "root"]

for p in passwords:
    try:
        conn = psycopg.connect(f"postgresql://postgres:{p}@localhost:5432/postgres")
        print(f"SUCCESS with password: {p}")
        conn.close()
        break
    except Exception as e:
        pass
