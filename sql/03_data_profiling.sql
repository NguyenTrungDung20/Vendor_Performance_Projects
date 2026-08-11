-- ============================================================
-- IMPORTANT:
-- No UPDATE / DELETE / TRUNCATE statements in this file.
-- This file is read-only.
-- ============================================================


-- ============================================================
-- 0. TEST DATABASE CONNECTION
-- ============================================================

SET search_path TO vendor, public;

SELECT
    current_database() AS database_name,
    current_user AS user_name,
    current_schema() AS current_schema;


-- ============================================================
-- 1. CHECK ALL TABLE ROW COUNTS
-- ============================================================

SELECT
    'begin_inventory' AS table_name,
    COUNT(*) AS row_count
FROM vendor.begin_inventory

UNION ALL

SELECT
    'end_inventory',
    COUNT(*)
FROM vendor.end_inventory

UNION ALL

SELECT
    'purchases',
    COUNT(*)
FROM vendor.purchases

UNION ALL

SELECT
    'purchase_prices',
    COUNT(*)
FROM vendor.purchase_prices

UNION ALL

SELECT
    'sales',
    COUNT(*)
FROM vendor.sales

UNION ALL

SELECT
    'vendor_invoice',
    COUNT(*)
FROM vendor.vendor_invoice

ORDER BY table_name;


-- ============================================================
-- 2. CHECK COLUMN DATA TYPES
-- ============================================================

SELECT
    table_name,
    ordinal_position,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'vendor'
ORDER BY
    table_name,
    ordinal_position;

/*
2. CHECK COLUMN DATA TYPES

Numeric fields       ✅ PASS
Integer fields       ✅ PASS
Text / ID fields     ✅ PASS
Import-log fields    ✅ PASS
Business date fields ⚠ NEED REVIEW
*/

-- ============================================================
-- 3. CHECK BEGIN INVENTORY DUPLICATES
-- ============================================================

SELECT
    "InventoryId",
    "Store",
    "City",
    "Brand",
    "Description",
    "Size",
    "onHand",
    "Price",
    "startDate",
    COUNT(*) AS duplicate_count
FROM vendor.begin_inventory
GROUP BY
    "InventoryId",
    "Store",
    "City",
    "Brand",
    "Description",
    "Size",
    "onHand",
    "Price",
    "startDate"
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;


-- ============================================================
-- 4. CHECK END INVENTORY DUPLICATES
-- ============================================================

SELECT
    "InventoryId",
    "Store",
    "City",
    "Brand",
    "Description",
    "Size",
    "onHand",
    "Price",
    "endDate",
    COUNT(*) AS duplicate_count
FROM vendor.end_inventory
GROUP BY
    "InventoryId",
    "Store",
    "City",
    "Brand",
    "Description",
    "Size",
    "onHand",
    "Price",
    "endDate"
HAVING COUNT(*) > 1
ORDER BY duplicate_count DESC;

-- ============================================================
-- 5. CHECK INVENTORY ID UNIQUENESS
-- ============================================================

SELECT
    'begin_inventory' AS table_name,
    COUNT(*) AS total_rows,
    COUNT(DISTINCT "InventoryId") AS unique_inventory_id,
    COUNT(*) - COUNT(DISTINCT "InventoryId") AS duplicated_inventory_id
FROM vendor.begin_inventory

UNION ALL

SELECT
    'end_inventory',
    COUNT(*),
    COUNT(DISTINCT "InventoryId"),
    COUNT(*) - COUNT(DISTINCT "InventoryId")
FROM vendor.end_inventory;

-- ============================================================
-- 6. CHECK NULL AND BLANK VALUES
-- ============================================================


-- ============================================================
-- 6.1 BEGIN INVENTORY
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE "InventoryId" IS NULL
           OR TRIM("InventoryId") = ''
    ) AS inventory_id_missing,

    COUNT(*) FILTER (
        WHERE "Store" IS NULL
    ) AS store_missing,

    COUNT(*) FILTER (
        WHERE "City" IS NULL
           OR TRIM("City") = ''
    ) AS city_missing,

    COUNT(*) FILTER (
        WHERE "Brand" IS NULL
    ) AS brand_missing,

    COUNT(*) FILTER (
        WHERE "Description" IS NULL
           OR TRIM("Description") = ''
    ) AS description_missing,

    COUNT(*) FILTER (
        WHERE "Size" IS NULL
           OR TRIM("Size") = ''
    ) AS size_missing,

    COUNT(*) FILTER (
        WHERE "onHand" IS NULL
    ) AS onhand_missing,

    COUNT(*) FILTER (
        WHERE "Price" IS NULL
    ) AS price_missing,

    COUNT(*) FILTER (
        WHERE "startDate" IS NULL
           OR TRIM("startDate") = ''
    ) AS start_date_missing

