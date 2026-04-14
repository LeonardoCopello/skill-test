# Troubleshooting Guide

Common issues when querying New Relic via CLI or curl, their root causes, and how to fix them. Read this file when a query returns empty or unexpected results, or when you need to help debug data visibility issues.

---

## Quick Diagnostic Table

| Symptom | Likely Cause | Fix |
| --- | --- | --- |
| Error query returns empty | Wrong app name or app uses OTEL | Verify name with entity search. If not found, try `SELECT uniques(service.name) FROM Span` |
| OTEL error query returns empty | Service not sending OTEL data | Verify with `SELECT uniques(service.name) FROM Span WHERE otel.library.name IS NOT NULL` |
| NRQL returns 0 rows | Wrong event type or time range | Check if app uses APM (`Transaction`) or OTEL (`Span`). Widen the `SINCE` window |
| Trace not found | Trace ID invalid or expired | Traces retained ~8 days. Verify ID format. Try NerdGraph `distributedTracing` query |
| Wrong account data | Querying wrong account | Use `newrelic nerdgraph query '{ actor { accounts { id name } } }'` and pass explicit `account_id` |
| 401 Unauthorized | Invalid or expired API key | Verify key starts with `NRAK-`. Regenerate if needed |
| 403 Forbidden | Insufficient permissions | User role lacks required access. Contact NR admin |
| Timeout on NRQL | Query too broad | Add more WHERE filters, reduce SINCE window, add LIMIT |
| Partial data | Account ID mismatch | App may report to a sub-account. Check available accounts |

---

## Detailed Troubleshooting

### 0. Access Mode Not Working

**Problem:** No access mode (CLI or curl) is producing results.

**Diagnostic steps:**

1. **CLI failing?** Run `which newrelic` — if not found, it's not installed. Fall back to Mode 2 (curl). If installed, check `newrelic profile list` for configured profiles.
2. **Curl failing?** Check `echo $NEW_RELIC_API_KEY` — if empty, the env var is not set. Guide setup via `references/api-key-setup.md` (Steps 1-3 only, takes 2 minutes).
3. **Getting 401?** The API key is invalid. Verify it starts with `NRAK-`. Regenerate if needed.
4. **No credentials at all?** Do NOT ask the user for keys in chat. Guide them to set up credentials locally via `references/api-key-setup.md`.

**Quick test for Mode 1 (CLI):**

```bash
newrelic profile list
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query 'SELECT count(*) FROM Transaction SINCE 1 hour ago'
```

