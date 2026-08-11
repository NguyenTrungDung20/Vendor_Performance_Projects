import json
import shutil
import uuid
import csv
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORTS_DIR = PROJECT_ROOT / "reports"
DATA_DIR = REPORTS_DIR / "powerbi_data"
PROJECT_NAME = "Vendor_Performance_PowerBI"
SCHEMA_BASE = "https://developer.microsoft.com/json-schemas/fabric/item/report/definition"
CANVAS_W = 1280
CANVAS_H = 720

INK = "#222222"
MUTED = "#666666"
SURFACE = "#F5F7FA"
CARD_BORDER = "#D9E2EC"
BLUE = "#1B4D89"
GREEN = "#2E8B57"
ORANGE = "#D95F02"
TEAL = "#00A6A6"
PURPLE = "#6C5B7B"
RED = "#B23A48"


TABLES = {
    "Vendor Sales Summary": {
        "file": "vendor_sales_summary_clean.csv",
        "columns": {
            "VendorNumber": "int64",
            "VendorName": "string",
            "Brand": "int64",
            "Description": "string",
            "PurchasePrice": "double",
            "ActualPrice": "double",
            "Volume": "double",
            "TotalPurchaseQuantity": "double",
            "TotalPurchaseDollars": "double",
            "TotalSalesQuantity": "double",
            "TotalSalesDollars": "double",
            "TotalSalesPrice": "double",
            "TotalExciseTax": "double",
            "FreightCost": "double",
            "GrossProfit": "double",
            "ProfitMargin": "double",
            "StockTurnover": "double",
            "SalesToPurchaseRatio": "double",
            "UnitPurchasePrice": "double",
            "UnsoldInventoryValue": "double",
            "OrderSize": "string",
            "PerformanceGroup": "string",
        },
    },
    "KPI Summary": {
        "file": "kpi_summary.csv",
        "columns": {"Metric": "string", "Value": "double", "DisplayOrder": "int64"},
    },
    "Top 10 Vendors By Sales": {
        "file": "top_10_vendors_by_sales.csv",
        "columns": {"Rank": "int64", "VendorName": "string", "TotalSalesDollars": "double"},
    },
    "Top 10 Brands By Sales": {
        "file": "top_10_brands_by_sales.csv",
        "columns": {"Rank": "int64", "Description": "string", "TotalSalesDollars": "double"},
    },
    "Vendor Purchase Contribution": {
        "file": "vendor_purchase_contribution.csv",
        "columns": {
            "Rank": "int64",
            "VendorName": "string",
            "TotalPurchaseDollars": "double",
            "GrossProfit": "double",
            "TotalSalesDollars": "double",
            "PurchaseContributionPct": "double",
            "CumulativeContributionPct": "double",
        },
    },
    "Vendor Purchase Share": {
        "file": "vendor_purchase_share.csv",
        "columns": {"VendorName": "string", "PurchaseContributionPct": "double"},
    },
    "Brand Margin Targets": {
        "file": "brand_margin_targets.csv",
        "columns": {
            "Description": "string",
            "TotalSalesDollars": "double",
            "ProfitMargin": "double",
            "IsTargetBrand": "boolean",
            "LowSalesThreshold": "double",
            "HighMarginThreshold": "double",
        },
    },
    "Target Brand Candidates": {
        "file": "target_brand_candidates.csv",
        "columns": {
            "Rank": "int64",
            "Description": "string",
            "TotalSalesDollars": "double",
            "ProfitMargin": "double",
            "IsTargetBrand": "boolean",
            "LowSalesThreshold": "double",
            "HighMarginThreshold": "double",
        },
    },
    "Bulk Purchase Analysis": {
        "file": "bulk_purchase_analysis.csv",
        "columns": {
            "OrderSize": "string",
            "AverageUnitPurchasePrice": "double",
            "MedianUnitPurchasePrice": "double",
            "ItemCount": "int64",
        },
    },
    "Low Turnover Vendors": {
        "file": "low_turnover_vendors.csv",
        "columns": {"Rank": "int64", "VendorName": "string", "StockTurnover": "double"},
    },
    "Top 10 Unsold Inventory Value": {
        "file": "top_10_unsold_inventory_value.csv",
        "columns": {"Rank": "int64", "VendorName": "string", "UnsoldInventoryValue": "double"},
    },
    "Correlation Matrix": {
        "file": "correlation_matrix.csv",
        "columns": {
            "Metric": "string",
            "VendorNumber": "double",
            "Brand": "double",
            "PurchasePrice": "double",
            "ActualPrice": "double",
            "Volume": "double",
            "TotalPurchaseQuantity": "double",
            "TotalPurchaseDollars": "double",
            "TotalSalesQuantity": "double",
            "TotalSalesDollars": "double",
            "TotalSalesPrice": "double",
            "TotalExciseTax": "double",
            "FreightCost": "double",
            "GrossProfit": "double",
            "ProfitMargin": "double",
            "StockTurnover": "double",
            "SalesToPurchaseRatio": "double",
            "UnitPurchasePrice": "double",
            "UnsoldInventoryValue": "double",
        },
    },
}


