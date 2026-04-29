import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kpi_diagnosis.data_loader import load_csv
from kpi_diagnosis.data_quality import run_all_checks

if len(sys.argv) != 2:
    print("使い方: python scripts/check_quality.py <CSVファイルのパス>", file=sys.stderr)
    sys.exit(1)

df = load_csv(sys.argv[1])
run_all_checks(df)
