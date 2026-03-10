## 1. 目的

Roadmap Design Skill は、課題候補・気づき・制約条件を入力として受け取り、実行可能な R&D 計画を JSON で返す。

本ツールは以下を構造化して出力する。

- problem_definition
- success_criteria
- hypotheses
- solution_options
- experiment_plan
- roadmap
- risks
- fallback_options
- next_actions

本ツールは単体の planner として振る舞い、検索・課題発見・永続化・外部連携は責務外とする。

---

## 2. 設計原則

- 入力は JSON を正とする
- 出力は JSON を正とする
- CLI / API / MCP は薄いラッパーにする
- 業務ロジックは `roadmap_core` に集約する
- 単発実行を正本とする
- 不足情報は無理に補完せず `open_questions` に逃がす
- 計画不能時はそれを構造化して返す

---

## 3. 用語

- `run`: 1回の処理実行単位
- `problem_statement`: 入力課題
- `problem_definition`: 再定義後の課題
- `hypothesis`: 検証可能な仮説
- `solution_option`: 解決方針候補
- `experiment`: 検証の最小単位
- `roadmap_phase`: フェーズ化された工程
- `risk`: 想定リスク
- `fallback`: 代替案
- `next_action`: 直近の具体作業

---

## 4. 共通データモデル

## 4.1 RunMeta

