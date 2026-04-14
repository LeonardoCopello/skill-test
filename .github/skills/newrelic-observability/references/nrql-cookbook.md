# NRQL Cookbook

Ready-to-use NRQL patterns organized by use case. When a user asks a plain-language question, find the matching pattern, adapt the placeholders, and execute.

## Table of Contents

1. Error Analysis
2. Performance & Latency
3. Throughput & Traffic
4. Log Analysis
5. Deployment Impact
6. SLI/SLO Queries
7. Infrastructure
8. OpenTelemetry Specific
9. Comparison & Trend
10. Advanced Patterns

---

## 1. Error Analysis

### Errors by endpoint

```sql
SELECT count(*) FROM TransactionError
WHERE appName = '{app_name}'
FACET request.uri
SINCE {timerange}
```

### Error count by type and message

```sql
SELECT count(*) FROM TransactionError
WHERE appName = '{app_name}'
FACET error.class, error.message
SINCE {timerange}
LIMIT 20
```

### Error rate as percentage

```sql
SELECT percentage(count(*), WHERE error IS true) AS 'Error Rate'
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
```

### Error rate over time (timeseries)

```sql
SELECT percentage(count(*), WHERE error IS true) AS 'Error Rate'
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
TIMESERIES AUTO
```

### Errors with stack traces

```sql
SELECT message, error.stack, error.class
FROM TransactionError
WHERE appName = '{app_name}'
SINCE {timerange}
LIMIT 50
```

### Error spike detection (compare with previous period)

```sql
SELECT count(*) FROM TransactionError
WHERE appName = '{app_name}'
SINCE 1 hour ago
COMPARE WITH 1 hour ago OFFSET 1 day
```

### Top errors by user impact

```sql
SELECT uniqueCount(user) AS 'Affected Users', count(*) AS 'Occurrences'
FROM TransactionError
WHERE appName = '{app_name}'
FACET error.message
SINCE {timerange}
LIMIT 10
```

---

## 2. Performance & Latency

### Latency overview (avg, p50, p95, p99)

```sql
SELECT average(duration), percentile(duration, 50, 95, 99), count(*)
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
```

### Slowest transactions

```sql
SELECT average(duration), max(duration), count(*)
FROM Transaction
WHERE appName = '{app_name}'
FACET name
SINCE {timerange}
ORDER BY average(duration) DESC
LIMIT 10
```

### Slow outlier transactions (individual requests)

```sql
SELECT timestamp, name, duration, request.uri
FROM Transaction
WHERE appName = '{app_name}' AND duration > {threshold_seconds}
SINCE {timerange}
LIMIT 20
```

### External service latency (dependency analysis)

```sql
SELECT average(duration), count(*), percentile(duration, 95)
FROM ExternalTransaction
WHERE appName = '{app_name}'
FACET host
SINCE {timerange}
ORDER BY average(duration) DESC
```

### Database query performance

```sql
SELECT average(duration), count(*)
FROM DatabaseTransaction
WHERE appName = '{app_name}'
FACET name
SINCE {timerange}
ORDER BY average(duration) DESC
LIMIT 10
```

### Latency trend over time

```sql
SELECT average(duration), percentile(duration, 95)
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
TIMESERIES AUTO
```

---

## 3. Throughput & Traffic

### Requests per minute

```sql
SELECT rate(count(*), 1 minute) AS 'RPM'
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
```

### Throughput by endpoint

```sql
SELECT rate(count(*), 1 minute) AS 'RPM'
FROM Transaction
WHERE appName = '{app_name}'
FACET name
SINCE {timerange}
ORDER BY RPM DESC
LIMIT 10
```

### Throughput over time

```sql
SELECT rate(count(*), 1 minute) AS 'RPM'
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
TIMESERIES AUTO
```

### HTTP status code distribution

```sql
SELECT count(*)
FROM Transaction
WHERE appName = '{app_name}'
FACET httpResponseCode
SINCE {timerange}
```

### Traffic by client/user-agent

```sql
SELECT count(*)
FROM Transaction
WHERE appName = '{app_name}'
FACET request.headers.userAgent
SINCE {timerange}
LIMIT 10
```

---

## 4. Log Analysis

### Error logs with context

```sql
SELECT message, error.stack, level, hostname
FROM Log
WHERE service.name = '{service_name}' AND level = 'ERROR'
SINCE {timerange}
LIMIT 100
```

