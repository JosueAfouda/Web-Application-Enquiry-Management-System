from io import BytesIO

import pandas as pd

from app.services.reports_service import ReportsService
from app.utils.excel import build_excel_report


def test_safe_ratio() -> None:
    assert ReportsService._safe_ratio(1, 2) == 0.5
    assert ReportsService._safe_ratio(0, 0) == 0.0


def test_build_excel_report_produces_openable_workbook() -> None:
    payload = [
        {"enquiry_no": "ENQ-1", "status": "RECEIVED"},
        {"enquiry_no": "ENQ-2", "status": "APPROVED"},
    ]

    blob = build_excel_report(payload, sheet_name="enquiries", columns=["enquiry_no", "status"])
    assert blob[:2] == b"PK"

    dataframe = pd.read_excel(BytesIO(blob), engine="openpyxl")
    assert list(dataframe.columns) == ["enquiry_no", "status"]
    assert len(dataframe.index) == 2
