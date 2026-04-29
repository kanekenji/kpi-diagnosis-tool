# Feature Spec: Phase 5 — CLI 整備と README 作成

## 前提

- Phase 1〜4 の実装はすべて完了している。
- 既存スクリプト（`inspect_csv.py` / `check_quality.py` / `check_monthly_change.py` / `generate_report.py`）は変更しない。
- Phase 5 で追加するのは `scripts/run_diagnosis.py` と `README.md` のみ。
- 高度な CLI オプション設計（argparse / typer によるフラグ体系など）は行わない。

---

## 1. 目的

Phase 1〜4 で作成した機能を、初見の利用者が迷わず実行できるように整理する。
統合エントリポイント `run_diagnosis.py` と `README.md` を追加し、ポートフォリオとして提示できる最小完成形とする。

---

## 2. 作成するファイル

| ファイル | 役割 |
|---------|------|
| `scripts/run_diagnosis.py` | CSV を渡すと品質チェック・前月比チェック・レポート生成を順に実行する統合エントリポイント |
| `README.md` | セットアップから実行まで自己完結したドキュメント |

---

## 3. `scripts/run_diagnosis.py` の仕様

### 目的

「CSV ファイルを1つ渡すだけでフル診断レポートが出力される」ワンライナー体験を提供する。

### 呼び出し形式

```bash
python3.11 scripts/run_diagnosis.py <CSVファイルのパス>
```

### 実行順序

1. Phase 1: `load_csv()` で CSV を読み込む
2. Phase 2: `run_all_checks()` でデータ品質チェックを実行し、結果を標準出力に表示する
3. Phase 3: `run_monthly_change()` で前月比チェックを実行し、結果を標準出力に表示する
4. Phase 4: `generate()` で Markdown レポートを生成し、出力パスを標準出力に表示する

### 出力

- Phase 2・3 の結果は標準出力に表示する（既存スクリプトと同じ出力）
- レポートは `reports/report_YYYYMMDD_HHMMSS.md` に出力する
- 最後に `レポートを出力しました: reports/report_YYYYMMDD_HHMMSS.md` を表示する

### エラーハンドリング

- 引数が 1 つでない場合: `使い方: python3.11 scripts/run_diagnosis.py <CSVファイルのパス>` を表示して終了する
- ファイル関連のエラーは Phase 1 の `load_csv()` が処理するため、このスクリプトでは追加処理しない

### サンプル実行イメージ

```
$ python3.11 scripts/run_diagnosis.py data/sample_kpi.csv

=== データ品質チェック結果 ===
...

=== 前月比変化率一覧 ===
...

レポートを出力しました: reports/report_20240415_143022.md
```

---

## 4. `README.md` の構成

### セクション構成

```
# kpi-diagnosis-tool

## ツールの目的
## 対象ユーザー
## できること（Phase 1〜4）
## セットアップ
## 実行方法
## サンプルデータ
## 出力例
## スコープ外
```

### 各セクションの内容仕様

#### ツールの目的

- CSV 形式の KPI データを読み込み、欠損・型不整合・重複・前月比急変を自動検出する
- 検出結果と Power BI 改善コメントを Markdown レポートとして出力する
- ローカルで動作する CLI ツール（外部サービス・API 不使用）

#### 対象ユーザー

- KPI レポートを管理するビジネスアナリスト
- Power BI ダッシュボードを保守するデータ担当者
- spec-driven development のデモや学習を目的とするエンジニア

#### できること（Phase 1〜4）

以下を箇条書きまたは表で記載する：

| フェーズ | 機能 |
|---------|------|
| Phase 1 | CSV 読み込み・基本構造の確認（行数・列数・型・欠損数・プレビュー） |
| Phase 2 | データ品質チェック（欠損率・型不整合・日付フォーマット・重複） |
| Phase 3 | 前月比変化率の算出・±20% 以上の急変検出 |
| Phase 4 | Markdown レポート生成・Power BI 改善コメントの自動付記 |

#### セットアップ

```bash
# 前提: Python 3.11
python3.11 --version

# 依存ライブラリのインストール
pip install -r requirements.txt
```

- Python 3.11 を明記する（システム Python 3.8 では動作しないことも注記する）
- `requirements.txt` に `pandas>=2.0.0` と `jinja2>=3.0.0` が含まれることを示す

#### 実行方法

```bash
# フル診断（推奨）
python3.11 scripts/run_diagnosis.py data/sample_kpi.csv

# 個別実行
python3.11 scripts/inspect_csv.py data/sample_kpi.csv
python3.11 scripts/check_quality.py data/sample_kpi.csv
python3.11 scripts/check_monthly_change.py data/sample_kpi.csv
python3.11 scripts/generate_report.py data/sample_kpi.csv
```

#### サンプルデータ

| ファイル | 内容 |
|---------|------|
| `data/sample_kpi.csv` | 基本動作確認用（欠損 1 件・急変あり） |
| `data/sample_kpi_quality_issues.csv` | Phase 2 検証用（欠損・型不整合・重複・フォーマット不正を含む） |
| `data/sample_kpi_monthly_change.csv` | Phase 3 検証用（急変・前月値ゼロ・欠損を含む） |

#### 出力例

- レポートは `reports/` ディレクトリに `report_YYYYMMDD_HHMMSS.md` 形式で出力される
- レポートの構成を概略で示す（見出し一覧程度）:
  - `# KPI 診断レポート`（対象ファイル・実行日時・行数・列数・総合判定）
  - `## データ品質チェック結果`（6 チェック）
  - `## 前月比急変チェック結果`（急変一覧・スキップ行）
  - `## Power BI 改善コメント`（ルールベースで自動生成）

#### スコープ外

- Excel (.xlsx) 対応
- Web UI
- Power BI API 連携
- LLM による自由文生成
- IQR・統計的外れ値検出
- 機械学習による異常検出
- 複雑な CLI オプション設計
- パッケージ公開・Docker 化

---

## 5. 成功条件

以下をすべて満たすとき、Phase 5 は完了とみなす。

- [ ] `python3.11 scripts/run_diagnosis.py data/sample_kpi.csv` を実行すると Phase 2〜4 の出力が順に表示される
- [ ] `reports/` 配下に Markdown レポートが生成される
- [ ] README.md を読んだ初見の人が環境構築から実行まで再現できる
- [ ] README.md に Python 3.11 前提が明記されている
- [ ] README.md に `data/sample_kpi.csv` を使った実行例が含まれている
- [ ] README.md にレポートの出力先（`reports/` ディレクトリ）が明記されている
- [ ] README.md を見てポートフォリオとして何を作ったか説明できる
- [ ] 既存の `inspect_csv.py` / `check_quality.py` / `check_monthly_change.py` / `generate_report.py` の動作が変わらない

---

## 6. Phase 5 ではやらないこと

| 項目 | 備考 |
|------|------|
| argparse / typer による高度な CLI オプション | 引数はファイルパスのみ |
| 閾値・出力先のオプション化 | 固定値のまま |
| Excel (.xlsx) 対応 | スコープ外 |
| Web UI | スコープ外 |
| Power BI API 連携 | スコープ外 |
| LLM による自由文生成 | スコープ外 |
| IQR・Z スコアによる外れ値検出 | スコープ外 |
| 機械学習による異常検出 | スコープ外 |
| パッケージ公開（PyPI など） | スコープ外 |
| Docker 化 | スコープ外 |
