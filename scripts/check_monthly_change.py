import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kpi_diagnosis.data_loader import load_csv
from kpi_diagnosis.monthly_change import run_monthly_change

if len(sys.argv) != 2:
    print("使い方: python scripts/check_monthly_change.py <CSVファイルのパス>", file=sys.stderr)
    sys.exit(1)

df = load_csv(sys.argv[1])
run_monthly_change(df)
