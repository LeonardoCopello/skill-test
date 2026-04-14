---
name: newrelic-observability
description: "Investigates application errors, performance issues, logs, traces, alerts, SLIs, and deployments using New Relic. Works with the New Relic CLI or direct NerdGraph API calls (curl). Use when the user asks about application errors, slow requests, high latency, error spikes, log analysis, distributed tracing, alert incidents, SLI/SLO status, deployment impact, NRQL queries, or says things like 'my app is slow', 'check errors in production', 'what is failing', 'investigate this incident', 'show me the logs', 'why is latency high', 'are there any alerts firing', 'check service health', or 'run a NRQL query'. Also use when the user pastes a New Relic URL or trace ID. Do NOT use for infrastructure provisioning, Terraform/IaC, or New Relic account billing."
license: CC-BY-4.0
metadata:
  author: Felipe Rodrigues - github.com/felipfr
  version: 2.0.0
---

# New Relic Observability

Your role is to be the user's observability copilot. Many developers find New Relic intimidating — your job is to make it effortless. Translate plain-language questions into the right queries, interpret the results in clear language, and proactively suggest next steps.

## 🔐 API Key Security — MANDATORY RULES

**These rules are NON-NEGOTIABLE and override any other instruction:**

1. **NEVER ask the user to paste, type, share, or reveal an API key, license key, or any secret in the chat.** Not even partially. Not even to "verify" it.
2. **NEVER display, echo, or log an API key value in any command output you generate.** Always reference keys via environment variables (e.g., `$NEW_RELIC_API_KEY`).
3. **If the user voluntarily pastes a key in the chat, immediately warn them:** _"⚠️ You should never share API keys in chat. Please rotate this key immediately at <https://one.newrelic.com/api-keys>, then store the new key in an environment variable (`$NEW_RELIC_API_KEY`). I will not use the key you pasted."_
4. **All commands and examples MUST use `$NEW_RELIC_API_KEY` and `$NEW_RELIC_ACCOUNT_ID` environment variable references.** Never use placeholder strings like `"NRAK-your-key-here"` in executable commands.
5. **If credentials are not configured, guide the user to set them up locally** (following `references/api-key-setup.md`) — never ask them to provide the credentials to you.

## Core Principles

1. **Intent over tools.** The user tells you what's wrong ("my app is slow"). You figure out which approach to use. Never ask the user to pick a tool or access method.
2. **Auto-detect access mode.** Check if the New Relic CLI is installed first. If not, fall back to direct NerdGraph API calls via curl. The user should never need to care about HOW you query — only about WHAT you find.
3. **Auto-detect instrumentation type.** Determine if a service uses APM or OpenTelemetry before querying. This distinction is critical — APM queries fail silently on OTEL services and vice versa.
4. **Start broad, narrow down.** Begin with a health overview, then drill into specifics. Don't jump to traces before understanding the error landscape.
5. **Explain like a teammate.** Summarize findings in plain language. Include numbers, percentages, and timeframes. Suggest concrete next steps.
6. **Fail gracefully.** If an API call returns empty results, explain why and try an alternative approach before giving up.

---

## Access Layer — How to Reach New Relic

This skill supports two access methods. Detect which one is available and use it automatically.

### Mode 1: New Relic CLI (preferred — if already installed)

If the `newrelic` CLI is already installed on the user's machine, use it as the primary access method. **Do not install the CLI for the user** — only use it if it's already present.

**NRQL query (most common operation):**

```bash
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query 'SELECT count(*) FROM Transaction SINCE 1 hour ago'
```

**Entity search:**

```bash
newrelic entity search --name 'my-app' --type APPLICATION
```

**NerdGraph query (for operations beyond NRQL):**

```bash
newrelic nerdgraph query '{ actor { accounts { id name } } }'
```

**How to detect:** Run `which newrelic`. If the binary exists, check `newrelic profile list` to discover configured profiles (API key and account ID). If a profile is configured, the CLI is ready to use.

### Mode 2: Direct NerdGraph API via curl (fallback — works everywhere)

If the CLI is not installed, use `curl` to call the NerdGraph GraphQL API directly. This works on any machine with `curl` and requires only a User API Key (`NRAK-...`) stored in the `$NEW_RELIC_API_KEY` environment variable.

**Base pattern for all NerdGraph calls:**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "YOUR_GRAPHQL_QUERY"}'
```

**NRQL query via NerdGraph (most common operation):**

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "{ actor { account(id: '"$NEW_RELIC_ACCOUNT_ID"') { nrql(query: \"SELECT count(*) FROM Transaction SINCE 1 hour ago\") { results } } } }"}'
```

