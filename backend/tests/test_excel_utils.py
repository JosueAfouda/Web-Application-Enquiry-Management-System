import pandas as pd
from fastapi import HTTPException

from app.schemas.masters import ImportErrorRow
from app.utils.excel import (
    build_error_report_csv,
    ensure_template_columns,
    normalize_string,
    parse_bool,
)


def test_parse_bool_values() -> None:
    assert parse_bool("true") is True
    assert parse_bool("FALSE") is False
    assert parse_bool("", default=False) is False


def test_parse_bool_invalid() -> None:
    try:
        parse_bool("not-a-bool")
    except ValueError:
        return
    raise AssertionError("parse_bool should raise ValueError for invalid inputs")


def test_template_columns_validation() -> None:
    df = pd.DataFrame(columns=["code", "name", "country"])
    ensure_template_columns(
        df,
        required_columns={"code", "name", "country"},
        allowed_columns={"code", "name", "country", "is_active"},
    )


def test_template_columns_validation_failure() -> None:
    df = pd.DataFrame(columns=["code", "name", "bad_col"])
    try:
        ensure_template_columns(
            df,
            required_columns={"code", "name", "country"},
            allowed_columns={"code", "name", "country"},
        )
    except HTTPException as exc:
        assert exc.status_code == 400
        assert "missing columns" in str(exc.detail)
        assert "unexpected columns" in str(exc.detail)
        return

    raise AssertionError("ensure_template_columns should raise HTTPException")


def test_build_error_report_csv() -> None:
    errors = [
        ImportErrorRow(row_number=2, error="missing country", payload={"code": "C1"}),
        ImportErrorRow(row_number=3, error="bad bool", payload={"is_active": "x"}),
    ]

    output = build_error_report_csv(errors).decode("utf-8")

    assert "row_number,error,payload" in output
    assert "missing country" in output
    assert "bad bool" in output


def test_normalize_string() -> None:
    assert normalize_string("  A  ") == "A"
    assert normalize_string(None) == ""