FROM vendor.begin_inventory;

-- ============================================================
-- 6.2 END INVENTORY
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE "InventoryId" IS NULL
           OR TRIM("InventoryId") = ''
    ) AS inventory_id_missing,

    COUNT(*) FILTER (
        WHERE "Store" IS NULL
    ) AS store_missing,

    COUNT(*) FILTER (
        WHERE "City" IS NULL
           OR TRIM("City") = ''
    ) AS city_missing,

    COUNT(*) FILTER (
        WHERE "Brand" IS NULL
    ) AS brand_missing,

    COUNT(*) FILTER (
        WHERE "Description" IS NULL
           OR TRIM("Description") = ''
    ) AS description_missing,

    COUNT(*) FILTER (
        WHERE "Size" IS NULL
           OR TRIM("Size") = ''
    ) AS size_missing,

    COUNT(*) FILTER (
        WHERE "onHand" IS NULL
    ) AS onhand_missing,

    COUNT(*) FILTER (
        WHERE "Price" IS NULL
    ) AS price_missing,

    COUNT(*) FILTER (
        WHERE "endDate" IS NULL
           OR TRIM("endDate") = ''
    ) AS end_date_missing

FROM vendor.end_inventory;

-- ============================================================
-- 6.3 PURCHASES
-- ============================================================
SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE "InventoryId" IS NULL
           OR TRIM("InventoryId") = ''
    ) AS inventory_id_missing,

    COUNT(*) FILTER (
        WHERE "Store" IS NULL
    ) AS store_missing,

    COUNT(*) FILTER (
        WHERE "Brand" IS NULL
    ) AS brand_missing,

    COUNT(*) FILTER (
        WHERE "VendorNumber" IS NULL
    ) AS vendor_number_missing,

    COUNT(*) FILTER (
        WHERE "VendorName" IS NULL
           OR TRIM("VendorName") = ''
    ) AS vendor_name_missing,

    COUNT(*) FILTER (
        WHERE "PONumber" IS NULL
    ) AS po_number_missing,

    COUNT(*) FILTER (
        WHERE "PODate" IS NULL
           OR TRIM("PODate") = ''
    ) AS po_date_missing,

    COUNT(*) FILTER (
        WHERE "ReceivingDate" IS NULL
           OR TRIM("ReceivingDate") = ''
    ) AS receiving_date_missing,

    COUNT(*) FILTER (
        WHERE "InvoiceDate" IS NULL
           OR TRIM("InvoiceDate") = ''
    ) AS invoice_date_missing,

    COUNT(*) FILTER (
        WHERE "PayDate" IS NULL
           OR TRIM("PayDate") = ''
    ) AS pay_date_missing,

    COUNT(*) FILTER (
        WHERE "PurchasePrice" IS NULL
    ) AS purchase_price_missing,

    COUNT(*) FILTER (
        WHERE "Quantity" IS NULL
    ) AS quantity_missing,

    COUNT(*) FILTER (
        WHERE "Dollars" IS NULL
    ) AS dollars_missing

FROM vendor.purchases;

-- ============================================================
-- 6.4 PURCHASES PRICES
-- ============================================================
SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE "Brand" IS NULL
    ) AS brand_missing,

    COUNT(*) FILTER (
        WHERE "Description" IS NULL
           OR TRIM("Description") = ''
    ) AS description_missing,

    COUNT(*) FILTER (
        WHERE "Price" IS NULL
    ) AS price_missing,

    COUNT(*) FILTER (
        WHERE "Size" IS NULL
           OR TRIM("Size") = ''
    ) AS size_missing,

    COUNT(*) FILTER (
        WHERE "Volume" IS NULL
    ) AS volume_missing,

    COUNT(*) FILTER (
        WHERE "Classification" IS NULL
    ) AS classification_missing,

    COUNT(*) FILTER (
        WHERE "PurchasePrice" IS NULL
    ) AS purchase_price_missing,

    COUNT(*) FILTER (
        WHERE "VendorNumber" IS NULL
    ) AS vendor_number_missing,

    COUNT(*) FILTER (
        WHERE "VendorName" IS NULL
           OR TRIM("VendorName") = ''
    ) AS vendor_name_missing

