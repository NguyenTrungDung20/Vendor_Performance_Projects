# Data Folder

Các file CSV nguồn của dự án nằm trong `raw/`, `processed/` và `backup/`, nhưng không được đưa lên GitHub vì có file rất lớn, đặc biệt `sales.csv` hơn 1.5GB.

Khi clone repo về máy mới, hãy đặt lại 6 file CSV sau vào `data/processed/` để chạy pipeline:

- `begin_inventory.csv`
- `end_inventory.csv`
- `purchase_prices.csv`
- `purchases.csv`
- `sales.csv`
- `vendor_invoice.csv`

Các bảng đã tổng hợp nhỏ hơn để dùng trực tiếp cho Power BI được lưu trong `reports/powerbi_data/`.
