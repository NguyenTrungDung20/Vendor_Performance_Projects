from __future__ import annotations

import argparse
import csv
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import psycopg2
from psycopg2 import sql

from config import DB_CONFIG


# ============================================================
# 1. CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_FOLDER = PROJECT_ROOT / "data" / "processed"

SCHEMA_NAME = "vendor"
IMPORT_LOG_TABLE = "csv_import_log"


# ============================================================
# 2. CSV -> POSTGRESQL TABLE MAPPING
# ============================================================

TABLE_MAPPING = {
    "begin_inventory.csv": "begin_inventory",
    "end_inventory.csv": "end_inventory",
    "purchases.csv": "purchases",
    "purchase_prices.csv": "purchase_prices",
    "sales.csv": "sales",
    "vendor_invoice.csv": "vendor_invoice",
}


# ============================================================
# 3. EXPECTED COLUMNS
# ============================================================

EXPECTED_COLUMNS = {
    "begin_inventory.csv": [
        "InventoryId",
        "Store",
        "City",
        "Brand",
        "Description",
        "Size",
        "onHand",
        "Price",
        "startDate",
    ],
    "end_inventory.csv": [
        "InventoryId",
        "Store",
        "City",
        "Brand",
        "Description",
        "Size",
        "onHand",
        "Price",
        "endDate",
    ],
    "purchases.csv": [
        "InventoryId",
        "Store",
        "Brand",
        "Description",
        "Size",
        "VendorNumber",
        "VendorName",
        "PONumber",
        "PODate",
        "ReceivingDate",
        "InvoiceDate",
        "PayDate",
        "PurchasePrice",
        "Quantity",
        "Dollars",
        "Classification",
    ],
    "purchase_prices.csv": [
        "Brand",
        "Description",
        "Price",
        "Size",
        "Volume",
        "Classification",
        "PurchasePrice",
        "VendorNumber",
        "VendorName",
    ],
    "sales.csv": [
        "InventoryId",
        "Store",
        "Brand",
        "Description",
        "Size",
        "SalesQuantity",
        "SalesDollars",
        "SalesPrice",
        "SalesDate",
        "Volume",
        "Classification",
        "ExciseTax",
        "VendorNo",
        "VendorName",
    ],
    "vendor_invoice.csv": [
        "VendorNumber",
        "VendorName",
        "InvoiceDate",
        "PONumber",
        "PODate",
        "PayDate",
        "Quantity",
        "Dollars",
        "Freight",
        "Approval",
    ],
}


@dataclass(frozen=True)
class CsvFileInfo:
    name: str
    path: Path
    size_bytes: int
    modified_at: datetime


@dataclass(frozen=True)
class TableColumn:
    name: str
    data_type: str

    @property
    def is_text_type(self) -> bool:
        return self.data_type == "text" or self.data_type.startswith("character ")


def print_banner(title: str) -> None:
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def table_id(schema_name: str, table_name: str) -> sql.Composed:
    return sql.Identifier(schema_name, table_name)


def column_list(columns: list[str]) -> sql.Composed:
    return sql.SQL(", ").join(sql.Identifier(column) for column in columns)


