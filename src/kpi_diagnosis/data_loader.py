import sys
from pathlib import Path

import pandas as pd

REQUIRED_COLUMNS = {"month", "department", "kpi_name", "kpi_value", "target_value", "updated_at"}


def load_csv(path: str) -> pd.DataFrame:
    file = Path(path)

    if not file.exists():
        print(f"エラー: ファイルが見つかりません: {path}", file=sys.stderr)
        sys.exit(1)

    if file.suffix.lower() != ".csv":
        print("エラー: CSV ファイルを指定してください", file=sys.stderr)
        sys.exit(1)

    try:
        df = pd.read_csv(file, encoding="utf-8")
    except UnicodeDecodeError:
        print("エラー: ファイルの文字コードを確認してください（UTF-8 を想定）", file=sys.stderr)
        sys.exit(1)

    if df.empty:
        print("エラー: データ行がありません", file=sys.stderr)
        sys.exit(1)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        print(f"エラー: 必須カラムが不足しています: {', '.join(sorted(missing))}", file=sys.stderr)
        sys.exit(1)

    return df


def inspect(df: pd.DataFrame) -> None:
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    print(f"列名: {', '.join(df.columns.tolist())}")

    print("\nデータ型:")
    for col, dtype in df.dtypes.items():
        print(f"  {col}: {dtype}")

    print("\n欠損数:")
    for col, count in df.isnull().sum().items():
        print(f"  {col}: {count}")

    print("\n先頭5行:")
    print(df.head().to_string(index=False))
