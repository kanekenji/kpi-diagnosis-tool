# kpi-diagnosis-tool

CSV 形式の KPI データを読み込み、データ品質の問題と前月比急変を自動検出して、Power BI 改善コメント付きの Markdown レポートを出力するローカル CLI ツールです。

Python 3.11 と `pip install -r requirements.txt` だけで動作します。外部 API や LLM による自由文生成は一切使用しません。

---

## ツールの目的

ビジネスアナリストやデータ担当者が手動で行っている KPI データの点検作業を自動化します。

- 欠損・型不整合・日付フォーマット不正・重複行を検出する
- 部署 × KPI 単位で前月比変化率を算出し、±20% 以上の急変を検出する
- 検出結果と Power BI 改善コメントを Markdown レポートとして出力する

---

## 対象ユーザー

- KPI レポートを管理するビジネスアナリスト
- Power BI ダッシュボードを保守するデータ担当者
- spec-driven development のデモや学習を目的とするエンジニア

---

## できること（Phase 1〜4）

| フェーズ | 機能 |
|---------|------|
| Phase 1 | CSV 読み込み・基本構造の確認（行数・列数・データ型・欠損数・先頭5行プレビュー） |
| Phase 2 | データ品質チェック（欠損率・型不整合・日付フォーマット・完全重複・キー重複） |
| Phase 3 | 前月比変化率の算出・±20% 以上の急変検出・スキップ理由の表示 |
| Phase 4 | Markdown レポート生成・Power BI 改善コメントのルールベース自動付記 |

### Power BI 改善コメントの生成ルール

| 検出内容 | 条件 | 推奨アクション |
|---------|------|--------------|
| 欠損が多い | 欠損率 20% 以上 | フィルター・欠損補完・データソース確認 |
| 欠損あり | 欠損数 1 件以上 | ビジュアルへの影響確認 |
| 型不一致 | 数値列に文字列混在 | Power Query で型変換確認 |
| 重複行あり | 完全重複またはキー重複 | 重複削除またはキー設計確認 |
| 前月比急変 | 変化率 ±20% 以上 | データ更新日・集計条件・ソース変更確認 |
| 前月値欠損 | 前月値が欠損でスキップ | データ更新漏れ・抽出条件確認 |

---

## セットアップ

### 前提

**Python 3.11 が必要です。** macOS に標準搭載されている Python 3.8 では `pandas>=2.0.0` のインストールに失敗します。

```bash
# Python 3.11 のバージョンを確認
python3.11 --version
# → Python 3.11.x
```

Python 3.11 が入っていない場合は [python.org](https://www.python.org/downloads/) または Homebrew でインストールしてください。

```bash
# Homebrew を使う場合
brew install python@3.11
```

### 依存ライブラリのインストール

```bash
python3.11 -m pip install -r requirements.txt
```

`requirements.txt` には以下が含まれています：

```
pandas>=2.0.0
jinja2>=3.0.0
```

---

## 実行方法

### フル診断（推奨）

CSV を1つ渡すと、品質チェック・前月比チェック・レポート生成を順に実行します。

```bash
python3.11 scripts/run_diagnosis.py data/sample_kpi.csv
```

実行後、`reports/report_YYYYMMDD_HHMMSS.md` にレポートが出力されます。

### 個別実行

各フェーズを単独で実行することもできます。

```bash
# Phase 1: CSV の基本構造を確認する
python3.11 scripts/inspect_csv.py data/sample_kpi.csv

# Phase 2: データ品質チェックを実行する
python3.11 scripts/check_quality.py data/sample_kpi.csv

# Phase 3: 前月比急変チェックを実行する
python3.11 scripts/check_monthly_change.py data/sample_kpi.csv

# Phase 4: Markdown レポートを生成する
python3.11 scripts/generate_report.py data/sample_kpi.csv
```

---

## サンプルデータ

`data/` 配下に3種類のサンプル CSV が含まれています。

| ファイル | 内容 | 推奨用途 |
|---------|------|---------|
| `data/sample_kpi.csv` | 10行・欠損1件・急変あり | 基本動作確認 |
| `data/sample_kpi_quality_issues.csv` | 欠損・型不整合・重複・フォーマット不正を含む | Phase 2 動作確認 |
| `data/sample_kpi_monthly_change.csv` | 急変・前月値ゼロ・欠損を含む | Phase 3 動作確認 |

### 入力 CSV の必須カラム

| カラム名 | 型 | フォーマット |
|---------|-----|------------|
| `month` | 文字列 | `YYYY-MM`（例: `2024-01`） |
| `department` | 文字列 | 任意 |
| `kpi_name` | 文字列 | 任意 |
| `kpi_value` | 数値 | 整数または小数 |
| `target_value` | 数値 | 整数または小数 |
| `updated_at` | 文字列 | `YYYY-MM-DD`（例: `2024-01-31`） |

---

## 出力例

### 標準出力（抜粋）

```
=== データ品質チェック結果 ===

[欠損チェック]
  kpi_value     : 欠損 1 件 (10.0%) → 問題あり  行番号: [7]
  ...

=== 前月比変化率一覧 ===

department       kpi_name   month    current   previous  change_rate  判定
------------------------------------------------------------------------
営業部           売上高     2024-01  1,200,000     -          -        (初月のためスキップ)
営業部           売上高     2024-02    950,000  1,200,000   -20.8%     急変 ⚠
...

レポートを出力しました: reports/report_20240415_143022.md
```

### 生成される Markdown レポート

レポートは `reports/` ディレクトリに `report_YYYYMMDD_HHMMSS.md` 形式で出力されます。

レポートの構成：

```
# KPI 診断レポート
  対象ファイル・実行日時・行数・列数・総合判定

## データ品質チェック結果
  欠損チェック / 型整合性チェック / month フォーマットチェック /
  updated_at フォーマットチェック / 完全重複チェック / キー重複チェック

## 前月比急変チェック結果（閾値: ±20%）
  急変一覧テーブル / スキップされた行

## Power BI 改善コメント
  ルールベースで自動生成されたコメント一覧
```

---

## ポートフォリオとしての説明

このツールは **spec-driven development（仕様駆動開発）** の学習・デモを目的として、仕様書（`specs/` 配下）を先に書いてからコードを実装するアプローチで構築しました。

- `specs/mission.md` / `specs/tech-stack.md` / `specs/roadmap.md` で Constitution を定義
- `specs/features/phase*.md` で各フェーズの Feature Spec を作成
- 仕様→実装→検証のサイクルを5フェーズにわたって繰り返した

技術スタック: Python 3.11 / pandas / Jinja2 / CSV / Markdown

---

## スコープ外

以下はこのツールの対象外です。

- Excel (.xlsx) 対応
- Web UI
- Power BI API への直接書き込み
- LLM による自由文コメント生成
- IQR・Z スコアによる統計的外れ値検出
- 機械学習による異常検出
- 複雑な CLI オプション設計
- パッケージ公開（PyPI）・Docker 化