def table_column_names(columns: list[TableColumn]) -> list[str]:
    return [column.name for column in columns]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Import processed vendor CSV files into PostgreSQL."
    )
    parser.add_argument(
        "--data-folder",
        type=Path,
        default=DATA_FOLDER,
        help="Folder that contains the processed CSV files.",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        help=(
            "Import only specific files. Accepts names with or without .csv, "
            "for example: --only sales purchases.csv"
        ),
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help=(
            "Run the import even when the same file was already completed. "
            "Existing rows are still protected by duplicate removal."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate files and database tables without inserting data.",
    )
    return parser.parse_args()


def normalize_selected_files(selected_files: list[str] | None) -> list[str]:
    if not selected_files:
        return list(TABLE_MAPPING)

    normalized_files = []
    for file_name in selected_files:
        normalized = file_name if file_name.endswith(".csv") else f"{file_name}.csv"
        if normalized not in TABLE_MAPPING:
            valid_names = ", ".join(TABLE_MAPPING)
            raise ValueError(f"Unknown CSV file '{file_name}'. Valid files: {valid_names}")
        normalized_files.append(normalized)

    return normalized_files


def get_file_info(data_folder: Path, csv_file: str) -> CsvFileInfo:
    file_path = data_folder / csv_file
    if not file_path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    file_stat = file_path.stat()
    modified_at = datetime.fromtimestamp(file_stat.st_mtime, tz=timezone.utc)

    return CsvFileInfo(
        name=csv_file,
        path=file_path,
        size_bytes=file_stat.st_size,
        modified_at=modified_at,
    )


def read_csv_header(file_path: Path) -> list[str]:
    with file_path.open("r", encoding="utf-8-sig", newline="") as csv_handle:
        reader = csv.reader(csv_handle)
        return next(reader)


def validate_csv_columns(file_info: CsvFileInfo) -> None:
    actual_columns = read_csv_header(file_info.path)
    expected_columns = EXPECTED_COLUMNS[file_info.name]

    if actual_columns != expected_columns:
        print("\nCOLUMN VALIDATION FAILED")
        print("Expected:", expected_columns)
        print("Actual  :", actual_columns)
        raise ValueError(f"Column mismatch detected in {file_info.name}")

    print("CSV columns: OK")


def fetch_table_columns(connection, table_name: str) -> list[TableColumn]:
    with connection.cursor() as cursor:
        cursor.execute(
            """
            SELECT
                attribute.attname,
                pg_catalog.format_type(attribute.atttypid, attribute.atttypmod)
            FROM pg_catalog.pg_attribute AS attribute
            JOIN pg_catalog.pg_class AS class
              ON class.oid = attribute.attrelid
            JOIN pg_catalog.pg_namespace AS namespace
              ON namespace.oid = class.relnamespace
            WHERE namespace.nspname = %s
              AND class.relname = %s
              AND attribute.attnum > 0
              AND NOT attribute.attisdropped
            ORDER BY attribute.attnum;
            """,
            (SCHEMA_NAME, table_name),
        )
        return [TableColumn(name=row[0], data_type=row[1]) for row in cursor.fetchall()]


def validate_target_table(connection, csv_file: str, table_name: str) -> list[TableColumn]:
    table_columns = fetch_table_columns(connection, table_name)
    if not table_columns:
        raise RuntimeError(f"Target table not found: {SCHEMA_NAME}.{table_name}")

    actual_columns = table_column_names(table_columns)
    expected_columns = EXPECTED_COLUMNS[csv_file]
    if actual_columns != expected_columns:
        print("\nDATABASE TABLE VALIDATION FAILED")
        print("Expected:", expected_columns)
        print("Actual  :", actual_columns)
        raise ValueError(f"Column mismatch detected in {SCHEMA_NAME}.{table_name}")

    print("Target table columns: OK")
    return table_columns


def ensure_import_log_table(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(
                sql.Identifier(SCHEMA_NAME)
            )
        )
        cursor.execute(
            sql.SQL(
                """
                CREATE TABLE IF NOT EXISTS {} (
                    import_id BIGSERIAL PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    file_size_bytes BIGINT NOT NULL,
                    file_modified_at TIMESTAMPTZ NOT NULL,
                    target_schema TEXT NOT NULL,
                    target_table TEXT NOT NULL,
                    status TEXT NOT NULL,
                    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                    finished_at TIMESTAMPTZ,
                    source_rows BIGINT,
                    inserted_rows BIGINT,
                    duplicate_rows BIGINT,
                    deleted_existing_duplicates BIGINT,
                    error_message TEXT
                );
                """
            ).format(table_id(SCHEMA_NAME, IMPORT_LOG_TABLE))
        )
        cursor.execute(
            sql.SQL(
                """
                CREATE INDEX IF NOT EXISTS {} ON {}
                    (
                        target_schema,
                        target_table,
                        file_name,
                        file_size_bytes,
                        file_modified_at,
                        status
                    );
                """
            ).format(
                sql.Identifier(f"idx_{IMPORT_LOG_TABLE}_lookup"),
                table_id(SCHEMA_NAME, IMPORT_LOG_TABLE),
            )
        )


def count_table_rows(connection, table_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL("SELECT COUNT(*) FROM {};").format(
                table_id(SCHEMA_NAME, table_name)
            )
        )
        return cursor.fetchone()[0]


def find_completed_import(connection, file_info: CsvFileInfo, table_name: str):
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                """
                SELECT import_id, finished_at, source_rows, inserted_rows
                FROM {}
                WHERE file_name = %s
                  AND file_path = %s
                  AND file_size_bytes = %s
                  AND file_modified_at = %s
                  AND target_schema = %s
                  AND target_table = %s
                  AND status = 'completed'
                ORDER BY finished_at DESC NULLS LAST, import_id DESC
                LIMIT 1;
                """
            ).format(table_id(SCHEMA_NAME, IMPORT_LOG_TABLE)),
            (
                file_info.name,
                str(file_info.path),
                file_info.size_bytes,
                file_info.modified_at,
                SCHEMA_NAME,
                table_name,
            ),
        )
        return cursor.fetchone()


