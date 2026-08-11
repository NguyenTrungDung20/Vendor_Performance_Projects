DROP TABLE IF EXISTS vendor.begin_inventory;
CREATE TABLE vendor.begin_inventory (
    "InventoryId" VARCHAR(30),
    "Store" INTEGER,
    "City" VARCHAR(50),
    "Brand" INTEGER,
    "Description" TEXT,
    "Size" VARCHAR(20),
    "onHand" INTEGER,
    "Price" NUMERIC(10,2),
    "startDate" VARCHAR(10)
);

DROP TABLE IF EXISTS vendor.end_inventory;
CREATE TABLE vendor.end_inventory (
    "InventoryId" VARCHAR(30),
    "Store" INTEGER,
    "City" VARCHAR(50),
    "Brand" INTEGER,
    "Description" TEXT,
    "Size" VARCHAR(20),
    "onHand" INTEGER,
    "Price" NUMERIC(10,2),
    "endDate" VARCHAR(10)
);

DROP TABLE IF EXISTS vendor.purchases;
CREATE TABLE vendor.purchases (
    "InventoryId" VARCHAR(30),
    "Store" INTEGER,
    "Brand" INTEGER,
    "Description" TEXT,
    "Size" VARCHAR(20),
    "VendorNumber" INTEGER,
    "VendorName" VARCHAR(100),
    "PONumber" INTEGER,
    "PODate" VARCHAR(10),
    "ReceivingDate" VARCHAR(10),
    "InvoiceDate" VARCHAR(10),
    "PayDate" VARCHAR(10),
    "PurchasePrice" NUMERIC(10,2),
    "Quantity" INTEGER,
    "Dollars" NUMERIC(12,2),
    "Classification" SMALLINT
);

DROP TABLE IF EXISTS vendor.purchase_prices;
CREATE TABLE vendor.purchase_prices (
    "Brand" INTEGER,
    "Description" TEXT,
    "Price" NUMERIC(10,2),
    "Size" VARCHAR(20),
    "Volume" NUMERIC(10,2),
    "Classification" SMALLINT,
    "PurchasePrice" NUMERIC(10,2),
    "VendorNumber" INTEGER,
    "VendorName" VARCHAR(100)
);

DROP TABLE IF EXISTS vendor.sales;
CREATE TABLE vendor.sales (
    "InventoryId" VARCHAR(30),
    "Store" INTEGER,
    "Brand" INTEGER,
    "Description" TEXT,
    "Size" VARCHAR(20),
    "SalesQuantity" INTEGER,
    "SalesDollars" NUMERIC(12,2),
    "SalesPrice" NUMERIC(10,2),
    "SalesDate" VARCHAR(10),
    "Volume" NUMERIC(10,2),
    "Classification" SMALLINT,
    "ExciseTax" NUMERIC(10,2),
    "VendorNo" INTEGER,
    "VendorName" VARCHAR(100)
);

DROP TABLE IF EXISTS vendor.vendor_invoice;
CREATE TABLE vendor.vendor_invoice (
    "VendorNumber" INTEGER,
    "VendorName" VARCHAR(100),
    "InvoiceDate" VARCHAR(10),
    "PONumber" INTEGER,
    "PODate" VARCHAR(10),
    "PayDate" VARCHAR(10),
    "Quantity" INTEGER,
    "Dollars" NUMERIC(12,2),
    "Freight" NUMERIC(10,2),
    "Approval" VARCHAR(50)
);
