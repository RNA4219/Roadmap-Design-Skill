# RUNBOOK

## 1. 目的

この Runbook は、仕様整理が終わった状態から実装へ入るときに、どの順で何を固定するかを示す。

## 2. 推奨ディレクトリ構成

初回実装では、以下のように責務を分ける。

```text
src/
  roadmap_core/
    models/
    validators/
    planner/
    presenters/
  wrappers/
    cli/
    http/
    mcp/
schemas/
examples/
tests/
  contract/
  unit/
  integration/
```

## 3. 実装順

### Step 0. workflow でロードマップ化可否を判定する

insight-agent の output_schema_v2 を含む上流 artifact を使う場合でも、本ツールへ直接流し込まない。先に workflow 側で「ロードマップ化する対象か」を判定し、planning-ready な request を組み立ててから以降の手順へ進む。

最低限確認する項目:

- `problem_statement` が 1 件に絞れているか
- `insights[*]`, `constraints[*]`, `available_assets[*]` を 1 件以上そろえられているか
- 未整理論点を `known_failures`, `evidence_refs`, `notes`, `assumptions` へ退避できているか
- 「探索継続」ではなく「計画化してよい」状態まで対象が絞れているか

接続用サンプル:

- `examples/request.from_insight_agent.json`
- 元 artifact 例: `C:\Users\ryo-n\Codex_dev\insight-agent\artifacts\2512.14982v1.v2.json`

### Step 1. 契約を固定する

- `schemas/roadmap-request.schema.json`
- `schemas/roadmap-response.schema.json`
- `schemas/validation-result.schema.json`
- `schemas/error.schema.json`
- `examples/request.full.json`
- `examples/response.success.json`
- `examples/validation.success.json`

ここで JSON Schema と fixture の整合を先に取り、以降のコードはこの契約に従う。

### Step 2. モデルとバリデータを実装する

- request / response / validation-result / error の内部モデル
- `run` と `validate` の分岐
- hard validation と soft planning failure の切り分け
- ID prefix と配列順序の安定化

### Step 3. `roadmap_core` の計画パイプラインを実装する

最低限の処理順は以下とする。

1. planning-ready request の組み立て
2. 課題再定義
3. 成功条件生成
4. 仮説生成
5. 解決方針候補生成
6. 実験計画生成
7. ロードマップ生成
8. リスク / フォールバック / 次アクション生成
9. failure / open question / confidence の最終調整

### Step 4. ラッパーを薄く載せる

- CLI: file / stdin / stdout / stderr / exit code のみ担当
- HTTP: request / response mapping のみ担当
- MCP: tool 名と payload 中継のみ担当

### Step 5. 契約テストを通す

- examples が schema validation を通る
- wrapper ごとの I/O が同一 shape を返す
- 広すぎる課題に対して無理な成功レスポンスを返さない
- `examples/request.from_insight_agent.json` が request schema を通る
- `examples/validation.success.json` と `examples/validation.failure.json` が validation-result schema を通る

## 4. 推奨実装ポリシー

- 先にラッパーを作り込まない
- LLM 呼び出し有無に関わらず、`roadmap_core` の入出力は純粋関数に寄せる
- response の未使用フィールドを勝手に削らない
- `run` の invalid input と `validate` の invalid input の返却契約を混線させない

## 5. 推奨初期スタック

言語は固定しないが、短期実装なら以下が相性が良い。

- モデル / validation: JSON Schema Draft 2020-12 対応ライブラリ
- 同期 API: 軽量な HTTP フレームワーク
- CLI: 引数解析が薄く書けるライブラリ
- 契約テスト: examples と schema を使った golden test

## 6. 先に着手すべきタスク

- schema validation を CI なしでもローカルで回せるようにする
- examples を success / failure / invalid request / validate の 4 系統に分ける
- workflow 判定後 request 例として `request.from_insight_agent.json` を維持する
- `roadmap_core` の最小ダミー実装で response shape と validation-result shape を先に返せるようにする
- `next_actions` の生成規則をユニットテスト化する

## 7. 実装完了判定

以下を満たしたら最初の実装完了とする。

- valid request から valid response を返せる
- `run` の invalid request に対して `error.schema.json` 準拠の応答を返せる
- `validate` の invalid request に対して `validation-result.schema.json` 準拠の応答を返せる
- broad problem に対して `failures` と `open_questions` を返せる
- CLI / HTTP / MCP が同一 contract を使っている

