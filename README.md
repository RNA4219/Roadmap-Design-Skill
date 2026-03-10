# Roadmap Design Skill

Roadmap Design Skill は、上流工程で見つかった課題候補、気づき、制約、利用可能資産を受け取り、実装と検証に着手できるロードマップへ再構成するための設計ツールです。

このリポジトリは `$agent-tools-hub` と `workflow-cookbook` の入口パターンを参照し、要件定義から仕様、I/F 契約、実装準備、評価基準までを一続きで読める構成へ整理しています。

## 現在の到達点

- 要件定義を再整理し、不足していた前提と判断基準を補完
- 仕様書を再作成し、MVP の正規契約を固定
- CLI / HTTP API / MCP の I/F を同期型 MVP に揃えて整理
- JSON Schema とサンプル入出力を追加し、実装前の契約テスト準備を完了
- 実装順序と受け入れ条件を `RUNBOOK.md` / `EVALUATION.md` に明記

## ドキュメント導線

- `BLUEPRINT.md`: このツールが何を解くか、何を解かないか、今回補完した設計判断
- `docs/src/requirements.md`: 正式な要件定義
- `docs/src/specification.md`: 実装時に参照する正規仕様
- `docs/src/interfaces.md`: CLI / HTTP API / MCP の外部契約
- `schemas/`: request / response / error の JSON Schema
- `examples/`: 正常系 / 失敗系のサンプル payload
- `RUNBOOK.md`: 実装着手順、推奨レイアウト、作業順
- `EVALUATION.md`: 受け入れ条件、契約テスト観点、レビュー観点

## MVP の境界

- 1 回のリクエストで扱う `problem_statement` は 1 件
- 単発同期実行を正本とし、永続化付きの run store は持たない
- `roadmap_core` を唯一の業務ロジック層とし、CLI / API / MCP は薄いラッパーとする
- 入力不足や課題の広すぎる状態も、`failures` と `open_questions` を含む構造化レスポンスで返す

## 今回補完した重要事項

- `schema_version` を request / response / error すべてに導入
- `constraints` と `available_assets` をオブジェクト配列化し、後工程で追跡しやすくした
- `next_actions` を文字列配列から構造化オブジェクトへ変更し、実装準備に直結する形へ固定
- `GET /runs/{id}` 系の I/F は、永続化要件と矛盾するため MVP から除外
- 出力順序、ID 命名規則、信頼度表現、入力との traceability を明文化

## 次に実装する人への入口

1. `BLUEPRINT.md`
2. `docs/src/requirements.md`
3. `docs/src/specification.md`
4. `schemas/` と `examples/`
5. `RUNBOOK.md`
6. `EVALUATION.md`
