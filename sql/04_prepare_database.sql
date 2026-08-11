-- ============================================================
-- VENDOR PERFORMANCE PROJECT
-- FILE: 04_prepare_database.sql
-- PURPOSE:
--     Prepare imported tables for analysis / EDA
-- ============================================================

SET search_path TO vendor, public;


-- ============================================================
-- 1. CONVERT VARCHAR DATE COLUMNS → DATE
-- ============================================================

BEGIN;

ALTER TABLE vendor.begin_inventory
ALTER COLUMN "startDate"
TYPE DATE
USING NULLIF(BTRIM("startDate"), '')::DATE;


ALTER TABLE vendor.end_inventory
ALTER COLUMN "endDate"
TYPE DATE
USING NULLIF(BTRIM("endDate"), '')::DATE;


ALTER TABLE vendor.purchases
ALTER COLUMN "PODate"
TYPE DATE
USING NULLIF(BTRIM("PODate"), '')::DATE,

ALTER COLUMN "ReceivingDate"
TYPE DATE
USING NULLIF(BTRIM("ReceivingDate"), '')::DATE,

ALTER COLUMN "InvoiceDate"
TYPE DATE
USING NULLIF(BTRIM("InvoiceDate"), '')::DATE,

ALTER COLUMN "PayDate"
TYPE DATE
USING NULLIF(BTRIM("PayDate"), '')::DATE;


ALTER TABLE vendor.sales
ALTER COLUMN "SalesDate"
TYPE DATE
USING NULLIF(BTRIM("SalesDate"), '')::DATE;


ALTER TABLE vendor.vendor_invoice
ALTER COLUMN "InvoiceDate"
TYPE DATE
USING NULLIF(BTRIM("InvoiceDate"), '')::DATE,

ALTER COLUMN "PODate"
TYPE DATE
USING NULLIF(BTRIM("PODate"), '')::DATE,

ALTER COLUMN "PayDate"
TYPE DATE
USING NULLIF(BTRIM("PayDate"), '')::DATE;

COMMIT;

-- ============================================================
-- 2. PRIMARY KEYS
-- ============================================================


-- 1. BEGIN INVENTORY
ALTER TABLE vendor.begin_inventory
ADD CONSTRAINT pk_begin_inventory
PRIMARY KEY ("InventoryId");


-- 2. END INVENTORY
ALTER TABLE vendor.end_inventory
ADD CONSTRAINT pk_end_inventory
PRIMARY KEY ("InventoryId");


-- 3. PURCHASE PRICES
ALTER TABLE vendor.purchase_prices
ADD CONSTRAINT pk_purchase_prices
PRIMARY KEY ("Brand");


-- 4. PURCHASES
ALTER TABLE vendor.purchases
ADD CONSTRAINT pk_purchases
PRIMARY KEY (
    "InventoryId",
    "PONumber",
    "ReceivingDate"
);


-- 5. SALES
ALTER TABLE vendor.sales
ADD CONSTRAINT pk_sales
PRIMARY KEY (
    "InventoryId",
    "SalesDate"
);


-- 6. VENDOR INVOICE
ALTER TABLE vendor.vendor_invoice
ADD CONSTRAINT pk_vendor_invoice
PRIMARY KEY ("PONumber");

-- ============================================================
-- 3. CHECK Primary Key AND Data Types
-- ============================================================
SELECT
    tc.table_name,
    tc.constraint_name,
    kcu.column_name,
    kcu.ordinal_position
FROM information_schema.table_constraints tc
JOIN information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
   AND tc.table_schema = kcu.table_schema
WHERE tc.table_schema = 'vendor'
  AND tc.constraint_type = 'PRIMARY KEY'
  AND tc.table_name IN (
      'begin_inventory',
      'end_inventory',
      'purchase_prices',
      'purchases',
      'sales',
      'vendor_invoice'
  )
ORDER BY
    tc.table_name,
    kcu.ordinal_position;



SELECT
    table_name,
    column_name,
    data_type
FROM information_schema.columns
WHERE table_schema = 'vendor'
  AND column_name IN (
      'startDate',
      'endDate',
      'PODate',
      'ReceivingDate',
      'InvoiceDate',
      'PayDate',
      'SalesDate'
  )
ORDER BY
    table_name,
    ordinal_position;