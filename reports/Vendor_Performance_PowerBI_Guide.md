# Vendor Performance Power BI Guide

## Files created

- `Vendor_Performance_PowerBI.pbip`: Power BI Project starter. Open this with Power BI Desktop, refresh data, then use `File > Save As` to save a `.pbix`.
- `Vendor_Performance_PowerBI.SemanticModel`: text-based semantic model loading CSV tables from `reports/powerbi_data`.
- `Vendor_Performance_PowerBI.Report`: starter report with four planned pages.
- `powerbi_data`: curated CSV tables generated from the notebook logic.
- `powerbi_images`: PNG exports from `notebooks/02_vendor_analysis.ipynb`.
- `PowerBI_Measures.dax`: DAX measures to copy/check in the model if Power BI Desktop does not auto-load them from the project model.
- `Vendor_Performance_Theme.json`: theme file to import from `View > Browse for themes`.

## Recommended pages

### 1. Executive Overview

Use:
- `KPI Summary`
- `Vendor Sales Summary`
- `Top 10 Vendors By Sales`
- `Top 10 Brands By Sales`

Visuals:
- Cards: Total Sales, Total Purchases, Gross Profit, Profit Margin %, Stock Turnover, Unsold Inventory Value.
- Bar chart: `Top 10 Vendors By Sales[VendorName]` by `TotalSalesDollars`.
- Bar chart: `Top 10 Brands By Sales[Description]` by `TotalSalesDollars`.

Notebook image equivalents:
- `powerbi_images/cell_29_chart_07.png`

### 2. Vendor Analysis

Use:
- `Vendor Purchase Contribution`
- `Vendor Purchase Share`
- `Vendor Sales Summary`

Visuals:
- Pareto chart: `VendorName` by `PurchaseContributionPct`, line by `CumulativeContributionPct`.
- Donut chart: `Vendor Purchase Share[VendorName]` by `PurchaseContributionPct`.
- Table: VendorName, TotalPurchaseDollars, TotalSalesDollars, GrossProfit, PurchaseContributionPct.

Notebook image equivalents:
- `powerbi_images/cell_32_chart_08.png`
- `powerbi_images/cell_34_chart_09.png`

### 3. Brand Pricing

Use:
- `Brand Margin Targets`
- `Bulk Purchase Analysis`
- `Vendor Sales Summary`

Visuals:
- Scatter chart: `TotalSalesDollars` on X, `ProfitMargin` on Y, legend/color by `IsTargetBrand`.
- Column chart: `OrderSize` by `AverageUnitPurchasePrice`.
- Table filtered to `IsTargetBrand = True`.

Notebook image equivalents:
- `powerbi_images/cell_24_chart_06.png`
- `powerbi_images/cell_38_chart_10.png`

### 4. Inventory & Statistics

Use:
- `Low Turnover Vendors`
- `Top 10 Unsold Inventory Value`
- `Profit Margin Confidence Intervals`
- `Profit Margin T Test`
- `Correlation Matrix`

Visuals:
- Bar chart: `Low Turnover Vendors[VendorName]` by `StockTurnover`.
- Bar chart: `Top 10 Unsold Inventory Value[VendorName]` by `UnsoldInventoryValue`.
- Error bar or combo chart: `PerformanceGroup`, `MeanProfitMargin`, `Lower95`, `Upper95`.
- Matrix: `Correlation Matrix` for the correlation heatmap.

Notebook image equivalents:
- `powerbi_images/cell_17_chart_05.png`
- `powerbi_images/cell_46_chart_11.png`

## Notes

The notebook filters analysis data to rows where `GrossProfit > 0`, `ProfitMargin > 0`, and `TotalSalesQuantity > 0`. The main Power BI table `Vendor Sales Summary` uses the same cleaned dataset.

Power BI `.pbix` is a binary Desktop file. This repository now contains a `.pbip` project and all report assets; after opening it in Power BI Desktop, save it as `reports/Vendor_Performance_PowerBI.pbix`.