FROM vendor.purchase_prices;

-- ============================================================
-- 6.5 SALES
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE "InventoryId" IS NULL
           OR TRIM("InventoryId") = ''
    ) AS inventory_id_missing,

    COUNT(*) FILTER (
        WHERE "Store" IS NULL
    ) AS store_missing,

    COUNT(*) FILTER (
        WHERE "Brand" IS NULL
    ) AS brand_missing,

    COUNT(*) FILTER (
        WHERE "Description" IS NULL
           OR TRIM("Description") = ''
    ) AS description_missing,

    COUNT(*) FILTER (
        WHERE "Size" IS NULL
           OR TRIM("Size") = ''
    ) AS size_missing,

    COUNT(*) FILTER (
        WHERE "SalesQuantity" IS NULL
    ) AS sales_quantity_missing,

    COUNT(*) FILTER (
        WHERE "SalesDollars" IS NULL
    ) AS sales_dollars_missing,

    COUNT(*) FILTER (
        WHERE "SalesPrice" IS NULL
    ) AS sales_price_missing,

    COUNT(*) FILTER (
        WHERE "SalesDate" IS NULL
           OR TRIM("SalesDate") = ''
    ) AS sales_date_missing,

    COUNT(*) FILTER (
        WHERE "VendorNo" IS NULL
    ) AS vendor_number_missing,

    COUNT(*) FILTER (
        WHERE "VendorName" IS NULL
           OR TRIM("VendorName") = ''
    ) AS vendor_name_missing

FROM vendor.sales;

-- ============================================================
-- 6.6 VENDOR INVOICE
-- ============================================================
SELECT
    COUNT(*) AS total_rows,

    COUNT(*) FILTER (
        WHERE "VendorNumber" IS NULL
    ) AS vendor_number_missing,

    COUNT(*) FILTER (
        WHERE "VendorName" IS NULL
           OR TRIM("VendorName") = ''
    ) AS vendor_name_missing,

    COUNT(*) FILTER (
        WHERE "InvoiceDate" IS NULL
           OR TRIM("InvoiceDate") = ''
    ) AS invoice_date_missing,

    COUNT(*) FILTER (
        WHERE "PONumber" IS NULL
    ) AS po_number_missing,

    COUNT(*) FILTER (
        WHERE "PODate" IS NULL
           OR TRIM("PODate") = ''
    ) AS po_date_missing,

    COUNT(*) FILTER (
        WHERE "PayDate" IS NULL
           OR TRIM("PayDate") = ''
    ) AS pay_date_missing,

    COUNT(*) FILTER (
        WHERE "Quantity" IS NULL
    ) AS quantity_missing,

    COUNT(*) FILTER (
        WHERE "Dollars" IS NULL
    ) AS dollars_missing,

    COUNT(*) FILTER (
        WHERE "Freight" IS NULL
    ) AS freight_missing,

    COUNT(*) FILTER (
        WHERE "Approval" IS NULL
           OR TRIM("Approval") = ''
    ) AS approval_missing

FROM vendor.vendor_invoice;

-- ============================================================
-- 7. CHECK CANDIDATE KEYS
-- ============================================================


-- ============================================================
-- 7.1 PURCHASE_PRICES
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNT(DISTINCT "Brand")
        AS unique_brand,

    COUNT(*) - COUNT(DISTINCT "Brand")
        AS duplicate_brand,

    COUNT(DISTINCT ("Brand", "VendorNumber"))
        AS unique_brand_vendor,

    COUNT(*) - COUNT(DISTINCT ("Brand", "VendorNumber"))
        AS duplicate_brand_vendor

FROM vendor.purchase_prices;

-- ============================================================
-- 7.2 PURCHASES
-- ============================================================

SELECT
    COUNT(*) AS total_rows,

    COUNT(
        DISTINCT (
            "InventoryId",
            "PONumber"
        )
    ) AS unique_inventory_po,

    COUNT(*) -
    COUNT(
        DISTINCT (
            "InventoryId",
            "PONumber"
        )
    ) AS duplicate_inventory_po,

    COUNT(
        DISTINCT (
            "InventoryId",
            "PONumber",
            "ReceivingDate"
        )
    ) AS unique_inventory_po_receiving,

    COUNT(*) -
    COUNT(
        DISTINCT (
            "InventoryId",
            "PONumber",
            "ReceivingDate"
        )
    ) AS duplicate_inventory_po_receiving

