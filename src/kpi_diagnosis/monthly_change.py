import math

import pandas as pd

THRESHOLD = 20.0
GROUP_COLS = ["department", "kpi_name"]
SKIP_FIRST = "(初月のためスキップ)"
SKIP_PREV_NAN = "(前月値が欠損のためスキップ)"
SKIP_ZERO = "(前月値が 0 のためスキップ)"
SKIP_CURRENT_NAN = "(当月値が欠損のためスキップ)"


def _format_value(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{v:,.0f}"


def _compute_change_rate(current, previous, is_first: bool):
    """Return (rate_float, skip_reason). rate_float is None when skipped."""
    if is_first:
        return None, SKIP_FIRST
    if current is None or (isinstance(current, float) and math.isnan(current)):
        return None, SKIP_CURRENT_NAN
    if previous is None or (isinstance(previous, float) and math.isnan(previous)):
        return None, SKIP_PREV_NAN
    if previous == 0:
        return None, SKIP_ZERO
    return (current - previous) / previous * 100, None


def compute_monthly_change(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["kpi_value"] = pd.to_numeric(df["kpi_value"], errors="coerce")
    df = df.sort_values(GROUP_COLS + ["month"]).reset_index(drop=True)

    rows = []
    for _, group in df.groupby(GROUP_COLS, sort=False):
        group = group.sort_values("month").reset_index(drop=True)
        prev_values = group["kpi_value"].shift(1)
        for i, row in group.iterrows():
            current = row["kpi_value"]
            previous = prev_values.iloc[i] if not pd.isna(prev_values.iloc[i]) else float("nan")
            is_first = i == 0
            rate, skip_reason = _compute_change_rate(
                None if pd.isna(current) else current,
                None if pd.isna(previous) else previous,
                is_first=is_first,
            )
            rows.append({
                "department": row["department"],
                "kpi_name": row["kpi_name"],
                "month": row["month"],
                "current_value": current,
                "previous_value": previous,
                "change_rate": rate,
                "skip_reason": skip_reason,
            })

    return pd.DataFrame(rows)


def _has_skip(skip_reason) -> bool:
    return skip_reason is not None and not (isinstance(skip_reason, float) and math.isnan(skip_reason))


def _verdict(rate, skip_reason) -> str:
    if _has_skip(skip_reason):
        return skip_reason
    if abs(rate) >= THRESHOLD:
        return "急変 ⚠"
    return "正常"


def _format_rate(rate, skip_reason) -> str:
    if _has_skip(skip_reason):
        return "-"
    sign = "+" if rate >= 0 else ""
    return f"{sign}{rate:.1f}%"


def print_all(result: pd.DataFrame) -> None:
    print("=== 前月比変化率一覧 ===\n")
    header = f"{'department':<16} {'kpi_name':<14} {'month':<9} {'current':>10} {'previous':>10}  {'change_rate':>12}  判定"
    print(header)
    print("-" * len(header))
    for _, row in result.iterrows():
        rate = row["change_rate"]
        skip = row["skip_reason"]
        verdict = _verdict(rate, skip)
        rate_str = _format_rate(rate, skip)
        cur_str = _format_value(row["current_value"])
        prev_str = _format_value(row["previous_value"])
        print(
            f"{row['department']:<16} {row['kpi_name']:<14} {row['month']:<9}"
            f" {cur_str:>10} {prev_str:>10}  {rate_str:>12}  {verdict}"
        )


def print_summary(result: pd.DataFrame) -> None:
    print("\n=== 急変サマリー（±20% 以上） ===\n")
    surges = result[result["change_rate"].notna() & (result["change_rate"].abs() >= THRESHOLD)]
    if surges.empty:
        print("急変なし")
        return
    print(f"急変検出: {len(surges)} 件\n")
    header = f"  {'department':<16} {'kpi_name':<14} {'month':<9}  change_rate"
    print(header)
    for _, row in surges.iterrows():
        rate_str = _format_rate(row["change_rate"], None)
        print(f"  {row['department']:<16} {row['kpi_name']:<14} {row['month']:<9}  {rate_str}")


def run_monthly_change(df: pd.DataFrame) -> dict:
    result = compute_monthly_change(df)
    print_all(result)
    print_summary(result)

    surges = result[result["change_rate"].notna() & (result["change_rate"].abs() >= THRESHOLD)]
    non_trivial = result[result["skip_reason"].apply(
        lambda x: _has_skip(x) and x != SKIP_FIRST
    )]

    sudden_detail = [
        {
            "department": r["department"],
            "kpi_name": r["kpi_name"],
            "month": r["month"],
            "current_value": r["current_value"],
            "previous_value": r["previous_value"],
            "change_rate": r["change_rate"],
        }
        for _, r in surges.iterrows()
    ]

    skipped_detail = [
        {
            "department": r["department"],
            "kpi_name": r["kpi_name"],
            "month": r["month"],
            "skip_reason": r["skip_reason"],
        }
        for _, r in non_trivial.iterrows()
    ]

    has_prev_nan = any(d["skip_reason"] == SKIP_PREV_NAN for d in skipped_detail)

    return {
        "all_changes": {"status": "ok", "count": len(result), "detail": None},
        "sudden_changes": {
            "status": "warning" if sudden_detail else "ok",
            "count": len(sudden_detail),
            "detail": sudden_detail or None,
        },
        "skipped": {
            "status": "warning" if has_prev_nan else "ok",
            "count": len(skipped_detail),
            "detail": skipped_detail or None,
        },
        "summary": {
            "total_rows": len(result),
            "sudden_change_count": len(sudden_detail),
            "skipped_count": len(skipped_detail),
        },
    }
