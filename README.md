# Vendor Performance Analysis

Dự án này phân tích hiệu suất nhà cung cấp dựa trên dữ liệu mua hàng, bán hàng, giá sản phẩm, hóa đơn vận chuyển và tồn kho. Trọng tâm chính của dự án nằm ở **SQL + PostgreSQL** và hai notebook:

- `notebooks/01_eda_.ipynb`: khám phá dữ liệu gốc và xây dựng bảng tổng hợp `vendor.vendor_sales_summary`.
- `notebooks/02_vendor_analysis.ipynb`: phân tích hiệu suất vendor/brand, inventory, pricing, margin và kiểm định thống kê.

Power BI trong repo hiện được xem là phần trực quan hóa phụ/thử nghiệm, chưa phải deliverable hoàn thiện nhất của dự án.

## Dự án giải quyết bài toán gì?

Trong hoạt động bán lẻ/bán buôn, doanh nghiệp thường phải trả lời nhiều câu hỏi cùng lúc:

- Nhà cung cấp nào đang tạo ra doanh thu lớn nhất?
- Doanh nghiệp có đang phụ thuộc quá nhiều vào một nhóm vendor không?
- Sản phẩm nào bán chậm nhưng vẫn có biên lợi nhuận tốt để có thể đẩy marketing hoặc điều chỉnh giá?
- Mua số lượng lớn có thật sự giúp giảm đơn giá mua không?
- Bao nhiêu vốn đang bị kẹt trong hàng tồn kho chưa bán?
- Nhóm vendor doanh số cao và doanh số thấp có khác biệt đáng kể về biên lợi nhuận không?

Dự án biến các câu hỏi này thành một pipeline phân tích có thể chạy lại: nhập CSV vào PostgreSQL, kiểm tra chất lượng dữ liệu bằng SQL, tạo bảng phân tích tổng hợp, sau đó dùng notebook để EDA, trực quan hóa và kiểm định giả thuyết.

## Insight chính

| Bài toán | Phát hiện từ notebook | Hàm ý kinh doanh |
| --- | --- | --- |
| Hiệu suất doanh thu | Vendor doanh thu cao nhất là `DIAGEO NORTH AMERICA INC` với khoảng **67.99M USD**, tiếp theo là `MARTIGNETTI COMPANIES` với **39.33M USD** và `PERNOD RICARD USA` với **32.06M USD**. | Cần ưu tiên quản trị các vendor lớn vì họ ảnh hưởng trực tiếp đến doanh thu tổng. |
| Rủi ro tập trung nhà cung cấp | Top 10 vendor đóng góp khoảng **65.84%** tổng giá trị mua hàng. | Có rủi ro phụ thuộc vào một nhóm nhỏ nhà cung cấp; nên theo dõi rủi ro chuỗi cung ứng và đa dạng hóa nguồn cung nếu cần. |
| Brand doanh số thấp nhưng margin cao | Notebook tìm ra **198 brand** thuộc nhóm doanh số thấp nhưng biên lợi nhuận cao. | Đây là nhóm ứng viên cho khuyến mãi có chọn lọc, tối ưu giá hoặc tăng hỗ trợ bán hàng. |
| Hiệu quả mua số lượng lớn | Đơn giá mua trung bình theo nhóm đơn hàng: `Small` **39.13 USD**, `Medium` **15.49 USD**, `Large` **10.78 USD**. Nhóm `Large` thấp hơn nhóm `Small` khoảng **72%**. | Bulk purchasing có thể tạo lợi thế chi phí, nhưng cần đi kèm kiểm soát tồn kho để tránh giữ hàng quá lâu. |
| Vốn bị kẹt trong tồn kho | Tổng giá trị hàng chưa bán khoảng **2.69M USD**. Các vendor có giá trị tồn chưa bán cao nhất gồm `DIAGEO NORTH AMERICA INC` **722.21K USD**, `JIM BEAM BRANDS COMPANY` **554.67K USD**, `PERNOD RICARD USA` **470.63K USD**. | Cần rà soát kế hoạch mua, markdown, thanh lý hoặc phân phối lại tồn kho theo vendor. |
| Chênh lệch biên lợi nhuận | Nhóm doanh số cao có margin trung bình khoảng **31.17%** với CI 95% từ **30.73% đến 31.60%**. Nhóm doanh số thấp có margin trung bình khoảng **41.53%** với CI 95% từ **40.46% đến 42.60%**. Welch t-test cho kết quả `Reject H0`. | Hai nhóm có mô hình sinh lời khác nhau; nhóm doanh số cao cần tối ưu margin, nhóm doanh số thấp cần cải thiện demand/marketing/phân phối. |