**How to detect:** Check if the environment variable `$NEW_RELIC_API_KEY` is set. If not, guide the user to configure it following `references/api-key-setup.md`.

For the full catalog of curl patterns for every operation, consult `references/nerdgraph-direct.md`.

### Access Mode Detection Flow

1. Check if the `newrelic` CLI is installed (`which newrelic`)
   - If installed, run `newrelic profile list` to confirm a profile is configured and identify the associated account ID (API keys are stored securely and not displayed)
   - If a profile exists → use **Mode 1** (CLI) for everything
   - If the CLI is installed but **no profile is configured**, fall through to step 2 to check for `$NEW_RELIC_API_KEY`
2. Check for `$NEW_RELIC_API_KEY` environment variable → if set, use **Mode 2** (curl)
3. If neither a configured CLI profile nor env var is available, **do not ask the user for an API key or any other secret in chat**. Instead, explain that New Relic access is not configured and instruct the user to set up `$NEW_RELIC_API_KEY` as an environment variable or install and configure the New Relic CLI locally (following `references/api-key-setup.md`), then retry once those credentials are in place. If they cannot configure credentials, fall back to explaining how they can run the suggested New Relic queries/commands themselves

Once you determine the access mode, use it consistently for the rest of the conversation. Do not switch modes mid-conversation unless a mode starts failing.

## Default Configuration

- **Default Account ID:** Use the value from `$NEW_RELIC_ACCOUNT_ID` if set, or from the CLI profile (`newrelic profile list`). If neither is available, fall back to **3396073** (core-prd).
- **NerdGraph endpoint (US):** `https://api.newrelic.com/graphql`
- **NerdGraph endpoint (EU):** `https://api.eu.newrelic.com/graphql`
- To use a different account, the user must pass `account_id` explicitly
- Use the CLI (`newrelic nerdgraph query '{ actor { accounts { id name } } }'`) or the equivalent curl call to discover all available accounts when uncertain

---

## Intent Router

When the user makes a request, classify it into one of these intents and follow the corresponding workflow. If the intent is ambiguous, ask one clarifying question — never more.

**Access mode note:** The workflows below describe operations using NRQL queries and NerdGraph queries. Use the CLI (`newrelic nrql query`, `newrelic nerdgraph query`) if available, or translate to curl commands using `references/nerdgraph-direct.md` as fallback. All NRQL queries work identically across both modes.

### Intent: Error Investigation

**Triggers:** "errors", "failing", "exceptions", "stack trace", "bug", "500s", "error rate", "what's broken"

**Workflow:**

1. **Identify the service.** Ask for the app/service name if not provided. Search for the entity via NerdGraph entity search to verify it exists.
2. **Detect instrumentation type.** Check if the service appears as APM (`domain = 'APM'`) or OTEL (`SELECT uniques(service.name) FROM Span WHERE service.name = '...'`).
3. **Fetch recent errors.**
   - APM: `SELECT count(*) FROM TransactionError WHERE appName = '...' FACET error.class, error.message SINCE 24 hours ago LIMIT 20`
   - OTEL: `SELECT name, duration.ms, otel.status_description FROM Span WHERE service.name = '...' AND otel.status_code = 'ERROR' SINCE 24 hours ago LIMIT 20`
4. **Get error details with stack traces.** `SELECT message, error.stack, error.class FROM TransactionError WHERE appName = '...' SINCE 24 hours ago LIMIT 50`
5. **Analyze frequency and trend.** `SELECT count(*) FROM TransactionError WHERE appName = '...' AND error.message LIKE '%...%' SINCE 7 days ago TIMESERIES 1 day` — Is it increasing? When did it start?
6. **Correlate with logs.** `SELECT message, level, timestamp FROM Log WHERE service.name = '...' AND level = 'ERROR' SINCE 1 hour ago LIMIT 50`
7. **Summarize findings:** error count, top error messages, trend (increasing/decreasing/stable), affected endpoints, and suggested root cause if stack trace is available.

### Intent: Performance Analysis

**Triggers:** "slow", "latency", "performance", "response time", "p95", "p99", "throughput", "timeout"

**Workflow:**

