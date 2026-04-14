# NerdGraph Direct API Reference (curl)

Use this file when Mode 2 (Direct NerdGraph API) is the active access mode (CLI not available). Each section documents the curl/NerdGraph equivalent for common operations.

All commands assume these environment variables are set:

```bash
export NEW_RELIC_API_KEY="<your-api-key>"   # Replace with key from New Relic → Profile → API Keys — never paste the real key here
export NEW_RELIC_ACCOUNT_ID="3396073"
```

**Base curl pattern** (all calls follow this structure):

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "YOUR_GRAPHQL_QUERY"}'
```

For EU region accounts, replace `api.newrelic.com` with `api.eu.newrelic.com`.

---

## Table of Contents

1. NRQL Query
2. List Accounts
3. Entity Search
4. Get Entity Details
5. Application Info (APM)
6. List APM Applications
7. Get Errors / Transaction Errors
8. Get Logs
9. Get Trace
10. Alert Policies
11. Open Incidents
12. Acknowledge Incident
13. SLI/SLO Query
14. Synthetics Monitors
15. Create Deployment Marker
16. OpenTelemetry Services
17. Arbitrary NerdGraph Query

---

## 1. NRQL Query

**CLI equivalent:** `newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query '...'`

This is the most common operation. Nearly every workflow step that uses NRQL can be done with this single pattern.

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { account(id: '"$NEW_RELIC_ACCOUNT_ID"') { nrql(query: \"SELECT count(*) FROM Transaction SINCE 1 hour ago\") { results } } } }"
  }'
```

**With a specific account ID:**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { account(id: 3396073) { nrql(query: \"SELECT average(duration) FROM Transaction WHERE appName = '"'"'my-app'"'"' SINCE 1 hour ago\") { results } } } }"
  }'
```

**Tip:** For complex NRQL with single quotes inside (like `WHERE appName = 'my-app'`), use the `'"'"'` pattern to escape single quotes in bash, or use the `jq` variable approach below.

**Variable + jq approach (recommended — works in all shell contexts):**

```bash
NRQL="SELECT count(*) FROM TransactionError WHERE appName = 'my-app' FACET error.message SINCE 24 hours ago"

curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "$(jq -n --arg acct "$NEW_RELIC_ACCOUNT_ID" --arg nrql "$NRQL" \
    '{ query: "{ actor { account(id: \($acct)) { nrql(query: \($nrql | tojson)) { results } } } }" }')"
```

This approach avoids all quoting issues by letting `jq` handle the JSON escaping.

**Heredoc approach (alternative — may not work in all shell contexts, e.g. IDE-embedded terminals):**

```bash
read -r -d '' QUERY << 'EOF'
{
  actor {
    account(id: ACCOUNT_ID) {
      nrql(query: "SELECT count(*) FROM TransactionError WHERE appName = 'my-app' FACET error.message SINCE 24 hours ago") {
        results
      }
    }
  }
}
EOF

QUERY="${QUERY//ACCOUNT_ID/$NEW_RELIC_ACCOUNT_ID}"

curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d "{\"query\": $(echo "$QUERY" | jq -Rs .)}"
```

> **Note:** The heredoc approach uses `read -r -d ''` which may fail silently in non-interactive shells or IDE-embedded terminals (returns exit code 1). If you encounter this, use the variable + jq approach above.

---

## 2. List Accounts

**CLI equivalent:** `newrelic nerdgraph query '{ actor { accounts { id name } } }'`

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { accounts { id name } } }"
  }'
```

---

## 3. Entity Search

**CLI equivalent:** `newrelic entity search --name '...' --type APPLICATION`

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entitySearch(query: \"name LIKE '"'"'my-app'"'"' AND type = '"'"'APPLICATION'"'"'\") { results { entities { guid name type domain accountId tags { key values } } } } } }"
  }'
```

**Search by domain (APM, INFRA, etc.):**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entitySearch(query: \"domain = '"'"'APM'"'"' AND tags.accountId = '"'"''"$NEW_RELIC_ACCOUNT_ID"''"'"'\") { results { entities { guid name type accountId } } } } }"
  }'