def start_import_log(connection, file_info: CsvFileInfo, table_name: str) -> int:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                """
                INSERT INTO {} (
                    file_name,
                    file_path,
                    file_size_bytes,
                    file_modified_at,
                    target_schema,
                    target_table,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, 'running')
                RETURNING import_id;
                """
            ).format(table_id(SCHEMA_NAME, IMPORT_LOG_TABLE)),
            (
                file_info.name,
                str(file_info.path),
                file_info.size_bytes,
                file_info.modified_at,
                SCHEMA_NAME,
                table_name,
            ),
        )
        return cursor.fetchone()[0]


def complete_import_log(
    connection,
    import_id: int,
    source_rows: int,
    inserted_rows: int,
    duplicate_rows: int,
    deleted_existing_duplicates: int,
) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                """
                UPDATE {}
                SET status = 'completed',
                    finished_at = NOW(),
                    source_rows = %s,
                    inserted_rows = %s,
                    duplicate_rows = %s,
                    deleted_existing_duplicates = %s,
                    error_message = NULL
                WHERE import_id = %s;
                """
            ).format(table_id(SCHEMA_NAME, IMPORT_LOG_TABLE)),
            (
                source_rows,
                inserted_rows,
                duplicate_rows,
                deleted_existing_duplicates,
                import_id,
            ),
        )


def fail_import_log(connection, import_id: int, error_message: str) -> None:
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                """
                UPDATE {}
                SET status = 'failed',
                    finished_at = NOW(),
                    error_message = %s
                WHERE import_id = %s;
                """
            ).format(table_id(SCHEMA_NAME, IMPORT_LOG_TABLE)),
            (error_message[:4000], import_id),
        )


def cast_staging_column(column: TableColumn) -> sql.Composed:
    missing_tokens = [""]
    if not column.is_text_type:
        missing_tokens.extend(["Unknown", "UNKNOWN", "N/A", "NA", "NULL"])

    expression: sql.Composable = sql.Identifier(column.name)
    for token in missing_tokens:
        expression = sql.SQL("NULLIF({}, {})").format(expression, sql.Literal(token))

    return sql.SQL("CAST({} AS {}) AS {}").format(
        expression,
        sql.SQL(column.data_type),
        sql.Identifier(column.name),
    )


def copy_csv_to_staging(
    cursor,
    file_info: CsvFileInfo,
    staging_table: str,
    target_table: str,
    columns: list[TableColumn],
) -> int:
    staging_columns = sql.SQL(", ").join(
        sql.SQL("{} TEXT").format(sql.Identifier(column.name)) for column in columns
    )

    cursor.execute(
        sql.SQL("CREATE TEMP TABLE {} ({}) ON COMMIT DROP;").format(
            sql.Identifier(staging_table),
            staging_columns,
        )
    )

    copy_command = sql.SQL(
        """
        COPY {} ({})
        FROM STDIN
        WITH (
            FORMAT CSV,
            HEADER TRUE,
            DELIMITER ',',
            QUOTE '"',
            NULL ''
        );
        """
    ).format(sql.Identifier(staging_table), column_list(table_column_names(columns)))

    with file_info.path.open("r", encoding="utf-8-sig", newline="") as csv_handle:
        cursor.copy_expert(copy_command.as_string(cursor), csv_handle)

    cursor.execute(
        sql.SQL("SELECT COUNT(*) FROM {};").format(sql.Identifier(staging_table))
    )
    return cursor.fetchone()[0]


