# Roadmap Design Skill Interfaces

## 1. 方針

外部インターフェースはすべて同一 contract を共有する。正本は以下の schema とする。

- `schemas/roadmap-request.schema.json`
- `schemas/roadmap-response.schema.json`
- `schemas/error.schema.json`

## 2. CLI Interface

### 2.1 Commands

- `roadmap-skill run --input <file> --output <file>`
- `roadmap-skill validate --input <file>`
- `roadmap-skill schema --kind request|response|error`

### 2.2 CLI behavior

- `run`: request schema に従う JSON を受け、response schema に従う JSON を返す
- `validate`: request schema の妥当性だけを検証する
- `schema`: 正規 schema の内容を表示または書き出す

### 2.3 Exit codes

- `0`: success
- `1`: validation error
- `2`: processing error

## 3. HTTP API Interface

### 3.1 Endpoints

- `POST /v1/roadmaps:plan`
- `POST /v1/roadmaps:validate`
- `GET /v1/roadmaps:schema/{kind}`

### 3.2 Notes

- 永続化前提の `GET /v1/runs/{run_id}` 系は MVP では提供しない
- `:plan` は同期レスポンスのみを返す

### 3.3 Status codes

- `200`: successful response
- `400`: validation error
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
- output: validation result または `error.schema.json`

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
- 正常系 response: `examples/response.success.json`
- 失敗系 response: `examples/response.failure.json`
