# Roadmap Design Skill

## 1. 目的

Roadmap Design Skill は、Insight Agent などの上流工程で得られた課題候補・気づき・制約条件を入力として受け取り、課題を実行可能な R&D 計画へ変換することを目的とする。

本ツールの役割は、単なる提案文の生成ではなく、以下を構造化して返すことである。

- 課題定義
- 成功条件
- 仮説
- 解決方針候補
- 実験計画
- ロードマップ
- リスク
- フォールバック
- 次アクション

Roadmap Design Skill は「課題をどう解くか」を設計することに専念する。

## 2. 背景

上流工程で発見された課題候補は、そのままでは問題提起に留まりやすい。  
実際に開発や検証へ進めるためには、課題を再定義し、仮説を立て、検証可能な工程へ分解する必要がある。

Roadmap Design Skill はこの変換を担う中核コンポーネントであり、曖昧な課題から次に動ける計画を生成する。

## 3. スコープ

### 3.1 対象

Roadmap Design Skill が扱う対象は以下とする。

- 課題候補
- 気づきや論点
- 制約条件
- 利用可能な技術・資産
- 既知の失敗知見
- 補助的なメモや注記

### 3.2 対象外

以下は本ツールの責務外とする。

- 課題発見そのもの
- 検索や情報収集
- 実験の自動実行
- 自動実装
- UI 生成
- 外部ストレージへの永続化
- 外部システムとの連携
- 多段解析そのもの

## 4. 役割

Roadmap Design Skill は、入力された課題をそのまま受け流すのではなく、次の段階を担う。

- 課題を扱える単位に再定義する
- 成功条件を明確化する
- 複数の仮説を立てる
- 仮説を検証可能な実験へ落とす
- 実装・検証順に工程を分解する
- リスクと代替案を明示する
- 直近で着手すべき作業を出す

## 5. 入力要件

### 5.1 必須入力

Roadmap Design Skill は最低限、以下を受け取る。

#### problem_statement
- problem_id
- title
- statement

#### insights
- 課題に紐づく気づき、論点、示唆

#### constraints
- 期間制約
- リソース制約
- 技術制約
- 開発体制制約

#### available_assets
- 利用可能な技術要素
- 既存コンポーネント
- 実装に使える前提条件

### 5.2 任意入力

必要に応じて以下を受け取れるものとする。

- known_failures
- evidence_refs
- notes
- priority_hint
- assumptions

## 6. 出力要件

Roadmap Design Skill は JSON を正規出力形式とし、最低限以下を返す。

- problem_definition
- success_criteria
- hypotheses
- solution_options
- experiment_plan
- roadmap
- risks
- fallback_options
- next_actions

必要に応じて以下を含めてもよい。

- open_questions
- assumptions
- failures
- confidence

## 7. 機能要件

### F-01 課題再定義

入力された課題候補を、実験や実装に耐える課題定義へ再構成すること。

要件:
- 課題が広すぎる場合はスコープを絞る
- 不明瞭な場合は曖昧さを残したまま open_questions に分離する
- 課題定義は扱える境界を持つこと

### F-02 成功条件の明確化

課題に対して、何をもって前進とみなすかを列挙すること。

要件:
- success_criteria は検証可能であること
- 少なくとも 1 つ以上は具体的な確認条件を含むこと
- 理念や願望だけで終わらないこと

### F-03 仮説生成

課題に対して複数の仮説を生成すること。

要件:
- 仮説は最低 2 件以上出力できること
- 仮説は検証可能な形で記述されること
- 各仮説に優先度または順序付けができること
- 1案決め打ちにしないこと

### F-04 解決方針候補の生成

仮説群を踏まえて、実装または検証の方針候補を生成すること。

要件:
- solution_options を 1 件以上出力できること
- 各 option は要約を持つこと
- option 同士の違いが分かること

### F-05 実験計画生成

仮説を PoC や検証可能な最小単位へ分解すること。

要件:
- experiment ごとに目的を持つこと
- 実験は 1 回で試せる最小単位に寄せること
- 依存関係を表現できること
- 小さく始められる順序になっていること

