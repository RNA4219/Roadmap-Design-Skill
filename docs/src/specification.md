# Roadmap Design Skill Specification

## 1. 仕様の位置付け

本書は `docs/src/requirements.md` を実装可能な契約へ変換した正規仕様である。request / response / error の最終的な shape は `schemas/` を正本とし、本書はその意味論と生成規則を説明する。

## 2. 正規処理フロー

Roadmap Design Skill は以下の順で処理する。

1. request schema validation
2. 入力正規化
3. 課題再定義
4. 成功条件生成
5. 仮説生成
6. 解決方針候補生成
7. 実験計画生成
8. ロードマップ生成
9. リスク / フォールバック / 次アクション生成
10. open question / failure / confidence 調整
11. response schema validation

## 3. Request Contract

### 3.1 Top-level fields

| field | required | type | note |
|---|---|---|---|
| `schema_version` | yes | string | `1.0.0` 固定 |
| `run_id` | no | string | 呼び出し側が与えない場合は内部生成可 |
| `mode` | yes | string | `roadmap` 固定 |
| `response_language` | no | string | 未指定時は入力言語を踏襲、判定不能なら `ja` |
| `problem_statement` | yes | object | 1 件のみ |
| `insights` | yes | array | 1 件以上 |
| `constraints` | yes | array | 1 件以上 |
| `available_assets` | yes | array | 1 件以上 |
| `known_failures` | no | array | 過去失敗の再発防止に使う |
| `evidence_refs` | no | array | エビデンス参照 |
| `notes` | no | array | 補助メモ |
| `priority_hint` | no | string | `urgent` `high` `medium` `low` |
| `assumptions` | no | array | 明示的前提 |

### 3.2 Request normalization rules

- 空白だけの文字列は無効
- `insights` `constraints` `available_assets` は順序を保ったまま扱う
- `importance` や `severity` がない場合は内部既定値を使ってよいが、レスポンスで捏造した事実として扱わない

### 3.3 Upstream artifact normalization

`insight-agent` の `output_schema_v2` を受ける場合、planner 本体へ渡す前に以下の正規化を行う。

- `problem_statement.problem_id`: `problems[0].id` があれば `pb_` prefix を維持して再利用し、なければ `pb_from_insight` 系で生成する
- `problem_statement.title`: `problems[0].problem_type` または artifact の主題を短く整形して作る
- `problem_statement.statement`: `problems[0].statement` を優先し、欠ける場合は `reasoning_summary.headline` を使う
- `insights[*]`: `insights[*].id` と `statement` を移し、`support_bundle` や `confidence` は `source` や `notes` 側へ要約する
- `constraints[*]`: `risk_notes[*].statement`、`open_questions[*].statement`、`reasoning_summary.what_remains_open[*]` から hard/soft を判断して組み立てる
- `available_assets[*]`: artifact 自体、元 PDF、参照 repo、利用 Skill を document / dataset / skill として列挙する
- `evidence_refs[*]`: `evidence_id` と `quote` を短い要約へ変換し、`kind=document` を基本とする

生の `nodes[*]` や `routing_plan` を request schema の新規 field として露出させない。MVP では planner が必要とする計画材料だけを抽出し、それ以外は `notes` に寄せる。

## 4. Response Contract

### 4.1 Top-level fields

以下の top-level fields は常に返す。

- `schema_version`
- `run`
- `problem_definition`
- `success_criteria`
- `hypotheses`
- `solution_options`
- `experiment_plan`
- `roadmap`
- `risks`
- `fallback_options`
- `next_actions`
- `open_questions`
- `assumptions`
- `failures`
- `confidence`

### 4.2 `run`

`run.status` は以下の意味を持つ。

- `completed`: 十分な計画が組めた
- `partial`: 一部は組めたが、不足情報や不確実性が高い
- `failed`: 構造化レスポンスは返したが、計画としては成立しない

### 4.3 `problem_definition`

- `scope` は今回扱う境界を 1 文以上で固定する
- `non_goals` は今回やらないことを列挙する
- `derived_from` は `insight_id` `constraint_id` `ref_id` のいずれかを含む

### 4.4 `success_criteria`

正常系では少なくとも 1 件を返す。

`verification_method` は以下のいずれかの観点を含む。

- schema validation
- fixture validation
- manual review
- prototype execution
- experiment result

