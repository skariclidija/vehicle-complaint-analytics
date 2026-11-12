import getpass
import psycopg

password = getpass.getpass("PostgreSQL password: ")

with psycopg.connect(
    host="127.0.0.1",
    port=5432,
    dbname="recalliq",
    user="postgres",
    password=password
) as connection:

    print("Successfully connected to PostgreSQL!")

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT COUNT(*) FROM vehicle_complaints;"
        )

        result = cursor.fetchone()

        print(f"Total complaints in database: {result[0]}")