def insert_distinct_rows(
    cursor,
    staging_table: str,
    target_table: str,
    columns: list[TableColumn],
) -> int:
    target_columns_sql = column_list(table_column_names(columns))
    casted_columns_sql = sql.SQL(", ").join(cast_staging_column(column) for column in columns)
    cursor.execute(
        sql.SQL(
            """
            INSERT INTO {} ({})
            SELECT {}
            FROM (
                SELECT DISTINCT {} FROM {}
                EXCEPT
                SELECT {} FROM {}
            ) AS rows_to_insert;
            """
        ).format(
            table_id(SCHEMA_NAME, target_table),
            target_columns_sql,
            target_columns_sql,
            casted_columns_sql,
            sql.Identifier(staging_table),
            target_columns_sql,
            table_id(SCHEMA_NAME, target_table),
        )
    )
    return cursor.rowcount


def delete_existing_duplicate_rows(
    cursor,
    table_name: str,
    columns: list[TableColumn],
    should_run: bool,
) -> int:
    if not should_run:
        return 0

    cursor.execute(
        sql.SQL(
            """
            WITH numbered_rows AS (
                SELECT
                    ctid,
                    ROW_NUMBER() OVER (
                        PARTITION BY {}
                        ORDER BY ctid
                    ) AS duplicate_rank
                FROM {}
            )
            DELETE FROM {} AS target
            USING numbered_rows
            WHERE target.ctid = numbered_rows.ctid
              AND numbered_rows.duplicate_rank > 1;
            """
        ).format(
            column_list(table_column_names(columns)),
            table_id(SCHEMA_NAME, table_name),
            table_id(SCHEMA_NAME, table_name),
        )
    )
    return cursor.rowcount


def analyze_table(cursor, table_name: str) -> None:
    cursor.execute(
        sql.SQL("ANALYZE {};").format(table_id(SCHEMA_NAME, table_name))
    )


def import_csv_file(
    connection,
    data_folder: Path,
    csv_file: str,
    table_name: str,
    force: bool,
    dry_run: bool,
) -> None:
    file_info = get_file_info(data_folder, csv_file)

    print_banner(f"FILE: {csv_file} -> TABLE: {SCHEMA_NAME}.{table_name}")
    print(f"Path: {file_info.path}")
    print(f"Size: {file_info.size_bytes:,} bytes")
    print(f"Modified UTC: {file_info.modified_at.isoformat()}")

    validate_csv_columns(file_info)
    table_columns = validate_target_table(connection, csv_file, table_name)

    current_rows = count_table_rows(connection, table_name)
    completed_import = find_completed_import(connection, file_info, table_name)

    print(f"Rows currently in table: {current_rows:,}")

    if completed_import and current_rows > 0 and not force:
        import_id, finished_at, source_rows, inserted_rows = completed_import
        print(
            "SKIPPED: this exact CSV file was already imported "
            f"(import_id={import_id}, finished_at={finished_at}, "
            f"source_rows={source_rows:,}, inserted_rows={inserted_rows:,})."
        )
        return

    if dry_run:
        action = "would import"
        if completed_import and current_rows > 0:
            action = "would skip"
        print(f"DRY RUN: validation passed; {action} {csv_file}.")
        return

    import_id = start_import_log(connection, file_info, table_name)
    connection.commit()

    staging_table = f"stg_{table_name[:32]}_{uuid.uuid4().hex[:8]}"

    try:
        with connection.cursor() as cursor:
            print("Copying CSV into temporary staging table...")
            source_rows = copy_csv_to_staging(
                cursor=cursor,
                file_info=file_info,
                staging_table=staging_table,
                target_table=table_name,
                columns=table_columns,
            )

            print(f"Rows read from CSV: {source_rows:,}")
            print("Inserting only distinct rows that do not already exist...")
            inserted_rows = insert_distinct_rows(
                cursor=cursor,
                staging_table=staging_table,
                target_table=table_name,
                columns=table_columns,
            )

            duplicate_rows = source_rows - inserted_rows
            deleted_duplicates = delete_existing_duplicate_rows(
                cursor=cursor,
                table_name=table_name,
                columns=table_columns,
                should_run=current_rows > 0,
            )
            analyze_table(cursor, table_name)

        connection.commit()

        complete_import_log(
            connection=connection,
            import_id=import_id,
            source_rows=source_rows,
            inserted_rows=inserted_rows,
            duplicate_rows=duplicate_rows,
            deleted_existing_duplicates=deleted_duplicates,
        )
        connection.commit()

    except Exception as error:
        connection.rollback()
        fail_import_log(connection, import_id, str(error))
        connection.commit()
        raise

    print("Import completed.")
    print(f"Inserted rows: {inserted_rows:,}")
    print(f"Duplicate rows skipped: {duplicate_rows:,}")
    print(f"Existing duplicate rows deleted: {deleted_duplicates:,}")


