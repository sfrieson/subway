import psycopg2
connection = psycopg2.connect("dbname=subway_schedule")
cursor = connection.cursor()

def get_one(query):
    cursor.execute(query)
    return cursor.fetchone()

def get_many(query):
    cursor.execute(query)
    return cursor.fetchall()