DAX_MEASURES = {
    "Total Sales": 'SUM(\'Vendor Sales Summary\'[TotalSalesDollars])',
    "Total Purchases": 'SUM(\'Vendor Sales Summary\'[TotalPurchaseDollars])',
    "Gross Profit": 'SUM(\'Vendor Sales Summary\'[GrossProfit])',
    "Profit Margin %": 'DIVIDE([Gross Profit], [Total Sales]) * 100',
    "Stock Turnover": 'DIVIDE(SUM(\'Vendor Sales Summary\'[TotalSalesQuantity]), SUM(\'Vendor Sales Summary\'[TotalPurchaseQuantity]))',
    "Unsold Inventory Value": 'SUM(\'Vendor Sales Summary\'[UnsoldInventoryValue])',
    "Sales To Purchase Ratio": 'DIVIDE([Total Sales], [Total Purchases])',
    "Average Unit Purchase Price": 'AVERAGE(\'Vendor Sales Summary\'[UnitPurchasePrice])',
    "Target Brand Count": 'CALCULATE(COUNTROWS(\'Brand Margin Targets\'), \'Brand Margin Targets\'[IsTargetBrand] = TRUE())',
    "Top Vendor Sales": 'SUM(\'Top 10 Vendors By Sales\'[TotalSalesDollars])',
    "Top Brand Sales": 'SUM(\'Top 10 Brands By Sales\'[TotalSalesDollars])',
    "Vendor Purchase Contribution %": 'SUM(\'Vendor Purchase Contribution\'[PurchaseContributionPct])',
    "Vendor Purchase Share %": 'SUM(\'Vendor Purchase Share\'[PurchaseContributionPct])',
    "Brand Profit Margin": 'AVERAGE(\'Brand Margin Targets\'[ProfitMargin])',
    "Target Candidate Margin": 'AVERAGE(\'Target Brand Candidates\'[ProfitMargin])',
    "Target Candidate Sales": 'SUM(\'Target Brand Candidates\'[TotalSalesDollars])',
    "Bulk Average Unit Price": 'AVERAGE(\'Bulk Purchase Analysis\'[AverageUnitPurchasePrice])',
    "Low Turnover Avg": 'AVERAGE(\'Low Turnover Vendors\'[StockTurnover])',
    "Top Unsold Inventory": 'SUM(\'Top 10 Unsold Inventory Value\'[UnsoldInventoryValue])',
}


def literal(value):
    if isinstance(value, bool):
        raw = "true" if value else "false"
    elif isinstance(value, (int, float)):
        raw = f"{value}D"
    else:
        raw = "'" + str(value).replace("'", "''") + "'"
    return {"expr": {"Literal": {"Value": raw}}}


def solid(hex_color: str) -> dict:
    return {"solid": {"color": literal(hex_color)}}


