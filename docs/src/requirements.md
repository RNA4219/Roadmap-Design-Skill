# Roadmap Design Skill Requirements

## 1. 目的

Roadmap Design Skill は、上流工程で得られた課題候補、気づき、制約、利用可能資産を入力として受け取り、実装と検証に着手できる構造化ロードマップを生成する。

このツールの責務は「課題をどう解くかの設計」に限定する。

## 2. 背景

課題候補は、そのままでは問題提起や論点整理に留まりやすい。実際に着手できる計画へ変換するには、課題を再定義し、仮説を立て、検証順と実装順を持つ工程へ分解する必要がある。

Roadmap Design Skill はこの変換を担う中核コンポーネントであり、文章のもっともらしさではなく、後工程で再利用できる構造化情報を返す。

## 3. スコープ

### 3.1 対象

- 単一の `problem_statement`
- 課題に紐づく `insights`
- 制約条件
- 利用可能な技術 / 資料 / 人的資産
- 既知の失敗知見
- 補助的なエビデンス参照
- 実装と検証に使う短中期ロードマップ

### 3.2 対象外

- 課題発見そのもの
- 検索や情報収集
- 実験の自動実行
- 実装コードの自動生成
- UI の自動生成
- 外部システムとの同期
- 長期 run store を前提とした永続化
- 複数課題の一括計画

## 4. 今回固定する前提

### R-01 1 リクエスト 1 課題

MVP では `problem_statement` は 1 件のみ扱う。複数課題の束ねや優先順位調整は上流工程の責務とする。

### R-02 同期実行を正本とする

MVP は同期 `run` と `validate` を正式機能とする。非同期実行や run 参照 API は将来拡張扱いとし、現時点では実装必須にしない。

### R-03 契約は versioned である

request / response / error には必ず `schema_version` を持たせる。初版は `1.0.0` とする。

### R-04 出力は入力に根拠を持つ

問題再定義、仮説、解決方針は、可能な限り `insight_id` `constraint_id` `ref_id` のいずれかへ trace できること。

### R-05 計画不能も正規出力で返す

十分な計画が組めない場合でも、空疎な成功レスポンスを捏造せず、`failures` `open_questions` `fallback_options` を返す。

## 5. 入力要件

### 5.1 必須入力

- `schema_version`
- `mode`
- `problem_statement`
- `insights`
- `constraints`
- `available_assets`

### 5.2 `problem_statement`

`problem_statement` は以下を必須とする。

- `problem_id`
- `title`
- `statement`

任意:

- `background`
- `desired_outcome`

### 5.3 `insights`

`insights` は 1 件以上の配列であること。

各要素は以下を持つ。

- `insight_id`
- `statement`

任意:

- `source`
- `importance`

### 5.4 `constraints`

`constraints` は 1 件以上の配列であること。

各要素は以下を持つ。

- `constraint_id`
- `category`
- `statement`
- `severity`

`category` は以下を推奨する。

- `time`
- `resource`
- `technology`
- `team`
- `compliance`
- `other`

`severity` は以下を推奨する。

- `hard`
- `soft`

### 5.5 `available_assets`

`available_assets` は 1 件以上の配列であること。

各要素は以下を持つ。

- `asset_id`
- `type`
- `name`
- `description`

`type` は以下を推奨する。

- `component`
- `dataset`
- `document`
- `skill`
- `people`
- `other`

### 5.6 任意入力

- `run_id`
- `response_language`
- `known_failures`
- `evidence_refs`
- `notes`
- `priority_hint`
- `assumptions`

### 5.7 入力の補助要件

- `mode` は `roadmap` 固定
- `response_language` 未指定時は入力言語を踏襲し、判定不能なら `ja`
- `priority_hint` は `urgent` `high` `medium` `low` のいずれか
- 任意入力が欠けていても hard validation error にしない

## 6. 出力要件

### 6.1 正規出力

レスポンスは JSON を正規形式とし、以下の top-level key を持つ。

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

### 6.2 `run`

`run` は最低限以下を持つ。

- `run_id`
- `mode`
- `status`
- `created_at`
- `updated_at`
- `planner_version`
- `response_language`

`status` は以下を持てる。

- `completed`
- `partial`
- `failed`

### 6.3 `problem_definition`

以下を必須とする。

- `problem_id`
- `title`
- `statement`
- `scope`
- `non_goals`
- `derived_from`

### 6.4 `success_criteria`

`success_criteria` は配列とし、各要素は以下を持つ。

- `criterion_id`
- `statement`
- `verification_method`
- `priority`

要件:

- 正常系では 1 件以上返す
- 検証方法を持つ
- 願望だけで終わらない

### 6.5 `hypotheses`

各要素は以下を持つ。

- `hypothesis_id`
- `statement`
- `why_this_might_work`
- `priority`
- `related_insight_ids`
- `related_constraint_ids`
- `status`

要件:

- 正常系では 2 件以上返す
- 検証可能な表現にする
- `status` は `open` `success` `failure` `inconclusive` のいずれか

### 6.6 `solution_options`

各要素は以下を持つ。

- `option_id`
- `title`
- `summary`
- `addresses_hypothesis_ids`
- `tradeoffs`
- `recommended`

### 6.7 `experiment_plan`

各要素は以下を持つ。

- `experiment_id`
- `title`
- `goal`
- `verifies_hypothesis_ids`
- `method`
- `success_condition`
- `failure_signal`
- `depends_on`
- `estimated_effort`

要件:

- 仮説と紐付く
- 依存関係が自己循環しない
- 小さく試せる単位に寄せる

### 6.8 `roadmap`