```

> **Note:** Use `tags.accountId = '<id>'` (with quotes around the value) instead of `accountId = <id>`. The bare `accountId` filter in entity search may return empty results even for valid accounts.

**Search by tags:**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entitySearch(query: \"tags.environment = '"'"'production'"'"'\") { results { entities { guid name type domain } } } } }"
  }'
```

---

## 4. Get Entity Details

**CLI equivalent:** `newrelic entity describe --guid 'YOUR_ENTITY_GUID'`

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entity(guid: \"YOUR_ENTITY_GUID\") { name type domain accountId tags { key values } ... on ApmApplicationEntity { apmSummary { apdexScore errorRate hostCount instanceCount responseTimeAverage throughput } } ... on BrowserApplicationEntity { browserSummary { ajaxRequestThroughput jsErrorRate pageLoadThroughput } } } } }"
  }'
```

---

## 5. Application Info (APM)

**CLI equivalent:** `newrelic apm application search --name 'my-app' --accountId $NEW_RELIC_ACCOUNT_ID`

Use entity search filtered by APM domain:

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entitySearch(query: \"name = '"'"'my-app'"'"' AND domain = '"'"'APM'"'"'\") { results { entities { guid name ... on ApmApplicationEntity { apmSummary { apdexScore errorRate hostCount instanceCount responseTimeAverage throughput } language runningAgentVersions { maxVersion minVersion } } } } } } }"
  }'
```

---

## 6. List APM Applications

**CLI equivalent:** `newrelic apm application search --accountId $NEW_RELIC_ACCOUNT_ID`

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entitySearch(query: \"domain = '"'"'APM'"'"' AND type = '"'"'APPLICATION'"'"' AND accountId = '"$NEW_RELIC_ACCOUNT_ID"'\") { results { entities { guid name tags { key values } ... on ApmApplicationEntity { apmSummary { errorRate responseTimeAverage throughput } } } } } } }"
  }'
```

---

## 7. Get Errors / Transaction Errors

**Operation:** Get errors and transaction errors for an APM application

Use NRQL queries via the pattern in Section 1:

**Recent errors by type:**

```sql
SELECT count(*) FROM TransactionError WHERE appName = 'my-app' FACET error.class, error.message SINCE 24 hours ago LIMIT 20
```

**Errors with stack traces:**

```sql
SELECT message, error.stack, error.class FROM TransactionError WHERE appName = 'my-app' SINCE 24 hours ago LIMIT 50
```

**Errors filtered by message:**

```sql
SELECT timestamp, error.class, error.message, error.stack, request.uri FROM TransactionError WHERE appName = 'my-app' AND error.message LIKE '%timeout%' SINCE 24 hours ago LIMIT 20
```

**Error frequency over time:**

```sql
SELECT count(*) FROM TransactionError WHERE appName = 'my-app' AND error.message LIKE '%connection refused%' SINCE 7 days ago TIMESERIES 1 day
```

---

## 8. Get Logs

**Operation:** Fetch logs for a service

Use NRQL:

```sql
SELECT timestamp, level, message FROM Log WHERE service.name = 'my-app' AND level = 'ERROR' SINCE 1 hour ago LIMIT 50
```

---

## 9. Get Trace

**Operation:** Fetch distributed trace by trace ID

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { distributedTracing { trace(traceId: \"YOUR_TRACE_ID\") { spans { spanId operationName durationMs startTimeMs attributes { key value } } } } } }"
  }'
```

---

## 10. Alert Policies

**Operation:** List alert policies

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { account(id: '"$NEW_RELIC_ACCOUNT_ID"') { alerts { policiesSearch { policies { id name incidentPreference } } } } } }"
  }'
```

**Filter by name:**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { account(id: '"$NEW_RELIC_ACCOUNT_ID"') { alerts { policiesSearch(searchCriteria: { nameLike: \"my-policy\" }) { policies { id name incidentPreference } } } } } }"
  }'
```

---

## 11. Open Incidents

**Operation:** List open incidents

Use NRQL to query incidents:

```sql
SELECT * FROM NrAiIncident WHERE event = 'open' SINCE 7 days ago LIMIT 50
```

