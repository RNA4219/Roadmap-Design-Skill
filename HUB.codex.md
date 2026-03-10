---
intent_id: RDS-001
owner: roadmap-design-skill
status: active
last_reviewed_at: 2026-03-10
next_review_due: 2026-04-10
---

# HUB.codex.md

リポジトリ内の仕様・運用MDを集約し、エージェントがタスクを自動分割できるようにするハブ定義。

## 1. 目的

- リポジトリ配下の計画資料から作業ユニットを抽出し、優先度順に配列
- 生成されたタスクリストを `TASK.*-MM-DD-YYYY` 形式の Task Seed へマッピング
- MVP 実装への具体的な作業単位へ分解

## 2. 入力ファイル分類

| 分類 | ファイル | 優先順 | 備考 |
|------|----------|--------|------|
| Blueprint | `BLUEPRINT.md` | 高 | 最上位方針・解くこと/解かないこと |
| Runbook | `RUNBOOK.md` | 中 | 実装着手順・推奨レイアウト |
| Guardrails | `GUARDRAILS.md` | 高 | 全メンバー必読・行動指針 |
| Evaluation | `EVALUATION.md` | 中 | 受け入れ基準・検収条件 |
| Checklist | `CHECKLISTS.md` | 低 | リリース/レビュー確認項目 |
| Requirements | `docs/src/requirements.md` | 高 | 正式な要件定義 |
| Specification | `docs/src/specification.md` | 高 | 正規仕様 |
| Interfaces | `docs/src/interfaces.md` | 高 | CLI/HTTP/MCP 外部契約 |
| Schemas | `schemas/*.schema.json` | 高 | JSON Schema 契約 |
| Examples | `examples/*.json` | 中 | 正常系/失敗系サンプル |

補完資料一覧:

- `README.md`: リポジトリ概要と参照リンク
- `CHANGELOG.md`: 完了タスクと履歴の記録

更新日: 2026-03-10

## 3. 自動タスク分割フロー

1. **スキャン**: ルート配下を再帰探索し、Markdown front matter (`---`) を含むファイルを優先取得。
2. **ノード生成**: 各ファイルから `##` レベルの節をノード化し、`Priority` `Dependencies` などのキーワードを抽出。
3. **依存解決**: RUNBOOK.md の実装順（Step 1-5）に従い、依存関係を解析。
4. **粒度調整**: ノード内の ToDo / 箇条書きを単位作業へ分割し、`<= 0.5d` を目安にまとめ直し。
5. **テンプレート投影**: 各作業ユニットを `TASK.*-MM-DD-YYYY` 形式の Task Seed (`Objective` `Requirements` `Commands`) へ変換。
6. **出力整形**: 優先度、依存、担当の有無でソートし、GitHub Issue もしくは PR下書きとしてJSON/YAMLに整形。
7. **タスク化**: タスクは独立性が保てる粒度まで分割し、責務の重複を避ける。変更は小さく・短時間で終わるブランチとして切り、早めの rebase で常に最新に追従する。

## 4. MVP 実装へのマッピング

### Phase 1: 契約固定（RUNBOOK Step 1）

- `schemas/roadmap-request.schema.json` の作成/検証
- `schemas/roadmap-response.schema.json` の作成/検証
- `schemas/error.schema.json` の作成/検証
- `examples/request.minimal.json` の作成
- `examples/request.full.json` の作成
- `examples/response.success.json` の作成
- `examples/response.failure.json` の作成

### Phase 2: コア実装（RUNBOOK Step 2-3）

- `roadmap_core/models/` の実装
- `roadmap_core/validators/` の実装
- `roadmap_core/planner/` の実装
- `roadmap_core/presenters/` の実装

### Phase 3: ラッパー実装（RUNBOOK Step 4）

- `wrappers/cli/` の実装
- `wrappers/http/` の実装
- `wrappers/mcp/` の実装

### Phase 4: テスト・検証（RUNBOOK Step 5）

- 契約テストの実装
- 結合テストの実装
- 受け入れテストの実装

## 5. ノード抽出ルール

- Front matter内の `priority`, `owner`, `deadline` を最優先で採用
- 節タイトルに `[Blocker]` を含む場合は依存解決フェーズで最上位へ昇格
- 箇条書きのうち `[]` or `[ ]` 形式はチェックリスト扱い、`- [ ]` はタスク分解対象

### Task Status & Blockers

```yaml
許容ステータス（Allowed）
- `[]` or `[ ]` or `- [ ]`：未着手・未割り振り
- planned：バックログ。着手順待ち
- active：受付済/優先キュー入り（担当/期日が付いた状態）
- in_progress：着手中
- reviewing：見直し中（レビュー/ふりかえり/承認待ち）
- blocked：ブロック中（外的依存で進められない）
- done：完了

遷移例（標準）
planned → active → in_progress → reviewing → done
ブロック例（例外）
in_progress → blocked → in_progress（解除後に戻す）
```

## 6. 出力例（擬似）

```yaml
- task_id: 20260310-01
  source: RUNBOOK.md#Step-1
  objective: JSON Schema 契約の固定と fixture 整合確認
  scope:
    in: [schemas/, examples/]
    out: [src/]
  requirements:
    behavior:
      - examples が schema validation を通る
    constraints:
      - schema_version を 1.0.0 とする
  commands:
    - ajv validate -s schemas/roadmap-request.schema.json -d examples/request.minimal.json
  dependencies: []
```

## 7. 運用メモ

- タスク自動生成ツールはドライランでJSON出力を確認後にIssue化
- 生成後は `CHANGELOG.md` へ反映済みタスクを移すことで履歴が追える
- MVP 境界（同期実行・単一課題）を維持し、将来拡張を混在させない