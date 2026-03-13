---
intent_id: RDS-001
owner: roadmap-design-skill
status: active
last_reviewed_at: 2026-03-13
next_review_due: 2026-04-13
---

# TASK.requirements-alignment-03-13-2026

## メタデータ

```yaml
task_id: 20260313-01
repo: https://github.com/owner/roadmap-design-skill
base_branch: main
work_branch: codex/rds-requirements-alignment
priority: P1
langs: [python]
```

## Objective

要件・仕様・schema の不一致を解消し、`validate` / `run` の契約を実装と動作確認まで進められる形に固定する。

## Scope

- In: `docs/src/**`, `schemas/**`, `examples/**`, `src/roadmap_core/**`, `src/wrappers/**`, `tests/**`
- Out: 非同期 run store、複数課題バッチ、外部連携

## Requirements

- Behavior:
  - `validate` が `validation-result.schema.json` 準拠の結果を返す
  - `run` は従来どおり `roadmap-response.schema.json` または `error.schema.json` を返す
  - `solution_options.recommended` の件数規則が status ごとに一貫する
  - `insight-agent` 正規化入力から `run` / `validate` の両方を確認できる
- I/O Contract:
  - Input: `roadmap-request.schema.json`, `examples/request.from_insight_agent.json`
  - Output: `roadmap-response.schema.json`, `validation-result.schema.json`, `error.schema.json`
- Constraints:
  - 同期 MVP・単一課題境界を維持する
  - `roadmap_core` と wrapper の責務分離を崩さない
  - docs / schema / examples / 実装 / tests の順で差分を揃える
- Acceptance Criteria:
  - docs/src, interfaces, schemas, examples の契約が相互に矛盾しない
  - `validate` の valid/invalid fixture が schema validation を通る
  - 実装後に CLI / HTTP / MCP の `validate` が同じ shape を返す
  - `run` の invalid input と `validate` の invalid input の返却挙動が区別される

## Affected Paths

- `docs/src/requirements.md`
- `docs/src/specification.md`
- `docs/src/interfaces.md`
- `schemas/roadmap-request.schema.json`
- `schemas/roadmap-response.schema.json`
- `schemas/validation-result.schema.json`
- `schemas/error.schema.json`
- `examples/request.from_insight_agent.json`
- `examples/validation.success.json`
- `examples/validation.failure.json`
- `src/roadmap_core/**`
- `src/wrappers/**`
- `tests/**`

## Plan

### Steps

1. 文書契約を固定する
2. `validation-result.schema.json` と validate fixture を追加する
3. `roadmap_core` に validate path と error path の分岐を実装する
4. CLI / HTTP / MCP wrapper で `run` と `validate` の返却契約を分離する
5. contract / unit / integration test を追加して invalid input の振る舞いを固定する
6. `examples/request.from_insight_agent.json` を使った動作確認を行う

## Tests

### Outline

- Contract:
  - request / response / validation-result / error の schema validation
  - `examples/request.from_insight_agent.json` の validate success
  - 欠損 request に対する validate failure fixture
- Unit:
  - `recommended` 件数規則の status 別確認
  - `run` と `validate` の error routing 分離
- Integration:
  - CLI `validate` が `valid=false` を返すケース
  - CLI `run` が invalid input で error envelope を返すケース
  - HTTP / MCP の `validate` が同一 shape を返すケース

## Commands

### Run gates

- `python -m pytest -q`
- `python -m json.tool examples/request.from_insight_agent.json > NUL`
- `python -m json.tool examples/validation.success.json > NUL`
- `python -m json.tool examples/validation.failure.json > NUL`

## Notes

### Rationale

- validate 契約を別 schema として固定すると、`run` の error envelope と責務が分離される。
- upstream 正規化例を fixture 化すると、`insight-agent` 連携の回帰確認がしやすい。

### Risks

- 既存実装が `validate` でも error envelope を返す前提だと wrapper 修正が必要になる。
- `recommended` 件数規則を厳密化すると、既存 fixture の更新が波及する可能性がある。

### Follow-ups

- `validation-result.schema.json` を README / HUB / CHECKLISTS にも展開する
- 実装完了後に CHANGELOG へ反映する
