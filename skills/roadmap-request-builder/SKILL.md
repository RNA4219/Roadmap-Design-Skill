---
name: roadmap-request-builder
description: Build a planning-ready roadmap request from workflow-approved problem material and run Roadmap Design Skill validation or planning. Use when a user has already decided the case should be roadmaped, wants to assemble `problem_statement` / `insights` / `constraints` / `available_assets`, or wants to turn workflow output into `examples/request.from_insight_agent.json`-style input without adding upstream-specific adapter logic.
---

# Roadmap Request Builder

Roadmap Design Skill に渡す planning-ready request を組み立てる。

## 1. 読み順

1. `README.md`
2. `docs/src/requirements.md`
3. `docs/src/specification.md`
4. `docs/src/interfaces.md`
5. `docs/project/RUNBOOK.md`

## 2. やること

- workflow 側で「ロードマップ化してよい」と判定済みであることを確認する
- 1 件の `problem_statement` に対象を絞る
- `insights`, `constraints`, `available_assets` を最低 1 件ずつそろえる
- 未整理論点は `known_failures`, `evidence_refs`, `notes`, `assumptions` に退避する
- request を `validate` に通し、必要なら `run` まで確認する

## 3. やらないこと

- `insight-agent` など上流 artifact を直接入力として扱わない
- planner 本体に upstream 固有 shape を持ち込まない
- workflow 判定ロジックそのものをこの skill に入れない

## 4. 最小チェックリスト

- `mode` は `roadmap`
- `schema_version` は `1.0.0`
- `problem_statement` は 1 件
- `insights` は 1 件以上
- `constraints` は 1 件以上
- `available_assets` は 1 件以上

## 5. 実行コマンド

```powershell
$env:PYTHONPATH='src'
python -m wrappers.cli.main validate -i examples/request.from_insight_agent.json
python -m wrappers.cli.main run -i examples/request.from_insight_agent.json --no-llm
python -m wrappers.cli.main schema --kind request
```

## 6. 参考 fixture

- `examples/request.full.json`
- `examples/request.from_insight_agent.json`
- `examples/validation.success.json`
- `examples/validation.failure.json`