## Dữ liệu sử dụng

Các file CSV lớn không được đưa lên GitHub. Khi chạy lại dự án, cần đặt 6 file sau vào `data/processed/`.

| File | Số dòng trong notebook | Vai trò |
| --- | ---: | --- |
| `begin_inventory.csv` | 206,529 | Tồn kho đầu kỳ theo store, brand, SKU. |
| `end_inventory.csv` | 224,489 | Tồn kho cuối kỳ theo store, brand, SKU. |
| `purchase_prices.csv` | 12,261 | Giá mua, giá bán, brand, vendor và thông tin sản phẩm. |
| `purchases.csv` | 2,372,474 | Giao dịch mua hàng, PO, ngày nhận hàng, số lượng và giá trị mua. |
| `sales.csv` | 12,825,363 | Giao dịch bán hàng, số lượng bán, doanh thu, giá bán, thuế và vendor. |
| `vendor_invoice.csv` | 5,543 | Hóa đơn vendor, chi phí vận chuyển, PO và approval. |

## Luồng xử lý chính

```text
data/processed/*.csv
        |
        v
PostgreSQL database: vendor_performance
        |
        v
SQL profiling + date/key preparation
        |
        v
notebooks/01_eda_.ipynb
        |
        v
vendor.vendor_sales_summary
        |
        v
notebooks/02_vendor_analysis.ipynb
        |
        v
business insights, charts, confidence intervals, Welch t-test
```

## Vai trò của SQL

Thư mục `sql/` chuẩn bị database để notebook có thể phân tích ổn định.

| File | Vai trò |
| --- | --- |
| `00_database_creation.sql` | Tạo lại database `vendor_performance`. |
| `01_create_tables.sql` | Tạo 6 bảng nguồn trong schema `vendor`: inventory, purchases, purchase prices, sales, vendor invoice. |
| `02_import_data.sql` | Đang để trống; import thực tế được xử lý bằng script Python `python/02_import_csv.py`. |
| `03_data_profiling.sql` | Read-only profiling: kiểm tra row count, data type, duplicate, missing value, candidate keys và định dạng ngày. |
| `04_prepare_database.sql` | Chuyển các cột ngày từ text sang `DATE` và thêm primary key cho các bảng nguồn. |
| `check_file.sql` | Các truy vấn kiểm tra nhanh bảng, log import, kiểu ngày và khoảng ngày sau khi chuẩn bị dữ liệu. |

Các khóa chính được thêm trong `04_prepare_database.sql`:

- `begin_inventory`: `InventoryId`
- `end_inventory`: `InventoryId`
- `purchase_prices`: `Brand`
- `purchases`: `InventoryId`, `PONumber`, `ReceivingDate`
- `sales`: `InventoryId`, `SalesDate`
- `vendor_invoice`: `PONumber`

## Notebook 01: EDA và tạo bảng tổng hợp

`notebooks/01_eda_.ipynb` là notebook nền tảng của dự án. Notebook này:

- Kết nối PostgreSQL bằng SQLAlchemy.
- Kiểm tra schema `vendor` và xác nhận các bảng đã import.
- Xem nhanh số dòng và sample của từng bảng nguồn.
- Chọn một vendor cụ thể (`VendorNumber = 4466`) để hiểu quan hệ giữa `purchases`, `purchase_prices`, `vendor_invoice` và `sales`.
- Tạo các bảng tổng hợp trung gian:
  - `FreightSummary`: tổng chi phí vận chuyển theo vendor.
  - `PurchaseSummary`: tổng số lượng và giá trị mua theo vendor-brand.
  - `SalesSummary`: tổng số lượng bán, doanh thu, giá bán và thuế theo vendor-brand.