def print_final_row_counts(connection) -> None:
    print_banner("FINAL POSTGRESQL ROW COUNT")
    for table_name in TABLE_MAPPING.values():
        row_count = count_table_rows(connection, table_name)
        print(f"{SCHEMA_NAME}.{table_name:<20} {row_count:>15,} rows")


def print_import_log_summary(connection) -> None:
    print_banner("CSV IMPORT LOG SUMMARY")
    with connection.cursor() as cursor:
        cursor.execute(
            sql.SQL(
                """
                SELECT
                    import_id,
                    file_name,
                    target_schema || '.' || target_table AS target_table,
                    status,
                    source_rows,
                    inserted_rows,
                    duplicate_rows,
                    deleted_existing_duplicates,
                    finished_at
                FROM {}
                ORDER BY import_id;
                """
            ).format(table_id(SCHEMA_NAME, IMPORT_LOG_TABLE))
        )

        rows = cursor.fetchall()
        if not rows:
            print("No import log records yet.")
            return

        for row in rows:
            (
                import_id,
                file_name,
                target,
                status,
                source_rows,
                inserted_rows,
                duplicate_rows,
                deleted_duplicates,
                finished_at,
            ) = row
            print(
                f"{import_id:>4} | {file_name:<20} | {target:<30} | "
                f"{status:<9} | source={source_rows or 0:>12,} | "
                f"inserted={inserted_rows or 0:>12,} | "
                f"skipped={duplicate_rows or 0:>12,} | "
                f"deleted={deleted_duplicates or 0:>8,} | {finished_at}"
            )


def test_connection(connection) -> None:
    with connection.cursor() as cursor:
        cursor.execute("SELECT current_database();")
        database_name = cursor.fetchone()[0]
    print(f"Connected to PostgreSQL database: {database_name}")


def main() -> None:
    args = parse_args()
    data_folder = args.data_folder.resolve()
    selected_files = normalize_selected_files(args.only)

    print_banner("CHECKING DATA FOLDER")
    if not data_folder.exists():
        raise FileNotFoundError(f"Data folder not found: {data_folder}")
    print(f"Data folder: {data_folder}")

    print_banner("TESTING POSTGRESQL CONNECTION")
    connection = psycopg2.connect(**DB_CONFIG)

    try:
        test_connection(connection)
        ensure_import_log_table(connection)
        connection.commit()

        for csv_file in selected_files:
            import_csv_file(
                connection=connection,
                data_folder=data_folder,
                csv_file=csv_file,
                table_name=TABLE_MAPPING[csv_file],
                force=args.force,
                dry_run=args.dry_run,
            )

        print_final_row_counts(connection)
        print_import_log_summary(connection)

    finally:
        connection.close()

    print_banner("CSV IMPORT PROCESS COMPLETED")


if __name__ == "__main__":
    main()
