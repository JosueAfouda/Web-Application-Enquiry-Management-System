from __future__ import annotations

import csv
import io
from typing import Any

import pandas as pd
from fastapi import HTTPException, status

from app.schemas.masters import ImportErrorRow


def load_excel_dataframe(file_bytes: bytes) -> pd.DataFrame:
    try:
        return pd.read_excel(io.BytesIO(file_bytes), engine="openpyxl")
    except Exception as exc:  # pragma: no cover
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"invalid excel file: {exc}",
        ) from exc


def ensure_template_columns(
    df: pd.DataFrame,
    *,
    required_columns: set[str],
    allowed_columns: set[str],
) -> None:
    columns = {str(col).strip() for col in df.columns}
    missing = sorted(required_columns - columns)
    unexpected = sorted(columns - allowed_columns)

    if missing or unexpected:
        details: list[str] = []
        if missing:
            details.append(f"missing columns: {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected columns: {', '.join(unexpected)}")

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="; ".join(details),
        )


def normalize_string(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and pd.isna(value):
        return ""
    return str(value).strip()


def parse_bool(value: Any, *, default: bool = True) -> bool:
    text = normalize_string(value)
    if not text:
        return default

    lowered = text.lower()
    if lowered in {"1", "true", "yes", "y"}:
        return True
    if lowered in {"0", "false", "no", "n"}:
        return False

    raise ValueError(f"invalid boolean value: {value}")


def build_error_report_csv(errors: list[ImportErrorRow]) -> bytes:
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=["row_number", "error", "payload"])
    writer.writeheader()

    for item in errors:
        writer.writerow(
            {
                "row_number": item.row_number,
                "error": item.error,
                "payload": item.payload,
            }
        )

    return buffer.getvalue().encode("utf-8")


def build_excel_report(
    rows: list[dict[str, Any]],
    *,
    sheet_name: str,
    columns: list[str] | None = None,
) -> bytes:
    dataframe = pd.DataFrame(rows, columns=columns)
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
        dataframe.to_excel(writer, index=False, sheet_name=sheet_name)
    return buffer.getvalue()
