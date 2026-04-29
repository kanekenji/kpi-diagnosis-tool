import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kpi_diagnosis.data_loader import load_csv
from kpi_diagnosis.data_quality import run_all_checks
from kpi_diagnosis.monthly_change import run_monthly_change
from kpi_diagnosis.report_generator import generate

if len(sys.argv) != 2:
    print("使い方: python scripts/generate_report.py <CSVファイルのパス>", file=sys.stderr)
    sys.exit(1)

csv_path = sys.argv[1]
df = load_csv(csv_path)
row_count, col_count = len(df), len(df.columns)

quality = run_all_checks(df)
change = run_monthly_change(df)

out_path = generate(
    quality=quality,
    change=change,
    filename=Path(csv_path).name,
    row_count=row_count,
    col_count=col_count,
)

print(f"\nレポートを出力しました: {out_path}")