### 4.5 `hypotheses`

- priority は `1` が最優先
- `related_insight_ids` は 1 件以上を推奨
- `related_constraint_ids` は relevant であれば付与する
- 1 件だけしか出せない場合は `open_questions` へ不足理由を出す

### 4.6 `solution_options`

- `completed` では `recommended=true` をちょうど 1 件にする
- `partial` または `failed` では 0 件または 1 件
- `tradeoffs` は空にしない
- `addresses_hypothesis_ids` は hypothesis と整合する

### 4.7 `experiment_plan`

- `depends_on` は先行 experiment の ID のみ参照する
- `estimated_effort` は `0.5d` `1d` のような短い表現を使う
- `failure_signal` は、実験が不成立だと判断する条件を明示する

### 4.8 `roadmap`

- `order` は 1 から始まる連番
- `tasks` は deliverable ベースで書く
- roadmap の最初の phase にある task が `next_actions` の出発点になる

### 4.9 `next_actions`

`next_actions` は以下の優先順で並べる。

1. schema / fixture 固定
2. 核となる planner 実装
3. wrapper 接続
4. 契約テスト

### 4.10 `failures` と `open_questions`

- `failures` は「現時点で成立しない理由」
- `open_questions` は「成立させるために埋めるべき不明点」

両者は混同しない。

### 4.11 `confidence`

- `score` は総合信頼度
- `reason` は 1 文から 3 文で、何が score を押し上げ / 押し下げたかを述べる

## 5. 生成規則

### 5.1 課題再定義規則

- 元の `statement` を単に短く言い換えない
- 実装可能な対象境界を 1 つに絞る
- 境界外は `non_goals` へ出す

### 5.2 仮説規則

- 仮説は「なぜ前進できそうか」を含む
- 証明できない信念文にしない
- 似た仮説を重複させない

### 5.3 実験規則

- 1 実験 1 目的を原則とする
- `success_condition` と `failure_signal` は両方必要
- 実験は phase 1 または phase 2 で消化できる単位に寄せる

### 5.4 ロードマップ規則

- phase 1 は contract / scope 固定を含める
- phase 2 は core planner を含める
- phase 3 以降で wrapper や周辺機能を扱う

## 6. Validation & Error Contracts

### 6.1 `validate` result

`validate` は `validation-result.schema.json` 準拠の JSON を返す。

- `valid=true`: request schema に適合
- `valid=false`: request schema に不適合
- `errors[*]`: `code`, `field`, `message` を持つ
- `warnings[*]`: 正規化時の補足や非致命の注意を持てる

### 6.2 Error envelope

`run` の hard validation error、または `run` / `validate` の内部障害では response schema ではなく `error.schema.json` 準拠の envelope を返す。

最低限以下を持つ。

- `schema_version`
- `error_code`
- `message`
- `details`
- `trace_id`

## 7. ラッパー別仕様

### 7.1 CLI

- 入力は file path または stdin
- `run` の出力は file path または stdout
- `validate` は `validation-result.schema.json` 準拠の JSON を stdout へ返す
- `run` の validation error は stderr へ error envelope を出し、exit code `1`
- `validate` の invalid request は validation result を返し、exit code `1`
- processing error は stderr へ error envelope を出し、exit code `2`

### 7.2 HTTP API

- `:plan` の request / response body shape は request / response schema と一致
- `:validate` は常に `validation-result.schema.json` を返す
- `:plan` の validation error は `400`
- `:validate` の invalid request は `200` で `valid=false` を返す
- processing failure は `422` または `500` を使い分ける

### 7.3 MCP

- tool 名は `roadmap.plan` `roadmap.validate` `roadmap.schema`
- `roadmap.plan` は request schema を入力にし、response schema を返す
- `roadmap.validate` は request schema を入力にし、`validation-result.schema.json` を返す
- 内部障害時のみ error envelope を返す

## 8. 互換性ポリシー

- 同一 major version 内では必須 field を削除しない
- field rename は major update 扱い
- enum の追加は minor update で許容

## 9. 実装前に最低限確認すること

- `schemas/` と `examples/` が相互に通る
- requirements と interfaces の field 名が一致している
- sync MVP の境界が保たれている
- `examples/request.from_insight_agent.json` で upstream 連携の写像例が確認できる







