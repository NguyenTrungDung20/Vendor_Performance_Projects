import os
import pandas as pd

# ==========================
# Đường dẫn
# ==========================
DATA_FOLDER = r"E:\LOCAL_DISK_E\DATA_ANALYSIS\Capstone_Projects\2\Vendor_Performance_Projects\data\processed"

OUTPUT_SQL = r"E:\LOCAL_DISK_E\DATA_ANALYSIS\Capstone_Projects\2\Vendor_Performance_Projects\sql\01_create_tables.sql"

SCHEMA = "vendor"


# ==========================
# Hàm suy luận datatype
# ==========================
def infer_sql_type(series):

    if pd.api.types.is_integer_dtype(series):
        return "BIGINT"

    elif pd.api.types.is_float_dtype(series):
        return "NUMERIC(18,2)"

    elif pd.api.types.is_bool_dtype(series):
        return "BOOLEAN"

    elif pd.api.types.is_datetime64_any_dtype(series):
        return "TIMESTAMP"

    else:
        max_len = series.astype(str).str.len().max()

        if pd.isna(max_len):
            max_len = 255

        if max_len <= 255:
            return f"VARCHAR({max_len})"

        return "TEXT"


# ==========================
# Sinh CREATE TABLE
# ==========================

sql_list = []

for file in os.listdir(DATA_FOLDER):

    if not file.endswith(".csv"):
        continue

    table_name = file.replace(".csv", "")

    print(f"Reading {file}...")

    df = pd.read_csv(
        os.path.join(DATA_FOLDER, file),
        nrows=5000,
        low_memory=False
    )

    sql = f"DROP TABLE IF EXISTS {SCHEMA}.{table_name};\n"

    sql += f"CREATE TABLE {SCHEMA}.{table_name} (\n"

    columns = []

    for col in df.columns:

        sql_type = infer_sql_type(df[col])

        columns.append(f'    "{col}" {sql_type}')

    sql += ",\n".join(columns)

    sql += "\n);\n\n"

    sql_list.append(sql)


# ==========================
# Ghi file SQL
# ==========================

with open(OUTPUT_SQL, "w", encoding="utf-8") as f:

    f.writelines(sql_list)

print("=" * 60)
print("Finished!")
print("Output:", OUTPUT_SQL)
print("=" * 60)