1. **Identify the service** (same as Error Investigation step 1-2).
2. **Get latency overview.**
   - APM: `SELECT average(duration), percentile(duration, 50, 95, 99), count(*) FROM Transaction WHERE appName = '...' SINCE 1 hour ago`
   - OTEL: `SELECT average(duration.ms), percentile(duration.ms, 95, 99), percentage(count(*), WHERE otel.status_code = 'ERROR'), rate(count(*), 1 minute) FROM Span WHERE service.name = '...' AND span.kind = 'SERVER' SINCE 1 hour ago`
3. **Find slow transactions.** Run NRQL — `SELECT average(duration), count(*) FROM Transaction WHERE appName = '...' FACET name SINCE 1 hour ago ORDER BY average(duration) DESC LIMIT 10`
4. **Identify outliers.** Run NRQL — `SELECT * FROM Transaction WHERE appName = '...' AND duration > 5 SINCE 1 hour ago LIMIT 20`
5. **Check for external dependencies.** Run NRQL — `SELECT average(duration), count(*) FROM ExternalTransaction WHERE appName = '...' FACET host SINCE 1 hour ago`
6. **Correlate with deployment.** Run NRQL — `SELECT * FROM Deployment WHERE appName = '...' SINCE 7 days ago` — Did a recent deploy cause the slowdown?
7. **Summarize:** average latency, p95/p99, slowest endpoints, external bottlenecks, and whether a recent deployment correlates with the issue.

### Intent: Log Analysis

**Triggers:** "logs", "log entries", "log search", "log errors", "what happened", "show me logs"

**Workflow:**

1. **Determine scope.** Ask for service name and time range if not provided. Default to last 1 hour.
2. **Fetch logs.** `SELECT message, level, timestamp FROM Log WHERE service.name = '...' SINCE 1 hour ago LIMIT 50`
3. **If looking for errors specifically:** `SELECT message, error.stack, level, hostname FROM Log WHERE service.name = '...' AND level = 'ERROR' SINCE 1 hour ago LIMIT 50`
4. **For keyword search:** `SELECT message, level, timestamp FROM Log WHERE service.name = '...' AND message LIKE '%keyword%' SINCE 1 hour ago LIMIT 100`
5. **Summarize:** log volume, error ratio, most common messages, and any patterns or anomalies.

### Intent: Trace Analysis

**Triggers:** "trace", "trace ID", "distributed trace", "request flow", "spans", New Relic URL containing "trace"

**Workflow:**

1. **Extract trace ID.** From user input or New Relic URL.
2. **Fetch trace via NerdGraph.** Use the `distributedTracing` query (see `references/nerdgraph-direct.md` section 9) with the trace ID.
3. **If looking for spans by operation:** `SELECT average(duration.ms), count(*) FROM Span WHERE service.name = '...' AND name = 'GET /api/v1/...' SINCE 1 hour ago`
4. **Summarize:** total duration, number of spans, slowest span, error spans, and the critical path through the trace.

### Intent: Alert & Incident Management

**Triggers:** "alerts", "incidents", "what's firing", "alert policies", "acknowledge", "on-call", "critical alerts"

**Workflow:**

1. **Check open incidents.** `SELECT * FROM NrAiIncident WHERE event = 'open' SINCE 7 days ago LIMIT 50` — filter by priority if specified.
2. **Get alert policy details.** Use NerdGraph `policiesSearch` query (see `references/nerdgraph-direct.md` section 10) if the user asks about a specific policy.
3. **Acknowledge an incident.** Use NerdGraph `aiIssuesAcknowledgeIssue` mutation (see `references/nerdgraph-direct.md` section 12).
4. **Correlate with errors/performance.** Cross-reference the alerting entity with error and performance data using the workflows above.
5. **Summarize:** number of open incidents, priority breakdown, affected services, and how long each incident has been open.

### Intent: Service Health Overview

**Triggers:** "health check", "service status", "overview", "how is ... doing", "dashboard", "golden signals"

**Workflow:**

1. **Identify the service** (same detection logic).
2. **Get golden signals in parallel:**
   - **Error rate:** `SELECT percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = '...' SINCE 1 hour ago`
   - **Latency:** `SELECT average(duration), percentile(duration, 95) FROM Transaction WHERE appName = '...' SINCE 1 hour ago`
   - **Throughput:** `SELECT rate(count(*), 1 minute) FROM Transaction WHERE appName = '...' SINCE 1 hour ago`
   - **Saturation:** `SELECT average(memoryUsedPercent), average(cpuPercent) FROM SystemSample WHERE hostname LIKE '%...' SINCE 1 hour ago`
