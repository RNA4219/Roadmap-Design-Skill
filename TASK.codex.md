---
intent_id: RDS-001
owner: roadmap-design-skill
status: active
last_reviewed_at: 2026-03-10
next_review_due: 2026-04-10
---

# Task Seed Template

Roadmap Design Skill 向けのタスクシードテンプレート。

## メタデータ

```yaml
task_id: YYYYMMDD-xx
repo: https://github.com/owner/roadmap-design-skill
base_branch: main
work_branch: feat/short-slug
priority: P1|P2|P3
langs: [auto]   # auto | python | typescript | go | rust | etc.
```

## Objective

{{一文で目的}}

## Scope

- In: {{対象(ディレクトリ/機能/CLI)を箇条書き}}
- Out: {{非対象(触らない領域)を箇条書き}}

## Requirements

- Behavior:
  - {{期待挙動1}}
  - {{期待挙動2}}
- I/O Contract:
  - Input: {{型/例}}
  - Output: {{型/例}}
- Constraints:
  - 既存契約(schema)破壊なし / 不要な依存追加なし
  - Lint/Type/Test はゼロエラー
  - MVP 境界（同期実行・単一課題）を維持
- Acceptance Criteria:
  - {{検収条件1}}
  - {{検収条件2}}

## Affected Paths

- {{glob例: schemas/**, examples/**, src/roadmap_core/**, src/wrappers/**}}

## Local Commands（存在するものだけ実行）

```bash
## Python
ruff check . && black --check . && mypy --strict . && pytest -q

## TypeScript/Node
pnpm lint && pnpm typecheck && pnpm test
npm run lint && npm run typecheck && npm test

## JSON Schema Validation
ajv validate -s schemas/roadmap-request.schema.json -d examples/request.minimal.json
ajv validate -s schemas/roadmap-response.schema.json -d examples/response.success.json

## Fallback
make ci || true
```

## Deliverables

- PR: タイトル/要約/影響/ロールバックに加え、本文へ `Intent: RDS-xxx` と `## EVALUATION` アンカーを明記
- Artifacts: 変更パッチ、テスト、必要ならREADME/CHANGELOG差分

---

## Plan

### Steps

1) 現状把握（対象ファイル列挙、既存テストとI/O確認）
2) 小さな差分で仕様を満たす実装
3) sample::fail の再現手順/前提/境界値を洗い出し、必要な工程を増補
4) テスト追加/更新（先に/同時）
5) コマンド群でゲート通過
6) ドキュメント最小更新（必要なら）

## Patch

***Provide a unified diff. Include full paths. New files must be complete.***

## Tests

### Outline

- Unit:
  - {{case-1: 入力→出力の最小例}}
  - {{case-2: エッジ/エラー例}}
- Integration:
  - {{代表シナリオ1つ}}
- Contract:
  - {{schema validation 例}}

## Commands

### Run gates

- （上の "Local Commands" から該当スタックを選んで実行）

## Notes

### Rationale

- {{設計判断を1～2行}}

### Risks

- {{既知の制約/互換性リスク}}

### Follow-ups

- {{後続タスクあれば}}

## MVP 実装用の具体化

### Phase 1: 契約固定タスク

```yaml
task_id: 20260310-01
objective: JSON Schema 契約の固定
scope:
  in: [schemas/, examples/]
  out: [src/]
requirements:
  behavior:
    - examples が schema validation を通る
  constraints:
    - schema_version を 1.0.0 とする
acceptance_criteria:
  - ajv validate が全 examples で成功
```

### Phase 2: コア実装タスク

```yaml
task_id: 20260310-02
objective: roadmap_core の最小実装
scope:
  in: [src/roadmap_core/]
  out: [src/wrappers/]
requirements:
  behavior:
    - valid request から valid response を返せる
    - invalid request に対して error.schema.json 準拠の応答を返せる
  constraints:
    - 同期実行のみ
    - 1リクエスト1課題
acceptance_criteria:
  - EVALUATION.md の A-01～A-06 を満たす
```

### Phase 3: ラッパー実装タスク

```yaml
task_id: 20260310-03
objective: CLI/HTTP/MCP ラッパーの実装
scope:
  in: [src/wrappers/]
  out: [src/roadmap_core/]
requirements:
  behavior:
    - 各ラッパーが同一 request/response schema を使用
  constraints:
    - ラッパーは薄く、業務ロジックは roadmap_core のみ
acceptance_criteria:
  - CLI / HTTP / MCP が同一契約を使用している
```