**Quick test for Mode 2 (curl):**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "{ actor { accounts { id name } } }"}' | jq .
```

If either returns data, the corresponding mode is working. Use `references/nerdgraph-direct.md` for curl equivalents of all operations.

### 1. Empty Results from Error Queries

**Problem:** Error queries (`TransactionError` or OTEL `Span`) return no data, but the user knows errors exist.

**Diagnostic steps:**

1. **Verify the app name is exact.** Search for the entity via NerdGraph entity search or CLI `newrelic entity search`. App names are case-sensitive and must match exactly.
2. **Check instrumentation type.** If the app doesn't appear in APM, it may be an OTEL service. Run `SELECT uniques(service.name) FROM Span WHERE service.name LIKE '%...' SINCE 1 day ago` to check.
3. **Widen the time range.** The error may have occurred outside the queried window. Try `SINCE 7 days ago`.
4. **Check the account.** List accounts and try passing `account_id` explicitly.

**Common confusion:** APM errors are in `TransactionError` (with `appName`). OTEL errors are in `Span` (with `service.name` and `otel.status_code = 'ERROR'`). Using the wrong event type returns empty results with no error.

### 2. NRQL Query Returns No Data

**Problem:** A NRQL query runs successfully but returns 0 results.

**Diagnostic steps:**

1. **Check the event type.** APM apps use `Transaction` and `TransactionError`. OTEL services use `Span`. Using the wrong one returns nothing.
2. **Check the WHERE clause:**
   - APM: `WHERE appName = '...'` (uses `appName`)
   - OTEL: `WHERE service.name = '...'` (uses `service.name`)
   - Logs: `WHERE service.name = '...'` (also uses `service.name`)
3. **Check the SINCE clause.** Default is 1 hour. If the event happened yesterday, you need `SINCE 2 days ago`.
4. **Check string quoting.** Values in WHERE must be in single quotes: `WHERE appName = 'my-app'`.
5. **Simplify the query.** Remove all filters and try: `SELECT count(*) FROM Transaction SINCE 1 day ago` — if this returns data, add filters back one at a time.

### 3. APM vs OTEL Confusion

**Problem:** User doesn't know if their service uses APM or OpenTelemetry instrumentation.

**How to detect automatically:**

1. Search for the entity via NerdGraph entity search (filter by `domain = 'APM'`).
   - If it returns data → APM service. Use `appName` in NRQL queries.
   - If it returns empty → likely OTEL or doesn't exist.
2. Check for OTEL: `SELECT uniques(service.name) FROM Span WHERE service.name LIKE '%...' SINCE 1 day ago`
   - If found → OTEL service. Use `service.name` in NRQL queries.
3. If neither finds it → the service may not be instrumented, or it may report to a different account.

**Key differences:**

| Aspect | APM | OpenTelemetry |
| --- | --- | --- |
| NRQL filter | `appName = '...'` | `service.name = '...'` |
| Transaction data | `FROM Transaction` | `FROM Span WHERE span.kind = 'SERVER'` |
| Error data | `FROM TransactionError` | `FROM Span WHERE otel.status_code = 'ERROR'` |
| Entity search domain | `domain = 'APM'` | `domain = 'EXT'` or NRQL-based detection |

### 4. Trace Lookup Failures

**Problem:** Trace lookup via NerdGraph `distributedTracing` returns no data for a given trace ID.

**Diagnostic steps:**

1. **Check trace ID format.** It should be a hex string (e.g., `abc123def456`). Remove any prefixes or URL encoding.
2. **Check retention.** Traces are retained for approximately 8 days. Older traces are gone.
3. **Use NerdGraph.** Use the `distributedTracing` query (see `references/nerdgraph-direct.md` section 9) — it works for both APM and OTEL traces.
4. **Check the account.** The trace may belong to a different account/sub-account.
5. **Extract from URL.** If the user pasted a New Relic URL, extract the trace ID from the path. It's usually the last segment after `/trace/`.

### 5. Log Visibility Issues

**Problem:** Log queries return no data or incomplete data.

**Diagnostic steps:**

1. **Verify service.name.** Log forwarding must include `service.name` attribute. Not all log configurations do this.
2. **Check log forwarding setup.** The application must be configured to send logs to New Relic (via agent log forwarding, Fluentd, Fluent Bit, etc.).
3. **Try a broader filter.** Start with just `service.name = '...'` without level or message filters.
4. **Check log retention.** Log retention depends on the New Relic plan. Some plans retain logs for only 8 days.
5. **Use NRQL directly.** Try: `SELECT * FROM Log WHERE service.name = '...' SINCE 1 hour ago LIMIT 10`

### 6. Alert and Incident Issues

**Problem:** Incident queries show no incidents, but alerts are configured.

**Diagnostic steps:**

1. **No open incidents is good.** If no conditions are currently violated, there are no open incidents. This doesn't mean alerts aren't configured.
2. **Check alert policies.** Use NerdGraph `policiesSearch` query to verify policies exist.
3. **Check the account.** Alert policies are account-scoped. Verify you're checking the right account.
4. **Historical incidents.** Open incidents only show currently active violations. For historical data, use NRQL: `SELECT * FROM NrAiIncident SINCE 7 days ago`

### 7. Performance Query Anomalies

**Problem:** Latency numbers seem wrong or inconsistent.

**Diagnostic steps:**

1. **Check transaction type.** Web transactions and background transactions have very different latency profiles. Filter with: `WHERE transactionType = 'Web'` or `WHERE transactionType = 'Other'`
2. **Check for sampling.** High-throughput apps may use sampling, which can skew percentiles. Increase the SINCE window for more data points.
3. **Exclude health checks.** Endpoints like `/health` or `/ping` have near-zero latency and drag down averages. Filter with: `WHERE name NOT LIKE '%health%'`
4. **Compare apples to apples.** When comparing periods, ensure both have similar traffic volume. Low-traffic periods have more volatile metrics.

---

## Error Recovery Strategies

When a tool fails, follow this escalation path:

1. **Retry once** — transient network errors are common
2. **Check parameters** — verify app name, account ID, time range
3. **Try alternative approach** — use NRQL directly instead of specialized tools
4. **Widen scope** — remove filters, increase time range, check other accounts
5. **Explain to user** — if still failing, explain what you tried and suggest manual verification in the New Relic UI

## Useful Diagnostic Queries

### Check if an app exists in any form

```sql
SELECT uniques(appName) FROM Transaction WHERE appName LIKE '%{partial_name}%' SINCE 1 day ago
```

### Check if an OTEL service exists

```sql
SELECT uniques(service.name) FROM Span WHERE service.name LIKE '%{partial_name}%' SINCE 1 day ago
```

### Check what event types have data

```sql
SELECT count(*) FROM Transaction, TransactionError, Span, Log SINCE 1 hour ago FACET eventType()
```

### Check available attributes for an event type

```sql
SELECT keyset() FROM Transaction WHERE appName = '{app_name}' SINCE 1 hour ago
```
