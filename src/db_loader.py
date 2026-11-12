import psycopg


def load_complaints(rows, password):
    inserted = 0
    existing = 0
    invalid = 0

    query = """
        INSERT INTO vehicle_complaints (
            odi_number,
            make,
            model,
            model_year,
            component,
            date_filed,
            summary
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (odi_number) DO NOTHING;
    """

    with psycopg.connect(
        host="127.0.0.1",
        port=5432,
        dbname="recalliq",
        user="postgres",
        password=password
    ) as connection:

        with connection.cursor() as cursor:
            for row in rows:

                odi_number = str(
                    row.get("odi_number") or ""
                ).strip()

                if not odi_number:
                    invalid += 1
                    continue

                cursor.execute(query, (
                    odi_number,
                    row["make"],
                    row["model"],
                    int(row["model_year"]),
                    row["component"],
                    row["date_filed"],
                    row["summary"]
                ))

                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    existing += 1

    return inserted, existing, invalid
