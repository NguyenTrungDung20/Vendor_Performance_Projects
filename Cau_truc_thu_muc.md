# Cấu trúc thư mục dự án Vendor Performance

Tài liệu này mô tả cấu trúc thực tế của dự án `Vendor_Performance_Projects`. Các thư mục môi trường như `Python(3.13.09).venv/` và cache như `__pycache__/`, `.pbi/cache.abf` không được xem là source chính của dự án.

```text
Vendor_Performance_Projects/
├── .vscode/
│   └── Cấu hình làm việc trong VS Code.
│
├── data/
│   ├── README.md
│   │
│   ├── raw/
│   │   ├── begin_inventory.csv
│   │   ├── end_inventory.csv
│   │   ├── purchase_prices.csv
│   │   ├── purchases.csv
│   │   ├── sales.csv
│   │   └── vendor_invoice.csv
│   │
│   ├── processed/
│   │   ├── begin_inventory.csv
│   │   ├── end_inventory.csv
│   │   ├── purchase_prices.csv
│   │   ├── purchases.csv
│   │   ├── sales.csv
│   │   └── vendor_invoice.csv
│   │
│   ├── backup/
│   │   ├── begin_inventory-checkpoint.csv
│   │   ├── begin_inventory.csv
│   │   ├── end_inventory.csv
│   │   ├── purchase_prices.csv
│   │   ├── purchases.csv
│   │   ├── sales.csv
│   │   └── vendor_invoice.csv
│   │
│   └── external/
│       └── Thư mục dự phòng cho dữ liệu ngoài; hiện chưa có file.
│
├── notebooks/
│   ├── 01_eda_.ipynb
│   └── 02_vendor_analysis.ipynb
│
├── outputs/
│   ├── existing_imports_20260808_132113.err.log
│   ├── existing_imports_20260808_132113.out.log
│   ├── existing_imports_20260808_132113.pid.txt
│   ├── sales_import_20260808_131153.err.log
│   └── sales_import_20260808_131153.out.log
│
├── python/
│   ├── config.py
│   ├── test_connection.py
│   ├── 01_generate_tables.py
│   ├── 02_import_csv.py
│   ├── 03_prepare_powerbi_report_data.py
│   └── 04_create_powerbi_project.py
│
├── reports/
│   ├── powerbi_data/
│   │   ├── brand_margin_targets.csv
│   │   ├── bulk_purchase_analysis.csv
│   │   ├── correlation_matrix.csv
│   │   ├── kpi_summary.csv
│   │   ├── low_turnover_vendors.csv
│   │   ├── profit_margin_confidence_intervals.csv
│   │   ├── profit_margin_t_test.csv
│   │   ├── target_brand_candidates.csv
│   │   ├── top_10_brands_by_sales.csv
│   │   ├── top_10_unsold_inventory_value.csv
│   │   ├── top_10_vendors_by_sales.csv
│   │   ├── vendor_purchase_contribution.csv
│   │   ├── vendor_purchase_share.csv
│   │   ├── vendor_sales_summary.csv
│   │   └── vendor_sales_summary_clean.csv
│   │
│   ├── powerbi_images/
│   │   ├── cell_10_chart_01.png
│   │   ├── cell_11_chart_02.png
│   │   ├── cell_15_chart_03.png
│   │   ├── cell_16_chart_04.png
│   │   ├── cell_17_chart_05.png
│   │   ├── cell_24_chart_06.png
│   │   ├── cell_29_chart_07.png
│   │   ├── cell_32_chart_08.png
│   │   ├── cell_34_chart_09.png
│   │   ├── cell_38_chart_10.png
│   │   └── cell_46_chart_11.png
│   │
│   ├── Reports_pdf/
│   │   ├── Vendor_Performance_Report.md
│   │   ├── image.png
│   │   ├── image-1.png
│   │   ├── image-2.png
│   │   ├── image-3.png
│   │   └── image-4.png
│   │
│   ├── Vendor_Performance_PowerBI.Report/
│   │   ├── definition.pbir
│   │   ├── definition/
│   │   │   ├── report.json
│   │   │   ├── version.json
│   │   │   └── pages/
│   │   │       ├── pages.json
│   │   │       ├── 90c2e07d8e84e7d5c026/
│   │   │       │   └── Executive Overview page definition and visuals.
│   │   │       ├── 7f5d2cc28f7a4a1d9b18/
│   │   │       │   └── Vendor Analysis page definition and visuals.
│   │   │       ├── 4f0c00a74e964927b2d4/
│   │   │       │   └── Brand Pricing page definition and visuals.
│   │   │       └── dbb0d5df3d134ef4a5c8/
│   │   │           └── Inventory & Statistics page definition and visuals.
│   │   └── StaticResources/
│   │       └── Shared Power BI theme resources.
│   │
│   ├── Vendor_Performance_PowerBI.SemanticModel/
│   │   ├── definition.pbism
│   │   └── definition/
│   │       ├── database.tmdl
│   │       ├── model.tmdl
│   │       └── tables/
│   │           ├── Brand Margin Targets.tmdl
│   │           ├── Bulk Purchase Analysis.tmdl
│   │           ├── Correlation Matrix.tmdl
│   │           ├── KPI Summary.tmdl
│   │           ├── Low Turnover Vendors.tmdl
│   │           ├── Report Measures.tmdl
│   │           ├── Target Brand Candidates.tmdl
│   │           ├── Top 10 Brands By Sales.tmdl
│   │           ├── Top 10 Unsold Inventory Value.tmdl
│   │           ├── Top 10 Vendors By Sales.tmdl
│   │           ├── Vendor Purchase Contribution.tmdl
│   │           ├── Vendor Purchase Share.tmdl
│   │           └── Vendor Sales Summary.tmdl
│   │
│   ├── .gitignore
│   ├── PowerBI_Measures.dax
│   ├── Vendor_Performance_PowerBI.pbip
│   ├── Vendor_Performance_PowerBI_Guide.md
│   ├── Vendor_Performance_PowerBI_Project.zip
│   └── Vendor_Performance_Theme.json
│
├── sql/
│   ├── 00_database_creation.sql
│   ├── 01_create_tables.sql
│   ├── 02_import_data.sql
│   ├── 03_data_profiling.sql
│   ├── 04_prepare_database.sql
│   └── check_file.sql
│
├── Python(3.13.09).venv/
│   └── Virtual environment cục bộ, không phải source chính.
│
├── .gitignore
├── README.md
├── Cau_truc_thu_muc.md
└── requirements.txt
```

