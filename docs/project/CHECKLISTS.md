---
intent_id: RDS-001
owner: roadmap-design-skill
status: active
last_reviewed_at: 2026-03-10
next_review_due: 2026-04-10
---

# Checklists

Roadmap Design Skill のチェックリスト。

## Development

- `TASK.*` を起票・更新し、`docs/HUB.codex.md` の運用ルールに沿ってスコープとフォローアップを同期
- 着手前に `docs/project/BLUEPRINT.md` と `docs/project/GUARDRAILS.md` を読み合わせ、最小差分と既存ガードレールへ整合
- テストを先行させ、`docs/project/EVALUATION.md` で定義された受け入れ基準を完了
- JSON Schema 契約（`schemas/`）の変更は、`examples/` との整合確認を必須とする
- Runbook 連携が必要な作業は `docs/project/RUNBOOK.md` へ手順差分を反映し、参照リンクを Task Seed に追記
- MVP 境界（同期実行・単一課題・永続化なし）を維持し、将来拡張を混在させない

## Pull Request / Review

- 失敗させたテストが緑化する最小コミット単位を維持し、差分を可視化
- `CHANGELOG.md` の `[Unreleased]` に Task Seed 番号付きで成果を追記
- PR 説明欄から `docs/project/BLUEPRINT.md`・`docs/project/RUNBOOK.md`・`docs/project/EVALUATION.md` 等の参照先へ遷移できるようリンクを付す
- レビュー観点は `docs/project/EVALUATION.md` の「レビュー観点」と `docs/project/GUARDRAILS.md` を再確認
- ラベル運用・テンプレ遵守は `docs/HUB.codex.md` と `docs/tasks/TASK.codex.md` のタスク分割フローに合わせる
- CLI / HTTP / MCP が同一契約（schema）を使用していることを確認

## Release

- 実装・レビューの完了条件は「Development」「Pull Request / Review」を満たしていることを前提に進行
- 変更点の要約
- リリースノート（`CHANGELOG.md` など）へ必要最小の項目を追記
- 未反映の `TASK.*` が残っていないか確認し、成果を `[Unreleased]` へ通番付きで転記済みかチェック
- `schema_version` の更新が必要か確認し、破壊的変更の場合は major version を更新
- 新規 ADR を含むリリースでは `docs/ADR/` の索引更新を完了し、レビューフローで確認する
- 受け入れ基準（`docs/project/EVALUATION.md`）に対するエビデンス
- 影響範囲の再確認
- PR に `type:*` および `semver:*` ラベルを付与済み
- 配布物へ `LICENSE` / `NOTICE` を同梱済み

## Hygiene

- 命名・ディレクトリ整備
- ドキュメント差分反映
- 旧呼称の混入チェック（例: `rg "<旧ブランド名>"` など抽象化したキーワードで固有表現を検索し、現行ブランド以外の名称が残存していないか確認）
- `examples/` と `schemas/` の整合性確認
- 未使用の schema field や examples の削除

## MVP 固有チェック

- [ ] 1リクエスト1課題の境界を維持している
- [ ] 同期実行のみ（非同期 run store を追加していない）
- [ ] `GET /v1/runs/{run_id}` 系の I/F を追加していない
- [ ] CLI / HTTP / MCP が同一の request/response schema を使用している
- [ ] `roadmap_core` 以外に業務ロジックを追加していない
- [ ] `schema_version` を適切に設定している（初版: 1.0.0）
- [ ] `failures` / `open_questions` / `fallback_options` を適切に返している
- [ ] `next_actions` が構造化オブジェクト配列になっている
