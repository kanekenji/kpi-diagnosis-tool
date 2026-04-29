import math
from datetime import datetime
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

TEMPLATES_DIR = Path(__file__).parent / "templates"
THRESHOLD = 20.0
SKIP_PREV_NAN = "(前月値が欠損のためスキップ)"


def _fmt_num(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    return f"{v:,.0f}"


def _fmt_pct(v) -> str:
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "-"
    sign = "+" if v >= 0 else ""
    return f"{sign}{v:.1f}%"


def _build_comments(quality: dict, change: dict) -> list:
    comments = []

    if quality["missing"]["detail"]:
        for d in quality["missing"]["detail"]:
            if d["rate"] >= 20.0:
                comments.append(
                    f"`{d['column']}` の欠損率は {d['rate']}% です。"
                    "Power BI ビジュアルで空白や集計ズレが生じる可能性があります。"
                    "データソースの欠損補完、または Power Query でのフィルター設定を確認してください。"
                )
            else:
                comments.append(
                    f"`{d['column']}` に欠損が {d['count']} 件あります。"
                    "欠損行がビジュアルに影響していないか確認してください。"
                )

    if quality["type_mismatch"]["detail"]:
        for d in quality["type_mismatch"]["detail"]:
            comments.append(
                f"`{d['column']}` に数値として扱えない値が混在しています。"
                "集計エラーや可視化不具合の原因になります。"
                "Power Query で列の型変換設定を確認してください。"
            )

    dup_count = quality["full_duplicates"]["count"] + quality["key_duplicates"]["count"]
    if dup_count > 0:
        comments.append(
            "重複行が検出されました。件数・売上などの集計値が二重にカウントされるリスクがあります。"
            "重複削除の処理、またはキー設計の見直しを検討してください。"
        )

    surge_count = change["sudden_changes"]["count"]
    if surge_count > 0:
        comments.append(
            f"前月比 ±20% 以上の急変が {surge_count} 件検出されました。KPI の急激な変動が含まれています。"
            "データ更新日・集計条件・データソースの変更を確認してください。"
        )

    if change["skipped"]["detail"]:
        has_prev_nan = any(d["skip_reason"] == SKIP_PREV_NAN for d in change["skipped"]["detail"])
        if has_prev_nan:
            comments.append(
                "前月値が欠損しているため比較できなかった KPI があります。"
                "データの連続性が失われている可能性があります。"
                "データ更新漏れや抽出条件を確認してください。"
            )

    return comments


def _total_problems(quality: dict, change: dict) -> int:
    return (
        quality["missing"]["count"]
        + quality["type_mismatch"]["count"]
        + quality["month_format"]["count"]
        + quality["updated_at_format"]["count"]
        + quality["full_duplicates"]["count"]
        + quality["key_duplicates"]["count"]
        + change["sudden_changes"]["count"]
    )


def generate(
    quality: dict,
    change: dict,
    filename: str,
    row_count: int,
    col_count: int,
    output_dir: str = "reports",
) -> Path:
    run_at = datetime.now()
    total = _total_problems(quality, change)
    overall = "✅ 問題なし" if total == 0 else f"⚠ 問題あり（{total} 件）"
    comments = _build_comments(quality, change)

    env = Environment(
        loader=FileSystemLoader(str(TEMPLATES_DIR)),
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    env.filters["fmt_num"] = _fmt_num
    env.filters["fmt_pct"] = _fmt_pct

    template = env.get_template("report.md.j2")
    rendered = template.render(
        filename=filename,
        run_at=run_at.strftime("%Y-%m-%d %H:%M:%S"),
        row_count=row_count,
        col_count=col_count,
        overall=overall,
        quality=quality,
        change=change,
        comments=comments,
        threshold=int(THRESHOLD),
    )

    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"report_{run_at.strftime('%Y%m%d_%H%M%S')}.md"
    out_path.write_text(rendered, encoding="utf-8")
    return out_path