## Vai trò các thư mục chính

| Thư mục | Vai trò |
| --- | --- |
| `data/raw/` | Dữ liệu gốc, dùng làm nguồn ban đầu. |
| `data/processed/` | Dữ liệu đã chuẩn hóa header/format và là nguồn import PostgreSQL, Power BI data prep. |
| `data/backup/` | Bản sao lưu dữ liệu CSV. |
| `data/README.md` | Ghi chú về việc không push CSV lớn lên GitHub và cách đặt lại dữ liệu khi clone repo. |
| `notebooks/` | Notebook EDA và phân tích vendor/brand. |
| `python/` | Script tự động hóa tạo bảng, import CSV, chuẩn bị dữ liệu Power BI và sinh Power BI Project. |
| `sql/` | SQL tạo database/table, profiling dữ liệu và chuẩn bị constraint/date type. |
| `reports/powerbi_data/` | Bảng CSV đã tổng hợp/curate để nạp vào Power BI. |
| `reports/powerbi_images/` | Biểu đồ PNG export từ notebook, dùng tham chiếu khi dựng report. |
| `reports/Reports_pdf/` | Báo cáo markdown và ảnh minh họa để xuất/đọc như report tĩnh. |
| `reports/Vendor_Performance_PowerBI.Report/` | Report definition của Power BI Project. |
| `reports/Vendor_Performance_PowerBI.SemanticModel/` | Semantic model dạng TMDL của Power BI Project. |
| `outputs/` | Log import CSV vào PostgreSQL. |

## Luồng file chính

```text
data/processed/*.csv
        │
        ├── python/02_import_csv.py
        │       └── PostgreSQL database: vendor_performance, schema: vendor
        │
        ├── notebooks/01_eda_.ipynb
        ├── notebooks/02_vendor_analysis.ipynb
        │
        └── python/03_prepare_powerbi_report_data.py
                └── reports/powerbi_data/*.csv
                        └── python/04_create_powerbi_project.py
                                └── reports/Vendor_Performance_PowerBI.pbip
```
