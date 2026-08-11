# CP2 Runtime Evidence

Date: 2026-08-11

## Langfuse configuration

API `/health` returned:

```json
{
  "ok": true,
  "tracing_enabled": true,
  "incidents": {
    "rag_slow": false,
    "tool_fail": false,
    "cost_spike": false
  }
}
```

## Load test

Command:

```bash
python scripts/load_test.py
```

Result: 10/10 sample requests returned HTTP 200.

Correlation IDs generated:

- `req-49cb23e7`
- `req-dee54c0a`
- `req-7c3704dc`
- `req-42836c0f`
- `req-2a2aa589`
- `req-4445eff6`
- `req-679067d2`
- `req-946bbd39`
- `req-f12bd48c`
- `req-8de615fb`

## Metrics snapshot

Command:

```bash
curl http://localhost:8000/metrics | python -m json.tool
```

Snapshot after load test:

```json
{
  "traffic": 10,
  "latency_p50": 1064.0,
  "latency_p95": 1118.0,
  "latency_p99": 1118.0,
  "avg_cost_usd": 0.002,
  "total_cost_usd": 0.0201,
  "tokens_in_total": 330,
  "tokens_out_total": 1271,
  "error_rate_pct": 0.0,
  "error_breakdown": {},
  "quality_avg": 0.88
}
```

## Dashboard validator

Command:

```bash
python scripts/validate_dashboard.py
```

Result:

```text
HỢP LỆ: 6/6 panel có trong dashboard contract.
```

## Required screenshots to add

Add these files after opening the Langfuse Cloud project:

- `submission/evidence/cp2_langfuse_trace_list.png`: trace list showing at least 10 traces.
- `submission/evidence/cp2_langfuse_waterfall.png`: one trace waterfall showing the parent `chat-response` span and child spans such as `rag-retrieval` and `llm-generation`.
