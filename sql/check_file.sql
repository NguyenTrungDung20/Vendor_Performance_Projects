SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_schema = 'vendor'
ORDER BY table_name;



SELECT * FROM vendor.begin_inventory AS begin_inv;
SELECT * FROM vendor.end_inventory AS end_inv;
SELECT * FROM vendor.purchases AS purchases;
SELECT * FROM vendor.purchase_prices AS purchase_prices LIMIT 100;
SELECT * FROM vendor.sales AS sales;
SELECT * FROM vendor.vendor_invoice AS vendor_invoice;

SELECT
    import_id,
    file_name,
    target_schema || '.' || target_table AS target_table,
    status,
    source_rows,
    inserted_rows,
    duplicate_rows,
    deleted_existing_duplicates,
    started_at,
    finished_at
FROM vendor.csv_import_log
WHERE status = 'completed'
ORDER BY import_id;


-- ============================================================
-- CHECK 10 DATE COLUMNS AFTER CONVERSION
-- ============================================================

SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'vendor'
  AND (
        (table_name = 'begin_inventory'
            AND column_name = 'startDate')

     OR (table_name = 'end_inventory'
            AND column_name = 'endDate')

     OR (table_name = 'purchases'
            AND column_name IN (
                'PODate',
                'ReceivingDate',
                'InvoiceDate',
                'PayDate'
            ))

     OR (table_name = 'sales'
            AND column_name = 'SalesDate')

     OR (table_name = 'vendor_invoice'
            AND column_name IN (
                'InvoiceDate',
                'PODate',
                'PayDate'
            ))
  )
ORDER BY
    table_name,
    ordinal_position;

-- ============================================================
-- CHECK DATE RANGES AFTER CONVERSION
-- ============================================================

SELECT
    'begin_inventory.startDate' AS date_column,
    MIN("startDate") AS min_date,
    MAX("startDate") AS max_date,
    COUNT(*) FILTER (WHERE "startDate" IS NULL) AS null_rows
FROM vendor.begin_inventory

UNION ALL

SELECT
    'end_inventory.endDate',
    MIN("endDate"),
    MAX("endDate"),
    COUNT(*) FILTER (WHERE "endDate" IS NULL)
FROM vendor.end_inventory

UNION ALL

SELECT
    'purchases.PODate',
    MIN("PODate"),
    MAX("PODate"),
    COUNT(*) FILTER (WHERE "PODate" IS NULL)
FROM vendor.purchases

UNION ALL

SELECT
    'purchases.ReceivingDate',
    MIN("ReceivingDate"),
    MAX("ReceivingDate"),
    COUNT(*) FILTER (WHERE "ReceivingDate" IS NULL)
FROM vendor.purchases

UNION ALL

SELECT
    'purchases.InvoiceDate',
    MIN("InvoiceDate"),
    MAX("InvoiceDate"),
    COUNT(*) FILTER (WHERE "InvoiceDate" IS NULL)
FROM vendor.purchases

UNION ALL

SELECT
    'purchases.PayDate',
    MIN("PayDate"),
    MAX("PayDate"),
    COUNT(*) FILTER (WHERE "PayDate" IS NULL)
FROM vendor.purchases

UNION ALL

SELECT
    'sales.SalesDate',
    MIN("SalesDate"),
    MAX("SalesDate"),
    COUNT(*) FILTER (WHERE "SalesDate" IS NULL)
FROM vendor.sales

UNION ALL

SELECT
    'vendor_invoice.InvoiceDate',
    MIN("InvoiceDate"),
    MAX("InvoiceDate"),
    COUNT(*) FILTER (WHERE "InvoiceDate" IS NULL)
FROM vendor.vendor_invoice

UNION ALL

SELECT
    'vendor_invoice.PODate',
    MIN("PODate"),
    MAX("PODate"),
    COUNT(*) FILTER (WHERE "PODate" IS NULL)
FROM vendor.vendor_invoice

UNION ALL

SELECT
    'vendor_invoice.PayDate',
    MIN("PayDate"),
    MAX("PayDate"),
    COUNT(*) FILTER (WHERE "PayDate" IS NULL)
FROM vendor.vendor_invoice;