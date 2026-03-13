---
intent_id: RDS-001
owner: roadmap-design-skill
status: active
last_reviewed_at: 2026-03-10
next_review_due: 2026-04-10
---

# Guardrails & 行動指針

Roadmap Design Skill のリポジトリ運用時に守るべき原則と振る舞いを体系化する。

## 目的

- JSON Schema で定義された契約（request / response / error）を厳密に遵守する。
- 変更は最小差分で行い、後方互換性を維持する。破壊的変更は schema_version の更新で明示する。
- 応答は簡潔で実務に直結させ、冗長な説明や代替案の羅列は避ける。
- 実装時はテスト駆動開発を基本とし、テストを先に記述する。

## スコープとドキュメント

1. 目的を一文で定義し、曖昧な課題を実装可能な計画単位へ落とすことを明示する。
2. Scope を固定し、In/Out の境界を先に決めて記録する（`docs/project/BLUEPRINT.md` の「解くこと / 解かないこと」）。
3. I/O 契約（入力/出力の型・例）を `schemas/` と `docs/src/interfaces.md` に整理する。
4. Acceptance Criteria（検収条件）を `docs/project/EVALUATION.md` に列挙する。
5. 最小フロー（準備→実行→確認）を `docs/project/RUNBOOK.md` に記す。
6. `docs/HUB.codex.md` の自動タスク分割フローに従い、タスク化した内容を `TASK.*-MM-DD-YYYY` 形式の Task Seed へマッピングして配布する。
7. タスク自動生成ツールはドライランで JSON 出力を確認してから Issue 化する。
8. 完了済みタスクは `CHANGELOG.md` へ移し、履歴を更新する。
9. テスト/型/lint/CI の実行結果を確認し、`docs/project/CHECKLISTS.md` でリリース可否を判断する。

## 実装原則

- **型安全**：新規・変更シグネチャには必ず型を付与し、Optional/Union は必要最小限に抑える。
- **例外設計**：既存 errors 階層に合わせ、再試行可否を区別する。
- **後方互換**：CLI/JSON 出力は互換性を維持し、破壊的変更は schema_version の更新で段階移行する。
- **インポート順序**：標準ライブラリ→外部依存→内部モジュールの順で空行区切りとする。
- **副作用の隔離**：`roadmap_core` と `wrappers/` のレイヤ分離を尊重する。
- **スコープ上限**：1 回の変更は合計 100 行または 2 ファイルまで。本ループでは最優先の塊のみ対応する。単一ファイルが 400 行を超える場合は機能単位で分割を検討する。
- **細かな Lint エラー**はスコープ上限の例外とし、重大なルール逸脱のみを是正する。
- 公開 API や CLI を変更した場合のみ、差分に簡潔な Docstring/Usage 例を添付する。

## JSON Schema 契約の遵守

- `schemas/roadmap-request.schema.json` が request の正本。
- `schemas/roadmap-response.schema.json` が response の正本。
- `schemas/error.schema.json` がエラー応答の正本。
- `examples/` 配下の fixture は契約テストの基準。
- `schema_version` は `1.0.0` を初版とし、破壊的変更時は major を更新する。

## プロセスと自己検証

- 競合解消時は双方の意図を最小限で統合し、判断を `ノート→` に 1 行で記す。
- 差分提示前に lint/type/test をメンタルで実行し、グリーン想定の変更のみ提出する。
- 実行コストやレイテンシへの影響は ±5% 以内を目標とし、超過見込みの場合は `ノート→` に代替策を 1 行で示す。
- セキュリティ上、秘密情報は扱わず、必要な場合は `.env` やサンプル参照に限定する。

## MVP 固有の制約

- **1 リクエスト 1 課題**：`problem_statement` は 1 件のみ受ける。複数課題の束ね処理は将来拡張。
- **同期実行**：MVP は同期 `run` / `validate` のみを正式化し、非同期実行は将来拡張へ切り出す。
- **永続化なし**：run store は持たない。`GET /v1/runs/{run_id}` 系の I/F は MVP から除外。
- **同一契約**：CLI / HTTP / MCP が同一の request / response schema を参照する。

## 例外処理

- スコープ上限を超える作業が必要な場合は、作業を分割してタスク化を提案する。
- ドキュメント更新（例：`*.md`）については、ファイル数上限を例外的に適用せず、必要に応じて超過を許可する。
- 破壊的変更が不可避な場合は、schema_version の更新と移行期間を明記したメモを添付する。

## リマインダー

- 変更は常にテストから着手し、最小の成功条件を先に満たす。
- 全ての関係者が同じ期待値を共有できるよう、上記ドキュメントを更新し続ける。

## 出力契約

- **`plan`**：読み込んだファイルと対象範囲、抜粋理由、未読箇所の扱い。
- **`patch`**：変更対象ファイルの相対パスを先頭コメントで明記。
- **`tests`**：対象ノードの `tests/*` を参照して増補。存在しなければ最小サンプルを併記。
- **`commands`**：読込に使ったツールと再現手順を列挙。
- **`notes`**：鮮度判断、スコープ外ファイル、既知リスク。

<!-- guardrails:yaml
forbidden_paths:
  - "/schemas/core/**"
require_human_approval:
  - "/schemas/**"
slo:
  lead_time_p95_hours: 72
  mttr_p95_minutes: 60
  change_failure_rate_max: 0.10
-->
