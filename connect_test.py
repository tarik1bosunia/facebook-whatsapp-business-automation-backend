import psycopg2

conn = psycopg2.connect(
    dbname="fbadb",
    user="tata",
    password="11235813",
    host="127.0.0.1",
    port="5432",
)
print("Connected successfully!")
conn.close()