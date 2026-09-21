import psycopg

url1 = "postgresql://postgres.gtaivhiuntamjeuinlal:pulsetrace%401234@aws-0-ap-south-1.pooler.supabase.com:5432/stateflow"
url2 = "postgresql://postgres.gtaivhiuntamjeuinlal:pulsetrace%401234@aws-0-ap-south-1.pooler.supabase.com:5432/stateflow_test"

try:
    c1 = psycopg.connect(url1)
    print("stateflow OK")
    c1.close()
    
    c2 = psycopg.connect(url2)
    print("stateflow_test OK")
    c2.close()
except Exception as e:
    print(f"Failed: {e}")
