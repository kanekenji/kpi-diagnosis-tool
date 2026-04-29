# Tech Stack

## 言語

- **Python 3.11+** — データ処理・CLI・Notebook すべてに使用

## コアライブラリ

| ライブラリ | 用途 | 採用理由 |
|-----------|------|---------|
| `pandas` | CSV の読み込みとデータ操作 | KPI集計・前月比計算に標準的 |
| `jinja2` | Markdown レポートのテンプレート生成 | ロジックとテンプレートを分離できる |

## 実行インターフェース

- **第一選択: CLI（`argparse` または `typer`）** — ファイルパスと設定を引数で渡す
- **補助: Jupyter Notebook** — 探索・デバッグ・デモ用途として併用可

## 将来拡張（MVP対象外）

- Excel (.xlsx) 対応: `openpyxl` を追加することで対応可能。Phase 5 以降の任意対応とする。
- 統計的異常値検出: IQR 法・Z スコアなど。MVP では扱わず、基本品質チェック（欠損・型・重複）に絞る。

## 出力形式

- **Markdown (.md)** — 診断結果と Power BI 改善コメントを含むレポート
- ファイル出力（stdout への出力もオプションで対応可）

## 依存管理

- `requirements.txt` で管理（軽量さを維持するため Poetry 等は使わない）

## 制約

- 外部サービス・API への接続なし
- インストールは `pip install -r requirements.txt` のみで完結すること
- Windows / Mac / Linux いずれでも動作すること