### Log volume by level

```sql
SELECT count(*)
FROM Log
WHERE service.name = '{service_name}'
FACET level
SINCE {timerange}
```

### Log keyword search

```sql
SELECT message, level, timestamp
FROM Log
WHERE service.name = '{service_name}' AND message LIKE '%{keyword}%'
SINCE {timerange}
LIMIT 100
```

### Log volume over time (detect spikes)

```sql
SELECT count(*)
FROM Log
WHERE service.name = '{service_name}'
SINCE {timerange}
TIMESERIES AUTO
```

### Error log trend

```sql
SELECT count(*)
FROM Log
WHERE service.name = '{service_name}' AND level IN ('ERROR', 'FATAL')
SINCE {timerange}
TIMESERIES AUTO
```

---

## 5. Deployment Impact

### Recent deployments

```sql
SELECT *
FROM Deployment
WHERE appName = '{app_name}'
SINCE 7 days ago
LIMIT 10
```

### Before vs after deployment (error rate)

```sql
-- Run these two separately and compare:

-- BEFORE (1 hour window before deploy)
SELECT percentage(count(*), WHERE error IS true) AS 'Error Rate Before'
FROM Transaction
WHERE appName = '{app_name}'
SINCE '{deploy_time_minus_1h}' UNTIL '{deploy_time}'

-- AFTER (1 hour window after deploy)
SELECT percentage(count(*), WHERE error IS true) AS 'Error Rate After'
FROM Transaction
WHERE appName = '{app_name}'
SINCE '{deploy_time}' UNTIL '{deploy_time_plus_1h}'
```

### Before vs after deployment (latency)

```sql
-- BEFORE
SELECT average(duration), percentile(duration, 95)
FROM Transaction
WHERE appName = '{app_name}'
SINCE '{deploy_time_minus_1h}' UNTIL '{deploy_time}'

-- AFTER
SELECT average(duration), percentile(duration, 95)
FROM Transaction
WHERE appName = '{app_name}'
SINCE '{deploy_time}' UNTIL '{deploy_time_plus_1h}'
```

---

## 6. SLI/SLO Queries

### Availability SLI (success rate)

```sql
SELECT percentage(count(*), WHERE error IS false) AS 'Availability'
FROM Transaction
WHERE appName = '{app_name}'
SINCE 7 days ago
```

### Latency SLI (requests under threshold)

```sql
SELECT percentage(count(*), WHERE duration < {threshold_seconds}) AS 'Latency SLI'
FROM Transaction
WHERE appName = '{app_name}'
SINCE 7 days ago
```

### Error budget consumption

```sql
SELECT 100 - percentage(count(*), WHERE error IS false) AS 'Error Budget Used (%)'
FROM Transaction
WHERE appName = '{app_name}'
SINCE 30 days ago
```

### SLI trend over time

```sql
SELECT percentage(count(*), WHERE error IS false) AS 'Availability'
FROM Transaction
WHERE appName = '{app_name}'
SINCE 30 days ago
TIMESERIES 1 day
```

---

## 7. Infrastructure

### Host CPU and memory

```sql
SELECT average(cpuPercent), average(memoryUsedPercent)
FROM SystemSample
WHERE hostname LIKE '%{hostname_pattern}%'
SINCE {timerange}
```

### Disk usage

```sql
SELECT average(diskUsedPercent)
FROM SystemSample
WHERE hostname LIKE '%{hostname_pattern}%'
FACET hostname
SINCE {timerange}
```

### Container metrics (Kubernetes)

```sql
SELECT average(cpuUsedCores), average(memoryWorkingSetBytes / 1e6) AS 'Memory MB'
FROM K8sContainerSample
WHERE containerName = '{container_name}'
SINCE {timerange}
TIMESERIES AUTO
```

### Pod restart count

```sql
SELECT max(restartCount)
FROM K8sContainerSample
WHERE podName LIKE '%{pod_pattern}%'
FACET podName
SINCE {timerange}
```

---

## 8. OpenTelemetry Specific

### OTEL service latency

```sql
SELECT average(duration.ms), percentile(duration.ms, 95, 99)
FROM Span
WHERE service.name = '{service_name}' AND span.kind = 'SERVER'
SINCE {timerange}
```

### OTEL error rate

```sql
SELECT percentage(count(*), WHERE otel.status_code = 'ERROR') AS 'Error Rate'
FROM Span
WHERE service.name = '{service_name}' AND span.kind = 'SERVER'
SINCE {timerange}
```