- Join các bảng tổng hợp để tạo dataset phân tích chính.
- Làm sạch dữ liệu: chuyển `Volume` sang numeric, fill missing sales bằng 0, strip khoảng trắng trong cột phân loại.
- Tạo các chỉ số phân tích:

```text
GrossProfit = TotalSalesDollars - TotalPurchaseDollars
ProfitMargin = GrossProfit / TotalSalesDollars * 100
StockTurnover = TotalSalesQuantity / TotalPurchaseQuantity
SalesToPurchaseRatio = TotalSalesDollars / TotalPurchaseDollars
```

Kết quả quan trọng nhất của notebook này là bảng:

```text
vendor.vendor_sales_summary
```

Bảng này có **10,648 dòng** ở cấp độ vendor-brand và là input chính cho notebook phân tích tiếp theo.

## Notebook 02: Phân tích vendor performance

`notebooks/02_vendor_analysis.ipynb` dùng bảng `vendor.vendor_sales_summary` để trả lời các câu hỏi kinh doanh.

Notebook load dữ liệu với shape ban đầu:

```text
(10648, 18)
```

Sau bước EDA ban đầu, notebook lọc dataset để tập trung vào các dòng phân tích có ý nghĩa kinh doanh:

```sql
WHERE "GrossProfit" > 0
  AND "ProfitMargin" > 0
  AND "TotalSalesQuantity" > 0
```

Sau lọc còn:

```text
(8541, 18)
```

Các phần phân tích chính gồm:

- Thống kê mô tả và phân phối các biến numeric.
- Nhận diện outlier bằng boxplot.
- Correlation heatmap giữa giá mua, doanh thu, lợi nhuận, turnover và các chỉ số mua/bán.
- Tìm brand doanh số thấp nhưng margin cao bằng ngưỡng bottom 15% sales và top 15% margin.
- Xếp hạng top vendor và top brand theo doanh thu.
- Phân tích Pareto mức đóng góp mua hàng của vendor.
- So sánh đơn giá mua theo quy mô đơn hàng bằng `pd.qcut`.
- Xác định vendor có `StockTurnover < 1`.
- Tính giá trị vốn bị kẹt trong hàng tồn chưa bán.
- Tính confidence interval 95% cho margin của nhóm doanh số cao và doanh số thấp.
- Kiểm định Welch two-sample t-test cho biên lợi nhuận giữa hai nhóm.

## Công thức và logic phân tích

| Chỉ số | Công thức | Ý nghĩa |
| --- | --- | --- |
| `GrossProfit` | `TotalSalesDollars - TotalPurchaseDollars` | Lợi nhuận gộp ở cấp vendor-brand. |
| `ProfitMargin` | `GrossProfit / TotalSalesDollars * 100` | Biên lợi nhuận gộp theo phần trăm doanh thu. |
| `StockTurnover` | `TotalSalesQuantity / TotalPurchaseQuantity` | Tốc độ bán ra so với lượng mua vào. |
| `SalesToPurchaseRatio` | `TotalSalesDollars / TotalPurchaseDollars` | Mức doanh thu tạo ra trên mỗi USD mua hàng. |
| `UnitPurchasePrice` | `TotalPurchaseDollars / TotalPurchaseQuantity` | Đơn giá mua trung bình. |
| `UnsoldInventoryValue` | `(TotalPurchaseQuantity - TotalSalesQuantity) * PurchasePrice` | Giá trị vốn còn nằm trong hàng chưa bán. |

## Cách chạy lại dự án

### 1. Chuẩn bị môi trường Python

```powershell
pip install -r requirements.txt
```

Các thư viện chính:

- `pandas`
- `numpy`
- `scipy`
- `psycopg2-binary`
- `jupyter`

### 2. Chuẩn bị dữ liệu

