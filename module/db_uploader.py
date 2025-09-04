import csv
import json
import logging
import os
import sys

from dotenv import load_dotenv
from jsonschema import ValidationError, validate
from supabase import Client, create_client

from util.path_utils import get_config_path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def load_schema(schema_path: str) -> dict:
    with open(schema_path, encoding="utf-8") as f:
        return json.load(f)


def convert_field_types(row: dict) -> dict:
    for key in ["lon", "lat"]:
        if row.get(key):
            try:
                row[key] = float(row[key])
            except ValueError:
                logger.warning(
                    f"Failed to convert {key}='{row[key]}' to float; leaving as is."
                )
    for key, value in row.items():
        if value == "":
            row[key] = None
    return row


def validate_row(row, schema):
    try:
        validate(instance=row, schema=schema)
        return True, None
    except ValidationError as e:
        return False, str(e)


def process_csv(csv_file: str, schema: dict) -> tuple[list, list]:
    valid_rows: list[dict] = []
    errors: list[dict] = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader, start=2):
            row = convert_field_types(row)
            is_valid, error = validate_row(row, schema)
            if is_valid:
                valid_rows.append(row)
            else:
                errors.append({"row": i, "error": error})
                logger.error(f"Validation error in row {i}: {error}")
    logger.info(
        f"CSV processing complete: {len(valid_rows)} valid rows, {len(errors)} errors."
    )
    return valid_rows, errors


def create_supabase_client() -> Client:
    load_dotenv()

    url: str = os.environ.get("SUPABASE_URL")
    key: str = os.environ.get("SUPABASE_KEY")

    if not url or not key:
        error_msg = "Supabase URL or KEY not found in environment variables."
        logger.error(error_msg)

        raise RuntimeError(error_msg)
    supabase: Client = create_client(url, key)

    return supabase


def insert_to_database(supabase: Client, schema: str, table: str, rows: list[dict]):
    try:
        supabase.schema(schema).table(table).insert(rows).execute()
    except Exception as e:
        logger.error(f"Insert request failed with exception: {e}")
        raise RuntimeError(f"Insert failed: {e}")
    else:
        logger.info(f"Inserted {len(rows)} rows into {schema}.{table} successfully.")


# def main(csv_file: str, schema_path: str):
def execute_db_upload(csv_file: str):
    try:
        schema_path = os.path.join(get_config_path(), 'parking_lot.schema.json')
        schema = load_schema(schema_path)
        valid_rows, errors = process_csv(csv_file, schema)
        if valid_rows:
            supabase = create_supabase_client()
            insert_to_database(supabase, "api", "parking_lot", valid_rows)
        else:
            logger.warning("No valid rows found; skipping database insertion.")
        if errors:
            return f"Validation errors in rows: {errors}"
    except Exception as e:
        return str(e)


# if __name__ == "__main__":
#     csv_path = input("path for CSV file: ")

#     sys.exit(main(csv_path, "parking_lot.schema.json"))
