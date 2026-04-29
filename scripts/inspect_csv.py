import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from kpi_diagnosis.data_loader import inspect, load_csv

if len(sys.argv) != 2:
    print("使い方: python scripts/inspect_csv.py <CSVファイルのパス>", file=sys.stderr)
    sys.exit(1)

df = load_csv(sys.argv[1])
inspect(df)