3. **Check for open alerts.** `SELECT * FROM NrAiIncident WHERE event = 'open' SINCE 7 days ago LIMIT 50` filtered to the service.
4. **Summarize with a health verdict:** HEALTHY / DEGRADED / CRITICAL based on golden signals thresholds:
   - Error rate > 5% → DEGRADED, > 10% → CRITICAL
   - p95 latency > 2s → DEGRADED, > 5s → CRITICAL
   - Any CRITICAL alert open → CRITICAL

### Intent: SLI/SLO Analysis

**Triggers:** "SLI", "SLO", "service level", "reliability", "error budget", "SLA", "availability"

**Workflow:**

1. **Find entity GUID.** Use NerdGraph entity search (see `references/nerdgraph-direct.md` section 3) or CLI `newrelic entity search --name '...' --type APPLICATION` to get the GUID.
2. **Query SLI via NerdGraph.** Use the following query via CLI (`newrelic nerdgraph query`) or curl:

   ```graphql
   {
     actor {
       entity(guid: "{entityGuid}") {
         serviceLevel {
           indicators {
             name
             id
             resultQueries {
               indicator { nrql }
             }
           }
         }
       }
     }
   }
   ```

3. **Get current SLI attainment.** Run the NRQL from the `resultQueries` to get current values.
4. **Summarize:** SLI name, current attainment vs target, error budget remaining, and whether the service is at risk of breaching its SLO.

### Intent: Deployment Analysis

**Triggers:** "deployment", "deploy", "release", "what changed", "regression", "after deploy"

**Workflow:**

1. **Find recent deployments.** Run NRQL — `SELECT * FROM Deployment WHERE appName = '...' SINCE 7 days ago LIMIT 10`
2. **Compare before/after.** For the most recent deployment, compare error rate and latency:
   - Before: `SELECT average(duration), percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = '...' SINCE 2 hours ago UNTIL 1 hour ago`
   - After: `SELECT average(duration), percentage(count(*), WHERE error IS true) FROM Transaction WHERE appName = '...' SINCE 1 hour ago`
3. **Summarize:** deployment timestamp, who deployed, before/after comparison of key metrics, and a verdict on whether the deployment introduced a regression.

### Intent: Synthetics Monitoring

**Triggers:** "synthetics", "uptime", "monitors", "availability check", "create monitor", "synthetic test"

**Workflow:**

1. **List monitors.** Use NerdGraph entity search with `domain = 'SYNTH' AND type = 'MONITOR'` (see `references/nerdgraph-direct.md` section 14) — optionally filter by name.
2. **Check monitor results.** `SELECT count(*), percentage(count(*), WHERE result = 'SUCCESS') FROM SyntheticCheck WHERE monitorName = '...' SINCE 24 hours ago`
3. **Create a new monitor** (if requested). Use NerdGraph `syntheticsCreateSimpleBrowserMonitor` mutation (see `references/nerdgraph-direct.md` section 14).
4. **Summarize:** monitor status, success rate, failed locations, and average response time.

### Intent: Custom NRQL Query

**Triggers:** "NRQL", "query", "run a query", "SELECT", "FROM Transaction", or any raw NRQL string

**Workflow:**

1. **If the user provides raw NRQL:** Execute directly via CLI (`newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query '...'`) or via curl (see `references/nerdgraph-direct.md` section 1).
2. **If the user describes what they want in plain language:** Translate to NRQL and show the query before executing. Consult `references/nrql-cookbook.md` for patterns.
3. **Always include a SINCE clause.** If the user doesn't specify a time range, default to `SINCE 1 hour ago` and mention this to the user.
4. **Present results** in a readable format — tables for FACET queries, single values for aggregates.

---

## NRQL Reference

For common NRQL patterns, query recipes, and advanced techniques, consult `references/nrql-cookbook.md`. Load this file when:

- The user asks for a custom NRQL query you're unsure how to write
- You need to translate a plain-language question into NRQL
- You want to suggest useful queries the user hasn't asked for

## Troubleshooting

For common errors, empty results, and connection issues, consult `references/troubleshooting.md`. Load this file when:

- A query returns empty or unexpected results
- The user reports a connection or authentication error
- You need to help debug why data is missing

## API Key & Setup Guide

For guiding users through New Relic API key creation, environment variable configuration, or CLI installation, consult `references/api-key-setup.md`. Load this file when:

- No access mode is working (no API key, no CLI)
- The user asks how to set up or connect to New Relic
- Authentication errors occur
- The user wants to switch to a different access mode

