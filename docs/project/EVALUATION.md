# EVALUATION

## 1. 受け入れ基準

### A-01 最小入力の受理

- 必須項目だけの request が schema validation を通る
- `problem_definition` `hypotheses` `roadmap` `next_actions` を含む response を返せる

### A-02 仮説の複数性

- 正常系では `hypotheses` を 2 件以上返せる
- 各 hypothesis に優先順位と根拠参照がある

### A-03 実験と仮説の対応

- `experiment_plan[*].verifies_hypothesis_ids` が空にならない
- 実験の依存関係が自己循環しない

### A-04 ロードマップの実行可能性

- roadmap が phase 単位で並ぶ
- 各 phase に task が 1 件以上ある
- `next_actions` が roadmap の初期 phase と整合する

### A-05 計画不能時の安全性

- 広すぎる課題では、見かけだけ整った roadmap を返さない
- `failures` `open_questions` `fallback_options` を返せる
- `confidence.score` が低くなる

### A-06 I/F 契約の一貫性

- CLI / HTTP / MCP が同一 request / response / validation-result schema を参照する
- `run` の validation error で `error.schema.json` に準拠する
- `validate` の invalid request で `validation-result.schema.json` に準拠する

## 2. 契約テスト観点

- `examples/request.minimal.json` が request schema を通る
- `examples/request.full.json` が request schema を通る
- `examples/request.from_insight_agent.json` が request schema を通る
- `examples/response.success.json` が response schema を通る
- `examples/response.failure.json` が response schema を通る
- `examples/validation.success.json` が validation-result schema を通る
- `examples/validation.failure.json` が validation-result schema を通る

## 3. レビュー観点

- requirements と specification の用語が一致しているか
- 永続化不要という前提と I/F が矛盾していないか
- `next_actions` が抽象論ではなく成果物ベースになっているか
- `failures` と error envelope の役割が分離されているか
- `validate` と `run` で invalid input の返却契約が混線していないか
- 将来拡張と MVP 境界が混ざっていないか

## 4. 実装時の最低テストセット

- request の hard validation
- broad problem の soft failure
- stable ordering
- schema version mismatch
- empty insight / empty constraint / empty asset の拒否
- traceability field の保持
- insight-agent artifact から request schema への写像確認
- `validate` success / failure fixture の契約確認