Or via NerdGraph:

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { account(id: '"$NEW_RELIC_ACCOUNT_ID"') { aiIssues { issues(filter: { states: [ACTIVATED, CREATED] }) { issues { issueId title state priority activatedAt sources { conditionName } } } } } } }"
  }'
```

---

## 12. Acknowledge Incident

**Operation:** Acknowledge an incident

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "mutation { aiIssuesAcknowledgeIssue(accountId: '"$NEW_RELIC_ACCOUNT_ID"', issueId: \"YOUR_ISSUE_ID\") { result } }"
  }'
```

---

## 13. SLI/SLO Query

**Operation:** Query SLI/SLO indicators for an entity

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entity(guid: \"YOUR_ENTITY_GUID\") { serviceLevel { indicators { name id objectives { target timeWindow { rolling { count unit } } } resultQueries { indicator { nrql } } } } } } }"
  }'
```

---

## 14. Synthetics Monitors

**Operation:** List and manage synthetics monitors

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "{ actor { entitySearch(query: \"domain = '"'"'SYNTH'"'"' AND type = '"'"'MONITOR'"'"'\") { results { entities { guid name ... on SyntheticMonitorEntity { monitorType period monitoredUrl } } } } } }"
  }'
```

**Create a simple browser monitor:**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "mutation { syntheticsCreateSimpleBrowserMonitor(accountId: '"$NEW_RELIC_ACCOUNT_ID"', monitor: { name: \"My Monitor\", uri: \"https://example.com\", period: EVERY_15_MINUTES, status: ENABLED, locations: { public: [\"AWS_US_EAST_1\"] } }) { monitor { guid name status } } }"
  }'
```

---

## 15. Create Deployment Marker

**Operation:** Create a deployment marker

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{
    "query": "mutation { changeTrackingCreateDeployment(deployment: { version: \"1.2.3\", entityGuid: \"YOUR_ENTITY_GUID\", description: \"Deployment via API\", user: \"deploy-bot\", commit: \"abc123\" }) { entityGuid deploymentId } }"
  }'
```

---

## 16. OpenTelemetry Services

**Operation:** List and summarize OpenTelemetry services

**List OTEL services:**

```sql
SELECT uniques(service.name) FROM Span WHERE otel.library.name IS NOT NULL SINCE 1 hour ago
```

**Service summary (latency, errors, throughput):**

```sql
SELECT average(duration.ms) AS 'Avg Latency (ms)', percentile(duration.ms, 95) AS 'p95 (ms)', percentage(count(*), WHERE otel.status_code = 'ERROR') AS 'Error Rate', rate(count(*), 1 minute) AS 'RPM' FROM Span WHERE service.name = 'my-service' AND span.kind = 'SERVER' SINCE 1 hour ago
```

**OTEL errors:**

```sql
SELECT name, duration.ms, otel.status_description FROM Span WHERE service.name = 'my-service' AND otel.status_code = 'ERROR' SINCE 24 hours ago LIMIT 20
```

**OTEL spans by operation:**

```sql
SELECT average(duration.ms), count(*) FROM Span WHERE service.name = 'my-service' FACET name SINCE 1 hour ago ORDER BY average(duration.ms) DESC LIMIT 10
```

---

## 17. Arbitrary NerdGraph Query

**CLI equivalent:** `newrelic nerdgraph query '...'`

For any NerdGraph operation not listed above, use the base curl pattern with your GraphQL query, or the CLI `newrelic nerdgraph query` command. The NerdGraph API explorer at `https://api.newrelic.com/graphiql` can help you build and test queries interactively.

---

## Tips for curl Usage

- **Parse JSON output:** Pipe curl output through `jq` for readable results: `curl ... | jq '.data.actor.account.nrql.results'`
- **Escape single quotes in NRQL:** Use `'"'"'` in bash or switch to the heredoc pattern shown in Section 1
- **Batch queries:** NerdGraph supports multiple queries in a single request — useful for the Service Health Overview workflow where you need error rate, latency, and throughput simultaneously
- **Rate limits:** NerdGraph allows up to 25 concurrent queries per user. Avoid tight loops with no delay
- **Error responses:** NerdGraph returns HTTP 200 even for errors. Always check the `errors` field in the JSON response