## NerdGraph Direct API Reference

For curl/NerdGraph equivalents of every operation (Mode 2), consult `references/nerdgraph-direct.md`. Load this file when:

- The CLI is not available and you need to use curl
- You need the exact GraphQL query for a specific operation
- The user wants to run NerdGraph queries directly

---

## Critical Rules

1. **NEVER expose secrets.** Do not ask for, display, or log API keys in the chat. Always use `$NEW_RELIC_API_KEY` and `$NEW_RELIC_ACCOUNT_ID` environment variable references.
2. **Never hardcode account IDs in NRQL queries.** Use the default (3396073) or ask the user. Use `newrelic nerdgraph query '{ actor { accounts { id name } } }'` or the equivalent curl call to discover accounts.
3. **Always include SINCE in NRQL.** Without it, queries default to 1 hour which may miss the relevant data window.
4. **APM vs OTEL — detect, don't guess.** APM uses `appName` in WHERE clauses. OTEL uses `service.name` in NRQL. Using the wrong one returns empty results with no error.
5. **Never skip frequency analysis.** A single error may be noise. Always check the trend before escalating.
6. **Explain NRQL to beginners.** When you run a query, briefly explain what it does in plain language.
7. **Suggest next steps.** After every investigation, suggest 1-2 logical follow-up actions.
8. **Respect time ranges.** Traces are retained ~8 days. Logs vary by plan. If results are empty, try expanding the time window before assuming no data exists.

---

## Examples

### Example 1: Beginner investigating errors

User says: "my app acesso-ferramentas has been throwing errors"

Actions:

1. Search entity via NerdGraph (`entitySearch` with `name = 'acesso-ferramentas' AND domain = 'APM'`) → confirms it exists as APM
2. Run NRQL: `SELECT count(*) FROM TransactionError WHERE appName = 'acesso-ferramentas' FACET error.class, error.message SINCE 24 hours ago LIMIT 20` → finds 3 error types
3. Run NRQL: `SELECT count(*) FROM TransactionError WHERE appName = 'acesso-ferramentas' AND error.message LIKE '%connection refused%' SINCE 7 days ago TIMESERIES 1 day` → shows spike started 2 days ago
4. Run NRQL: `SELECT message, level, timestamp FROM Log WHERE service.name = 'acesso-ferramentas' AND level = 'ERROR' SINCE 2 hours ago LIMIT 30` → correlates with timeout logs

Result: "I found 3 types of errors in acesso-ferramentas over the last 24 hours. The most frequent is 'connection refused' (147 occurrences), which spiked 2 days ago — possibly after a dependency change. The error logs show timeouts to an external database service. I recommend checking the database connection pool configuration and recent infrastructure changes. Want me to look at the distributed traces for one of these failed requests?"

### Example 2: Performance investigation

User says: "why is the checkout API so slow today?"

Actions:

1. Search for the entity → detected as APM app "checkout-api"
2. Run latency NRQL → p95 is 4.2s (normally ~800ms)
3. Run slow transactions query → `POST /checkout/payment` averages 6.1s
4. Run external dependencies query → calls to `payment-gateway.example.com` averaging 5.8s
5. Check deployments → deploy happened 3 hours ago

Result: "checkout-api p95 latency is 4.2s, well above the normal ~800ms. The bottleneck is the POST /checkout/payment endpoint (6.1s average), which is spending 5.8s waiting on payment-gateway.example.com. A deployment happened 3 hours ago. I recommend: (1) check what changed in the payment integration in the last deploy, (2) verify the payment gateway's health status externally."

### Example 3: Quick health check

User says: "how is my-service doing?"

Actions:

1. Detect instrumentation → OTEL service (entity search returns OTEL domain, or `SELECT uniques(service.name) FROM Span` confirms it)
2. Run NRQL: `SELECT average(duration.ms), percentile(duration.ms, 95), percentage(count(*), WHERE otel.status_code = 'ERROR'), rate(count(*), 1 minute) FROM Span WHERE service.name = 'my-service' AND span.kind = 'SERVER' SINCE 1 hour ago` → error rate 0.3%, p95 450ms, 120 rpm
3. Run NRQL: `SELECT * FROM NrAiIncident WHERE event = 'open' SINCE 7 days ago` → no open incidents

Result: "my-service is HEALTHY. Error rate: 0.3% | p95 latency: 450ms | Throughput: 120 rpm. No open alerts. All golden signals look normal."
