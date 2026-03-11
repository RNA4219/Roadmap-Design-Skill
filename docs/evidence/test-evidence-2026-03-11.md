# Test Evidence

Test execution results for Roadmap-Design-Skill verification.

## Execution Summary

| Item | Result |
|------|--------|
| Date | 2026-03-11 |
| Platform | Windows 10 (win32) |
| Python | 3.10.6 |
| pytest | 8.3.5 |
| Total Tests | 31 |
| Passed | 31 |
| Failed | 0 |
| Duration | 0.37s |

## Test Categories

### Contract Tests (6 tests)

Tests that validate JSON Schema compliance.

| Test | Status |
|------|--------|
| test_request_minimal_valid | PASSED |
| test_request_full_valid | PASSED |
| test_response_success_valid | PASSED |
| test_response_failure_valid | PASSED |
| test_error_schema_has_required_fields | PASSED |
| test_error_sample_valid | PASSED |

### Integration Tests (4 tests)

End-to-end tests for the complete pipeline.

| Test | Status |
|------|--------|
| test_valid_request_produces_valid_response | PASSED |
| test_response_status_consistency | PASSED |
| test_experiments_verify_hypotheses | PASSED |
| test_roadmap_phase_ordering | PASSED |

### Unit Tests - CLI (4 tests)

| Test | Status |
|------|--------|
| test_defaults_to_deterministic_when_env_unset | PASSED |
| test_env_can_enable_llm | PASSED |
| test_no_llm_flag_wins_over_env_default | PASSED |
| test_llm_flag_enables_immediately | PASSED |

### Unit Tests - LLM Planner (10 tests)

| Test | Status |
|------|--------|
| test_plan_without_llm_returns_baseline | PASSED |
| test_is_llm_available_false_without_config | PASSED |
| test_is_llm_available_true_with_mock | PASSED |
| test_plan_async_without_llm | PASSED |
| test_planner_version_includes_llm | PASSED |
| test_default_config_has_none_provider | PASSED |
| test_from_env_defaults | PASSED |
| test_from_env_respects_enable_var | PASSED |
| test_openai_config_from_env | PASSED |
| test_alibaba_config_from_env | PASSED |

### Unit Tests - Planner (5 tests)

| Test | Status |
|------|--------|
| test_plan_returns_response | PASSED |
| test_plan_generates_hypotheses | PASSED |
| test_plan_generates_roadmap | PASSED |
| test_plan_handles_broad_problem | PASSED |
| test_next_actions_are_structured | PASSED |

### Unit Tests - Validators (2 tests)

| Test | Status |
|------|--------|
| test_valid_request_passes | PASSED |
| test_empty_insights_fails | PASSED |

## CLI Verification

### Minimal Request

```bash
python -m wrappers.cli.main -i examples/request.minimal.json
```

**Result:** OK - Generated valid roadmap response with `status: "completed"`

### Full Request

```bash
python -m wrappers.cli.main -i examples/request.full.json
```

**Result:** OK - Generated valid roadmap response with hypotheses, solution options, and roadmap phases

## HTTP API Verification

Server started on `http://127.0.0.1:8765`

### Health Check

```bash
curl http://127.0.0.1:8765/health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "llm_enabled": false,
  "llm_provider": "none"
}
```

### Run Endpoint

```bash
curl -X POST http://127.0.0.1:8765/v1/run \
  -H "Content-Type: application/json" \
  -d @examples/request.minimal.json
```

**Result:** OK - HTTP 200, valid roadmap JSON response

### Validate Endpoint

```bash
curl -X POST http://127.0.0.1:8765/v1/validate \
  -H "Content-Type: application/json" \
  -d @examples/request.minimal.json
```

**Response:**
```json
{
  "valid": true,
  "errors": []
}
```

## Fixes Applied

### pyproject.toml

Added missing hatch build configuration:

```toml
[tool.hatch.build.targets.wheel]
packages = ["src/roadmap_core", "src/wrappers"]
```

This was required for editable installation (`pip install -e .[dev]`) to succeed.

## Conclusion

All 31 tests pass. CLI and HTTP API endpoints function correctly. The Roadmap-Design-Skill is ready for use.