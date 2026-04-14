# New Relic Setup Guide

Guide for connecting to New Relic from your IDE or terminal. Covers both access methods: New Relic CLI and Direct API (curl). Read this file when the user needs help connecting to New Relic or when authentication errors occur.

> **🔐 SECURITY REMINDER:** NEVER share, paste, or reveal API keys in chat messages. All commands below use environment variable references (`$NEW_RELIC_API_KEY`). If a user attempts to share a key, warn them immediately and instruct them to rotate it.

## Which Setup Do I Need?

| I want to... | Fastest path | Setup time |
| --- | --- | --- |
| Use CLI for NRQL queries, scripts, or CI/CD | **New Relic CLI** (Mode 1) | 1 min (existing install) or 5 min (fresh install) |
| Just query NR from my terminal right now | **API key + env var** (Mode 2 — curl) | 2 minutes |

**Recommendation:** If the `newrelic` CLI is already installed, configure a profile (Step 4) and you're ready. Otherwise, start with the API key setup (Steps 1-3) for immediate curl access.

---

## Step 1: Create a New Relic User API Key

1. Log in to [New Relic](https://one.newrelic.com)
2. Click on your profile icon (bottom-left corner) → **API Keys**
3. Or navigate directly to: `https://one.newrelic.com/api-keys`
4. Click **Create a key**
5. Select **Key type: User**
6. Add a description (e.g., "CLI / API Integration")
7. Click **Create a key**
8. **Copy the key immediately** — it starts with `NRAK-` and won't be shown again

### Key Type Explanation

| Key Type | Use Case | Format |
| --- | --- | --- |
| **User API Key** (recommended) | NerdGraph API, NRQL, full access scoped to your permissions | `NRAK-...` |
| License Key | Data ingest (agents, OTEL) — NOT for querying | Alphanumeric |
| Browser Key | Browser agent only — NOT for API queries | Alphanumeric |

**Always use a User API Key for any New Relic API access.** License and Browser keys will not work with NerdGraph or the CLI.

---

## Step 2: Find Your Account ID

1. In New Relic, click on your profile icon → **Account settings**
2. Or look at any New Relic URL — the account ID is in the path: `https://one.newrelic.com/nr1-core?account={ACCOUNT_ID}`
3. Default for this organization: **3396073** (core-prd)

To discover all available accounts programmatically (after setup):

```bash
newrelic nerdgraph query '{ actor { accounts { id name } } }'
```

---

## Step 3: Configure Environment Variables

### 🔐 Security Best Practices — MANDATORY

**NEVER** do these:

- **NEVER paste, type, or share API keys in chat messages, AI assistants, tickets, or documentation**
- NEVER hardcode API keys in source code or config files committed to git
- NEVER use the same API key across multiple environments
- NEVER send API keys over unencrypted channels

**ALWAYS** do these:

- **ALWAYS store API keys in environment variables or CLI profiles — never in plain text**
- ALWAYS use a secrets manager for production environments
- ALWAYS rotate keys periodically (every 90 days recommended)
- ALWAYS use the minimum required permissions
- ALWAYS add `.envrc` and similar files to `.gitignore`

### Setting Environment Variables

#### Option A: Shell Profile (persistent, personal machine only)

Add to `~/.zshrc` or `~/.bashrc`:

```bash
export NEW_RELIC_API_KEY="<your-api-key>"   # Replace with key from New Relic → Profile → API Keys (never paste the real key here)
export NEW_RELIC_ACCOUNT_ID="3396073"
```

Then reload:

```bash
source ~/.zshrc
```

#### Option B: direnv (recommended for projects)

Create a `.envrc` file in your project root:

```bash
export NEW_RELIC_API_KEY="<your-api-key>"   # Replace with key from New Relic → Profile → API Keys (never commit the real key)
export NEW_RELIC_ACCOUNT_ID="3396073"
```

**CRITICAL:** Add `.envrc` to your `.gitignore` to prevent committing secrets:

```bash
echo ".envrc" >> .gitignore
```

Then allow the file:

```bash
direnv allow
```

#### Option C: IDE terminal

Set environment variables in your IDE's integrated terminal settings. This keeps keys scoped to your IDE and not exposed in shell history.

---

## Step 4: Install & Configure New Relic CLI (Mode 1)

The New Relic CLI is the preferred access method. It stores credentials in local profiles (never in chat) and provides a rich set of commands for NRQL queries, entity management, and NerdGraph operations.

**Install via Homebrew (macOS):**

```bash
brew install newrelic-cli
```

**Install via binary (Linux/Windows):** Download from [github.com/newrelic/newrelic-cli/releases](https://github.com/newrelic/newrelic-cli/releases)

**Configure a profile:**

```bash
newrelic profile add --profile default --region US --apiKey $NEW_RELIC_API_KEY --accountId $NEW_RELIC_ACCOUNT_ID
```

**List configured profiles:**

```bash
newrelic profile list
```

**Set default profile:**

```bash
newrelic profile default --profile default
```

**Test:**

```bash
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query 'SELECT count(*) FROM Transaction SINCE 1 hour ago'
```

---

## Step 5: Verify Your Setup

Test whichever mode you configured:

**Mode 1 (CLI):**

```bash
newrelic profile list
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query 'SELECT count(*) FROM Transaction SINCE 1 hour ago'
```

**Mode 2 (curl):** Run this in your terminal:

```bash
curl -s -X POST https://api.newrelic.com/graphql \
  -H 'Content-Type: application/json' \
  -H "API-Key: $NEW_RELIC_API_KEY" \
  -d '{"query": "{ actor { accounts { id name } } }"}' | jq .
```

If any of these return account/query data, you're connected.

---

## Troubleshooting Connection Issues

### "401 Unauthorized" or "Invalid API key"

1. Verify the key starts with `NRAK-`
2. Check for extra whitespace or quotes around the key value
3. Generate a new key if the current one may have been revoked
4. Ensure the key belongs to the correct account

### "403 Forbidden" or "Access Denied"

1. Your user role may not have sufficient permissions
2. Check with your New Relic admin for role-based access
3. User API keys inherit the permissions of the user who created them

### Empty results but no errors

1. Verify the account ID matches the account where your apps report data
2. Use `newrelic nerdgraph query '{ actor { accounts { id name } } }'` or the equivalent curl call to check available accounts
3. The app may report to a different sub-account

### Region considerations

- US region (default): `https://api.newrelic.com/graphql`
- EU region: `https://api.eu.newrelic.com/graphql`
- If your account is in the EU region, set `NEW_RELIC_REGION="EU"` environment variable for the CLI, or use `api.eu.newrelic.com` for curl calls

---

## Key Rotation Procedure

1. Create a new User API Key in New Relic
2. Update the key in your environment variables and/or CLI profile
3. Verify the new key works: `newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query 'SELECT count(*) FROM Transaction SINCE 1 hour ago'`
4. Delete the old key in New Relic's API Keys page
5. Record the rotation date for compliance tracking