### OTEL spans by operation

```sql
SELECT average(duration.ms), count(*)
FROM Span
WHERE service.name = '{service_name}'
FACET name
SINCE {timerange}
ORDER BY average(duration.ms) DESC
LIMIT 10
```

### OTEL error details

```sql
SELECT name, duration.ms, otel.status_description
FROM Span
WHERE service.name = '{service_name}' AND otel.status_code = 'ERROR'
SINCE {timerange}
LIMIT 20
```

### OTEL throughput

```sql
SELECT rate(count(*), 1 minute) AS 'RPM'
FROM Span
WHERE service.name = '{service_name}' AND span.kind = 'SERVER'
SINCE {timerange}
TIMESERIES AUTO
```

---

## 9. Comparison & Trend

### Compare with previous period

```sql
SELECT count(*), average(duration)
FROM Transaction
WHERE appName = '{app_name}'
SINCE 1 hour ago
COMPARE WITH 1 day ago
```

### Week-over-week comparison

```sql
SELECT count(*), average(duration), percentage(count(*), WHERE error IS true)
FROM Transaction
WHERE appName = '{app_name}'
SINCE 1 week ago
COMPARE WITH 1 week ago
```

### Anomaly detection (standard deviation)

```sql
SELECT average(duration) AS 'avg', stddev(duration) AS 'stddev'
FROM Transaction
WHERE appName = '{app_name}'
SINCE 24 hours ago
TIMESERIES 1 hour
```

---

## 10. Advanced Patterns

### Multi-app correlation

```sql
SELECT average(duration)
FROM Transaction
WHERE appName IN ('{app1}', '{app2}', '{app3}')
FACET appName
SINCE {timerange}
TIMESERIES AUTO
```

### Apdex score

```sql
SELECT apdex(duration, {threshold})
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
```

### Funnel analysis (multi-step transaction)

```sql
SELECT funnel(session,
  WHERE name = 'WebTransaction/Action/home' AS 'Home',
  WHERE name = 'WebTransaction/Action/cart' AS 'Cart',
  WHERE name = 'WebTransaction/Action/checkout' AS 'Checkout'
)
FROM Transaction
WHERE appName = '{app_name}'
SINCE {timerange}
```

### Unique users affected by errors

```sql
SELECT uniqueCount(user), count(*)
FROM TransactionError
WHERE appName = '{app_name}'
SINCE {timerange}
FACET error.message
```

### Custom event query template

```sql
SELECT count(*), average({numeric_attribute})
FROM {custom_event_type}
WHERE {filter_condition}
FACET {grouping_attribute}
SINCE {timerange}
```

---

## Placeholder Reference

| Placeholder | Description | Example |
| --- | --- | --- |
| `{app_name}` | APM application name (exact match) | `'checkout-api'` |
| `{service_name}` | OTEL service name (used in `service.name`) | `'payment-service'` |
| `{timerange}` | NRQL time range clause | `1 hour ago`, `24 hours ago`, `7 days ago` |
| `{threshold_seconds}` | Duration threshold in seconds | `5`, `2`, `0.5` |
| `{keyword}` | Log search keyword | `timeout`, `connection refused` |
| `{hostname_pattern}` | Hostname pattern for LIKE clause | `prod-web` |
| `{deploy_time}` | Deployment timestamp | `'2025-01-15 14:30:00'` |

## NRQL Tips for Beginners

- **SINCE is required** — Always specify a time range. Without it, NR defaults to 1 hour which may miss your data.
- **FACET = GROUP BY** — Use FACET to break down results by a dimension (endpoint, error type, host, etc.).
- **TIMESERIES** — Adds time dimension to see trends. Use `TIMESERIES AUTO` to let NR pick the best interval.
- **COMPARE WITH** — Compares current period with a previous one. Great for detecting regressions.
- **LIMIT** — Default is 10 for FACET queries. Increase it if you need more results.
- **Event types matter:**
  - `Transaction` → APM web/background transactions
  - `TransactionError` → APM errors
  - `Span` → OpenTelemetry spans
  - `Log` → Log entries
  - `SystemSample` → Infrastructure host metrics
  - `K8sContainerSample` → Kubernetes container metrics
  - `Deployment` → Deployment markers
  - `SyntheticCheck` → Synthetic monitor results