### F-06 ロードマップ生成

工程を phase 単位で整理し、順序立てて出力すること。

要件:
- roadmap は phase 単位で構成されること
- 各 phase は tasks を持つこと
- phase は時系列または依存順に並んでいること
- 実行可能な粒度であること

### F-07 リスク生成

進行上のリスクを明示すること。

要件:
- risks を 1 件以上返せること
- 実装、設計、検証、運用のいずれかのリスクを表現できること
- 具体性があること

### F-08 フォールバック生成

失敗時や詰まり時の代替案を返すこと。

要件:
- fallback_options を 1 件以上返せること
- 現実的な次善策であること
- 計画不能時でも何を見直すべきかを示せること

### F-09 次アクション生成

直近で着手すべき作業を明示すること。

要件:
- next_actions を複数返せること
- 抽象論ではなく実作業単位であること
- すぐに着手可能な内容を含むこと

### F-10 構造化出力

全結果を機械可読な JSON で返すこと。

要件:
- 同一 schema を CLI / API / MCP で利用できること
- 後工程で検証可能であること
- JSON schema validation を前提にできること

## 8. 非機能要件

### N-01 薄いラッパー構成

- CLI / API / MCP は薄いラッパーとする
- 業務ロジックは `roadmap_core` に集約する

### N-02 単一利用前提

- 自分用ツールとして使う前提とする
- 認証やマルチテナントは対象外とする

### N-03 実行形態

- 単発実行を正本とする
- 必要に応じて非同期バッチに対応可能とする
- コアロジックは入出力の純粋性を優先する

### N-04 安定性

- 同一入力に対して極端に不安定な出力を避ける
- 不明な点を無理に補完しない
- 不足情報は open_questions へ逃がせること

### N-05 可観測性

- run_id を持てること
- 処理結果を status 付きで返せること
- 失敗時も構造化された応答を返せること

### N-06 保守性

- 責務が roadmap_core に閉じること
- 上流の課題発見ロジックと混ざらないこと
- 外部連携なしで単体テストしやすいこと

## 9. 失敗時要件

Roadmap Design Skill は、十分な計画を組めない場合でも結果を捨てない。

要件:
- failures を返せること
- open_questions を返せること
- fallback_options を返せること
- confidence を低くして返せること
- 無理にそれらしい計画を捏造しないこと

## 10. データ要件

最低限必要な識別子は以下とする。

- run_id
- problem_id
- hypothesis_id
- experiment_id
- option_id
- risk_id
- fallback_id

推奨 status は以下とする。

- queued
- running
- completed
- failed

必要に応じて出力内容の状態として以下を用いる。

- success
- failure
- inconclusive
- open

## 11. MVP 要件

### MVP-1
以下を返せること。

- problem_definition
- success_criteria
- hypotheses
- roadmap
- next_actions

### MVP-2
以下を追加する。

- solution_options
- experiment_plan
- risks
- fallback_options

### MVP-3
以下を追加する。

- failures
- open_questions
- confidence
- 非同期実行への対応準備

## 12. 受け入れ条件

Roadmap Design Skill は、以下を満たしたとき MVP として受け入れ可能とする。

- 1つの problem_statement から課題再定義を返せる
- 仮説を 2 件以上出せる
- 仮説ごとに experiment を紐づけられる
- roadmap を phase 単位で返せる
- risks と fallback_options を返せる
- 入力不足時に failures と open_questions を返せる
- JSON として機械可読である

## 13. 設計原則

- Roadmap Design Skill は「解決を設計する」ことに専念する
- 問題発見は別コンポーネントの責務とする
- 検索や取得は別工程とする
- コア価値は「仮説生成」と「工程分解」に置く
- 賢く見える文章より、再利用可能な構造を優先する
- 計画不能な場合は、不能な理由を返す

## 14. 現時点の判断

Roadmap Design Skill は、完成品を先に目指すのではなく、MVP として段階的に育てる前提で進める。  
まずは I/F と責務を固定し、実装しながら粒度や生成品質を調整する。