FROM vendor.purchases;

-- ============================================================
-- 7.3. SALES
-- ============================================================
SELECT
    COUNT(*) AS total_rows,

    COUNT(
        DISTINCT (
            "InventoryId",
            "SalesDate"
        )
    ) AS unique_inventory_date,

    COUNT(*) -
    COUNT(
        DISTINCT (
            "InventoryId",
            "SalesDate"
        )
    ) AS duplicate_inventory_date

FROM vendor.sales;
-- ============================================================
-- 7.4. VENDOR INVOICE
-- ============================================================
SELECT
    COUNT(*) AS total_rows,

    COUNT(DISTINCT "PONumber")
        AS unique_po_number,

    COUNT(*) - COUNT(DISTINCT "PONumber")
        AS duplicate_po_number,

    COUNT(
        DISTINCT (
            "VendorNumber",
            "PONumber"
        )
    ) AS unique_vendor_po,

    COUNT(*) -
    COUNT(
        DISTINCT (
            "VendorNumber",
            "PONumber"
        )
    ) AS duplicate_vendor_po,

    COUNT(
        DISTINCT (
            "VendorNumber",
            "PONumber",
            "InvoiceDate"
        )
    ) AS unique_vendor_po_invoice,

    COUNT(*) -
    COUNT(
        DISTINCT (
            "VendorNumber",
            "PONumber",
            "InvoiceDate"
        )
    ) AS duplicate_vendor_po_invoice

FROM vendor.vendor_invoice;

-- ============================================================
-- 8. CHECK DATE FORMAT
-- Expected format: YYYY-MM-DD
-- ============================================================

SELECT
    'begin_inventory.startDate' AS date_column,
    COUNT(*) AS invalid_rows
FROM vendor.begin_inventory
WHERE "startDate" IS NOT NULL
  AND BTRIM("startDate") <> ''
  AND BTRIM("startDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'end_inventory.endDate',
    COUNT(*)
FROM vendor.end_inventory
WHERE "endDate" IS NOT NULL
  AND BTRIM("endDate") <> ''
  AND BTRIM("endDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'purchases.PODate',
    COUNT(*)
FROM vendor.purchases
WHERE "PODate" IS NOT NULL
  AND BTRIM("PODate") <> ''
  AND BTRIM("PODate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'purchases.ReceivingDate',
    COUNT(*)
FROM vendor.purchases
WHERE "ReceivingDate" IS NOT NULL
  AND BTRIM("ReceivingDate") <> ''
  AND BTRIM("ReceivingDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'purchases.InvoiceDate',
    COUNT(*)
FROM vendor.purchases
WHERE "InvoiceDate" IS NOT NULL
  AND BTRIM("InvoiceDate") <> ''
  AND BTRIM("InvoiceDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'purchases.PayDate',
    COUNT(*)
FROM vendor.purchases
WHERE "PayDate" IS NOT NULL
  AND BTRIM("PayDate") <> ''
  AND BTRIM("PayDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'sales.SalesDate',
    COUNT(*)
FROM vendor.sales
WHERE "SalesDate" IS NOT NULL
  AND BTRIM("SalesDate") <> ''
  AND BTRIM("SalesDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'vendor_invoice.InvoiceDate',
    COUNT(*)
FROM vendor.vendor_invoice
WHERE "InvoiceDate" IS NOT NULL
  AND BTRIM("InvoiceDate") <> ''
  AND BTRIM("InvoiceDate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'vendor_invoice.PODate',
    COUNT(*)
FROM vendor.vendor_invoice
WHERE "PODate" IS NOT NULL
  AND BTRIM("PODate") <> ''
  AND BTRIM("PODate") !~ '^\d{4}-\d{2}-\d{2}$'

UNION ALL

SELECT
    'vendor_invoice.PayDate',
    COUNT(*)
FROM vendor.vendor_invoice
WHERE "PayDate" IS NOT NULL
  AND BTRIM("PayDate") <> ''
  AND BTRIM("PayDate") !~ '^\d{4}-\d{2}-\d{2}$';