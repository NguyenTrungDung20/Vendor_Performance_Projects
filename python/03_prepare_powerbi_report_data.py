from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"
POWERBI_DATA_DIR = REPORTS_DIR / "powerbi_data"


def ensure_output_dir() -> None:
    POWERBI_DATA_DIR.mkdir(parents=True, exist_ok=True)


def read_purchase_prices() -> pd.DataFrame:
    cols = [
        "Brand",
        "Description",
        "Price",
        "Volume",
        "PurchasePrice",
        "VendorNumber",
        "VendorName",
    ]
    df = pd.read_csv(DATA_DIR / "purchase_prices.csv", usecols=cols)
    df["VendorNumber"] = pd.to_numeric(df["VendorNumber"], errors="coerce").astype("Int64")
    df["Brand"] = pd.to_numeric(df["Brand"], errors="coerce").astype("Int64")
    df["ActualPrice"] = pd.to_numeric(df["Price"], errors="coerce")
    df["Volume"] = pd.to_numeric(df["Volume"], errors="coerce")
    return df.drop(columns=["Price"])


def aggregate_purchases() -> pd.DataFrame:
    cols = [
        "VendorNumber",
        "VendorName",
        "Brand",
        "Description",
        "PurchasePrice",
        "Quantity",
        "Dollars",
    ]
    purchases = pd.read_csv(DATA_DIR / "purchases.csv", usecols=cols)
    purchases["VendorNumber"] = pd.to_numeric(purchases["VendorNumber"], errors="coerce").astype("Int64")
    purchases["Brand"] = pd.to_numeric(purchases["Brand"], errors="coerce").astype("Int64")
    purchases["PurchasePrice"] = pd.to_numeric(purchases["PurchasePrice"], errors="coerce")
    purchases["Quantity"] = pd.to_numeric(purchases["Quantity"], errors="coerce")
    purchases["Dollars"] = pd.to_numeric(purchases["Dollars"], errors="coerce")
    purchases = purchases[purchases["PurchasePrice"] > 0]

    purchase_prices = read_purchase_prices()
    merged = purchases.merge(
        purchase_prices[["VendorNumber", "Brand", "ActualPrice", "Volume"]],
        on=["VendorNumber", "Brand"],
        how="inner",
    )

    summary = (
        merged.groupby(
            ["VendorNumber", "VendorName", "Brand", "Description", "PurchasePrice", "ActualPrice", "Volume"],
            dropna=False,
            as_index=False,
        )
        .agg(
            TotalPurchaseQuantity=("Quantity", "sum"),
            TotalPurchaseDollars=("Dollars", "sum"),
        )
        .sort_values("TotalPurchaseDollars", ascending=False)
    )
    return summary


def aggregate_sales(chunksize: int = 1_000_000) -> pd.DataFrame:
    cols = ["VendorNo", "Brand", "SalesQuantity", "SalesDollars", "SalesPrice", "ExciseTax"]
    grouped_chunks = []
    for chunk in pd.read_csv(DATA_DIR / "sales.csv", usecols=cols, chunksize=chunksize):
        chunk["VendorNo"] = pd.to_numeric(chunk["VendorNo"], errors="coerce").astype("Int64")
        chunk["Brand"] = pd.to_numeric(chunk["Brand"], errors="coerce").astype("Int64")
        for col in ["SalesQuantity", "SalesDollars", "SalesPrice", "ExciseTax"]:
            chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

        grouped_chunks.append(
            chunk.groupby(["VendorNo", "Brand"], dropna=False, as_index=False).agg(
                TotalSalesQuantity=("SalesQuantity", "sum"),
                TotalSalesDollars=("SalesDollars", "sum"),
                TotalSalesPrice=("SalesPrice", "sum"),
                TotalExciseTax=("ExciseTax", "sum"),
            )
        )

    sales = pd.concat(grouped_chunks, ignore_index=True)
    return sales.groupby(["VendorNo", "Brand"], dropna=False, as_index=False).sum()


