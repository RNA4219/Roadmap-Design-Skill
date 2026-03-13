# Roadmap Design Skill

Roadmap Design Skill は、上流工程で見つかった課題候補、気づき、制約、利用可能資産を受け取り、実装と検証に着手できるロードマップへ再構成するための設計ツールです。

このリポジトリは `$agent-tools-hub` と `workflow-cookbook` の入口パターンを参照し、要件定義から仕様、I/F 契約、実装準備、評価基準までを一続きで読める構成へ整理しています。

## 現在の到達点

- 要件定義を再整理し、不足していた前提と判断基準を補完
- 仕様書を再作成し、MVP の正規契約を固定
- CLI / HTTP API / MCP の I/F を同期型 MVP に揃えて整理
- JSON Schema とサンプル入出力を追加し、実装前の契約テスト準備を完了
- 実装順序と受け入れ条件を `docs/project/RUNBOOK.md` / `docs/project/EVALUATION.md` に明記

## ルート構成と導線

ルート直下は README.md・設定ファイル・コード/データ用ディレクトリだけに絞り、運用ドキュメントは docs/ 配下へ整理しています。

- `docs/project/BLUEPRINT.md`: このツールが何を解くか、何を解かないか、今回補完した設計判断
- `docs/project/GUARDRAILS.md`: リポジトリ運用時に守るべき原則と振る舞い
- `docs/src/requirements.md`: 正式な要件定義
- `docs/src/specification.md`: 実装時に参照する正規仕様
- `docs/src/interfaces.md`: CLI / HTTP API / MCP の外部契約
- `schemas/`: request / response / validation-result / error の JSON Schema
- `examples/`: 正常系 / 失敗系のサンプル payload
- `docs/project/RUNBOOK.md`: 実装着手順、推奨レイアウト、作業順
- `docs/project/EVALUATION.md`: 受け入れ条件、契約テスト観点、レビュー観点
- `docs/HUB.codex.md`: タスク分割ハブ、自動タスク分割フロー
- `docs/tasks/TASK.codex.md`: タスクシードテンプレート
- `docs/tasks/implementation-brushup-2026-03-14.md`: 追加ブラッシュアップ要件を実装へ落とし込む次期タスクプラン`r`n- `skills/roadmap-request-builder/SKILL.md`: workflow 判定後の request 組み立てと validate/run の再利用 Skill
- `docs/project/CHECKLISTS.md`: Development / PR / Release / Hygiene チェックリスト

## 実行メモ

- CLI は既定で deterministic planner を使い、高速に応答します
- LLM 強化が必要なときだけ `python -m wrappers.cli.main --llm -i examples/request.full.json` のように明示してください
- CLI の既定を LLM にしたい場合は `RDS_CLI_USE_LLM=1` を設定できます
- HTTP API で LLM を使う場合は `RDS_HTTP_USE_LLM=1` を設定してください

## おすすめサンプル

「ある程度まともな要件定義を入れたときに、どんなロードマップが返るか」を見る入口として、AIエージェント構築を題材にしたサンプルを置いています。

- 要件テキスト: `docs/evidence/ai-agent-builder-brief-2026-03-14.md`
- 入力JSON: `examples/request.ai_agent_builder.json`
- 出力JSON: `examples/response.ai_agent_builder.json`
- 保存済み実行結果: `artifacts/response.ai_agent_builder.json`

再現コマンド:

```powershell
$env:PYTHONPATH='src'
python -m wrappers.cli.main -i examples\request.ai_agent_builder.json -o artifacts\response.ai_agent_builder.json --no-llm
```

このサンプルは「AIエージェントの作り方をロードマップで出す」ケースを想定し、MVP境界、契約分離、サンプル整備、評価導線まで含めた段階計画を返します。

## insight-agent との関係

insight-agent は課題候補と根拠を発見する上流、Roadmap Design Skill は workflow 側で「ロードマップ化する」と判定された後の入力だけを受ける下流です。

- insight-agent の output_schema_v2 は本ツールの直接入力ではありません
- 上位 workflow が、対象をロードマップ化すべきかを先に判定します
- 本ツールは schemas/roadmap-request.schema.json を満たす planning-ready な入力だけを受けます

planning-ready の最小条件は次のとおりです。

- 1 件の problem_statement に対象が絞られている
- insights, constraints, available_assets が最低 1 件ずつ揃っている
- 検討対象が「課題探索中」ではなく「計画化してよい」状態まで整理されている
- 未整理の論点は known_failures, evidence_refs, notes, assumptions に退避済みである

参考として、workflow 判定後の入力例は [examples/request.from_insight_agent.json](C:/Users/ryo-n/Codex_dev/Roadmap-Design-Skill/examples/request.from_insight_agent.json) を参照してください。元データの参考例は [insight-agent/artifacts/2512.14982v1.v2.json](C:/Users/ryo-n/Codex_dev/insight-agent/artifacts/2512.14982v1.v2.json) です。`r`n`r`nこの組み立て手順を繰り返し使う場合は [SKILL.md](/C:/Users/ryo-n/Codex_dev/Roadmap-Design-Skill/skills/roadmap-request-builder/SKILL.md) を使います。

## 環境設定

- ひな形は `.env.example` にあります
- Provider: `LLM_PROVIDER` で設定（openai, alibaba, local, none）
- OpenAI: `OPENAI_API_KEY` と `LLM_MODEL`（デフォルト: gpt-4o-mini）
- Alibaba: `DASHSCOPE_API_KEY` と `LLM_MODEL`（デフォルト: qwen-plus）
- 共通設定: `LLM_BASE_URL`, `LLM_TIMEOUT_SECONDS`, `LLM_MAX_TOKENS`, `LLM_TEMPERATURE`

## MVP の境界

- 1 回のリクエストで扱う `problem_statement` は 1 件
- 単発同期実行を正本とし、永続化付きの run store は持たない
- `roadmap_core` を唯一の業務ロジック層とし、CLI / API / MCP は薄いラッパーとする
- 入力不足や課題の広すぎる状態も、`failures` と `open_questions` を含む構造化レスポンスで返す

## 今回補完した重要事項

- `schema_version` を request / response / error すべてに導入
- `constraints` と `available_assets` をオブジェクト配列化し、後工程で追跡しやすくした
- `next_actions` を文字列配列から構造化オブジェクトへ変更し、実装準備に直結する形へ固定
- `GET /runs/{id}` 系の I/F は、永続化要件と矛盾するため MVP から除外
- 出力順序、ID 命名規則、信頼度表現、入力との traceability を明文化

## 次に読む順番

1. `README.md`
2. `docs/src/requirements.md`
3. `docs/src/specification.md`
4. `schemas/` と `examples/`
5. `docs/project/RUNBOOK.md`
6. `docs/project/EVALUATION.md`




