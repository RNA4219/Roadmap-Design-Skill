---
intent_id: RDS-002
owner: roadmap-design-skill
status: active
last_reviewed_at: 2026-03-14
next_review_due: 2026-03-28
---

# 実装ブラッシュアップタスクプラン

## Objective

MVP の契約を崩さずに、`validate` 契約、schema 配布、workflow 判定後入力契約、examples 同期、wrapper 名称一致を運用可能な状態へ保ちつつ、再利用性と互換方針を明確化する。

## 背景

現状は core / wrapper / examples が一通りそろっており、次は再利用性と運用明確化を詰める段階にある。

- `validate` 契約と schema 配布 I/F は実装済み
- workflow 判定後入力契約は文書へ反映済み
- README と examples の導線も成立している
- 残件は Skill 化、進捗文書の更新、legacy alias 方針の明文化である

## 追加要件トレース

- BR-01: `validate` 契約の完全実装
- BR-02: schema 配布 I/F の実装
- BR-03: workflow 判定後入力契約の明文化
- BR-04: examples / artifacts / contract test の同期
- BR-05: wrapper 契約の名称一致
- BR-06: request 組み立て手順の Skill 化
- BR-07: legacy alias 方針の明文化

## Scope

- In:
  - `skills/**`
  - `docs/src/interfaces.md`
  - `docs/project/EVALUATION.md`
  - `docs/tasks/implementation-brushup-2026-03-14.md`
  - `README.md`
- Out:
  - 非同期 run store
  - 認証 / 認可
  - LLM 推論品質そのものの改善
  - 複数課題バッチ入力

## フェーズ別タスク

### Phase 1: `validate` 契約統一

- CLI / HTTP / MCP で `validation-result.schema.json` 準拠結果を返す
- invalid request と internal error の返却経路を分離する

Acceptance:

- invalid request で CLI / HTTP / MCP が同じ shape を返す
- validation result が `schemas/validation-result.schema.json` を通る
- Status: completed

### Phase 2: schema 配布 I/F 実装

- CLI に `schema --kind ...` を追加する
- HTTP に `GET /v1/roadmaps:schema/{kind}` を追加する
- MCP に `roadmap.schema` を追加する

Acceptance:

- 4 種類の schema が wrapper ごとに取得できる
- 取得した schema 本文が `schemas/` の内容と一致する
- Status: completed

### Phase 3: workflow 判定後入力契約の固定

- insight-agent を含む上流 artifact は参考例に留め、直接入力契約から外す
- planning-ready 条件を README / requirements / specification / interfaces / runbook に反映する
- request.from_insight_agent.json は workflow 判定後の request 例として維持する

Acceptance:

- 文書間で workflow 判定後の入力条件が一致している
- AI エージェント sample と workflow 判定後 sample の両方が README から辿れる
- Status: completed

### Phase 4: examples / artifacts / test 同期

- README 参照ファイルをすべて実在状態にする
- validation success / failure fixture を examples に追加する
- contract test を README 参照 examples まで拡張する

Acceptance:

- `pytest` が examples の欠落なしで通る
- README に書いたコマンドで sample を再生成できる
- Status: completed

### Phase 5: wrapper 名称整理

- CLI / HTTP / MCP の正規名を interfaces と一致させる
- 互換 alias は短期維持の対象として扱う

Acceptance:

- interfaces.md と実装の名称が一致する
- wrapper ごとの互換疎通が test で固定されている
- Status: in_progress

### Phase 6: request 組み立て手順の Skill 化

- workflow 判定後 request の組み立て手順を repo 内 skill として切り出す
- `insight-agent` 直接入力ではなく planning-ready request を作ることを Skill に明記する
- README から skill へ到達できるようにする

Acceptance:

- repo 内に再利用可能な SKILL.md が存在する
- README から skill 導線が辿れる
- Status: completed

### Phase 7: legacy alias 方針の明文化

- interfaces / evaluation / task plan に alias の扱いを追記する
- 正規名のみを案内する方針を README と矛盾しない形で固定する

Acceptance:

- alias の扱いが docs 間で矛盾しない
- 正規名と互換 alias の役割が明確に分かる
- Status: completed

## 推奨タスク分割

### Task 5

- Title: wrapper 契約名の最終整理
- Priority: P2
- Deliverables:
  - canonical names only in docs
  - compatibility aliases in implementation
  - integration tests for alias retention

### Task 6

- Title: request 組み立て手順の Skill 化
- Priority: P2
- Deliverables:
  - repo local skill
  - README skill link
  - planning-ready workflow guide

### Task 7

- Title: legacy alias 方針の明文化
- Priority: P2
- Deliverables:
  - interfaces compatibility policy
  - evaluation check update
  - task plan sync

## 実行コマンド

```powershell
$env:PYTHONPATH='src'
pytest
python -m wrappers.cli.main validate -i examples/request.from_insight_agent.json
python -m wrappers.cli.main schema --kind request
```

## リスク

- wrapper 名称変更は既存利用手順とのズレを生むため、互換 alias の扱いを先に決める必要がある
- `insight-agent` 側 schema 変更の影響を本リポジトリへ持ち込まないため、workflow 境界を明確に保つ必要がある
- Skill と README の導線が二重化すると保守コストが上がるため、役割を明確に分ける必要がある

## 推敲後の結論

今後の優先順は、`wrapper 名称整理` を続けつつ、repo local skill を入口にして planning-ready request の再利用性を上げ、legacy alias は docs 上で役割を固定してから縮退させるのが妥当である。