def aggregate_freight() -> pd.DataFrame:
    invoice = pd.read_csv(DATA_DIR / "vendor_invoice.csv", usecols=["VendorNumber", "Freight"])
    invoice["VendorNumber"] = pd.to_numeric(invoice["VendorNumber"], errors="coerce").astype("Int64")
    invoice["Freight"] = pd.to_numeric(invoice["Freight"], errors="coerce")
    return invoice.groupby("VendorNumber", dropna=False, as_index=False).agg(FreightCost=("Freight", "sum"))


def format_rank(df: pd.DataFrame, value_col: str, rank_col: str = "Rank") -> pd.DataFrame:
    out = df.copy()
    out[rank_col] = range(1, len(out) + 1)
    cols = [rank_col] + [c for c in out.columns if c != rank_col]
    return out[cols]


def confidence_interval(values: pd.Series, confidence: float = 0.95) -> tuple[float, float, float, int]:
    clean = values.dropna()
    mean_val = clean.mean()
    std_err = clean.std(ddof=1) / np.sqrt(len(clean))
    t_critical = stats.t.ppf((1 + confidence) / 2, df=len(clean) - 1)
    margin = t_critical * std_err
    return mean_val, mean_val - margin, mean_val + margin, len(clean)


def build_report_tables(df: pd.DataFrame) -> None:
    clean = df[
        (df["GrossProfit"] > 0)
        & (df["ProfitMargin"] > 0)
        & (df["TotalSalesQuantity"] > 0)
    ].copy()

    clean["UnitPurchasePrice"] = clean["TotalPurchaseDollars"] / clean["TotalPurchaseQuantity"]
    clean["UnsoldInventoryValue"] = (
        clean["TotalPurchaseQuantity"] - clean["TotalSalesQuantity"]
    ) * clean["PurchasePrice"]
    clean["OrderSize"] = pd.qcut(
        clean["TotalPurchaseQuantity"],
        q=3,
        labels=["Small", "Medium", "Large"],
        duplicates="drop",
    )
    clean["PerformanceGroup"] = np.select(
        [
            clean["TotalSalesDollars"] >= clean["TotalSalesDollars"].quantile(0.75),
            clean["TotalSalesDollars"] <= clean["TotalSalesDollars"].quantile(0.25),
        ],
        ["High Sales", "Low Sales"],
        default="Mid Sales",
    )

    df.to_csv(POWERBI_DATA_DIR / "vendor_sales_summary.csv", index=False)
    clean.to_csv(POWERBI_DATA_DIR / "vendor_sales_summary_clean.csv", index=False)

    kpi = pd.DataFrame(
        [
            {
                "Metric": "Total Sales Dollars",
                "Value": clean["TotalSalesDollars"].sum(),
                "DisplayOrder": 1,
            },
            {
                "Metric": "Total Purchase Dollars",
                "Value": clean["TotalPurchaseDollars"].sum(),
                "DisplayOrder": 2,
            },
            {
                "Metric": "Gross Profit",
                "Value": clean["GrossProfit"].sum(),
                "DisplayOrder": 3,
            },
            {
                "Metric": "Average Profit Margin",
                "Value": clean["ProfitMargin"].mean(),
                "DisplayOrder": 4,
            },
            {
                "Metric": "Average Stock Turnover",
                "Value": clean["StockTurnover"].mean(),
                "DisplayOrder": 5,
            },
            {
                "Metric": "Unsold Inventory Value",
                "Value": clean["UnsoldInventoryValue"].sum(),
                "DisplayOrder": 6,
            },
        ]
    )
    kpi.to_csv(POWERBI_DATA_DIR / "kpi_summary.csv", index=False)

    top_vendors_sales = (
        clean.groupby("VendorName", as_index=False)["TotalSalesDollars"]
        .sum()
        .sort_values("TotalSalesDollars", ascending=False)
        .head(10)
    )
    format_rank(top_vendors_sales, "TotalSalesDollars").to_csv(
        POWERBI_DATA_DIR / "top_10_vendors_by_sales.csv", index=False
    )

    top_brands_sales = (
        clean.groupby("Description", as_index=False)["TotalSalesDollars"]
        .sum()
        .sort_values("TotalSalesDollars", ascending=False)
        .head(10)
    )
    format_rank(top_brands_sales, "TotalSalesDollars").to_csv(
        POWERBI_DATA_DIR / "top_10_brands_by_sales.csv", index=False
    )

    vendor_purchase = (
        clean.groupby("VendorName", as_index=False)
        .agg(
            TotalPurchaseDollars=("TotalPurchaseDollars", "sum"),
            GrossProfit=("GrossProfit", "sum"),
            TotalSalesDollars=("TotalSalesDollars", "sum"),
        )
        .sort_values("TotalPurchaseDollars", ascending=False)
    )
    vendor_purchase["PurchaseContributionPct"] = (
        vendor_purchase["TotalPurchaseDollars"] / vendor_purchase["TotalPurchaseDollars"].sum() * 100
    )
    vendor_purchase["CumulativeContributionPct"] = vendor_purchase["PurchaseContributionPct"].cumsum()
    format_rank(vendor_purchase, "TotalPurchaseDollars").to_csv(
        POWERBI_DATA_DIR / "vendor_purchase_contribution.csv", index=False
    )

    top10_purchase = vendor_purchase.head(10).copy()
    other_share = 100 - top10_purchase["PurchaseContributionPct"].sum()
    purchase_share = pd.concat(
        [
            top10_purchase[["VendorName", "PurchaseContributionPct"]],
            pd.DataFrame([{"VendorName": "Other Vendors", "PurchaseContributionPct": other_share}]),
        ],
        ignore_index=True,
    )
    purchase_share.to_csv(POWERBI_DATA_DIR / "vendor_purchase_share.csv", index=False)

    brand_performance = (
        clean.groupby("Description", as_index=False)
        .agg(TotalSalesDollars=("TotalSalesDollars", "sum"), ProfitMargin=("ProfitMargin", "mean"))
    )
    low_sales_threshold = brand_performance["TotalSalesDollars"].quantile(0.15)
    high_margin_threshold = brand_performance["ProfitMargin"].quantile(0.85)
    brand_performance["IsTargetBrand"] = (
        (brand_performance["TotalSalesDollars"] <= low_sales_threshold)
        & (brand_performance["ProfitMargin"] >= high_margin_threshold)
    )
    brand_performance["LowSalesThreshold"] = low_sales_threshold
    brand_performance["HighMarginThreshold"] = high_margin_threshold
    brand_performance.to_csv(POWERBI_DATA_DIR / "brand_margin_targets.csv", index=False)

    target_brand_candidates = (
        brand_performance[brand_performance["IsTargetBrand"]]
        .sort_values(["ProfitMargin", "TotalSalesDollars"], ascending=[False, True])
        .head(20)
        .copy()
    )
    target_brand_candidates.insert(0, "Rank", range(1, len(target_brand_candidates) + 1))
    target_brand_candidates.to_csv(POWERBI_DATA_DIR / "target_brand_candidates.csv", index=False)

    bulk = (
        clean.groupby("OrderSize", observed=False, as_index=False)
        .agg(
            AverageUnitPurchasePrice=("UnitPurchasePrice", "mean"),
            MedianUnitPurchasePrice=("UnitPurchasePrice", "median"),
            ItemCount=("Brand", "count"),
        )
    )
    bulk.to_csv(POWERBI_DATA_DIR / "bulk_purchase_analysis.csv", index=False)

    low_turnover = (
        clean[clean["StockTurnover"] < 1]
        .groupby("VendorName", as_index=False)["StockTurnover"]
        .mean()
        .sort_values("StockTurnover")
        .head(10)
    )
    format_rank(low_turnover, "StockTurnover").to_csv(
        POWERBI_DATA_DIR / "low_turnover_vendors.csv", index=False
    )

    inventory = (
        clean.groupby("VendorName", as_index=False)["UnsoldInventoryValue"]
        .sum()
        .sort_values("UnsoldInventoryValue", ascending=False)
        .head(10)
    )
    format_rank(inventory, "UnsoldInventoryValue").to_csv(
        POWERBI_DATA_DIR / "top_10_unsold_inventory_value.csv", index=False
    )

    numeric_cols = clean.select_dtypes(include=np.number).columns
    correlation = clean[numeric_cols].corr().reset_index().rename(columns={"index": "Metric"})
    correlation.to_csv(POWERBI_DATA_DIR / "correlation_matrix.csv", index=False)

    top_threshold = clean["TotalSalesDollars"].quantile(0.75)
    low_threshold = clean["TotalSalesDollars"].quantile(0.25)
    high_group = clean[clean["TotalSalesDollars"] >= top_threshold]["ProfitMargin"]
    low_group = clean[clean["TotalSalesDollars"] <= low_threshold]["ProfitMargin"]
    high_mean, high_lower, high_upper, high_n = confidence_interval(high_group)
    low_mean, low_lower, low_upper, low_n = confidence_interval(low_group)
    ci = pd.DataFrame(
        [
            {
                "PerformanceGroup": "High Sales",
                "MeanProfitMargin": high_mean,
                "Lower95": high_lower,
                "Upper95": high_upper,
                "N": high_n,
            },
            {
                "PerformanceGroup": "Low Sales",
                "MeanProfitMargin": low_mean,
                "Lower95": low_lower,
                "Upper95": low_upper,
                "N": low_n,
            },
        ]
    )
    ci.to_csv(POWERBI_DATA_DIR / "profit_margin_confidence_intervals.csv", index=False)

    t_stat, p_value = stats.ttest_ind(high_group.dropna(), low_group.dropna(), equal_var=False)
    pd.DataFrame(
        [
            {
                "Test": "Welch Two-Sample T-Test",
                "TStatistic": t_stat,
                "PValue": p_value,
                "Alpha": 0.05,
                "Conclusion": "Reject H0" if p_value < 0.05 else "Fail to reject H0",
            }
        ]
    ).to_csv(POWERBI_DATA_DIR / "profit_margin_t_test.csv", index=False)


