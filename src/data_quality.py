
def check_data_quality(rows):
    seen_ids = set()

    missing_ids = 0
    duplicate_ids = 0

    for row in rows:
        odi_number = str(row.get("odi_number") or "").strip()

        if not odi_number:
            missing_ids += 1
            continue

        if odi_number in seen_ids:
            duplicate_ids += 1
        else:
            seen_ids.add(odi_number)

    return {
        "total_records": len(rows),
        "missing_ids": missing_ids,
        "duplicate_ids": duplicate_ids
    }


def remove_invalid_and_duplicate_rows(rows):
    cleaned_rows = []
    seen_ids = set()

    for row in rows:
        odi_number = str(row.get("odi_number") or "").strip()

        if not odi_number:
            continue

        if odi_number in seen_ids:
            continue

        seen_ids.add(odi_number)

        cleaned_row = row.copy()
        cleaned_row["odi_number"] = odi_number
        cleaned_rows.append(cleaned_row)

    return cleaned_rows