Đặt 6 file CSV nguồn vào:

```text
data/processed/
```

Xem thêm `data/README.md` để biết lý do các file CSV lớn không được push lên GitHub.

### 3. Tạo database và bảng nguồn

```powershell
psql -U postgres -f sql\00_database_creation.sql
psql -U postgres -d vendor_performance -c "CREATE SCHEMA IF NOT EXISTS vendor;"
psql -U postgres -d vendor_performance -f sql\01_create_tables.sql
```

### 4. Import CSV vào PostgreSQL

```powershell
$env:VENDOR_DB_PASSWORD = "your_postgres_password"
python python\test_connection.py
python python\02_import_csv.py --dry-run
python python\02_import_csv.py
```

Có thể import một số file cụ thể:

```powershell
python python\02_import_csv.py --only sales
python python\02_import_csv.py --only purchases purchase_prices --force
```

### 5. Profiling và chuẩn bị database

```powershell
psql -U postgres -d vendor_performance -f sql\03_data_profiling.sql
psql -U postgres -d vendor_performance -f sql\04_prepare_database.sql
```

### 6. Chạy notebook theo thứ tự

```powershell
jupyter notebook notebooks\01_eda_.ipynb
jupyter notebook notebooks\02_vendor_analysis.ipynb
```

Hai notebook sẽ hỏi mật khẩu PostgreSQL qua `getpass`.

## Cấu trúc repo

```text
Vendor_Performance_Projects/
|-- data/
|   |-- README.md
|   |-- processed/              # CSV nguồn, không push lên GitHub
|-- notebooks/
|   |-- 01_eda_.ipynb           # tạo bảng vendor_sales_summary
|   |-- 02_vendor_analysis.ipynb # phân tích chính
|-- python/
|   |-- 01_generate_tables.py
|   |-- 02_import_csv.py
|   |-- 03_prepare_powerbi_report_data.py
|   |-- 04_create_powerbi_project.py
|   |-- config.py
|   |-- test_connection.py
|-- sql/
|   |-- 00_database_creation.sql
|   |-- 01_create_tables.sql
|   |-- 02_import_data.sql
|   |-- 03_data_profiling.sql
|   |-- 04_prepare_database.sql
|   |-- check_file.sql
|-- reports/
|   |-- Reports_pdf/            # báo cáo markdown/export tĩnh từ phân tích
|   |-- powerbi_data/           # dữ liệu curate phụ cho thử nghiệm Power BI
|   |-- powerbi_images/         # ảnh biểu đồ xuất từ notebook
|-- requirements.txt
|-- README.md
```

## Ghi chú về Power BI

Repo có chứa một số artifact Power BI trong `reports/`, bao gồm `.pbip`, semantic model, theme và các file CSV đã curate. Tuy nhiên, phần này chưa được xem là phần hoàn thiện nhất của dự án.

Nếu đánh giá năng lực phân tích của dự án, nên đọc theo thứ tự:

1. `sql/03_data_profiling.sql`
2. `sql/04_prepare_database.sql`
3. `notebooks/01_eda_.ipynb`
4. `notebooks/02_vendor_analysis.ipynb`
5. `reports/Reports_pdf/Vendor_Performance_Report.md`

## Giới hạn và giả định

- Dữ liệu nguồn lớn nên không được commit lên GitHub. Người chạy lại dự án cần tự đặt các file CSV vào `data/processed/`.
- Phân tích chính được thực hiện ở cấp vendor-brand, không phải từng giao dịch đơn lẻ.
- Các kết luận chính trong `02_vendor_analysis.ipynb` dựa trên dataset đã lọc `GrossProfit > 0`, `ProfitMargin > 0`, `TotalSalesQuantity > 0`.
- Correlation không chứng minh quan hệ nhân quả.
- Welch t-test xác nhận sự khác biệt thống kê về margin giữa hai nhóm doanh số, nhưng quyết định kinh doanh vẫn cần thêm bối cảnh về thị trường, sản phẩm, mùa vụ và năng lực vận hành.

