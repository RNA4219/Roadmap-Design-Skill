---
intent_id: RDS-002
owner: roadmap-design-skill
status: proposed
last_reviewed_at: 2026-03-14
next_review_due: 2026-03-28
---

# 実装ブラッシュアップタスクプラン

## Objective

MVP の契約を崩さずに、`validate` 契約、schema 配布、workflow 判定後入力契約、examples 同期、wrapper 名称一致を実装し、README どおりに再現できる状態へ引き上げる。

## 背景

現状はロードマップ生成自体は動くが、次のズレが残っている。

- `validation-result.schema.json` は追加済みだが、wrapper 実装がまだ完全追従していない
- `docs/src/interfaces.md` と CLI / HTTP / MCP の名称・endpoint が一致していない
- README と interfaces が参照する example fixture の一部が未整備または運用ルール化されていない
- workflow 判定後に渡す planning-ready 条件が文書上の規約に留まっている

## 追加要件トレース

- BR-01: `validate` 契約の完全実装
- BR-02: schema 配布 I/F の実装
- BR-03: workflow 判定後入力契約の明文化
- BR-04: examples / artifacts / contract test の同期
- BR-05: wrapper 契約の名称一致

## Scope

- In:
  - `src/roadmap_core/validators/**`
  - `src/roadmap_core/models/**`
  - `src/wrappers/cli/**`
  - `src/wrappers/http/**`
  - `src/wrappers/mcp/**`
  - `schemas/**`
  - `examples/**`
  - `docs/src/interfaces.md`
  - `README.md`
  - `tests/**`
- Out:
  - 非同期 run store
  - 認証 / 認可
  - LLM 推論品質そのものの改善
  - 複数課題バッチ入力

## 実装方針

1. contract を先に統一する
2. wrapper は薄いままにして、validation serialization と schema 配布は共通化する
3. examples は README 用と contract test 用を分離せず、同じ fixture を使う
4. `insight-agent` 連携の判定と request 組み立ては workflow 側に残し、planner 本体の責務を増やしすぎない

## フェーズ別タスク

### Phase 0: broken reference 修復

- `examples/request.ai_agent_builder.json` を examples に復元する
- `examples/request.from_insight_agent.json` を examples に追加する
- `examples/validation.success.json` と `examples/validation.failure.json` を追加する
- README / EVALUATION / specification が参照する fixture を先に実在状態へ揃える

Acceptance:

- README と EVALUATION の参照パスがすべて存在する
- contract test の前提 fixture が欠けていない

### Phase 1: `validate` 契約統一

- `SchemaValidator` に validation-result schema 読み込みを追加する
- validation issue 正規化関数を追加し、`code`, `field`, `message` へ落とす
- CLI に `validate` サブコマンドを追加する
- HTTP `POST /v1/roadmaps:validate` を interfaces 契約どおりに揃える
- MCP `roadmap.validate` を契約どおりに揃える

Acceptance:

- invalid request で CLI / HTTP / MCP が同じ shape を返す
- validation result が `schemas/validation-result.schema.json` を通る

### Phase 2: schema 配布 I/F 実装

- CLI に `schema --kind ...` を追加する
- HTTP に `GET /v1/roadmaps:schema/{kind}` を追加する
- MCP に `roadmap.schema` を追加する
- schema kind の不正値は error envelope で返す

Acceptance:

- 4 種類の schema が wrapper ごとに取得できる
- 取得した schema 本文が `schemas/` の内容と一致する

### Phase 3: workflow 判定後入力契約の固定

- insight-agent を含む上流 artifact は参考例に留め、直接入力契約から外す
- planning-ready 条件を README / requirements / specification / interfaces / runbook に反映する
- request.from_insight_agent.json は workflow 判定後の request 例として維持する

Acceptance:

- 文書間で workflow 判定後の入力条件が一致している
- AI エージェント sample と workflow 判定後 sample の両方が README から辿れる

### Phase 4: examples / artifacts / test 同期

- README 参照ファイルをすべて実在状態にする
- validation success / failure fixture を examples に追加する
- contract test を README 参照 examples まで拡張する
- artifact 再生成コマンドを task doc か README に残す

Acceptance:

- `pytest` が examples の欠落なしで通る
- README に書いたコマンドで sample を再生成できる

### Phase 5: wrapper 名称整理

- CLI command 名を interfaces と一致させる
- HTTP endpoint 名を interfaces と一致させる
- MCP tool 名を `roadmap.plan`, `roadmap.validate`, `roadmap.schema` に揃える
- 必要なら互換 alias を短期的に残すが、README では正規名だけを案内する

Acceptance:

- interfaces.md と実装の名称が一致する
- wrapper ごとの snapshot test か integration test を追加する

## 推奨タスク分割

### Task 0

- Title: broken reference 修復
- Priority: P1
- Deliverables:
  - restored example fixtures
  - README / EVALUATION path sync
  - contract test preconditions

### Task 1

- Title: `validate` 契約統一
- Priority: P1
- Deliverables:
  - validation serializer
  - CLI / HTTP / MCP validate 実装
  - validation fixture tests

### Task 2

- Title: schema 配布 I/F 実装
- Priority: P1
- Deliverables:
  - schema loader utility
  - CLI / HTTP / MCP schema endpoint/tool
  - schema retrieval tests

### Task 3

- Title: workflow 判定後入力契約の固定
- Priority: P2
- Deliverables:
  - planning-ready contract updates
  - maintained examples/request.from_insight_agent.json
  - docs consistency checks

### Task 4

- Title: examples と README の同期
- Priority: P2
- Deliverables:
  - missing fixtures restoration
  - README command refresh
  - sample regeneration notes

### Task 5

- Title: wrapper 契約名の最終整理
- Priority: P3
- Deliverables:
  - renamed commands / endpoints / tool names
  - compatibility notes
  - integration tests

## 実行コマンド

```powershell
$env:PYTHONPATH='src'
pytest
python -m wrappers.cli.main --help
python -m wrappers.cli.main validate -i examples/request.full.json
python -m wrappers.cli.main schema --kind response
```

## リスク

- wrapper 名称変更は既存利用手順とのズレを生むため、互換 alias の扱いを先に決める必要がある
- `insight-agent` 側 schema 変更の影響を本リポジトリへ持ち込まないため、workflow 境界を明確に保つ必要がある
- examples を増やすほど maintenance cost が上がるため、README 導線と contract fixture を同一化して二重管理を避ける

## 推敲後の結論

最優先は broken reference の修復で、その直後に `validate` 契約統一へ進む順が妥当である。今すでに README と EVALUATION が fixture の存在を前提にしているため、入口を直してから contract と schema 配布 I/F を固めるほうが、レビューと実装の両方で手戻りが少ない。




