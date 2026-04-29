import re

import pandas as pd

KEY_COLS = ["month", "department", "kpi_name"]
NUMERIC_COLS = ["kpi_value", "target_value"]
MONTH_RE = re.compile(r"^\d{4}-\d{2}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def _csv_row(df_index: int) -> int:
    return df_index + 2


def check_missing(df: pd.DataFrame) -> dict:
    print("[欠損チェック]")
    total = len(df)
    detail = []
    for col in df.columns:
        count = int(df[col].isnull().sum())
        rate = round(count / total * 100, 1)
        if count == 0:
            print(f"  {col:<14}: 欠損 0 件 (0.0%) → 問題なし")
        else:
            rows = [_csv_row(i) for i in df[df[col].isnull()].index]
            print(f"  {col:<14}: 欠損 {count} 件 ({rate:.1f}%) → 問題あり  行番号: {rows}")
            detail.append({"column": col, "count": count, "rate": rate, "rows": rows})
    return {"status": "warning" if detail else "ok", "count": len(detail), "detail": detail or None}


def check_numeric_types(df: pd.DataFrame) -> dict:
    print("[型整合性チェック]")
    total_count = 0
    detail = []
    for col in NUMERIC_COLS:
        coerced = pd.to_numeric(df[col], errors="coerce")
        bad = df[coerced.isnull() & df[col].notnull()]
        if bad.empty:
            print(f"  {col:<14}: 問題なし")
        else:
            rows = [_csv_row(i) for i in bad.index]
            vals = [str(v) for v in bad[col].tolist()]
            print(f"  {col:<14}: 型不整合 {len(bad)} 件 → 問題あり  行番号: {rows}  値: {vals}")
            detail.append({"column": col, "count": len(bad), "rows": rows, "bad_values": vals})
            total_count += len(bad)
    return {"status": "warning" if detail else "ok", "count": total_count, "detail": detail or None}


def check_month_format(df: pd.DataFrame) -> dict:
    print("[month フォーマットチェック]")
    non_null = df["month"].dropna()
    bad = non_null[~non_null.astype(str).str.match(MONTH_RE)]
    if bad.empty:
        print("  問題なし")
        return {"status": "ok", "count": 0, "detail": None}
    rows = [_csv_row(i) for i in bad.index]
    vals = bad.tolist()
    print(f"  フォーマット不正 {len(bad)} 件 → 問題あり  行番号: {rows}  値: {vals}")
    return {"status": "warning", "count": len(bad), "detail": [{"count": len(bad), "rows": rows, "bad_values": vals}]}


def check_updated_at_format(df: pd.DataFrame) -> dict:
    print("[updated_at フォーマットチェック]")
    non_null = df["updated_at"].dropna()
    bad = non_null[~non_null.astype(str).str.match(DATE_RE)]
    if bad.empty:
        print("  問題なし")
        return {"status": "ok", "count": 0, "detail": None}
    rows = [_csv_row(i) for i in bad.index]
    vals = bad.tolist()
    print(f"  フォーマット不正 {len(bad)} 件 → 問題あり  行番号: {rows}  値: {vals}")
    return {"status": "warning", "count": len(bad), "detail": [{"count": len(bad), "rows": rows, "bad_values": vals}]}


def check_full_duplicates(df: pd.DataFrame) -> dict:
    print("[完全重複チェック]")
    dup = df[df.duplicated(keep="first")]
    if dup.empty:
        print("  問題なし")
        return {"status": "ok", "count": 0, "detail": None}
    rows = [_csv_row(i) for i in dup.index]
    print(f"  完全重複 {len(dup)} 件 → 問題あり  行番号: {rows}")
    return {"status": "warning", "count": len(dup), "detail": [{"count": len(dup), "rows": rows}]}


def check_key_duplicates(df: pd.DataFrame) -> dict:
    key_label = " + ".join(KEY_COLS)
    print(f"[キー重複チェック]  キー: {key_label}")
    dup = df[df.duplicated(subset=KEY_COLS, keep="first")]
    if dup.empty:
        print("  問題なし")
        return {"status": "ok", "count": 0, "detail": None}
    detail = []
    for i in dup.index:
        row = df.loc[i]
        key_val = tuple(row[c] for c in KEY_COLS)
        print(f"  キー重複 → 問題あり  行番号: [{_csv_row(i)}]  キー値: {key_val}")
        detail.append({"row": _csv_row(i), "key": list(key_val)})
    return {"status": "warning", "count": len(dup), "detail": detail}


def run_all_checks(df: pd.DataFrame) -> dict:
    print("=== データ品質チェック結果 ===\n")

    missing = check_missing(df)
    type_mismatch = check_numeric_types(df)
    month_format = check_month_format(df)
    updated_at_format = check_updated_at_format(df)
    full_duplicates = check_full_duplicates(df)
    key_duplicates = check_key_duplicates(df)

    checks = [missing, type_mismatch, month_format, updated_at_format, full_duplicates, key_duplicates]
    issues = sum(1 for c in checks if c["status"] != "ok")

    print(f"\n=== サマリー ===")
    print(f"チェック項目数: {len(checks)}")
    print(f"問題あり: {issues} 件")
    print(f"問題なし: {len(checks) - issues} 件")

    return {
        "missing": missing,
        "type_mismatch": type_mismatch,
        "month_format": month_format,
        "updated_at_format": updated_at_format,
        "full_duplicates": full_duplicates,
        "key_duplicates": key_duplicates,
    }
