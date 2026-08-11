import os


DB_CONFIG = {
    "host": os.getenv("VENDOR_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("VENDOR_DB_PORT", "5432")),
    "database": os.getenv("VENDOR_DB_NAME", "vendor_performance"),
    "user": os.getenv("VENDOR_DB_USER", "postgres"),
    "password": os.getenv("VENDOR_DB_PASSWORD", ""),
}