`roadmap` は phase 配列とし、各 phase は以下を持つ。

- `phase_id`
- `order`
- `title`
- `goal`
- `exit_criteria`
- `tasks`

`tasks[*]` は以下を持つ。

- `task_id`
- `title`
- `description`
- `deliverable`
- `depends_on`

要件:

- phase は依存順または時系列順
- 各 phase は task を 1 件以上持つ
- phase 1 に着手可能な `next_actions` と整合する

### 6.9 `risks`

各要素は以下を持つ。

- `risk_id`
- `statement`
- `severity`
- `mitigation`

### 6.10 `fallback_options`

各要素は以下を持つ。

- `fallback_id`
- `trigger`
- `statement`
- `tradeoff`

### 6.11 `next_actions`

`next_actions` は構造化オブジェクト配列とする。

各要素は以下を持つ。

- `action_id`
- `title`
- `description`
- `deliverable`
- `depends_on`

要件:

- 正常系では 3 件以上を推奨
- 直近で着手可能なものを優先
- deliverable が明示される

### 6.12 `open_questions`

各要素は以下を持つ。

- `question_id`
- `statement`
- `blocking`
- `affects`

### 6.13 `failures`

各要素は以下を持つ。

- `failure_id`
- `type`
- `summary`
- `recoverable`

`type` は以下を推奨する。

- `input_gap`
- `scope_error`
- `planning_blocker`
- `internal_error`

### 6.14 `confidence`

`confidence` は以下を持つ。

- `score`
- `reason`

要件:

- `score` は 0.0 以上 1.0 以下
- 失敗や未解決事項を隠すために使わない

## 7. 機能要件

### F-01 課題再定義

- 広すぎる課題は scope を絞る
- 絞れない部分は `open_questions` へ逃がす
- `non_goals` を明示し、扱わない境界を固定する

### F-02 成功条件生成

- 成功条件を検証可能な単位で返す
- 少なくとも 1 件は具体的確認方法を持つ

### F-03 仮説生成

- 複数仮説を生成する
- 優先度を付ける
- 入力 insight / constraint と紐づける

### F-04 解決方針候補生成

- 複数方針を比較可能な形で返す
- `tradeoffs` を持つ
- 少なくとも 1 つに `recommended=true` を付けられる

### F-05 実験計画生成

- 仮説ごとに検証手段を割り当てる
- 成功条件と失敗シグナルを持つ
- 小さく始められる順に並べる

### F-06 ロードマップ生成

- phase 単位で整理する
- phase は実装順または依存順で並ぶ
- deliverable ベースの task を返す

### F-07 リスク / フォールバック生成

- リスクは mitigation を持つ
- フォールバックは trigger と tradeoff を持つ
- 詰まったときの次善策を示す

### F-08 次アクション生成

- 直近で着手可能な作業を返す
- Task Seed や Issue に転記しやすい粒度にする

### F-09 構造化出力

- 同一 schema を CLI / HTTP API / MCP で利用できる
- JSON Schema で検証可能である

### F-10 安定順序

- `hypotheses` `experiment_plan` `roadmap` `next_actions` の順序は入力が同じなら極端にぶれない
- ID prefix は固定する

## 8. バリデーション要件

### V-01 Hard validation error

以下は hard error とする。

- `schema_version` 不一致
- `mode` 不一致
- `problem_statement.statement` 欠落
- `insights` 空配列
- `constraints` 空配列
- `available_assets` 空配列

### V-02 Soft planning failure

以下は structured response で返す。

- 課題が広すぎて安定した計画を作れない
- 制約が相互矛盾している
- 利用可能資産が曖昧すぎて進行案を固定できない

### V-03 Error envelope

hard error 時は別途 `error.schema.json` に準拠した error envelope を返す。

## 9. 非機能要件

### N-01 薄いラッパー構成

- CLI / HTTP API / MCP は薄いラッパー
- 業務ロジックは `roadmap_core` に集約

### N-02 単一利用前提

- 自分用ツールを前提とする
- 認証、権限分離、マルチテナントは対象外

### N-03 純粋性優先

- `roadmap_core` は入出力の純粋性を優先する
- 永続化の有無に依存しない

### N-04 安定性

- 同一入力に対して過度に不安定な出力を避ける
- 不明点は無理に埋めない

### N-05 可観測性

- `run_id` を持つ
- `planner_version` を返す
- 失敗時も構造化情報を保持する

### N-06 保守性

- 上流の課題発見ロジックと混在させない
- schema と examples を回帰テストの起点にできる

### N-07 セキュリティ / 取り扱い

- 外部送信を前提としない
- notes や evidence をログへ全文転記しない
- 将来ログを持つ場合も最小限の要約に留める

## 10. ID / 命名規則

- `problem_id`: `pb_`
- `criterion_id`: `sc_`
- `hypothesis_id`: `hy_`
- `option_id`: `op_`
- `experiment_id`: `exp_`
- `phase_id`: `ph_`
- `task_id`: `tk_`
- `risk_id`: `rk_`
- `fallback_id`: `fb_`
- `action_id`: `na_`
- `question_id`: `oq_`
- `failure_id`: `fl_`

## 11. MVP 受け入れ条件

- 1 件の `problem_statement` から structured response を返せる
- 正常系で 2 件以上の仮説を返せる
- 仮説ごとに experiment を紐づけられる
- roadmap が phase 単位で返る
- next_actions が成果物単位になっている
- 計画不能時に `failures` と `open_questions` を返せる
- request / response / error が schema validation を通る

## 12. 将来拡張

- 非同期 submit / status
- run store
- 複数課題バッチ
- 外部連携
- 長期改善ループ