def main() -> None:
    ensure_output_dir()
    purchases = aggregate_purchases()
    sales = aggregate_sales()
    freight = aggregate_freight()

    summary = purchases.merge(
        sales,
        left_on=["VendorNumber", "Brand"],
        right_on=["VendorNo", "Brand"],
        how="left",
    ).drop(columns=["VendorNo"])
    summary = summary.merge(freight, on="VendorNumber", how="left")

    numeric_cols = [
        "PurchasePrice",
        "ActualPrice",
        "Volume",
        "TotalPurchaseQuantity",
        "TotalPurchaseDollars",
        "TotalSalesQuantity",
        "TotalSalesDollars",
        "TotalSalesPrice",
        "TotalExciseTax",
        "FreightCost",
    ]
    summary[numeric_cols] = summary[numeric_cols].fillna(0)
    summary["VendorName"] = summary["VendorName"].fillna("").str.strip()
    summary["Description"] = summary["Description"].fillna("").str.strip()
    summary["GrossProfit"] = summary["TotalSalesDollars"] - summary["TotalPurchaseDollars"]
    summary["ProfitMargin"] = np.where(
        summary["TotalSalesDollars"] != 0,
        summary["GrossProfit"] / summary["TotalSalesDollars"] * 100,
        0,
    )
    summary["StockTurnover"] = np.where(
        summary["TotalPurchaseQuantity"] != 0,
        summary["TotalSalesQuantity"] / summary["TotalPurchaseQuantity"],
        0,
    )
    summary["SalesToPurchaseRatio"] = np.where(
        summary["TotalPurchaseDollars"] != 0,
        summary["TotalSalesDollars"] / summary["TotalPurchaseDollars"],
        0,
    )
    summary = summary.sort_values("TotalPurchaseDollars", ascending=False)
    build_report_tables(summary)


if __name__ == "__main__":
    main()