def col(entity: str, prop: str) -> dict:
    return {"Column": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def meas(entity: str, prop: str) -> dict:
    return {"Measure": {"Expression": {"SourceRef": {"Entity": entity}}, "Property": prop}}


def projection(field: dict, entity: str, prop: str, active: bool = False) -> dict:
    item = {"field": field, "queryRef": f"{entity}.{prop}", "nativeQueryRef": prop}
    if active:
        item["active"] = True
    return item


def transparent_container() -> dict:
    return {
        "background": [{"properties": {"show": literal(False)}}],
        "border": [{"properties": {"show": literal(False)}}],
        "title": [{"properties": {"show": literal(False)}}],
    }


def card_container(title: str | None = None) -> dict:
    container = {
        "background": [
            {"properties": {"show": literal(True), "color": solid("#FFFFFF"), "transparency": literal(0)}}
        ],
        "border": [
            {
                "properties": {
                    "show": literal(True),
                    "color": solid(CARD_BORDER),
                    "radius": literal(8),
                }
            }
        ],
        "dropShadow": [
            {
                "properties": {
                    "show": literal(True),
                    "preset": literal("BottomRight"),
                    "position": literal("Outer"),
                    "color": solid("#9AA6B2"),
                    "transparency": literal(88),
                }
            }
        ],
    }
    if title:
        container["title"] = [
            {
                "properties": {
                    "show": literal(True),
                    "text": literal(title),
                    "fontColor": solid(INK),
                    "fontSize": literal(13),
                    "fontFamily": literal("Segoe UI Semibold"),
                    "alignment": literal("left"),
                }
            }
        ]
    else:
        container["title"] = [{"properties": {"show": literal(False)}}]
    return container


def visual_container(name: str, x: int, y: int, z: int, width: int, height: int, visual: dict) -> dict:
    return {
        "$schema": f"{SCHEMA_BASE}/visualContainer/1.0.0/schema.json",
        "name": name,
        "position": {"x": x, "y": y, "z": z, "width": width, "height": height},
        "visual": visual,
    }


def textbox(name: str, x: int, y: int, z: int, width: int, height: int, text: str, size: int = 16, color: str = INK) -> dict:
    visual = {
        "visualType": "textbox",
        "drillFilterOtherVisuals": True,
        "objects": {
            "general": [
                {
                    "properties": {
                        "paragraphs": [
                            {
                                "textRuns": [
                                    {
                                        "value": text,
                                        "textStyle": {
                                            "fontFamily": "Segoe UI",
                                            "fontWeight": "bold" if size >= 18 else "normal",
                                            "fontSize": f"{size}pt",
                                            "color": color,
                                        },
                                    }
                                ],
                                "horizontalTextAlignment": "left",
                            }
                        ]
                    }
                }
            ]
        },
        "visualContainerObjects": transparent_container(),
    }
    return visual_container(name, x, y, z, width, height, visual)


def shape(name: str, x: int, y: int, z: int, width: int, height: int, fill: str, radius: int = 6) -> dict:
    visual = {
        "visualType": "shape",
        "drillFilterOtherVisuals": True,
        "objects": {
            "shape": [
                {
                    "properties": {
                        "tileShape": literal("rectangleRounded"),
                        "rectangleRoundedCurve": literal(radius),
                    },
                    "selector": {"id": "default"},
                }
            ],
            "fill": [
                {"properties": {"show": literal(True)}},
                {
                    "properties": {"fillColor": solid(fill), "transparency": literal(0)},
                    "selector": {"id": "default"},
                },
            ],
            "outline": [{"properties": {"show": literal(False)}}],
        },
        "visualContainerObjects": transparent_container(),
    }
    return visual_container(name, x, y, z, width, height, visual)


def kpi_card(name: str, x: int, y: int, z: int, title: str, measure_name: str, accent: str) -> list[dict]:
    return [
        shape(f"{name}_bg", x, y, z, 285, 116, "#FFFFFF", 7),
        textbox(f"{name}_title", x + 16, y + 12, z + 1, 240, 24, title, 10, MUTED),
        visual_container(
            name,
            x + 8,
            y + 38,
            z + 2,
            265,
            64,
            {
                "visualType": "card",
                "drillFilterOtherVisuals": True,
                "query": {
                    "queryState": {
                        "Values": {
                            "projections": [
                                projection(meas("Report Measures", measure_name), "Report Measures", measure_name)
                            ]
                        }
                    }
                },
                "objects": {
                    "labels": [
                        {
                            "properties": {
                                "fontSize": literal(21),
                                "color": solid(accent),
                                "fontFamily": literal("Segoe UI Semibold"),
                                "labelDisplayUnits": literal(0),
                                "labelPrecision": literal(1),
                            }
                        }
                    ],
                    "categoryLabels": [{"properties": {"show": literal(False)}}],
                },
                "visualContainerObjects": transparent_container(),
            },
        ),
    ]


def bar_chart(
    name: str,
    x: int,
    y: int,
    z: int,
    width: int,
    height: int,
    table: str,
    category: str,
    value_measure: str,
    title: str,
    accent: str,
    horizontal: bool = True,
) -> dict:
    value_field = meas("Report Measures", value_measure)
    visual = {
        "visualType": "barChart" if horizontal else "columnChart",
        "drillFilterOtherVisuals": True,
        "query": {
            "queryState": {
                "Category": {"projections": [projection(col(table, category), table, category, active=True)]},
                "Y": {"projections": [projection(value_field, "Report Measures", value_measure)]},
            },
            "sortDefinition": {
                "sort": [{"field": value_field, "direction": "Descending"}],
                "isDefaultSort": True,
            },
        },
        "objects": {
            "legend": [{"properties": {"show": literal(False)}}],
            "categoryAxis": [
                {
                    "properties": {
                        "show": literal(True),
                        "fontSize": literal(9),
                        "labelColor": solid(MUTED),
                        "showAxisTitle": literal(False),
                    }
                }
            ],
            "valueAxis": [{"properties": {"show": literal(False), "showAxisTitle": literal(False)}}],
            "dataPoint": [{"properties": {"fill": solid(accent)}}],
            "labels": [
                {
                    "properties": {
                        "show": literal(True),
                        "labelPosition": literal("OutsideEnd"),
                        "color": solid(MUTED),
                        "fontSize": literal(9),
                        "labelDisplayUnits": literal(0),
                        "labelPrecision": literal(1),
                    }
                }
            ],
        },
        "visualContainerObjects": card_container(title),
    }
    return visual_container(name, x, y, z, width, height, visual)


def donut_chart(name: str, x: int, y: int, z: int, width: int, height: int, table: str, category: str, value: str, title: str) -> dict:
    visual = {
        "visualType": "donutChart",
        "drillFilterOtherVisuals": True,
        "query": {
            "queryState": {
                "Category": {"projections": [projection(col(table, category), table, category, active=True)]},
                "Y": {"projections": [projection(meas("Report Measures", value), "Report Measures", value)]},
            }
        },
        "objects": {
            "legend": [
                {
                    "properties": {
                        "show": literal(True),
                        "position": literal("RightCenter"),
                        "showTitle": literal(False),
                        "fontSize": literal(9),
                        "labelColor": solid(MUTED),
                    }
                }
            ],
            "labels": [
                {
                    "properties": {
                        "show": literal(True),
                        "labelStyle": literal("Percent of total"),
                        "labelPrecision": literal(1),
                        "fontSize": literal(9),
                        "color": solid(MUTED),
                    }
                }
            ],
        },
        "visualContainerObjects": card_container(title),
    }
    return visual_container(name, x, y, z, width, height, visual)


def table_visual(name: str, x: int, y: int, z: int, width: int, height: int, table: str, fields: list[str], title: str) -> dict:
    visual = {
        "visualType": "tableEx",
        "drillFilterOtherVisuals": True,
        "query": {
            "queryState": {
                "Values": {
                    "projections": [projection(col(table, field), table, field, active=(idx == 0)) for idx, field in enumerate(fields)]
                }
            }
        },
        "objects": {
            "grid": [{"properties": {"outlineColor": solid("#E6EAF0"), "textSize": literal(9)}}],
            "columnHeaders": [{"properties": {"fontColor": solid(INK), "backColor": solid("#EEF3F8"), "textSize": literal(9)}}],
            "values": [{"properties": {"fontColor": solid(MUTED), "textSize": literal(9)}}],
        },
        "visualContainerObjects": card_container(title),
    }
    return visual_container(name, x, y, z, width, height, visual)


def write_visuals(report_dir: Path, page_id: str, visuals: list[dict]) -> None:
    for visual in visuals:
        write_json(
            report_dir / "definition" / "pages" / page_id / "visuals" / visual["name"] / "visual.json",
            visual,
        )


def read_t_test_result() -> dict[str, str]:
    path = DATA_DIR / "profit_margin_t_test.csv"
    if not path.exists():
        return {
            "Test": "Welch Two-Sample T-Test",
            "TStatistic": "N/A",
            "PValue": "N/A",
            "Alpha": "0.05",
            "Conclusion": "N/A",
        }
    with path.open(newline="", encoding="utf-8") as handle:
        return next(csv.DictReader(handle))


def read_ci_results() -> list[dict[str, str]]:
    path = DATA_DIR / "profit_margin_confidence_intervals.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def ci_panel(name: str, x: int, y: int, z: int, width: int, height: int) -> list[dict]:
    rows = read_ci_results()
    if not rows:
        return [
            shape(f"{name}_bg", x, y, z, width, height, "#FFFFFF", 8),
            textbox(f"{name}_title", x + 16, y + 10, z + 1, width - 32, 30, "Mean Profit Margin by Sales Group", 14, INK),
            textbox(f"{name}_missing", x + 20, y + 80, z + 2, width - 40, 40, "Confidence interval data is unavailable.", 12, MUTED),
        ]

    rows = sorted(rows, key=lambda item: item["PerformanceGroup"])
    max_mean = max(float(item["MeanProfitMargin"]) for item in rows)
    visuals = [
        shape(f"{name}_bg", x, y, z, width, height, "#FFFFFF", 8),
        textbox(f"{name}_title", x + 16, y + 10, z + 1, width - 32, 30, "Mean Profit Margin by Sales Group", 14, INK),
    ]
    bar_x = x + 185
    bar_max_w = width - 260
    for idx, row in enumerate(rows):
        y0 = y + 62 + idx * 68
        group = row["PerformanceGroup"]
        mean = float(row["MeanProfitMargin"])
        lower = float(row["Lower95"])
        upper = float(row["Upper95"])
        n_value = int(float(row["N"]))
        bar_w = int((mean / max_mean) * bar_max_w)
        color = PURPLE if group == "High Sales" else BLUE
        visuals.append(textbox(f"{name}_{idx}_label", x + 24, y0 + 4, z + 2 + idx * 10, 140, 24, group, 11, MUTED))
        visuals.append(shape(f"{name}_{idx}_bar", bar_x, y0, z + 3 + idx * 10, bar_w, 28, color, 3))
        visuals.append(textbox(f"{name}_{idx}_mean", bar_x + bar_w + 12, y0 - 2, z + 4 + idx * 10, 90, 28, f"{mean:.1f}%", 12, INK))
        visuals.append(textbox(f"{name}_{idx}_ci", x + 24, y0 + 32, z + 5 + idx * 10, width - 48, 22, f"95% CI: {lower:.1f}% to {upper:.1f}%  |  n={n_value:,}", 9, MUTED))
    return visuals


def t_test_panel(name: str, x: int, y: int, z: int, width: int, height: int) -> list[dict]:
    result = read_t_test_result()
    t_stat = float(result["TStatistic"])
    p_value = float(result["PValue"])
    alpha = float(result["Alpha"])
    conclusion = result["Conclusion"]
    business_text = (
        "Significant difference in profit margin between high-sales and low-sales groups."
        if conclusion == "Reject H0"
        else "No statistically significant difference detected."
    )
    return [
        shape(f"{name}_bg", x, y, z, width, height, "#FFFFFF", 8),
        textbox(f"{name}_title", x + 16, y + 10, z + 1, width - 32, 30, "Profit Margin T-Test Result", 14, INK),
        textbox(f"{name}_test", x + 18, y + 50, z + 2, width - 36, 28, result["Test"], 10, MUTED),
        textbox(f"{name}_tstat_label", x + 24, y + 90, z + 3, 150, 22, "T-Statistic", 10, MUTED),
        textbox(f"{name}_tstat", x + 24, y + 116, z + 4, 150, 34, f"{t_stat:.2f}", 18, RED),
        textbox(f"{name}_pvalue_label", x + 210, y + 90, z + 5, 150, 22, "P-Value", 10, MUTED),
        textbox(f"{name}_pvalue", x + 210, y + 116, z + 6, 180, 34, f"{p_value:.2e}", 18, PURPLE),
        textbox(f"{name}_alpha_label", x + 430, y + 90, z + 7, 100, 22, "Alpha", 10, MUTED),
        textbox(f"{name}_alpha", x + 430, y + 116, z + 8, 100, 34, f"{alpha:.2f}", 18, BLUE),
        textbox(f"{name}_conclusion", x + 24, y + 164, z + 9, width - 48, 26, conclusion, 15, GREEN if conclusion == "Reject H0" else ORANGE),
        textbox(f"{name}_business", x + 24, y + 192, z + 10, width - 48, 24, business_text, 9, MUTED),
    ]


def build_page_visuals(page_id: str, display_name: str) -> list[dict]:
    visuals = [
        shape(f"{page_id}_surface", 8, 8, 0, CANVAS_W - 16, CANVAS_H - 16, SURFACE, 4),
        textbox(f"{page_id}_title", 28, 22, 10, 620, 42, display_name, 20, INK),
    ]

    if display_name == "Executive Overview":
        visuals += kpi_card(f"{page_id}_sales_card", 28, 76, 20, "Total Sales", "Total Sales", BLUE)
        visuals += kpi_card(f"{page_id}_purchase_card", 326, 76, 21, "Total Purchases", "Total Purchases", GREEN)
        visuals += kpi_card(f"{page_id}_profit_card", 624, 76, 22, "Gross Profit", "Gross Profit", ORANGE)
        visuals += kpi_card(f"{page_id}_margin_card", 922, 76, 23, "Profit Margin %", "Profit Margin %", PURPLE)
        visuals.append(bar_chart(f"{page_id}_top_vendors", 28, 216, 30, 594, 452, "Top 10 Vendors By Sales", "VendorName", "Top Vendor Sales", "Top 10 Vendors by Sales", BLUE))
        visuals.append(bar_chart(f"{page_id}_top_brands", 650, 216, 31, 594, 452, "Top 10 Brands By Sales", "Description", "Top Brand Sales", "Top 10 Brands by Sales", RED))
    elif display_name == "Vendor Analysis":
        visuals += kpi_card(f"{page_id}_sales_card", 28, 76, 20, "Total Sales", "Total Sales", BLUE)
        visuals += kpi_card(f"{page_id}_purchase_card", 326, 76, 21, "Total Purchases", "Total Purchases", GREEN)
        visuals += kpi_card(f"{page_id}_ratio_card", 624, 76, 22, "Sales / Purchase Ratio", "Sales To Purchase Ratio", TEAL)
        visuals += kpi_card(f"{page_id}_inventory_card", 922, 76, 23, "Unsold Inventory Value", "Unsold Inventory Value", ORANGE)
        visuals.append(bar_chart(f"{page_id}_pareto", 28, 216, 30, 594, 452, "Vendor Purchase Contribution", "VendorName", "Vendor Purchase Contribution %", "Vendor Purchase Contribution %", GREEN))
        visuals.append(donut_chart(f"{page_id}_share", 650, 216, 31, 594, 452, "Vendor Purchase Share", "VendorName", "Vendor Purchase Share %", "Top Vendor Purchase Share"))
    elif display_name == "Brand Pricing":
        visuals += kpi_card(f"{page_id}_target_card", 28, 76, 20, "Target Brand Count", "Target Brand Count", RED)
        visuals += kpi_card(f"{page_id}_unit_card", 326, 76, 21, "Avg Unit Purchase Price", "Average Unit Purchase Price", ORANGE)
        visuals += kpi_card(f"{page_id}_margin_card", 624, 76, 22, "Profit Margin %", "Profit Margin %", PURPLE)
        visuals += kpi_card(f"{page_id}_profit_card", 922, 76, 23, "Gross Profit", "Gross Profit", GREEN)
        visuals.append(bar_chart(f"{page_id}_brand_margin", 28, 216, 30, 594, 452, "Brand Margin Targets", "Description", "Brand Profit Margin", "Brands by Profit Margin", PURPLE))
        visuals.append(bar_chart(f"{page_id}_bulk", 650, 216, 31, 594, 210, "Bulk Purchase Analysis", "OrderSize", "Bulk Average Unit Price", "Bulk Purchasing Impact on Unit Price", TEAL, horizontal=False))
        visuals.append(bar_chart(f"{page_id}_targets", 650, 448, 32, 594, 220, "Target Brand Candidates", "Description", "Target Candidate Margin", "Low Sales / High Margin Brand Candidates", RED))
    else:
        visuals += kpi_card(f"{page_id}_turnover_card", 28, 76, 20, "Stock Turnover", "Stock Turnover", TEAL)
        visuals += kpi_card(f"{page_id}_inventory_card", 326, 76, 21, "Unsold Inventory Value", "Unsold Inventory Value", ORANGE)
        visuals += kpi_card(f"{page_id}_margin_card", 624, 76, 22, "Profit Margin %", "Profit Margin %", PURPLE)
        visuals += kpi_card(f"{page_id}_profit_card", 922, 76, 23, "Gross Profit", "Gross Profit", GREEN)
        visuals.append(bar_chart(f"{page_id}_low_turnover", 28, 216, 30, 594, 210, "Low Turnover Vendors", "VendorName", "Low Turnover Avg", "Lowest Inventory Turnover Vendors", RED))
        visuals.append(bar_chart(f"{page_id}_unsold", 650, 216, 31, 594, 210, "Top 10 Unsold Inventory Value", "VendorName", "Top Unsold Inventory", "Top Unsold Inventory Value", ORANGE))
        visuals += ci_panel(f"{page_id}_ci", 28, 448, 32, 594, 220)
        visuals += t_test_panel(f"{page_id}_ttest", 650, 448, 33, 594, 220)
    return visuals


def m_type(tabular_type: str) -> str:
    return {
        "string": "type text",
        "double": "type number",
        "int64": "Int64.Type",
        "boolean": "type logical",
    }[tabular_type]


def power_query_expression(csv_path: Path, columns: dict[str, str]) -> list[str]:
    path = str(csv_path).replace("\\", "\\\\")
    transforms = ", ".join(f'{{"{name}", {m_type(dtype)}}}' for name, dtype in columns.items())
    return [
        "let",
        f'    Source = Csv.Document(File.Contents("{path}"), [Delimiter=",", Columns={len(columns)}, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
        '    #"Promoted Headers" = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),',
        f'    #"Changed Type" = Table.TransformColumnTypes(#"Promoted Headers", {{{transforms}}})',
        "in",
        '    #"Changed Type"',
    ]


def table_definition(table_name: str, spec: dict) -> dict:
    columns = [
        {
            "name": column,
            "dataType": dtype,
            "sourceColumn": column,
            "summarizeBy": "none" if dtype in {"string", "boolean"} else "sum",
        }
        for column, dtype in spec["columns"].items()
    ]
    return {
        "name": table_name,
        "columns": columns,
        "partitions": [
            {
                "name": f"{table_name} Partition",
                "mode": "import",
                "source": {
                    "type": "m",
                    "expression": power_query_expression(DATA_DIR / spec["file"], spec["columns"]),
                },
            }
        ],
    }


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    semantic_dir = REPORTS_DIR / f"{PROJECT_NAME}.SemanticModel"
    report_dir = REPORTS_DIR / f"{PROJECT_NAME}.Report"
    report_definition_dir = report_dir / "definition"

    if report_definition_dir.exists():
        shutil.rmtree(report_definition_dir)

    write_json(
        REPORTS_DIR / f"{PROJECT_NAME}.pbip",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json",
            "version": "1.0",
            "artifacts": [
                {"report": {"path": f"{PROJECT_NAME}.Report"}},
            ],
            "settings": {"enableAutoRecovery": True},
        },
    )

    write_json(
        semantic_dir / "definition.pbism",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json",
            "version": "4.0",
        },
    )

    write_json(
        semantic_dir / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {
                "type": "SemanticModel",
                "displayName": PROJECT_NAME,
            },
            "config": {
                "version": "2.0",
                "logicalId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{PROJECT_NAME}-semantic-model")),
            },
        },
    )

    model_tables = [table_definition(name, spec) for name, spec in TABLES.items()]
    model_tables.append(
        {
            "name": "Report Measures",
            "columns": [{"name": "MeasureTable", "dataType": "string", "isHidden": True}],
            "partitions": [
                {
                    "name": "Report Measures",
                    "mode": "import",
                    "source": {
                        "type": "m",
                        "expression": [
                            "let",
                            '    Source = #table(type table [MeasureTable = text], {{"Measures"}})',
                            "in",
                            "    Source",
                        ],
                    },
                }
            ],
            "measures": [
                {"name": name, "expression": expression, "formatString": "0.00"}
                for name, expression in DAX_MEASURES.items()
            ],
        }
    )

    write_json(
        semantic_dir / "model.bim",
        {
            "name": PROJECT_NAME,
            "compatibilityLevel": 1567,
            "model": {
                "culture": "en-US",
                "defaultPowerBIDataSourceVersion": "powerBI_V3",
                "tables": model_tables,
            },
        },
    )

    write_json(
        report_dir / "definition.pbir",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json",
            "version": "4.0",
            "datasetReference": {
                "byPath": {"path": f"../{PROJECT_NAME}.SemanticModel"}
            },
        },
    )

    write_json(
        report_dir / ".platform",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/gitIntegration/platformProperties/2.0.0/schema.json",
            "metadata": {
                "type": "Report",
                "displayName": PROJECT_NAME,
            },
            "config": {
                "version": "2.0",
                "logicalId": str(uuid.uuid5(uuid.NAMESPACE_URL, f"{PROJECT_NAME}-report")),
            },
        },
    )

    write_json(
        report_dir / "definition" / "version.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/versionMetadata/1.0.0/schema.json",
            "version": "2.0.0",
        },
    )
    write_json(
        report_dir / "definition" / "report.json",
        {
            "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/report/3.2.0/schema.json",
            "themeCollection": {
                "baseTheme": {
                    "name": "CY26SU04",
                    "reportVersionAtImport": {
                        "visual": "2.8.0",
                        "page": "2.1.0",
                        "report": "3.2.0",
                    },
                    "type": "SharedResources",
                }
            },
            "objects": {},
            "settings": {
                "pagesPosition": "Bottom",
            },
        },
    )

    pages = [
        ("90c2e07d8e84e7d5c026", "Executive Overview"),
        ("7f5d2cc28f7a4a1d9b18", "Vendor Analysis"),
        ("4f0c00a74e964927b2d4", "Brand Pricing"),
        ("dbb0d5df3d134ef4a5c8", "Inventory & Statistics"),
    ]
    write_json(
        report_dir / "definition" / "pages" / "pages.json",
        {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/pagesMetadata/1.0.0/schema.json",
                "pageOrder": [page_id for page_id, _ in pages],
                "activePageName": pages[0][0],
            },
        )
    for page_id, display_name in pages:
        write_json(
            report_dir / "definition" / "pages" / page_id / "page.json",
            {
                "$schema": "https://developer.microsoft.com/json-schemas/fabric/item/report/definition/page/2.1.0/schema.json",
                "name": page_id,
                "displayName": display_name,
                "displayOption": "FitToPage",
                "height": CANVAS_H,
                "width": CANVAS_W,
                "objects": {},
                "visualInteractions": [],
            },
        )
        write_visuals(report_dir, page_id, build_page_visuals(page_id, display_name))


if __name__ == "__main__":
    main()