```json
{
  "run_id": "run_01HXXXXXXX",
  "mode": "roadmap",
  "status": "completed",
  "created_at": "2026-03-10T12:00:00Z",
  "updated_at": "2026-03-10T12:00:20Z"
}
````

## 4.2 ProblemStatement

```json
{
  "problem_id": "pb_001",
  "title": "Lack of long-horizon evaluation",
  "statement": "The approach may not generalize to long-running agent workflows."
}
```

## 4.3 InsightItem

```json
{
  "insight_id": "in_001",
  "statement": "The core gap is not retrieval quality itself but persistence under multi-step tasks."
}
```

## 4.4 ConstraintSet

```json
{
  "time_budget_days": 7,
  "resource_budget": "single developer",
  "stack": ["python", "sqlite", "mcp"]
}
```

## 4.5 AvailableAssets

```json
{
  "components": [
    "open_deep_search",
    "learn-claude-code"
  ],
  "notes": [
    "thin wrapper architecture",
    "single-user tool"
  ]
}
```

## 4.6 ErrorModel

```json
{
  "error_code": "INVALID_INPUT",
  "message": "problem_statement.statement is required",
  "details": {
    "field": "problem_statement.statement"
  }
}
```

---

## 5. Request Schema

Roadmap Design Skill の基本リクエストは以下とする。

```json
{
  "run_id": "optional",
  "mode": "roadmap",
  "problem_statement": {
    "problem_id": "pb_001",
    "title": "Lack of long-horizon evaluation",
    "statement": "The approach may not generalize to long-running agent workflows."
  },
  "insights": [
    {
      "insight_id": "in_001",
      "statement": "The core gap is not retrieval quality itself but persistence under multi-step tasks."
    }
  ],
  "constraints": {
    "time_budget_days": 7,
    "resource_budget": "single developer",
    "stack": ["python", "sqlite", "mcp"]
  },
  "available_assets": {
    "components": ["open_deep_search", "learn-claude-code"],
    "notes": ["thin wrapper architecture"]
  },
  "known_failures": [
    "large integrated OSS tends to blur ownership"
  ],
  "evidence_refs": [
    "ev_001"
  ],
  "notes": [
    "MVP first"
  ],
  "priority_hint": "medium",
  "assumptions": [
    "single-user use case"
  ]
}
```

---

## 6. Response Schema

Roadmap Design Skill の基本レスポンスは以下とする。

```json
{
  "run": {
    "run_id": "run_01HYYYYYYY",
    "mode": "roadmap",
    "status": "completed",
    "created_at": "2026-03-10T12:00:00Z",
    "updated_at": "2026-03-10T12:00:20Z"
  },
  "problem_definition": {
    "problem_id": "pb_001",
    "statement": "Long-running agent workflows lack stable evaluation and planning boundaries.",
    "scope": "roadmap generation for research-core MVP"
  },
  "success_criteria": [
    "problem is narrowed to an implementable scope",
    "at least two testable hypotheses are produced",
    "roadmap is broken into executable phases"
  ],
  "hypotheses": [
    {
      "hypothesis_id": "hy_001",
      "statement": "Separating insight and roadmap stages will improve planning stability.",
      "why_this_might_work": "Responsibility boundaries become clearer.",
      "priority": 1,
      "status": "open"
    },
    {
      "hypothesis_id": "hy_002",
      "statement": "Contract-first design will reduce downstream drift.",
      "why_this_might_work": "Input and output become stable before implementation.",
      "priority": 2,
      "status": "open"
    }
  ],
  "solution_options": [
    {
      "option_id": "op_001",
      "title": "Two-core thin-wrapper design",
      "summary": "Keep roadmap_core pure and wrappers minimal."
    }
  ],
  "experiment_plan": [
    {
      "experiment_id": "exp_001",
      "title": "Freeze JSON contracts",
      "goal": "stabilize I/O before coding",
      "input": ["problem_statement", "insights"],
      "method": "define request/response schema and validate examples",
      "success_condition": "sample requests produce valid structured outputs",
      "depends_on": []
    },
    {
      "experiment_id": "exp_002",
      "title": "Implement roadmap_core skeleton",
      "goal": "verify phase/task generation",
      "input": ["problem_definition", "constraints"],
      "method": "generate hypotheses, experiments, roadmap",
      "success_condition": "returns at least 2 hypotheses and 3 next actions",
      "depends_on": ["exp_001"]
    }
  ],
  "roadmap": [
    {
      "phase": 1,
      "title": "Contract first",
      "tasks": [
        "freeze requirements.md",
        "freeze interfaces.md",
        "prepare example request/response fixtures"
      ]
    },
    {
      "phase": 2,
      "title": "Core implementation",
      "tasks": [
        "implement problem redefinition",
        "implement hypothesis generation",
        "implement experiment planning"
      ]
    },
    {
      "phase": 3,
      "title": "Wrapper integration",
      "tasks": [
        "add CLI entrypoint",
        "add HTTP API surface",
        "add MCP tool interface"
      ]
    }
  ],
  "risks": [
    {
      "risk_id": "rk_001",
      "statement": "The problem may remain too broad and produce vague plans."
    }
  ],
  "fallback_options": [
    {
      "fallback_id": "fb_001",
      "statement": "Reduce scope and regenerate roadmap with a narrower problem statement."
    }
  ],
  "next_actions": [
    "write models for request and response",
    "implement problem_definition generation",
    "implement hypothesis schema validation"
  ],
  "open_questions": [
    {
      "question_id": "oq_001",
      "statement": "What is the smallest acceptable unit for one experiment?"
    }
  ],
  "assumptions": [
    "single-user local development"
  ],
  "failures": [],
  "confidence": 0.79
}
```

---

## 7. 出力フィールド詳細

## 7.1 problem_definition

課題の再定義結果。

必須:

* `problem_id`
* `statement`

任意:

* `scope`

## 7.2 success_criteria

前進判定に使う条件群。

* 配列で返す
* 1件以上必須
* 検証可能な表現にする

## 7.3 hypotheses

仮説群。

各要素は以下を持つ。

* `hypothesis_id`
* `statement`
* `why_this_might_work`
* `priority`
* `status`

`status` は以下を推奨する。

* `open`
* `success`
* `failure`
* `inconclusive`

## 7.4 solution_options

解決方針候補。

各要素は以下を持つ。

* `option_id`
* `title`
* `summary`

## 7.5 experiment_plan

実験計画。

各要素は以下を持つ。

* `experiment_id`
* `title`
* `goal`
* `input`
* `method`
* `success_condition`
* `depends_on`

## 7.6 roadmap

フェーズ化された工程。

各要素は以下を持つ。

* `phase`
* `title`
* `tasks`

## 7.7 risks

想定リスク。

各要素は以下を持つ。

* `risk_id`
* `statement`

## 7.8 fallback_options

代替案。

各要素は以下を持つ。

* `fallback_id`
* `statement`

## 7.9 next_actions

直近で着手可能な作業。

* 文字列配列で返す
* 3件以上推奨

## 7.10 open_questions

不明点や追加確認事項。

各要素は以下を持つ。

* `question_id`
* `statement`

## 7.11 failures

計画不能・入力不足・不安定出力などを構造化して返す。

各要素は以下を持つ。

* `failure_id`
* `type`
* `summary`

例:

```json
{
  "failure_id": "fl_001",
  "type": "problem_too_broad",
  "summary": "The problem statement is too broad to derive a stable roadmap."
}
```

---

## 8. 最低限の必須条件

リクエストで必須なのは以下。

* `mode`
* `problem_statement.statement`
* `insights`
* `constraints`
* `available_assets`

レスポンスで必須なのは以下。

* `run`
* `problem_definition`
* `success_criteria`
* `hypotheses`
* `roadmap`
* `next_actions`

---

## 9. バリデーションルール

* `mode` は `roadmap` 固定
* `problem_statement.statement` は空文字不可
* `insights` は空配列可だが推奨しない
* `hypotheses` は最低 2 件以上を推奨
* `roadmap` は phase 単位で返す
* `next_actions` は最低 1 件以上必須
* 計画不能時は `failures` または `open_questions` を返す
* 無理に空疎な roadmap を生成しない

---

## 10. CLI Interface

## 10.1 コマンド

* `tool roadmap run --input <file> --output <file>`
* `tool roadmap validate --input <file>`

## 10.2 入力例

```bash
tool roadmap run --input ./input/problem_a.json --output ./out/roadmap_a.json
tool roadmap validate --input ./input/problem_a.json
```

## 10.3 CLI 振る舞い

* 標準出力は最小限
* 本体結果は JSON ファイルまたは stdout に出す
* 異常時は ErrorModel を stderr に出す
* exit code:

  * `0`: success
  * `1`: validation error
  * `2`: processing error

---

## 11. HTTP API Interface

## 11.1 Endpoint

* `POST /v1/roadmap/run`
* `POST /v1/roadmap/validate`
* `GET /v1/runs/{run_id}`
* `GET /v1/runs/{run_id}/result`

## 11.2 Content-Type

* request: `application/json`
* response: `application/json`

## 11.3 POST /v1/roadmap/run

Request body は本 `Request Schema` に従う。
Response body は本 `Response Schema` に従う。

---

## 12. MCP Tool Interface

## 12.1 tools

* `roadmap.plan`
* `roadmap.validate`
* `roadmap.status`
* `roadmap.result`

## 12.2 入出力

MCP の入出力は HTTP API と同一 JSON schema を使う。

---

## 13. 非同期実行

MVPでは単発同期実行を正本とする。
将来的に非同期実行へ拡張する場合、以下を使う。

### 13.1 Submit Response

```json
{
  "run_id": "run_01HZZZZZZZ",
  "status": "queued"
}
```

### 13.2 Status Response

```json
{
  "run_id": "run_01HZZZZZZZ",
  "mode": "roadmap",
  "status": "running"
}
```

非同期は外側の制御責務であり、`roadmap_core` 自体は同期関数的に扱う。

---

## 14. 失敗時レスポンス例

```json
{
  "run": {
    "run_id": "run_01HFAIL001",
    "mode": "roadmap",
    "status": "completed",
    "created_at": "2026-03-10T12:00:00Z",
    "updated_at": "2026-03-10T12:00:05Z"
  },
  "problem_definition": {
    "problem_id": "pb_001",
    "statement": "problem statement remains too broad"
  },
  "success_criteria": [],
  "hypotheses": [],
  "solution_options": [],
  "experiment_plan": [],
  "roadmap": [],
  "risks": [
    {
      "risk_id": "rk_001",
      "statement": "No testable boundary was defined."
    }
  ],
  "fallback_options": [
    {
      "fallback_id": "fb_001",
      "statement": "Refine the problem statement before roadmap generation."
    }
  ],
  "next_actions": [
    "narrow the scope of the problem statement",
    "provide at least one concrete constraint",
    "retry roadmap generation"
  ],
  "open_questions": [
    {
      "question_id": "oq_001",
      "statement": "What concrete boundary should this roadmap target?"
    }
  ],
  "failures": [
    {
      "failure_id": "fl_001",
      "type": "problem_too_broad",
      "summary": "A stable roadmap could not be generated from the current input."
    }
  ],
  "confidence": 0.24
}
```

---

## 15. MVP境界

MVPでは以下を優先する。

* 単一 `problem_statement` を受ける
* 構造化された roadmap JSON を返す
* failure / open_questions を返せる
* CLI / API / MCP で同一 schema を使う

MVPでは以下を対象外とする。

* 外部検索
* 課題発見
* 永続化
* 外部システム同期
* UI
* 高度な最適化