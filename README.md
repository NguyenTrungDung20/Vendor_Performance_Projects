# Vendor Performance Projects

Dự án phân tích hiệu suất nhà cung cấp dựa trên dữ liệu tồn kho, mua hàng, giá mua, bán hàng và hóa đơn nhà cung cấp. Mục tiêu là xây dựng một pipeline từ CSV, PostgreSQL, EDA bằng notebook/Python đến bộ dữ liệu và báo cáo Power BI để đánh giá doanh thu, biên lợi nhuận, mức độ tập trung nhà cung cấp, hiệu quả mua theo quy mô đơn hàng và rủi ro tồn kho.

## Mục tiêu phân tích

- Xác định nhà cung cấp và thương hiệu đóng góp doanh thu/mua hàng lớn nhất.
- Phân tích mức độ tập trung mua hàng theo nhà cung cấp và tỷ trọng nhóm top vendor.
- Đánh giá biên lợi nhuận, gross profit, sales-to-purchase ratio và stock turnover.
- Phát hiện vendor có vòng quay tồn kho thấp và giá trị tồn kho chưa bán cao.
- Tìm nhóm brand có doanh số thấp nhưng biên lợi nhuận cao để làm ứng viên tối ưu pricing/marketing.
- Kiểm định thống kê sự khác biệt profit margin giữa nhóm high-sales và low-sales.

## Nguồn dữ liệu chính

Dữ liệu làm việc nằm trong `data/processed/` và được import sang schema PostgreSQL `vendor`.

| File | Số dòng | Mô tả |
| --- | ---: | --- |
| `begin_inventory.csv` | 206,529 | Tồn kho đầu kỳ theo store, brand, SKU. |
| `end_inventory.csv` | 224,489 | Tồn kho cuối kỳ theo store, brand, SKU. |
| `purchase_prices.csv` | 12,261 | Bảng giá mua, giá bán, brand và vendor. |
| `purchases.csv` | 2,372,474 | Giao dịch mua hàng, PO, ngày nhận hàng, số lượng và giá trị mua. |
| `sales.csv` | 12,825,363 | Giao dịch bán hàng, số lượng bán, doanh thu, thuế và vendor. |
| `vendor_invoice.csv` | 5,543 | Hóa đơn nhà cung cấp, freight, PO và approval. |

## Pipeline dự án

1. Chuẩn bị môi trường Python.

```powershell
.\Python(3.13.09).venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Cấu hình PostgreSQL trong `python/config.py`.

```python
import os

DB_CONFIG = {
    "host": os.getenv("VENDOR_DB_HOST", "127.0.0.1"),
    "port": int(os.getenv("VENDOR_DB_PORT", "5432")),
    "database": os.getenv("VENDOR_DB_NAME", "vendor_performance"),
    "user": os.getenv("VENDOR_DB_USER", "postgres"),
    "password": os.getenv("VENDOR_DB_PASSWORD", "")
}
```

Trên PowerShell, đặt mật khẩu database trước khi chạy import:

```powershell
$env:VENDOR_DB_PASSWORD = "your_postgres_password"
```

3. Tạo database/schema/tables.

```powershell
psql -U postgres -f sql\00_database_creation.sql
psql -U postgres -d vendor_performance -c "CREATE SCHEMA IF NOT EXISTS vendor;"
psql -U postgres -d vendor_performance -f sql\01_create_tables.sql
```

Nếu cần sinh lại DDL từ các CSV trong `data/processed/`, chạy:

```powershell
python python\01_generate_tables.py
```

4. Import CSV vào PostgreSQL.

```powershell
python python\test_connection.py
python python\02_import_csv.py --dry-run
python python\02_import_csv.py
```

Script `02_import_csv.py` có cơ chế kiểm tra header, ghi log vào `vendor.csv_import_log`, bỏ qua dòng trùng và hỗ trợ import một số file cụ thể:

```powershell
python python\02_import_csv.py --only sales
python python\02_import_csv.py --only purchases purchase_prices --force
```

5. Kiểm tra chất lượng dữ liệu và chuẩn bị database.

```powershell
psql -U postgres -d vendor_performance -f sql\03_data_profiling.sql
psql -U postgres -d vendor_performance -f sql\04_prepare_database.sql
```

`03_data_profiling.sql` là file read-only để kiểm tra row count, datatype, duplicate, missing value, candidate key và format ngày. `04_prepare_database.sql` chuyển các cột ngày từ text sang `DATE` và thêm primary key.

6. Phân tích EDA trong notebook.

- `notebooks/01_eda_.ipynb`: tổng quan dữ liệu, kiểm tra bảng và chuẩn bị logic tổng hợp.
- `notebooks/02_vendor_analysis.ipynb`: phân tích vendor/brand, margin, turnover, correlation và thống kê.

7. Sinh dữ liệu cho Power BI.

```powershell
python python\03_prepare_powerbi_report_data.py
```

Kết quả được ghi vào `reports/powerbi_data/`, gồm `vendor_sales_summary_clean.csv`, `kpi_summary.csv`, top vendor/brand, purchase contribution, target brand candidates, confidence interval, t-test và các bảng phụ cho dashboard.

8. Sinh hoặc cập nhật Power BI Project.

```powershell
python python\04_create_powerbi_project.py
```

Mở file `reports/Vendor_Performance_PowerBI.pbip` bằng Power BI Desktop. Dự án đang lưu theo dạng Power BI Project, gồm semantic model TMDL và report definition tách file. Sau khi mở trong Power BI Desktop, có thể refresh và Save As thành `.pbix` nếu cần.

## Báo cáo Power BI

Các trang báo cáo hiện có:

| Trang | Nội dung chính |
| --- | --- |
| Executive Overview | KPI tổng quan, top 10 vendors by sales, top 10 brands by sales. |
| Vendor Analysis | Sales, purchase, sales/purchase ratio, purchase contribution và vendor share. |
| Brand Pricing | Target brand count, unit purchase price, brand profit margin, bulk purchase impact. |
| Inventory & Statistics | Stock turnover, unsold inventory, confidence intervals và Welch t-test. |

Tài liệu hướng dẫn riêng cho Power BI nằm tại `reports/Vendor_Performance_PowerBI_Guide.md`.

## Output quan trọng

- `reports/powerbi_data/`: 15 bảng CSV đã curate cho dashboard.
- `reports/powerbi_images/`: 11 biểu đồ PNG export từ notebook.
- `reports/Reports_pdf/`: báo cáo markdown tĩnh và ảnh minh họa.
- `reports/PowerBI_Measures.dax`: nhóm DAX measure lõi.
- `reports/Vendor_Performance_Theme.json`: theme Power BI.
- `reports/Vendor_Performance_PowerBI_Project.zip`: gói nén Power BI Project.
- `outputs/`: log import PostgreSQL và file PID của các lần import đã chạy.

## Lưu ý vận hành

- `sales.csv` hơn 12.8 triệu dòng, nên các bước import và aggregate có thể mất thời gian.
- `03_prepare_powerbi_report_data.py` đọc `sales.csv` theo chunk để giảm áp lực bộ nhớ.
- `README.md` và `Cau_truc_thu_muc.md` mô tả hiện trạng dự án; thư mục virtual environment `Python(3.13.09).venv/` và `__pycache__/` không phải source code chính.
- Các CSV lớn trong `data/raw/`, `data/processed/` và `data/backup/` không nên push trực tiếp lên GitHub. Xem thêm `data/README.md`.
