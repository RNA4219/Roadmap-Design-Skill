# Roadmap Design Skill Interfaces

## 1. 方針

外部インターフェースはすべて同一 contract を共有する。正本は以下の schema とする。

- `schemas/roadmap-request.schema.json`
- `schemas/roadmap-response.schema.json`
- `schemas/validation-result.schema.json`
- `schemas/error.schema.json`

## 2. CLI Interface

### 2.1 Commands

- `roadmap-skill run --input <file> --output <file>`
- `roadmap-skill validate --input <file>`
- `roadmap-skill schema --kind request|response|validation-result|error`

### 2.2 CLI behavior

- `run`: request schema に従う JSON を受け、response schema に従う JSON を返す
- `validate`: request schema の妥当性だけを検証し、`validation-result.schema.json` 準拠の JSON を返す
- `schema`: 正規 schema の内容を表示または書き出す

### 2.3 Exit codes

- `0`: success (`run` 成功、または `validate` で `valid=true`)
- `1`: validation failed (`run` の validation error、または `validate` で `valid=false`)
- `2`: processing error

## 3. HTTP API Interface

### 3.1 Endpoints

- `POST /v1/roadmaps:plan`
- `POST /v1/roadmaps:validate`
- `GET /v1/roadmaps:schema/{kind}  # request | response | validation-result | error`

### 3.2 Notes

- 永続化前提の `GET /v1/runs/{run_id}` 系は MVP では提供しない
- `:plan` は同期レスポンスのみを返す

### 3.3 Status codes

- `200`: successful response、または `:validate` の validation result
- `400`: `:plan` validation error
- `422`: planning could not produce a viable roadmap but request was valid
- `500`: internal error

## 4. MCP Interface

### 4.1 Tools

- `roadmap.plan`
- `roadmap.validate`
- `roadmap.schema`

### 4.2 Tool contracts

#### `roadmap.plan`

- input: `roadmap-request.schema.json`
- output: `roadmap-response.schema.json`

#### `roadmap.validate`

- input: `roadmap-request.schema.json`
- output: `validation-result.schema.json`
- internal failure only: `error.schema.json`

#### `roadmap.schema`

- input:

```json
{
  "kind": "request"
}
```

- output: 指定された schema 本文

## 5. Error envelope

validation error と processing error では、以下の shape を使う。

```json
{
  "schema_version": "1.0.0",
  "error_code": "INVALID_INPUT",
  "message": "constraints must contain at least one item",
  "details": {
    "field": "constraints"
  },
  "trace_id": "trace_01J..."
}
```

## 6. サンプル参照

- 正常系 request: `examples/request.full.json`
- 最小 request: `examples/request.minimal.json`
- workflow 判定後 request: `examples/request.from_insight_agent.json`
- 正常系 response: `examples/response.success.json`
- 失敗系 response: `examples/response.failure.json`
- validate 成功: `examples/validation.success.json`
- validate 失敗: `examples/validation.failure.json`










