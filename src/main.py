"""Vehicle complaint data pipeline using NHTSA, Python and PostgreSQL."""
import argparse
import csv
import json
import getpass
import logging
import psycopg
from db_loader import load_complaints
from data_quality import (
    check_data_quality,
    remove_invalid_and_duplicate_rows
)
from collections import Counter
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import urlopen

API = 'https://api.nhtsa.gov/complaints/complaintsByVehicle'
OUTPUT = Path(__file__).resolve().parents[1] / 'data' / 'output'
FIELDS = ['odi_number', 'make', 'model', 'model_year', 'component', 'date_filed', 'summary']

def fetch_complaints(make: str, model: str, year: int) -> list[dict]:
    """Fetch NHTSA's complaints for one exact model/year (real public data)."""
    url = API + '?' + urlencode({'make': make, 'model': model, 'modelYear': year})
    with urlopen(url, timeout=25) as response:
        payload = json.load(response)
    results = payload.get('results', [])
    if not isinstance(results, list):
        raise ValueError('Unexpected API structure: results must be a list')
    return results

def normalise(item: dict, make: str, model: str, year: int) -> dict:
    """Map API fields to a consistent shape without inventing missing values."""
    def val(*names):
        for name in names:
            value = item.get(name)
            if value is not None and value != '':
                return str(value).strip()
        return ''
    return {
        'odi_number': val('odiNumber', 'ODINumber', 'odNumber'),
        'make': val('make') or make.upper(),
        'model': val('model') or model.upper(),
        'model_year': val('modelYear') or str(year),
        'component': val('components', 'component') or 'UNSPECIFIED',
        'date_filed': val('dateComplaintFiled', 'dateOfIncident'),
        'summary': val('summary'),
    }

def component_counts(rows: list[dict]) -> list[dict]:
    counts = Counter(row['component'] for row in rows)
    return [{'component': component, 'report_count': count}
            for component, count in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))]

def export_csv(path: Path, rows: list[dict], columns: list[str]):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8-sig') as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description='NHTSA vehicle complaint report')
    parser.add_argument('--make', required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--year', type=int, required=True)
    args = parser.parse_args()
    log_folder = Path(__file__).resolve().parents[1] / "logs"
    log_folder.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        filename=log_folder / "recalliq.log",
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
        encoding="utf-8"
    )

    try:
        raw = fetch_complaints(args.make, args.model, args.year)
    except Exception as error:
        parser.exit(1, f'Could not fetch data: {error}\n')
    rows = [normalise(item, args.make, args.model, args.year) for item in raw]
    print("\nTOP 5 REPORTED COMPONENTS:")
    for item in component_counts(rows)[:5]:
        print(f"{item['component']}: {item['report_count']}")    
    suffix = f'{args.make}_{args.model}_{args.year}'.lower().replace(' ', '_')
    out1 = OUTPUT / f'complaints_{suffix}.csv'
    out2 = OUTPUT / f'components_{suffix}.csv'
    export_csv(out1, rows, FIELDS)
    export_csv(out2, component_counts(rows), ['component', 'report_count'])
    print(f'Fetched {len(rows)} public complaint records')
    print(f'Saved: {out1}\nSaved: {out2}')
    print('Reminder: report counts are NOT vehicle defect rates.')
    quality = check_data_quality(rows)
    print("\nDATA QUALITY REPORT")
    print(f"Total records: {quality['total_records']}")
    print(f"Missing IDs: {quality['missing_ids']}")
    print(f"Duplicate IDs: {quality['duplicate_ids']}")

    logging.info("Data quality: %s", quality)

    cleaned_rows = remove_invalid_and_duplicate_rows(rows)

    removed_count = len(rows) - len(cleaned_rows)

    print("\nDATA CLEANING RESULTS")
    print(f"Original records: {len(rows)}")
    print(f"Clean records: {len(cleaned_rows)}")
    print(f"Removed records: {removed_count}")

    logging.info(
        "Data cleaning: original=%s | clean=%s | removed=%s",
        len(rows),
        len(cleaned_rows),
        removed_count
    )

    password = getpass.getpass("PostgreSQL password: ")

    try:
        inserted, existing, invalid = load_complaints(
            cleaned_rows, password
        )

    except psycopg.Error:
        logging.exception("Database import failed")

        print(
            "ERROR: Database import failed. "
            "Check logs/recalliq.log"
        )

        raise SystemExit(1)


    print("\nDATABASE IMPORT RESULTS")
    print(f"New records: {inserted}")
    print(f"Already existing: {existing}")
    print(f"Invalid IDs skipped: {invalid}")
    logging.info(
        "Import: %s %s %s | fetched=%s | new=%s | existing=%s | invalid=%s",
        args.make,
        args.model,
        args.year,
        len(rows),
        inserted,
        existing,
        invalid
    )
if __name__ == '__main__':
    main()
